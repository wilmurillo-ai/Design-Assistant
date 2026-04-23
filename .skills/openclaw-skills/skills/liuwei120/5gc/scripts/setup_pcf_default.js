/**
 * setup_pcf_default.js - 为任意工程配置PCF默认规则（完整版）
 *
 * 完整链路：
 *   1. 创建 QoS 模板（自动选不同5qi）
 *   2. 创建 Traffic Control 模板（tc1）
 *   3. 创建 PCC 规则，填写所有必填 xm-select
 *   4. 创建 sm_policy_default 并绑定 PCC
 *   5. 配置 PCF 的 default_smpolicy 下拉
 *
 * 用法: node setup_pcf_default.js --project XW_SUPF_SN4_5_2_8 [--qos-id qos1] [--tc-id tc1] [--5qi 8] \
 *       [--maxbr-ul 10000000 --maxbr-dl 20000000 --gbr-ul 5000000 --gbr-dl 5000000] [--headed]
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    project: null,
    qosId: 'qos1',
    tcId: 'tc1',
    qi: null,
    maxbrUl: null,
    maxbrDl: null,
    gbrUl: null,
    gbrDl: null,
    pccId: null,
    precedence: null,
    headed: false,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--qos-id') opts.qosId = args[++i];
    else if (args[i] === '--tc-id') opts.tcId = args[++i];
    else if (args[i] === '--5qi') opts.qi = args[++i];
    else if (args[i] === '--maxbr-ul') opts.maxbrUl = args[++i];
    else if (args[i] === '--maxbr-dl') opts.maxbrDl = args[++i];
    else if (args[i] === '--gbr-ul') opts.gbrUl = args[++i];
    else if (args[i] === '--gbr-dl') opts.gbrDl = args[++i];
    else if (args[i] === '--pcc-id') opts.pccId = args[++i];
    else if (args[i] === '--precedence') opts.precedence = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  if (!opts.project) {
    console.error('❌ 缺少 --project 参数');
    process.exit(1);
  }
  return opts;
}

const DEFAULT_BR = { maxbrUl: '10000000', maxbrDl: '20000000', gbrUl: '5000000', gbrDl: '5000000' };

async function login(page) {
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);
  console.log('✅ 登录成功');
}

async function selectProject(page, name) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.locator('input[name="project_search_name"]').fill(name);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  const clicked = await page.evaluate((n) => {
    const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) {
        cells[1].querySelector('.iconfont').click();
        return true;
      }
    }
    return false;
  }, name);
  if (!clicked) { console.log('❌ 选择工程失败'); process.exit(1); }
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${name}" 已选`);
}

// 获取已使用的5qi（排除空值）
async function getUsed5qis(page) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const qis = await page.evaluate(() => {
    const set = new Set();
    document.querySelectorAll('.layui-table tbody tr').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 4) {
        const v = cells[3].textContent.trim();
        if (v && !isNaN(parseInt(v))) set.add(parseInt(v));
      }
    });
    return [...set];
  });
  return qis;
}

function autoSelect5qi(usedQis) {
  const candidates = [8, 9, 6, 5, 4, 3, 2, 1];
  for (const c of candidates) {
    if (!usedQis.includes(c)) return c;
  }
  return 8;
}

// 通用xm-select选择函数
async function xmSelectChoose(page, index, optionText) {
  await page.evaluate((idx) => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[idx]) inputs[idx].parentElement.click();
  }, index);
  await page.waitForTimeout(1000);
  
  const result = await page.evaluate((text) => {
    const opts = document.querySelectorAll('.xm-option.show-icon');
    for (const opt of opts) {
      if (opt.textContent.trim() === text) {
        opt.click();
        return 'selected';
      }
    }
    return 'not_found';
  }, optionText);
  
  if (result === 'selected') {
    console.log(`   ✅ 选择 ${optionText}`);
  } else {
    console.log(`   ⚠️ 未找到选项: ${optionText}`);
  }
  await page.waitForTimeout(300);
}

// ─── 创建 QoS 模板 ────────────────────────────────────────────────────────
async function addQos(page, opts) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(2000);

  const iframe = page.locator('iframe[name="layui-layer-iframe2"]');
  const frame = (await iframe.count() > 0) ? page.frame('layui-layer-iframe2') : page;
  await frame.waitForTimeout(2000);

  await frame.locator('input[name="qosId"]').first().fill(String(opts.qosId));
  await frame.locator('input[name="5qi"]').first().fill(String(opts.qi));
  await frame.locator('input[name="maxbrUl"]').first().fill(String(opts.maxbrUl));
  await frame.locator('input[name="maxbrDl"]').first().fill(String(opts.maxbrDl));
  await frame.locator('input[name="gbrUl"]').first().fill(String(opts.gbrUl));
  await frame.locator('input[name="gbrDl"]').first().fill(String(opts.gbrDl));

  await frame.locator('button:has-text("提交")').first().click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ QoS模板 ${opts.qosId} 已创建 (5qi=${opts.qi})`);
}

// ─── 创建 Traffic Control 模板 ───────────────────────────────────────────
async function addTc(page, opts) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/trafficCtl/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  // 检查是否已存在
  const exists = await page.evaluate((id) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.trim() === id) return true;
      }
    }
    return false;
  }, opts.tcId);
  
  if (exists) {
    console.log(`   ℹ️ TC模板 ${opts.tcId} 已存在，跳过`);
    return;
  }

  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);

  const iframe = page.locator('iframe[name="layui-layer-iframe2"]');
  const frame = (await iframe.count() > 0) ? page.frame('layui-layer-iframe2') : page;
  await frame.waitForTimeout(2000);

  // 填写 tcId（必填）
  await frame.locator('input[name="tcId"]').first().fill(String(opts.tcId));
  console.log(`   tcId = ${opts.tcId}`);

  await frame.locator('button:has-text("提交")').first().click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ TC模板 ${opts.tcId} 已创建`);
}

// ─── 创建 PCC 规则（所有必填xm-select） ─────────────────────────────────
async function addPcc(page, opts) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);
  await page.waitForFunction(() => window.location.href.includes('/predfPolicy/pcc/edit'), { timeout: 10000 });
  await page.waitForTimeout(3000);

  // 填写文本字段
  await page.locator('input[name="pccRuleId"]').fill(String(opts.pccId));
  const precedence = opts.precedence !== null ? String(opts.precedence) : '63';
  await page.locator('input[name="precedence"]').fill(precedence);
  console.log(`   pccRuleId=${opts.pccId}, precedence=${precedence}`);

  // xm-select[0] = refQosData（QoS）
  await xmSelectChoose(page, 0, opts.qosId);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // xm-select[1] = refTcData（Traffic Control）
  await xmSelectChoose(page, 1, opts.tcId);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  // xm-select[2] = refChgData（Charging）—— 如果有可选的
  // 先检查是否有 Charging 选项
  const hasCharging = await page.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[2]) {
      inputs[2].parentElement.click();
    }
    return false;
  });
  await page.waitForTimeout(1000);
  
  const chargingOpts = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.xm-option.show-icon')).map(o => o.textContent.trim());
  });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
  
  if (chargingOpts.length > 0) {
    console.log(`   ℹ️ Charging 有选项: ${JSON.stringify(chargingOpts)}，尝试选择`);
    await xmSelectChoose(page, 2, chargingOpts[0]);
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
  }

  await page.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ PCC规则 ${opts.pccId} 已创建`);
}

// ─── 创建 sm_policy_default ────────────────────────────────────────────────
async function addSmpolicyDefault(page, opts) {
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);
  await page.locator('iframe[name="layui-layer-iframe2"]').waitFor({ timeout: 5000 });
  const frame = page.frame('layui-layer-iframe2');
  await frame.waitForLoadState('domcontentloaded');
  await frame.waitForTimeout(1000);

  // 填写名称
  await frame.locator('input[name="name"]').fill(String(opts.name));

  // smpolicy edit iframe 中 xm-select[1] = pccRules
  await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[1]) inputs[1].parentElement.click();
  });
  await frame.waitForTimeout(1000);
  
  await frame.evaluate((text) => {
    const opts2 = document.querySelectorAll('.xm-option.show-icon');
    for (const opt of opts2) {
      if (opt.textContent.trim() === text) { opt.click(); return; }
    }
  }, opts.pccId);
  
  await page.keyboard.press('Escape');
  await frame.waitForTimeout(500);

  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ sm_policy_default 已创建并绑定 ${opts.pccId}`);
}

// ─── 配置 PCF 的 default_smpolicy ────────────────────────────────────────
async function configurePcfDefaultSmpolicy(page, smpolicyName) {
  await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    if (rows.length > 0) {
      const links = rows[0].querySelectorAll('a');
      for (const l of links) {
        if (l.textContent.trim() === '编辑') { l.click(); return; }
      }
    }
  });
  await page.waitForTimeout(3000);
  await page.locator('iframe[name="layui-layer-iframe2"]').waitFor({ timeout: 5000 });
  const frame = page.frame('layui-layer-iframe2');
  await frame.waitForLoadState('domcontentloaded');
  await frame.waitForTimeout(1000);

  // default_smpolicy 下拉 = xm-select[0]
  await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[0]) inputs[0].parentElement.click();
  });
  await frame.waitForTimeout(1000);
  
  await frame.evaluate((text) => {
    const opts2 = document.querySelectorAll('.xm-option.show-icon');
    for (const opt of opts2) {
      if (opt.textContent.trim() === text) { opt.click(); return; }
    }
  }, smpolicyName);
  
  await page.keyboard.press('Escape');
  await frame.waitForTimeout(500);

  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ PCF default_smpolicy 已配置为 ${smpolicyName}`);
}

// ─── 验证 PCC 规则的 refQosData 和 refTcData ─────────────────────────────
async function verifyPcc(page, pccId) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const pccData = await page.evaluate((targetId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      // cells[2]=pccRuleId, cells[4]=precedence, cells[5]=refQosData, cells[6]=refTcData
      if (cells.length >= 7 && cells[2].textContent.trim() === targetId) {
        return {
          id: cells[1].textContent.trim(),
          pccRuleId: cells[2].textContent.trim(),
          precedence: cells[4].textContent.trim(),
          refQosData: cells[5].textContent.trim(),
          refTcData: cells[6].textContent.trim(),
        };
      }
    }
    return null;
  }, pccId);
  return pccData;
}

async function main() {
  const opts = parseArgs();
  const browser = await chromium.launch({ headless: !opts.headed, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);

  // 自动确定 5qi
  if (opts.qi === null) {
    console.log('\n📋 检测已有 QoS 模板的 5qi...');
    const usedQis = await getUsed5qis(page);
    opts.qi = autoSelect5qi(usedQis);
    console.log(`   已使用5qi: ${usedQis.join(', ')}，自动选择 5qi=${opts.qi}`);
  } else {
    console.log(`\n📋 用户指定 5qi = ${opts.qi}`);
  }

  const params = {
    qosId: opts.qosId,
    tcId: opts.tcId,
    qi: opts.qi,
    maxbrUl: opts.maxbrUl || DEFAULT_BR.maxbrUl,
    maxbrDl: opts.maxbrDl || DEFAULT_BR.maxbrDl,
    gbrUl: opts.gbrUl || DEFAULT_BR.gbrUl,
    gbrDl: opts.gbrDl || DEFAULT_BR.gbrDl,
    pccId: opts.pccId || `pcc_${opts.qosId}`,
    name: 'sm_policy_default',
    precedence: opts.precedence,
  };

  console.log('\n📋 最终参数:');
  console.log(`   qosId     = ${params.qosId} (5qi=${params.qi})`);
  console.log(`   tcId      = ${params.tcId}`);
  console.log(`   maxbrUl   = ${params.maxbrUl}`);
  console.log(`   maxbrDl   = ${params.maxbrDl}`);
  console.log(`   gbrUl     = ${params.gbrUl}`);
  console.log(`   gbrDl     = ${params.gbrDl}`);
  console.log(`   pccId     = ${params.pccId}`);

  // Step 1: 创建 QoS
  console.log('\n📦 Step 1: 创建 QoS 模板...');
  await addQos(page, params);

  // Step 2: 创建 TC
  console.log('\n📦 Step 2: 创建 Traffic Control 模板...');
  await addTc(page, params);

  // Step 3: 创建 PCC
  console.log('\n📦 Step 3: 创建 PCC 规则...');
  await addPcc(page, params);

  // Step 4: 创建 sm_policy_default
  console.log('\n📦 Step 4: 创建 sm_policy_default...');
  await addSmpolicyDefault(page, params);

  // Step 5: 配置 PCF default_smpolicy
  console.log('\n📦 Step 5: 配置 PCF default_smpolicy...');
  await configurePcfDefaultSmpolicy(page, params.name);

  // 验证
  console.log('\n📋 验证 PCC 规则...');
  const pccResult = await verifyPcc(page, params.pccId);
  if (pccResult) {
    console.log(`   pccRuleId  = ${pccResult.pccRuleId}`);
    console.log(`   precedence = ${pccResult.precedence}`);
    console.log(`   refQosData = ${pccResult.refQosData} ${pccResult.refQosData === params.qosId ? '✅' : '❌'}`);
    console.log(`   refTcData  = ${pccResult.refTcData} ${pccResult.refTcData === params.tcId ? '✅' : '❌'}`);
  }

  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const smp = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 6 && cells[2].textContent.trim() === 'sm_policy_default') {
        return cells[4].textContent.trim();
      }
    }
    return null;
  });
  console.log(`\n   sm_policy_default pccRules = ${smp}`);

  console.log('\n✅ 完成！');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });