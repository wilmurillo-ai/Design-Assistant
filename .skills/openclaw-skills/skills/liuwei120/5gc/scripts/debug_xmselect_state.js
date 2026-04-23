const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';

async function main() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);

  // 选择工程
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.locator('input[name="project_search_name"]').fill('XW_SUPF_5_1_2_4');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  await page.evaluate(() => {
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === 'XW_SUPF_5_1_2_4') cells[1].querySelector('.iconfont').click();
    });
  });
  await page.waitForTimeout(3000);

  // 直接打开 PCC 编辑页 ID=17491
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/edit/17491`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const before = await page.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return { value: inputs[0]?.value, display: inputs[0]?.parentElement?.textContent?.substring(0, 120) };
  });
  console.log('编辑前:', JSON.stringify(before));

  // 打开 xm-select[0]
  await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[0].parentElement.click());
  await page.waitForTimeout(1000);

  // 检查所有 .xm-option 的状态
  const allOptions = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.xm-option')).map(opt => ({
      text: opt.textContent.trim(),
      classes: opt.className,
      visible: opt.offsetWidth > 0 && opt.offsetHeight > 0,
    }));
  });
  console.log('\n下拉打开后所有选项:');
  allOptions.forEach(o => console.log(`  [${o.visible ? '可见' : '隐藏'}] "${o.text}" classes=${o.classes}`));

  // 检查 .xm-option.show-icon
  const showIconOpts = await page.evaluate(() =>
    Array.from(document.querySelectorAll('.xm-option.show-icon')).map(o => o.textContent.trim())
  );
  console.log('\n.show-icon 选项:', showIconOpts);

  // 检查 .xm-option.selected
  const selectedOpts = await page.evaluate(() =>
    Array.from(document.querySelectorAll('.xm-option.selected')).map(o => o.textContent.trim())
  );
  console.log('.selected 选项:', selectedOpts);

  // 尝试点击 qos_high_rate（用 locator）
  const qosLocator = page.locator('.xm-option', { hasText: 'qos_high_rate' });
  console.log('\nqos_high_rate isVisible:', await qosLocator.isVisible().catch(() => false));
  console.log('qos_high_rate count:', await qosLocator.count());

  // 点击已选项
  const selLocator = page.locator('.xm-option.selected');
  if (await selLocator.count() > 0) {
    console.log('\n点击已选项...');
    await selLocator.first().click();
    await page.waitForTimeout(1000);
    console.log('点击后 value:', await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[0].value));
  }

  // 重新打开
  await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[0].parentElement.click());
  await page.waitForTimeout(1000);

  const afterReopen = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.xm-option')).map(opt => ({
      text: opt.textContent.trim(),
      visible: opt.offsetWidth > 0 && opt.offsetHeight > 0,
    }));
  });
  console.log('\n重新打开后所有选项:');
  afterReopen.forEach(o => console.log(`  [${o.visible ? '可见' : '隐藏'}] "${o.text}"`));

  const showIconAfter = await page.evaluate(() =>
    Array.from(document.querySelectorAll('.xm-option.show-icon')).map(o => o.textContent.trim())
  );
  console.log('重新打开后 .show-icon:', showIconAfter);

  const selectedAfter = await page.evaluate(() =>
    Array.from(document.querySelectorAll('.xm-option.selected')).map(o => o.textContent.trim())
  );
  console.log('重新打开后 .selected:', selectedAfter);

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });