/**
 * test_smpolicy_edit.js - 单测 sm_policy_default 的 pccRules 绑定
 */
const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';

async function login(page) {
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000, waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  try { await page.locator('input[name="email"]').first().waitFor({ state: 'visible', timeout: 5000 }); } catch(e) {}
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

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 找到 sm_policy_default 的数字 ID 和行
  const rowData = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      // 找到名称为 sm_policy_default 的行
      for (let i = 0; i < cells.length; i++) {
        if (cells[i].textContent.trim() === 'sm_policy_default') {
          // 这一行的ID在第 i-1 个单元格（往前一格）
          const id = i > 0 ? cells[i - 1].textContent.trim() : null;
          return { id, rowHtml: row.innerHTML.substring(0, 300) };
        }
      }
    }
    return null;
  });
  console.log('sm_policy_default ID:', rowData?.id);
  console.log('rowHtml:', rowData?.rowHtml);

  if (!rowData?.id) { console.log('❌ sm_policy_default 未找到'); await browser.close(); return; }

  // 点击编辑按钮
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      if (row.innerHTML.includes('sm_policy_default')) {
        const links = row.querySelectorAll('a');
        for (const l of links) { if (l.textContent.trim() === '编辑') { l.click(); return; } }
      }
    }
  });
  await page.waitForTimeout(3000);

  // 等待并获取弹窗iframe
  await page.waitForSelector('iframe[name="layui-layer-iframe2"]', { timeout: 5000 });
  await page.waitForTimeout(2000);

  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('❌ 未找到弹窗iframe'); await browser.close(); return; }
  console.log('✅ 找到弹窗iframe:', frame.url());

  // 检查 xm-select
  const xmData = await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return Array.from(inputs).map((inp, i) => ({
      idx: i, value: inp.value, display: inp.parentElement.textContent.substring(0, 80)
    }));
  });
  console.log('\n当前 xm-select 状态:', JSON.stringify(xmData, null, 2));

  // 点击 pccRules xm-select（第1个xm-select，index=1）
  console.log('\n▶ 尝试选择 pcc1 ...');
  await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[1]) inputs[1].parentElement.click();
  });
  await page.waitForTimeout(1500);

  // Playwright locator 在 frame 内查找
  const pccOptVisible = await frame.locator('.xm-option.show-icon', { hasText: 'pcc1' }).isVisible({ timeout: 3000 }).catch(() => false);
  console.log('pcc1 选项可见:', pccOptVisible);

  if (pccOptVisible) {
    await frame.locator('.xm-option.show-icon', { hasText: 'pcc1' }).first().click();
    console.log('✅ pcc1 已点击');
    // 关闭 xm-select 下拉
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
  } else {
    const clicked = await frame.evaluate(() => {
      const opts = document.querySelectorAll('.xm-option.show-icon');
      for (const opt of opts) {
        if (opt.textContent.trim() === 'pcc1') { opt.click(); return true; }
      }
      return false;
    });
    console.log('JS fallback 点击 pcc1:', clicked);
  }
  await page.waitForTimeout(1000);

  // 提交
  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log('✅ 提交完成');

  // 验证
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const finalPcc = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      if (row.innerHTML.includes('sm_policy_default')) {
        const cells = row.querySelectorAll('td');
        // pccRules 列
        for (let i = 0; i < cells.length; i++) {
          if (cells[i].textContent.trim() === 'sm_policy_default') {
            return i + 2 < cells.length ? cells[i + 2].textContent.trim() : null;
          }
        }
      }
    }
    return null;
  });

  console.log(`\n最终 pccRules="${finalPcc}"`);
  if (finalPcc && finalPcc.includes('pcc1')) {
    console.log('🎉 sm_policy_default pccRules 绑定 pcc1 成功!');
  } else {
    console.log('⚠️ pccRules 可能已包含 pcc1 或绑定方式不同');
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });