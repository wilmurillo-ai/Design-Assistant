/**
 * debug_pcf_xmselect.js - 深入分析 PCF 弹窗中 default_smpolicy xm-select 的行为
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

  await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 点击编辑按钮
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    if (rows.length > 0) {
      const links = rows[0].querySelectorAll('a');
      for (const l of links) { if (l.textContent.trim() === '编辑') { l.click(); return; } }
    }
  });
  await page.waitForTimeout(3000);
  await page.waitForSelector('iframe[name="layui-layer-iframe2"]', { timeout: 5000 });
  await page.waitForTimeout(2000);

  const frame = page.frame('layui-layer-iframe2');
  console.log('✅ 找到弹窗iframe:', frame.url());

  // 初始状态
  const initVal = await frame.evaluate(() => document.querySelectorAll('input.xm-select-default')[0]?.value);
  console.log('初始 default_smpolicy value:', initVal);

  // 打开下拉
  await frame.evaluate(() => document.querySelectorAll('input.xm-select-default')[0]?.parentElement.click());
  await page.waitForTimeout(1500);

  // 查看所有可见选项
  const options = await frame.evaluate(() => {
    return Array.from(document.querySelectorAll('.xm-option.show-icon')).map(o => ({
      text: o.textContent.trim(),
      visible: o.offsetHeight > 0 && window.getComputedStyle(o).display !== 'none',
      selected: o.classList.contains('selected')
    }));
  });
  console.log('\n下拉选项:', JSON.stringify(options, null, 2));

  // 直接用 JS 点击 sm_policy_default 选项（不通过 Playwright locator）
  const clicked = await frame.evaluate(() => {
    const opts = document.querySelectorAll('.xm-option.show-icon');
    for (const opt of opts) {
      if (opt.textContent.trim() === 'sm_policy_default') {
        opt.click();
        return true;
      }
    }
    return false;
  });
  console.log('\nJS 点击 sm_policy_default:', clicked);
  await page.waitForTimeout(1000);

  // 检查点击后的值
  const afterJsClick = await frame.evaluate(() => document.querySelectorAll('input.xm-select-default')[0]?.value);
  console.log('JS点击后 value:', afterJsClick);

  // 也测试 Playwright locator 点击
  // 先重新打开下拉
  await frame.evaluate(() => document.querySelectorAll('input.xm-select-default')[0]?.parentElement.click());
  await page.waitForTimeout(1500);

  const pwVisible = await frame.locator('.xm-option.show-icon', { hasText: 'sm_policy_default' }).isVisible({ timeout: 3000 }).catch(() => false);
  console.log('\nPlaywright locator sm_policy_default 可见:', pwVisible);

  if (pwVisible) {
    await frame.locator('.xm-option.show-icon', { hasText: 'sm_policy_default' }).first().click();
    console.log('Playwright locator 点击完成');
    await page.waitForTimeout(500);
  }

  const afterPwClick = await frame.evaluate(() => document.querySelectorAll('input.xm-select-default')[0]?.value);
  console.log('Playwright点击后 value:', afterPwClick);

  await page.screenshot({ path: 'pcf_xmselect_debug.png', fullPage: true });
  console.log('截图: pcf_xmselect_debug.png');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });