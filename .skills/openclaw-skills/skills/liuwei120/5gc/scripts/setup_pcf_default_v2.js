/**
 * setup_pcf_default_v2.js - 为任意工程配置PCF默认规则（修复版）
 *
 * 修复内容：
 *   1. TC 创建：填写必填字段 flowStatus（SELECT）
 *   2. PCC 创建：正确选择所有 xm-select（refQosData, refTcData）
 *
 * 用法: node setup_pcf_default_v2.js --project XW_SUPF_SN4_5_2_8 [--headed]
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { project: null, headed: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  if (!opts.project) { console.error('❌ 缺少 --project'); process.exit(1); }
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

async function getUsed5qis(page) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const qis = await page.evaluate(() => {
    const set = new Set();
    document.querySelectorAll('.layui-table tbody tr').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 4) {
        const v = parseInt(cells[3].textContent.trim());
        if (!isNaN(v)) set.add(v);
      }
    });
    return [...set];
  });
  return qis;
}

function autoSelect5qi(usedQis) {
  const cands = [8, 9, 6, 5, 4, 3, 2, 1];
  for (const c of cands) if (!usedQis.includes(c)) return c;
  return 8;
}

// ─── 创建 QoS ──────────────────────────────────────────────────────────
async function addQos(page, opts) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(2000);
  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('❌ 未找到弹窗iframe'); return; }
  await frame.waitForTimeout(2000);

  await frame.locator('input[name="qosId"]').fill(String(opts.qosId));
  await frame.locator('input[name="5qi"]').fill(String(opts.qi));
  await frame.locator('input[name="maxbrUl"]').fill(String(opts.maxbrUl));
  await frame.locator('input[name="maxbrDl"]').fill(String(opts.maxbrDl));
  await frame.locator('input[name="gbrUl"]').fill(String(opts.gbrUl));
  await frame.locator('input[name="gbrDl"]').fill(String(opts.gbrDl));
  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ QoS ${opts.qosId} (5qi=${opts.qi})`);
}

// ─── 创建 TC ──────────────────────────────────────────────────────────
async function addTc(page, tcId) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/trafficCtl/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  // 检查是否已存在
  const exists = await page.evaluate((id) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (const c of cells) { if (c.textContent.trim() === id) return true; }
    }
    return false;
  }, tcId);
  if (exists) { console.log(`   ℹ️ TC ${tcId} 已存在，跳过`); return; }

  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);
  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('❌ TC弹窗iframe未找到'); return; }
  await frame.waitForLoadState('domcontentloaded');
  await frame.waitForTimeout(2000);

  // 填写 tcId
  await frame.locator('input[name="tcId"]').fill(tcId);
  console.log(`   tcId = ${tcId}`);

  // 通过 JS 直接设置 flowStatus 的值（避免 visibility 问题）
  const flowStatusSet = await frame.evaluate(() => {
    const sel = document.querySelector('select[name="flowStatus"]');
    if (!sel) return false;
    // 选择 "ENABLED" 或第一个非空选项
    const opts = Array.from(sel.options).map(o => o.value).filter(v => v && v !== '');
    if (opts.length > 0) {
      sel.value = opts[0];
      sel.dispatchEvent(new Event('change', { bubbles: true }));
      return opts[0];
    }
    return false;
  });
  console.log(`   flowStatus = ${flowStatusSet} (via JS)`);

  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  
  // 验证
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/trafficCtl/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const verify = await page.evaluate((id) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (const c of cells) { if (c.textContent.trim() === id) return true; }
    }
    return false;
  }, tcId);
  console.log(`   ${verify ? '✅' : '❌'} TC ${tcId} ${verify ? '创建成功' : '创建失败（请手动检查）'}`);
}

// ─── 创建 PCC ──────────────────────────────────────────────────────────
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

  // 逐个处理 xm-select（用 Playwright locator 直接点击可见选项）
  // xm-select[0] = refQosData, xm-select[1] = refTcData, xm-select[2] = refChgData, xm-select[3] = refUmData

  // refQosData = qosId
  await page.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[0]) inputs[0].parentElement.click();
  });
  await page.waitForTimeout(1000);
  const qos1Visible = await page.locator('.xm-option.show-icon', { hasText: opts.qosId }).isVisible({ timeout: 3000 }).catch(() => false);
  if (qos1Visible) {
    await page.locator('.xm-option.show-icon', { hasText: opts.qosId }).click();
    console.log(`   ✅ refQosData=${opts.qosId} 已选`);
  } else {
    console.log(`   ⚠️ refQosData=${opts.qosId} 选项不可见`);
  }
  await page.waitForTimeout(500);

  // refTcData = tcId
  await page.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[1]) inputs[1].parentElement.click();
  });
  await page.waitForTimeout(1000);
  const tcVisible = await page.locator('.xm-option.show-icon', { hasText: opts.tcId }).isVisible({ timeout: 3000 }).catch(() => false);
  if (tcVisible) {
    await page.locator('.xm-option.show-icon', { hasText: opts.tcId }).click();
    console.log(`   ✅ refTcData=${opts.tcId} 已选`);
  } else {
    console.log(`   ⚠️ refTcData=${opts.tcId} 选项不可见`);
  }
  await page.waitForTimeout(500);

  // refChgData — 如果有可选的
  await page.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[2]) inputs[2].parentElement.click();
  });
  await page.waitForTimeout(1000);
  const firstChgOpt = page.locator('.xm-option.show-icon').first();
  if (await firstChgOpt.isVisible({ timeout: 2000 }).catch(() => false)) {
    await firstChgOpt.click();
    console.log(`   ℹ️ refChgData 已选第一项`);
  }
  await page.waitForTimeout(500);

  await page.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ PCC ${opts.pccId} 已提交`);
}

// ─── 创建 sm_policy_default ────────────────────────────────────────────
async function addSmpolicyDefault(page, opts) {
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);
  await page.locator('iframe[name="layui-layer-iframe2"]').waitFor({ timeout: 5000 });
  const frame = page.frame('layui-layer-iframe2');
  await frame.waitForLoadState('domcontentloaded');
  await frame.waitForTimeout(1000);

  await frame.locator('input[name="name"]').fill(opts.name);

  // pccRules = xm-select[1] — 用 Playwright locator 点击
  await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[1]) inputs[1].parentElement.click();
  });
  await page.waitForTimeout(1000);
  const pccOpt = frame.locator('.xm-option.show-icon', { hasText: opts.pccId });
  if (await pccOpt.isVisible({ timeout: 3000 }).catch(() => false)) {
    await pccOpt.click();
    console.log(`   ✅ pccRules=${opts.pccId}`);
  } else {
    console.log(`   ⚠️ pccRules=${opts.pccId} 不可见`);
  }
  await page.waitForTimeout(500);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);

  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ sm_policy_default 已创建`);
}

// ─── 配置 PCF default_smpolicy ──────────────────────────────────────────
async function configurePcfDefaultSmpolicy(page, smpolicyName) {
  await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    if (rows.length > 0) {
      const links = rows[0].querySelectorAll('a');
      for (const l of links) { if (l.textContent.trim() === '编辑') { l.click(); return; } }
    }
  });
  await page.waitForTimeout(3000);
  await page.locator('iframe[name="layui-layer-iframe2"]').waitFor({ timeout: 5000 });
  const frame = page.frame('layui-layer-iframe2');
  await frame.waitForLoadState('domcontentloaded');
  await frame.waitForTimeout(1000);

  // default_smpolicy = xm-select[0]
  await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[0]) inputs[0].parentElement.click();
  });
  await page.waitForTimeout(1000);
  const smpOpt = frame.locator('.xm-option.show-icon', { hasText: smpolicyName });
  if (await smpOpt.isVisible({ timeout: 3000 }).catch(() => false)) {
    await smpOpt.click();
    console.log(`   ✅ default_smpolicy=${smpolicyName}`);
  } else {
    console.log(`   ⚠️ default_smpolicy=${smpolicyName} 不可见`);
  }
  await page.waitForTimeout(500);

  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ PCF default_smpolicy = ${smpolicyName}`);
}

// ─── 验证 ──────────────────────────────────────────────────────────────
async function verify(page, pccId, tcId) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const pccData = await page.evaluate((targetId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      // cells[5]=refQosData, cells[6]=refTcData
      if (cells.length >= 7 && cells[2].textContent.trim() === targetId) {
        return {
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
  const pccId = `pcc_default`;
  const tcId = `tc1`;
  const qosId = `qos1`;

  // 自动选5qi
  const browser = await chromium.launch({ headless: !opts.headed, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);

  console.log('\n📋 检测 5qi...');
  const usedQis = await getUsed5qis(page);
  const qi = autoSelect5qi(usedQis);
  console.log(`   已使用5qi: ${usedQis.join(', ')}，将使用 5qi=${qi}`);

  const params = {
    qosId, tcId, qi,
    maxbrUl: DEFAULT_BR.maxbrUl,
    maxbrDl: DEFAULT_BR.maxbrDl,
    gbrUl: DEFAULT_BR.gbrUl,
    gbrDl: DEFAULT_BR.gbrDl,
    pccId, name: 'sm_policy_default',
    precedence: null, // 默认63
  };

  console.log('\n📋 参数:');
  console.log(`   qosId=${qosId}, tcId=${tcId}, 5qi=${qi}`);
  console.log(`   maxbrUl=${params.maxbrUl}, maxbrDl=${params.maxbrDl}`);
  console.log(`   gbrUl=${params.gbrUl}, gbrDl=${params.gbrDl}`);

  console.log('\n📦 Step 1: QoS...');
  await addQos(page, params);

  console.log('\n📦 Step 2: TC...');
  await addTc(page, tcId);

  console.log('\n📦 Step 3: PCC...');
  await addPcc(page, params);

  console.log('\n📦 Step 4: sm_policy_default...');
  await addSmpolicyDefault(page, params);

  console.log('\n📦 Step 5: PCF default_smpolicy...');
  await configurePcfDefaultSmpolicy(page, params.name);

  console.log('\n📋 验证 PCC 规则:');
  const result = await verify(page, pccId, tcId);
  if (result) {
    console.log(`   pccRuleId  = ${result.pccRuleId}`);
    console.log(`   precedence = ${result.precedence}`);
    console.log(`   refQosData = ${result.refQosData} ${result.refQosData === qosId ? '✅' : '❌'}`);
    console.log(`   refTcData  = ${result.refTcData} ${result.refTcData === tcId ? '✅' : '❌'}`);
  } else {
    console.log('   ❌ 未找到 PCC 规则');
  }

  console.log('\n✅ 完成！');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });