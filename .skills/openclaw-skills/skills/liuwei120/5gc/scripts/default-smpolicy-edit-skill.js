/**
 * default-smpolicy-edit-skill.js - Default Smpolicy 配置修改技能
 *
 * 完整链路（只读模式）：
 *   读取 PCC规则 pcc2 的 flowDescription（直接导航到 /predfPolicy/pcc/edit/{id}）
 *   读取信令负载 dedicated 的 pcc_rule（直接导航到 /load/edit/{id}）
 *
 * 链路（修改模式）：
 *   PCC规则 /predfPolicy/pcc/edit/{id} → flowInfos[flowDescription][] 修改
 *   信令负载 /load/edit/{id} → process_conf[2][params][2][param_val] 修改
 *
 * 用法（读取）：
 *   node default-smpolicy-edit-skill.js --project XW_SUPF_5_1_2_4
 *
 * 用法（修改）：
 *   node default-smpolicy-edit-skill.js --project XW_SUPF_5_1_2_4
 *     --flow-desc "permit out ip from aaaa::203:9:121 to assigned"
 *     --load-ip "permit out ip from aaaa::203:9:121/24 to assigned"
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    project: 'XW_S5GC_1',
    flowDesc: null,        // PCC规则 flowDescription 新值
    loadIp: null,          // 信令负载 pcc_rule 新值
    loadName: 'dedicated', // 信令负载名称（默认 dedicated）
    pccRuleId: 'pcc2',    // PCC规则 ID
    headed: false,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--flow-desc') opts.flowDesc = args[++i];
    else if (args[i] === '--load-ip') opts.loadIp = args[++i];
    else if (args[i] === '--load-name') opts.loadName = args[++i];
    else if (args[i] === '--pcc-rule-id') opts.pccRuleId = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  return opts;
}

// ─── 登录 ───────────────────────────────────────────────────────────────
async function login(page) {
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);
  console.log('✅ 登录成功');
}

// ─── 选择工程 ───────────────────────────────────────────────────────────
async function selectProject(page, projectName) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  const clicked = await page.evaluate((name) => {
    const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === name) {
        const icon = cells[1].querySelector('.iconfont');
        if (icon) { icon.click(); return true; }
      }
    }
    return false;
  }, projectName);
  if (!clicked) {
    for (let p = 2; p <= 10; p++) {
      const nextBtn = document.querySelector('.jsgrid-pager a.jsgrid-pager-next');
      if (!nextBtn) break;
      nextBtn.click();
      await new Promise(r => setTimeout(r, 1000));
      const found = page.evaluate((n) => {
        const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
        for (const row of rows) {
          const cells = row.querySelectorAll('td');
          if (cells.length >= 3 && cells[2].textContent.trim() === n) {
            const icon = cells[1].querySelector('.iconfont');
            if (icon) { icon.click(); return true; }
          }
        }
        return false;
      }, projectName);
      if (found) break;
    }
  }
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${projectName}" 已选`);
}

// ─── 修改 PCC 规则 flowDescription ──────────────────────────────────────
// 直接导航到 /predfPolicy/pcc/edit/{id}（无需弹窗）
// input[name="flowInfos[flowDescription][]"]
async function editPccFlowDesc(page, pccRuleId, newFlowDesc) {
  // ① 先到列表页获取 pccRuleId 对应的数字 ID
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'commit', ignoreHTTPSErrors: true });

  // 等 pccRuleId 文本出现在页面中
  try {
    await page.waitForFunction(
      (id) => document.body.textContent.includes(id),
      pccRuleId,
      { timeout: 20000 }
    );
  } catch(e) {
    console.log('   ❌ pcc2 未出现在页面文本中（20秒超时）');
    return null;
  }
  // 等 DOM 彻底渲染
  await page.waitForTimeout(3000);

  const pccId = await page.evaluate((targetId) => {
    const tables = document.querySelectorAll('.layui-table');
    for (let ti = 0; ti < tables.length; ti++) {
      const rows = tables[ti].querySelectorAll('tbody tr');
      for (let ri = 0; ri < rows.length; ri++) {
        const cells = rows[ri].querySelectorAll('td');
        if (cells.length >= 9 && cells[2].textContent.trim() === targetId) {
          return JSON.stringify({ found: true, id: cells[1].textContent.trim() });
        }
      }
    }
    return JSON.stringify({ found: false });
  }, pccRuleId);

  const parsed = JSON.parse(pccId);
  console.log('   [debug] PCC lookup:', JSON.stringify(parsed));
  if (!parsed.found) { console.log(`❌ 未找到PCC规则ID: ${pccRuleId}`); return null; }
  const numericId = parsed.id;
  console.log(`✅ 找到 PCC规则 "${pccRuleId}"，数字ID=${numericId}`);

  // ② 直接导航到编辑页
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/edit/${numericId}`, { waitUntil: 'commit', ignoreHTTPSErrors: true });
  // 等 flowDescription input 出现
  await page.waitForFunction(
    () => document.querySelector('input[name="flowInfos[flowDescription][]"]') !== null,
    { timeout: 15000 }
  );
  await page.waitForTimeout(1000);

  // ③ 修改 flowDescription
  const result = await page.evaluate((arg) => {
    const inputs = document.querySelectorAll('input[name="flowInfos[flowDescription][]"]');
    if (inputs.length > 0) {
      const inp = inputs[0];
      const oldVal = inp.value;
      if (arg.newVal !== null) {
        inp.value = arg.newVal;
        inp.dispatchEvent(new Event('input', {bubbles: true}));
      }
      return { found: true, value: oldVal };
    }
    return { found: false };
  }, { newVal: newFlowDesc });

  if (result.found) {
    if (newFlowDesc !== null) {
      console.log(`   flowDescription → "${newFlowDesc}"`);
      // ④ 提交
      await page.locator('button:has-text("提交")').click();
      await page.waitForTimeout(2000);
    } else {
      console.log(`   当前 flowDescription: "${result.value}"`);
      return result.value;
    }
  } else {
    console.log('⚠️ 未找到 flowDescription input');
  }
  return true;
}

// ─── 修改信令负载 pcc_rule ───────────────────────────────────────────────
// 直接导航到 /load/edit/{id}
// textarea: process_conf[2][params][2][param_val] 实际是 input[type=text]
async function editLoadPccRule(page, loadName, newIp) {
  // ① 先到列表页获取 dedicated 对应的数字 ID
  await page.goto(`${globalBaseUrl}/sim_5gc/load/index`, { waitUntil: 'commit', ignoreHTTPSErrors: true });

  // 等 dedicated 文本出现在页面中
  try {
    await page.waitForFunction(
      (name) => document.body.textContent.includes(name),
      loadName,
      { timeout: 20000 }
    );
  } catch(e) {
    console.log('   ❌ dedicated 未出现在页面文本中（20秒超时）');
    return null;
  }
  await page.waitForTimeout(3000);

  const loadIdResult = await page.evaluate((targetName) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 5 && cells[2].textContent.trim() === targetName) {
        // cells[0]=checkbox, cells[1]=ID, cells[2]=名称, ...
        return JSON.stringify({ found: true, id: cells[1].textContent.trim() });
      }
    }
    return JSON.stringify({ found: false });
  }, loadName);

  const parsedLoad = JSON.parse(loadIdResult);
  console.log('   [debug] Load lookup:', JSON.stringify(parsedLoad));
  if (!parsedLoad.found) { console.log(`❌ 未找到信令负载条目ID: ${loadName}`); return null; }
  const loadId = parsedLoad.id;

  if (!loadId) { console.log(`❌ 未找到信令负载条目ID: ${loadName}`); return null; }
  console.log(`✅ 找到信令负载 "${loadName}"，ID=${loadId}`);

  // ② 直接导航到编辑页
  await page.goto(`${globalBaseUrl}/sim_5gc/load/edit/${loadId}`, { waitUntil: 'commit', ignoreHTTPSErrors: true });
  // 等 pcc_rule input 出现
  await page.waitForFunction(
    () => document.querySelector('input[name="process_conf[2][params][2][param_val]"]') !== null,
    { timeout: 15000 }
  );
  await page.waitForTimeout(1000);

  // ③ 修改 pcc_rule
  const result = await page.evaluate((arg) => {
    // pcc_rule 在 process_conf[2][params][2][param_val]
    const inputs = Array.from(document.querySelectorAll('input'));
    const pccInput = inputs.find(i => i.name === 'process_conf[2][params][2][param_val]');
    if (pccInput) {
      const oldVal = pccInput.value;
      if (arg.newVal !== null) {
        pccInput.value = arg.newVal;
        pccInput.dispatchEvent(new Event('input', {bubbles: true}));
      }
      return { found: true, value: oldVal };
    }
    return { found: false };
  }, { newVal: newIp });

  if (result.found) {
    if (newIp !== null) {
      console.log(`   pcc_rule → "${newIp}"`);
      // ④ 提交
      await page.locator('button:has-text("提交")').click();
      await page.waitForTimeout(2000);
    } else {
      console.log(`   当前 pcc_rule: "${result.value}"`);
      return result.value;
    }
  } else {
    console.log('⚠️ 未找到 pcc_rule input');
  }
  return true;
}

// ─── 主流程 ───────────────────────────────────────────────────────────
async function main() {
  const opts = parseArgs();
  const browser = await chromium.launch({
    headless: !opts.headed,
    args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*']
  });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);

  // ─── PCC规则 flowDescription ───────────────────────────────────────
  if (opts.flowDesc !== null) {
    console.log(`\n▶ 修改 PCC规则 "${opts.pccRuleId}" flowDescription`);
    await editPccFlowDesc(page, opts.pccRuleId, opts.flowDesc);
  } else {
    console.log(`\n▶ 读取 PCC规则 "${opts.pccRuleId}" 当前 flowDescription`);
    const val = await editPccFlowDesc(page, opts.pccRuleId, null);
    if (val) console.log(`   → "${val}"`);
  }

  // ─── 信令负载 pcc_rule ──────────────────────────────────────────────
  if (opts.loadIp !== null) {
    console.log(`\n▶ 修改信令负载 "${opts.loadName}" pcc_rule`);
    await editLoadPccRule(page, opts.loadName, opts.loadIp);
  } else {
    console.log(`\n▶ 读取信令负载 "${opts.loadName}" 当前 pcc_rule`);
    const val = await editLoadPccRule(page, opts.loadName, null);
    if (val) console.log(`   → "${val}"`);
  }

  console.log('\n✅ 完成');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
