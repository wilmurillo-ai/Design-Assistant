const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';
async function main() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
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
  await page.goto(globalBaseUrl + '/sim_5gc/predfPolicy/pcc/index', { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const headers = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.layui-table thead th')).map((th, i) => i + ':' + th.textContent.trim());
  });
  console.log('表头:', JSON.stringify(headers));
  
  const rows = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.layui-table tbody tr')).map((row, ri) => {
      return Array.from(row.querySelectorAll('td')).map((td, i) => i + '=' + td.textContent.trim());
    });
  });
  console.log('行数:', rows.length);
  if (rows.length > 0) {
    console.log('第1行:', JSON.stringify(rows[0]));
    console.log('列数:', rows[0].length);
  }
  
  // 查看 TCC列表
  await page.goto(globalBaseUrl + '/sim_5gc/predfPolicy/trafficCtl/index', { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const tcHeaders = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.layui-table thead th')).map((th, i) => i + ':' + th.textContent.trim());
  });
  const tcRows = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.layui-table tbody tr')).map(row => {
      return Array.from(row.querySelectorAll('td')).map((td, i) => i + '=' + td.textContent.trim());
    });
  });
  console.log('\nTC表头:', JSON.stringify(tcHeaders));
  console.log('TC行数:', tcRows.length);
  if (tcRows.length > 0) console.log('TC第1行:', JSON.stringify(tcRows[0]));
  
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });