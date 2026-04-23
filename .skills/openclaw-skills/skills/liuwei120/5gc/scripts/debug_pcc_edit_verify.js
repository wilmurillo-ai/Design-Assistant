const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';
async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await page.goto(globalBaseUrl + '/login', { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);
  await page.goto(globalBaseUrl + '/sim_5gc/project/index', { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.locator('input[name="project_search_name"]').fill('XW_SUPF_SN4_5_2_8');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  await page.evaluate(() => {
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === 'XW_SUPF_SN4_5_2_8') cells[1].querySelector('.iconfont').click();
    });
  });
  await page.waitForTimeout(3000);
  
  // 直接导航到 PCC 编辑页（ID=17484）
  await page.goto(globalBaseUrl + '/sim_5gc/predfPolicy/pcc/edit/17484', { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  // 打印页面内容
  const pageText = await page.evaluate(() => document.body.innerText);
  console.log('PCC编辑页内容（前2000字）:', pageText.substring(0, 2000));
  
  // 检查 xm-select 的值
  const xmValues = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('input.xm-select-default')).map((inp, i) => {
      return { idx: i, value: inp.value, parentText: inp.parentElement.textContent.substring(0, 100) };
    });
  });
  console.log('\nxm-select值:', JSON.stringify(xmValues, null, 2));
  
  await page.screenshot({ path: 'pcc_edit_check.png', fullPage: true });
  console.log('截图: pcc_edit_check.png');
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });