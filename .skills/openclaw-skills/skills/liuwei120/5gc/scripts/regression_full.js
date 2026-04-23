/**
 * regression_full.js - 回归测试：清理 + 重建 + 验证
 *
 * 测试工程: XW_SUPF_5_1_2_4
 *
 * 步骤:
 *   1. 清理无效 pcc_default（refQosData/refTcData 为空）
 *   2. 创建新 PCC 规则 pcc_reg_test（绑定 qos1 + tc1）
 *   3. 将 pcc_reg_test 添加到 sm_policy_default 的 pccRules
 *   4. 验证所有绑定正确
 */
const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';
const TEST_PROJECT = 'XW_SUPF_5_1_2_4';
const PCC_NEW = 'pcc_reg_test';
const QOS_ID = 'qos1';
const TC_ID = 'tc1';

async function login(page) {
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);
}

async function selectProject(page, name) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.locator('input[name="project_search_name"]').fill(name);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  await page.evaluate((n) => {
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) cells[1].querySelector('.iconfont').click();
    });
  }, name);
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${name}" 已选`);
}

async function goto(page, url) {
  await page.goto(`${globalBaseUrl}${url}`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
}

async function delPcc(page, pccRuleId) {
  await goto(page, '/sim_5gc/predfPolicy/pcc/index');
  const del = await page.evaluate((id) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 10 && cells[2].textContent.trim() === id) {
        const links = cells[9].querySelectorAll('a');
        for (const l of links) {
          if (l.textContent.trim() === '删除') { l.click(); return true; }
        }
      }
    }
    return false;
  }, pccRuleId);
  if (del) {
    await page.waitForTimeout(2000);
    console.log(`   🗑️ 已删除 pcc_default`);
  }
}

async function addPcc(page, pccId, qosId, tcId, precedence = '63') {
  await goto(page, '/sim_5gc/predfPolicy/pcc/index');
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);
  await page.waitForFunction(() => window.location.href.includes('/predfPolicy/pcc/edit'), { timeout: 10000 });
  await page.waitForTimeout(3000);
  console.log(`   添加页URL: ${page.url()}`);

  // 填写字段
  await page.locator('input[name="pccRuleId"]').fill(pccId);
  await page.locator('input[name="precedence"]').fill(precedence);

  // xm-select[0] = refQosData
  await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[0].parentElement.click());
  await page.waitForTimeout(1000);
  await page.locator('.xm-option.show-icon', { hasText: qosId }).click();
  console.log(`   ✅ refQosData=${qosId}`);
  await page.waitForTimeout(500);

  // xm-select[1] = refTcData
  await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[1].parentElement.click());
  await page.waitForTimeout(1000);
  await page.locator('.xm-option.show-icon', { hasText: tcId }).click();
  console.log(`   ✅ refTcData=${tcId}`);
  await page.waitForTimeout(500);

  // 提交
  await page.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ PCC ${pccId} 已提交`);
}

async function addPccToSmpolicy(page, pccId) {
  await goto(page, '/sim_5gc/smpolicy/default/index');
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    if (rows.length > 0) rows[0].querySelector('a')?.click();
  });
  await page.waitForTimeout(3000);

  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.error('❌ iframe 未找到'); return; }

  // pccRules = xm-select[1]
  await frame.evaluate(() => document.querySelectorAll('input.xm-select-default')[1].parentElement.click());
  await page.waitForTimeout(1000);
  const opt = frame.locator('.xm-option.show-icon', { hasText: pccId });
  if (await opt.isVisible({ timeout: 3000 }).catch(() => false)) {
    await opt.click();
    console.log(`   ✅ pccRules+=${pccId}`);
  } else {
    const avail = await frame.evaluate(() =>
      Array.from(document.querySelectorAll('.xm-option.show-icon')).map(o => o.textContent.trim())
    );
    console.log(`   ❌ ${pccId} 不可见，可用: ${avail.join(', ')}`);
    return;
  }
  await page.waitForTimeout(500);

  // 关闭 xm-select 下拉（按 Escape 避免遮罩层）
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ sm_policy_default 已提交`);
}

async function verify(page) {
  await goto(page, '/sim_5gc/predfPolicy/pcc/index');
  const pccData = await page.evaluate((targetId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 8 && cells[2].textContent.trim() === targetId) {
        return {
          pccRuleId: cells[2].textContent.trim(),
          precedence: cells[4].textContent.trim(),
          refQosData: cells[5].textContent.trim(),
          refTcData: cells[6].textContent.trim(),
        };
      }
    }
    return null;
  }, PCC_NEW);

  await goto(page, '/sim_5gc/smpolicy/default/index');
  const smpData = await page.evaluate((targetId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 6 && cells[2].textContent.trim() === targetId) {
        return { pccRules: cells[4].textContent.trim() };
      }
    }
    return null;
  }, 'sm_policy_default');

  console.log('\n========================================');
  console.log('回归测试结果');
  console.log('========================================');
  const tests = [
    { name: `PCC ${PCC_NEW} 创建`, pass: !!pccData },
    { name: `PCC refQosData=${QOS_ID}`, pass: pccData?.refQosData === QOS_ID },
    { name: `PCC refTcData=${TC_ID}`, pass: pccData?.refTcData === TC_ID },
    { name: `sm_policy_default 包含 ${PCC_NEW}`, pass: smpData?.pccRules?.includes(PCC_NEW) },
  ];
  let allPass = true;
  for (const t of tests) {
    console.log(`  ${t.pass ? '✅' : '❌'} ${t.name}`);
    if (!t.pass) allPass = false;
  }
  console.log('========================================');
  if (allPass) {
    console.log('🎉 全部通过！');
  } else {
    console.log('⚠️ 部分失败');
    if (pccData) console.log('  PCC数据:', JSON.stringify(pccData));
    if (smpData) console.log('  smp数据:', JSON.stringify(smpData));
  }
  return allPass;
}

async function main() {
  console.log('========================================');
  console.log('5GC PCC 技能回归测试');
  console.log(`工程: ${TEST_PROJECT} | PCC: ${PCC_NEW}`);
  console.log('========================================\n');

  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, TEST_PROJECT);

  // Step 1: 删除无效 pcc_default
  console.log('📦 Step 1: 清理无效 pcc_default...');
  await delPcc(page, 'pcc_default');

  // Step 2: 创建新 PCC 规则
  console.log(`\n📦 Step 2: 创建 PCC ${PCC_NEW} (qos=${QOS_ID}, tc=${TC_ID})...`);
  await addPcc(page, PCC_NEW, QOS_ID, TC_ID);

  // Step 3: 添加到 sm_policy_default
  console.log(`\n📦 Step 3: 添加到 sm_policy_default...`);
  await addPccToSmpolicy(page, PCC_NEW);

  // Step 4: 验证
  console.log('\n📦 Step 4: 验证...');
  const ok = await verify(page);

  await browser.close();
  process.exit(ok ? 0 : 1);
}

main().catch(e => { console.error(e); process.exit(1); });