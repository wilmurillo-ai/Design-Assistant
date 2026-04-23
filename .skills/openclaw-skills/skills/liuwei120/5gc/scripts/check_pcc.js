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
  await page.evaluate(n => {
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) cells[1].querySelector('.iconfont').click();
    });
  }, 'XW_SUPF_5_1_2_4');
  await page.waitForTimeout(3000);
  await page.goto(globalBaseUrl + '/sim_5gc/predfPolicy/pcc/index', { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const result = await page.evaluate(() => {
    // 找包含 pcc_default_test 的行
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      // cells[2] 是 pccRuleId
      if (cells.length >= 5 && cells[2].textContent.trim() === 'pcc_default_test') {
        return {
          id: cells[1].textContent.trim(),
          pccRuleId: cells[2].textContent.trim(),
          precedence: cells[4].textContent.trim(),
          qosId: cells[5].textContent.trim(),
        };
      }
    }
    return null;
  });
  
  console.log('pcc_default_test:', JSON.stringify(result, null, 2));
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });
