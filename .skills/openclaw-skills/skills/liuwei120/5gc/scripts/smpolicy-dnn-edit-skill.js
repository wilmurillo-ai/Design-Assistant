/**
 * smpolicy-dnn-edit-skill.js - DNN Smpolicy 编辑工具
 *
 * 用法：
 *   node smpolicy-dnn-edit-skill.js --project XW_SUPF_5_1_2_4 --name dnn_policy1 --dnn internet_new
 *   node smpolicy-dnn-edit-skill.js --project XW_SUPF_5_1_2_4 --name dnn_policy1 --pcc-rules pcc2,pcc_default
 *
 * 参数：
 *   --project       工程名（默认 XW_S5GC_1）
 *   --name          DNN策略名称（精确匹配，要编辑的策略）
 *   --dnn           新 DNN 值（可选）
 *   --sst           新 sNssai SST（可选）
 *   --sd            新 sNssai SD（可选）
 *   --sess-rules    会话规则（xm-select，多个逗号分隔）
 *   --pcc-rules     PCC规则（xm-select，多个逗号分隔）
 *   --pra-rules     PRA规则（xm-select，可选）
 *   --ref-qos-timer reflectiveQoSTimer（秒）
 *   --headed        显示浏览器窗口
 *
 * 编辑页：/sim_5gc/smpolicy/dnn/edit/{id}（直接渲染在主页面，非 iframe）
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    project: 'XW_S5GC_1',
    name: null,
    dnn: null, sst: null, sd: null,
    sessRules: null, pccRules: null, praRules: null,
    refQosTimer: null,
    headed: false,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--name') opts.name = args[++i];
    else if (args[i] === '--dnn') opts.dnn = args[++i];
    else if (args[i] === '--sst') opts.sst = args[++i];
    else if (args[i] === '--sd') opts.sd = args[++i];
    else if (args[i] === '--sess-rules') opts.sessRules = args[++i];
    else if (args[i] === '--pcc-rules') opts.pccRules = args[++i];
    else if (args[i] === '--pra-rules') opts.praRules = args[++i];
    else if (args[i] === '--ref-qos-timer') opts.refQosTimer = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  if (!opts.name) { console.error('❌ 缺少 --name 参数'); process.exit(1); }
  return opts;
}

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
  const found = await page.evaluate((n) => {
    let result = false;
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) {
        cells[1].querySelector('.iconfont')?.click();
        result = true;
      }
    });
    return result;
  }, name);
  if (!found) { console.error(`❌ 未找到工程: ${name}`); process.exit(1); }
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${name}" 已选`);
}

async function xmSelectChooseOne(target, page, index, value) {
  if (!value) return;

  await target.evaluate((idx) => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[idx]) inputs[idx].parentElement.click();
  }, index);
  await page.waitForTimeout(1000);

  const clicked = await target.evaluate((text) => {
    const opts = document.querySelectorAll('.xm-option');
    for (const opt of opts) {
      if (opt.textContent.trim() === text) {
        opt.click();
        return true;
      }
    }
    return false;
  }, value);

  if (clicked) {
    console.log(`   ✅ xm-select[${index}] += ${value}`);
  } else {
    console.log(`   ⚠️ xm-select[${index}] 未找到: ${value}`);
  }

  await page.waitForTimeout(500);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
}

async function main() {
  const opts = parseArgs();
  const browser = await chromium.launch({ headless: !opts.headed, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);

  // ① 去列表页找数字 ID
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/dnn/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const dnnInfo = await page.evaluate((targetName) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 8 && cells[2].textContent.trim() === targetName) {
        return { id: cells[1].textContent.trim(), name: cells[2].textContent.trim() };
      }
    }
    return null;
  }, opts.name);

  if (!dnnInfo) {
    console.error(`❌ 未找到 DNN Smpolicy: ${opts.name}`);
    process.exit(1);
  }
  console.log(`✅ 找到 DNN Smpolicy "${opts.name}"，数字ID=${dnnInfo.id}`);

  // ② 直接导航到编辑页（主页面渲染，无 iframe）
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/dnn/edit/${dnnInfo.id}`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  console.log(`✅ 进入编辑页面`);

  // ③ 修改文本字段（只处理提供的字段）
  const textFields = [
    { name: 'name', value: opts.name },
    { name: 'dnn', value: opts.dnn },
    { name: 'sNssai[sst]', value: opts.sst },
    { name: 'sNssai[sd]', value: opts.sd },
    { name: 'smPolicyDecision[reflectiveQoSTimer]', value: opts.refQosTimer },
  ];

  for (const f of textFields) {
    if (f.value !== null) {
      const loc = page.locator(`[name="${f.name}"]`).first();
      if (await loc.count() > 0) {
        await loc.fill(String(f.value));
        console.log(`   ✅ ${f.name} = "${f.value}"`);
      }
    }
  }

  // ④ xm-select（sessRules=idx0, pccRules=idx1, praRules=idx2）
  if (opts.sessRules) {
    const sessDisplay = await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[0]?.parentElement?.textContent || '');
    if (!sessDisplay.includes('暂无数据')) {
      for (const item of opts.sessRules.split(',').map(s => s.trim()).filter(Boolean)) {
        await xmSelectChooseOne(page, page, 0, item);
      }
    }
  }

  if (opts.pccRules) {
    for (const item of opts.pccRules.split(',').map(s => s.trim()).filter(Boolean)) {
      await xmSelectChooseOne(page, page, 1, item);
    }
  }

  if (opts.praRules) {
    const praDisplay = await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[2]?.parentElement?.textContent || '');
    if (!praDisplay.includes('暂无数据')) {
      for (const item of opts.praRules.split(',').map(s => s.trim()).filter(Boolean)) {
        await xmSelectChooseOne(page, page, 2, item);
      }
    }
  }

  // ⑤ 提交
  await page.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log('✅ 已提交');

  // ⑥ 验证
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/dnn/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const updated = await page.evaluate((targetName) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 8 && cells[2].textContent.trim() === targetName) {
        return {
          name: cells[2].textContent.trim(),
          dnn: cells[3].textContent.trim(),
          sst: cells[4].textContent.trim(),
          sd: cells[5].textContent.trim(),
          pccRules: cells[7].textContent.trim(),
        };
      }
    }
    return null;
  }, opts.name);

  if (updated) {
    console.log('\n📋 验证结果:');
    console.log(`   name     = ${updated.name}`);
    console.log(`   dnn      = ${updated.dnn} ${opts.dnn ? (updated.dnn === opts.dnn ? '✅' : '❌') : ''}`);
    console.log(`   pccRules = ${updated.pccRules}`);
  }

  console.log('\n✅ 完成');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
