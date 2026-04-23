const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);

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

  // 直接访问编辑页
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/ue/edit/8756`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  console.log('编辑页URL:', page.url());
  console.log('页面内容:', (await page.evaluate(() => document.body.innerText)).substring(0, 800));

  const frames = page.frames();
  console.log('\n所有iframe:', frames.map(f => ({ url: f.url(), name: f.name() })));

  const fields = await page.evaluate(() => {
    const result = [];
    document.querySelectorAll('input[name], select[name], textarea[name]').forEach(el => {
      result.push({ tag: el.tagName, name: el.name, value: el.value, type: el.type || '' });
    });
    return result;
  });
  console.log('\n主页面字段:', JSON.stringify(fields, null, 2));

  const btns = await page.evaluate(() =>
    Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim())
  );
  console.log('\n主页面按钮:', btns);

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });