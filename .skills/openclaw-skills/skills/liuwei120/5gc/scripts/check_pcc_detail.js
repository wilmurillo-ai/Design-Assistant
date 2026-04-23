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
  
  const result = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 9 && cells[2].textContent.trim() === 'pcc_default') {
        const headers = Array.from(document.querySelectorAll('.layui-table thead th')).map((th, i) => i + ':' + th.textContent.trim());
        return { headers, cells: Array.from(cells).map((c, i) => i + '=' + c.textContent.trim()) };
      }
    }
    return null;
  });
  
  console.log('表头:', JSON.stringify(result ? result.headers : 'null'));
  console.log('行数据:', JSON.stringify(result ? result.cells : 'null'));
  
  // 也查看PCC编辑页的字段
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 9 && cells[2].textContent.trim() === 'pcc_default') {
        const links = cells[9].querySelectorAll('a');
        for (const l of links) { if (l.textContent.trim() === '编辑') { l.click(); return; } }
      }
    }
  });
  await page.waitForTimeout(3000);
  
  const frame = page.frame('layui-layer-iframe2');
  if (frame) {
    const fields = await frame.evaluate(() => {
      return Array.from(document.querySelectorAll('.layui-form-item')).map(item => {
        const label = item.querySelector('.layui-form-label')?.textContent?.trim() || '';
        const input = item.querySelector('input[name]');
        const select = item.querySelector('select');
        return { label, name: input?.name || select?.name || '', value: input?.value || '' };
      });
    });
    console.log('\nPCC编辑页字段:', JSON.stringify(fields, null, 2));
    
    // xm-select 值
    const xmValues = await frame.evaluate(() => {
      return Array.from(document.querySelectorAll('input.xm-select-default')).map((inp, i) => ({ idx: i, value: inp.value }));
    });
    console.log('\nxm-select值:', JSON.stringify(xmValues));
  }
  
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });