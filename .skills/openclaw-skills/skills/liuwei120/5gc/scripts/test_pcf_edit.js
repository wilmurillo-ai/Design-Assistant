/**
 * test_pcf_edit.js - 单测 PCF 编辑弹窗的 default_smpolicy 下拉
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

  console.log('PCF列表 URL:', page.url());

  // 点击编辑按钮
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    if (rows.length > 0) {
      const links = rows[0].querySelectorAll('a');
      for (const l of links) { if (l.textContent.trim() === '编辑') { l.click(); return; } }
    }
  });
  await page.waitForTimeout(3000);

  // 等待弹窗
  await page.waitForSelector('iframe[name="layui-layer-iframe2"]', { timeout: 5000 });
  await page.waitForTimeout(2000);

  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('❌ 未找到弹窗iframe'); await browser.close(); return; }
  console.log('✅ 找到弹窗iframe:', frame.url());

  // 检查 xm-select 状态
  const xmData = await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return Array.from(inputs).map((inp, i) => ({
      idx: i, value: inp.value, display: inp.parentElement.textContent.substring(0, 80)
    }));
  });
  console.log('\n当前 xm-select 状态:', JSON.stringify(xmData, null, 2));

  // 点击 default_smpolicy xm-select（第0个）
  console.log('\n▶ 尝试选择 sm_policy_default ...');
  await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[0]) inputs[0].parentElement.click();
  });
  await page.waitForTimeout(1500);

  // Playwright locator 在 frame 内查找
  const smpOptVisible = await frame.locator('.xm-option.show-icon', { hasText: 'sm_policy_default' }).isVisible({ timeout: 3000 }).catch(() => false);
  console.log('sm_policy_default 选项可见:', smpOptVisible);

  if (smpOptVisible) {
    await frame.locator('.xm-option.show-icon', { hasText: 'sm_policy_default' }).first().click();
    console.log('✅ sm_policy_default 已点击');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
  } else {
    console.log('❌ sm_policy_default 选项不可见');
    // JS fallback
    const clicked = await frame.evaluate(() => {
      const opts = document.querySelectorAll('.xm-option.show-icon');
      for (const opt of opts) {
        if (opt.textContent.trim().includes('sm_policy_default')) { opt.click(); return true; }
      }
      return false;
    });
    console.log('JS fallback:', clicked);
  }

  // 获取更新后的值
  const afterValue = await frame.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return inputs.length >= 1 ? inputs[0].value : '';
  });
  console.log('选择后 default_smpolicy value:', afterValue);

  // 提交
  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log('✅ 提交完成');

  // 验证
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
  await page.waitForSelector('iframe[name="layui-layer-iframe2"]', { timeout: 5000 });
  await page.waitForTimeout(2000);
  
  const frame2 = page.frame('layui-layer-iframe2');
  const finalVal = await frame2.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return inputs.length >= 1 ? inputs[0].value : '';
  });
  console.log(`\n最终 default_smpolicy="${finalVal}"`);
  if (finalVal && finalVal.includes('sm_policy_default')) {
    console.log('🎉 PCF default_smpolicy 配置成功!');
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });