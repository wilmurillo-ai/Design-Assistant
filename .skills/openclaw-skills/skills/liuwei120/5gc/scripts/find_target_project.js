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
  await page.waitForTimeout(3000);
  
  // 尝试触发搜索
  await page.locator('input[type="search"], input[name*="search"], input[placeholder*="搜索"]').first().fill('SUPF_SN4');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  
  const searchResults = await page.evaluate(() => {
    const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
    return Array.from(rows).map(row => {
      const cells = row.querySelectorAll('td');
      return cells.length >= 3 ? cells[2].textContent.trim() : null;
    }).filter(Boolean);
  });
  
  console.log('搜索结果 SUPF_SN4:', JSON.stringify(searchResults));
  
  // 清除搜索，看总共多少页
  await page.locator('input[type="search"], input[name*="search"], input[placeholder*="搜索"]').first().fill('');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  
  // 快速计算总页数
  const pageInfo = await page.evaluate(() => {
    const pager = document.querySelector('.jsgrid-pager');
    if (!pager) return null;
    const text = pager.textContent;
    // 查找类似 "1 / 50" 的模式
    const match = text.match(/(\d+)\s*\/\s*(\d+)/);
    if (match) return { current: parseInt(match[1]), total: parseInt(match[2]) };
    // 也可能分开显示
    const spans = pager.querySelectorAll('span');
    const nums = [];
    spans.forEach(s => { if (!isNaN(parseInt(s.textContent))) nums.push(parseInt(s.textContent)); });
    return nums.length >= 2 ? { current: nums[0], total: nums[1] } : null;
  });
  
  console.log('分页信息:', pageInfo);
  
  // 直接跳到后面几页看看
  if (pageInfo && pageInfo.total > 10) {
    // 跳到第5页
    await page.evaluate(() => {
      const links = document.querySelectorAll('.jsgrid-pager a');
      links.forEach(l => {
        if (l.textContent.trim() === '5') l.click();
      });
    });
    await page.waitForTimeout(2000);
    
    const p5 = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row')).map(row => {
        const cells = row.querySelectorAll('td');
        return cells.length >= 3 ? cells[2].textContent.trim() : null;
      }).filter(Boolean);
    });
    console.log('第5页:', JSON.stringify(p5));
    
    // 跳到第10页
    await page.evaluate(() => {
      const links = document.querySelectorAll('.jsgrid-pager a');
      links.forEach(l => {
        if (l.textContent.trim() === '10') l.click();
      });
    });
    await page.waitForTimeout(2000);
    
    const p10 = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row')).map(row => {
        const cells = row.querySelectorAll('td');
        return cells.length >= 3 ? cells[2].textContent.trim() : null;
      }).filter(Boolean);
    });
    console.log('第10页:', JSON.stringify(p10));
  }
  
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });