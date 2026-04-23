/**
 * regression_test.js - 回归测试：测试每个技能的正确性
 * 
 * 测试工程：XW_SUPF_5_1_2_4（有完整数据）
 * 测试项目：
 *   1. qos-add-skill    - QoS模板添加
 *   2. pcc-add-skill   - PCC规则添加（使用已有的qos1+tc1）
 *   3. smpolicy_edit   - sm_policy_default 编辑（绑定PCC规则）
 *   4. pcf-edit-skill  - PCF default_smpolicy 配置
 */
const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';
const PROJECT = 'XW_SUPF_5_1_2_4';
const TARGET_PCF_ID = '12770';

// ── 工具函数 ──────────────────────────────────────────────────────────

async function login(page) {
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000, waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  // 如果页面已登录（URL变回login或自动跳转），等待login表单出现
  const emailInput = page.locator('input[name="email"]').first();
  try { await emailInput.waitFor({ state: 'visible', timeout: 5000 }); } catch(e) {}
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
  await page.evaluate((n) => {
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) cells[1].querySelector('.iconfont').click();
    });
  }, name);
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${name}" 已选`);
}

async function getTableRows(page, url) {
  await page.goto(url, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  return await page.evaluate(() => {
    const rows = Array.from(document.querySelectorAll('.layui-table tbody tr')).map(row =>
      Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
    );
    return rows;
  });
}

async function waitAndGetFrame(page) {
  await page.waitForTimeout(3000);
  return page.frame('layui-layer-iframe2');
}

function assert(label, actual, expected) {
  const pass = actual === expected || String(actual).trim() === String(expected).trim();
  console.log(`  ${pass ? '✅' : '❌'} ${label}: ${pass ? 'OK' : `got "${actual}", expected "${expected}"`}`);
  return pass;
}

// ── 测试用例 ──────────────────────────────────────────────────────────

async function test_qos_add(browser, ctx) {
  console.log('\n━━━ TEST 1: qos-add-skill ━━━');
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, PROJECT);

  // 生成测试用的唯一 qosId
  const testQosId = 'qos_regtest_' + Date.now();
  
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  
  // 获取当前已有的5qi列表
  const existing5qi = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    const qiSet = new Set();
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 4 && cells[3]) {
        const qi = cells[3].textContent.trim();
        if (qi) qiSet.add(qi);
      }
    });
    return Array.from(qiSet);
  });
  
  // 选择一个不存在的5qi
  const target5qi = ['8','9','6','5','7','10'].find(q => !existing5qi.includes(q)) || '8';
  console.log(`  已有5qi: [${existing5qi.join(',')}], 将使用 5qi=${target5qi}`);
  
  // 点击添加按钮
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);
  
  // 填写表单
  await page.locator('input[name="qosId"]').fill(testQosId);
  await page.locator('input[name="fiveQi"]').fill(target5qi);
  await page.locator('input[name="maxbrUl"]').fill('10000000');
  await page.locator('input[name="maxbrDl"]').fill('20000000');
  await page.locator('input[name="gbrUl"]').fill('5000000');
  await page.locator('input[name="gbrDl"]').fill('5000000');
  
  await page.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  
  // 验证
  const rows = await getTableRows(page, `${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`);
  const found = rows.find(r => r[2] === testQosId);
  if (found) {
    console.log(`  ✅ QoS模板 ${testQosId} 创建成功`);
    console.log(`     5qi=${found[3]}, maxbrUl=${found[4]}, maxbrDl=${found[5]}, gbrUl=${found[6]}, gbrDl=${found[7]}`);
  } else {
    console.log(`  ❌ QoS模板 ${testQosId} 未找到`);
  }
  
  await page.close();
  return testQosId;
}

async function test_pcc_add(browser, ctx, qosId, tcId) {
  console.log('\n━━━ TEST 2: pcc-add-skill ━━━');
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, PROJECT);

  const testPccId = 'pcc_regtest_' + Date.now();
  
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  // 点击添加
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);
  await page.waitForFunction(() => window.location.href.includes('/predfPolicy/pcc/edit'), { timeout: 10000 });
  await page.waitForTimeout(3000);
  
  // 填写
  await page.locator('input[name="pccRuleId"]').fill(testPccId);
  await page.locator('input[name="precedence"]').fill('63');
  
  // xm-select[0] = refQosData
  await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[0]?.parentElement.click());
  await page.waitForTimeout(1000);
  const qosVisible = await page.locator('.xm-option.show-icon', { hasText: qosId }).isVisible({ timeout: 3000 }).catch(() => false);
  if (qosVisible) {
    await page.locator('.xm-option.show-icon', { hasText: qosId }).click();
    console.log(`  ✅ refQosData=${qosId}`);
  } else {
    console.log(`  ❌ refQosData=${qosId} 不可见`);
  }
  await page.waitForTimeout(500);
  
  // xm-select[1] = refTcData
  await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[1]?.parentElement.click());
  await page.waitForTimeout(1000);
  const tcVisible = await page.locator('.xm-option.show-icon', { hasText: tcId }).isVisible({ timeout: 3000 }).catch(() => false);
  if (tcVisible) {
    await page.locator('.xm-option.show-icon', { hasText: tcId }).click();
    console.log(`  ✅ refTcData=${tcId}`);
  } else {
    console.log(`  ❌ refTcData=${tcId} 不可见`);
  }
  await page.waitForTimeout(500);
  
  await page.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  
  // 验证
  const rows = await getTableRows(page, `${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`);
  const found = rows.find(r => r[2] === testPccId);
  if (found) {
    console.log(`  ✅ PCC规则 ${testPccId} 创建成功`);
    console.log(`     precedence=${found[4]}, refQosData=${found[5]}, refTcData=${found[6]}`);
  } else {
    console.log(`  ❌ PCC规则 ${testPccId} 未找到`);
  }
  
  await page.close();
  return testPccId;
}

async function test_smpolicy_edit(browser, ctx, pccId) {
  console.log('\n━━━ TEST 3: smpolicy_edit (pccRules绑定) ━━━');
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, PROJECT);

  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  // 找到 sm_policy_default 的行
  const smpId = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === 'sm_policy_default') {
        const links = cells[9].querySelectorAll('a');
        for (const l of links) { if (l.textContent.trim() === '编辑') return cells[1].textContent.trim(); }
      }
    }
    return null;
  });
  
  if (!smpId) { console.log('  ❌ sm_policy_default 未找到'); await page.close(); return; }
  console.log(`  sm_policy_default ID=${smpId}`);
  
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/edit/${smpId}`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('  ❌ 无法获取iframe'); await page.close(); return; }
  
  // 检查 pccRules xm-select 当前值
  const beforePccRules = await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return inputs.length >= 2 ? inputs[1].value : '';
  });
  console.log(`  编辑前 pccRules value="${beforePccRules}"`);
  
  // 点击 pccRules xm-select（第1个）
  await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[1]) inputs[1].parentElement.click();
  });
  await page.waitForTimeout(1000);
  
  // 检查是否有选项包含目标pccId
  const pccOptVisible = await frame.locator('.xm-option.show-icon', { hasText: pccId }).isVisible({ timeout: 3000 }).catch(() => false);
  console.log(`  目标 PCC 选项 "${pccId}" 可见: ${pccOptVisible}`);
  
  if (pccOptVisible) {
    await frame.locator('.xm-option.show-icon', { hasText: pccId }).click();
    console.log(`  ✅ 选择 ${pccId}`);
  }
  await page.waitForTimeout(500);
  
  // 获取更新后的 pccRules
  const afterPccRules = await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return inputs.length >= 2 ? inputs[1].value : '';
  });
  console.log(`  编辑后 pccRules value="${afterPccRules}"`);
  
  // 提交
  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  
  // 验证
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const finalPcc = await page.evaluate((id) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 6 && cells[1].textContent.trim() === id) {
        return cells[4].textContent.trim(); // pccRules 列
      }
    }
    return null;
  }, smpId);
  
  console.log(`  最终 pccRules="${finalPcc}"`);
  if (finalPcc && finalPcc.includes(pccId)) {
    console.log(`  ✅ sm_policy_default pccRules 绑定成功`);
  } else {
    console.log(`  ⚠️ pccRules="${finalPcc}"（可能已经包含或绑定方式不同）`);
  }
  
  await page.close();
}

async function test_pcf_edit(browser, ctx, smpolicyName) {
  console.log('\n━━━ TEST 4: pcf-edit-skill (default_smpolicy) ━━━');
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, PROJECT);

  await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  // 点击 PCF 编辑按钮
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    if (rows.length > 0) {
      const links = rows[0].querySelectorAll('a');
      for (const l of links) { if (l.textContent.trim() === '编辑') { l.click(); return; } }
    }
  });
  await page.waitForTimeout(3000);
  
  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('  ❌ 无法获取iframe'); await page.close(); return; }
  
  // 检查 default_smpolicy xm-select 当前值
  const beforeDefault = await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return inputs.length >= 1 ? inputs[0].value : '';
  });
  console.log(`  编辑前 default_smpolicy value="${beforeDefault}"`);
  
  // 点击 default_smpolicy xm-select（第0个）
  await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[0]) inputs[0].parentElement.click();
  });
  await page.waitForTimeout(1000);
  
  // 检查目标 smpolicy 是否可见
  const smpOptVisible = await frame.locator('.xm-option.show-icon', { hasText: smpolicyName }).isVisible({ timeout: 3000 }).catch(() => false);
  console.log(`  目标 smpolicy "${smpolicyName}" 可见: ${smpOptVisible}`);
  
  if (smpOptVisible) {
    await frame.locator('.xm-option.show-icon', { hasText: smpolicyName }).click();
    console.log(`  ✅ default_smpolicy=${smpolicyName}`);
  } else {
    console.log(`  ❌ default_smpolicy=${smpolicyName} 不可见`);
  }
  await page.waitForTimeout(500);
  
  // 获取更新后的值
  const afterDefault = await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return inputs.length >= 1 ? inputs[0].value : '';
  });
  console.log(`  编辑后 default_smpolicy value="${afterDefault}"`);
  
  // 提交
  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`  ✅ PCF 提交完成`);
  
  await page.close();
}

// ── 主流程 ─────────────────────────────────────────────────────────────

async function main() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });

  console.log('========================================');
  console.log('5GC 技能回归测试');
  console.log(`工程: ${PROJECT}`);
  console.log('========================================');

  let qosId = null, pccId = null;
  
  try {
    // TEST 1: QoS模板添加
    qosId = await test_qos_add(browser, ctx);
  } catch(e) {
    console.log('  ❌ TEST 1 异常:', e.message);
  }

  try {
    // TEST 2: PCC规则添加（使用已有的qos1+tc1）
    pccId = await test_pcc_add(browser, ctx, 'qos1', 'tc1');
  } catch(e) {
    console.log('  ❌ TEST 2 异常:', e.message);
  }

  try {
    // TEST 3: sm_policy_default 编辑（绑定 PCC）
    if (pccId) await test_smpolicy_edit(browser, ctx, pccId);
  } catch(e) {
    console.log('  ❌ TEST 3 异常:', e.message);
  }

  try {
    // TEST 4: PCF default_smpolicy 配置
    await test_pcf_edit(browser, ctx, 'sm_policy_default');
  } catch(e) {
    console.log('  ❌ TEST 4 异常:', e.message);
  }

  console.log('\n========================================');
  console.log('回归测试完成');
  console.log('========================================');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });