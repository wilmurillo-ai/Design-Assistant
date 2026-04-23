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
  
  const allProjects = [];
  let pageNum = 1;
  let emptyCount = 0;
  
  while (pageNum <= 200) {
    const projects = await page.evaluate(() => {
      const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
      const names = [];
      rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 3) names.push(cells[2].textContent.trim());
      });
      return names;
    });
    
    if (projects.length === 0) {
      emptyCount++;
      if (emptyCount >= 3) {
        console.log('连续3页为空，停止');
        break;
      }
    } else {
      emptyCount = 0;
      allProjects.push(...projects);
    }
    
    if (pageNum % 10 === 0) {
      console.log(`Page ${pageNum}: ${projects.length} projects, total ${allProjects.length}`);
    }
    
    // 检查Next按钮状态
    const nextState = await page.evaluate(() => {
      const links = document.querySelectorAll('.jsgrid-pager a');
      for (const l of links) {
        if (l.textContent.trim() === 'Next') {
          return l.classList.contains('jsgrid-pager-disabled') || l.getAttribute('aria-disabled') === 'true';
        }
      }
      return true;
    });
    
    if (nextState) break;
    
    await page.evaluate(() => {
      const links = document.querySelectorAll('.jsgrid-pager a');
      for (const l of links) {
        if (l.textContent.trim() === 'Next') { l.click(); break; }
      }
    });
    await page.waitForTimeout(2000);
    pageNum++;
  }
  
  console.log(`\n完成！总工程数: ${allProjects.length}`);
  
  // 搜索目标
  const targets = allProjects.filter(n => n.includes('SN4') || n.includes('5_2_8') || n.includes('5_2'));
  console.log('\n包含SN4/5_2_8/5_2的工程:', JSON.stringify(targets, null, 2));
  
  // 打印所有SUPF工程
  const supf = allProjects.filter(n => n.includes('SUPF'));
  console.log('\n所有SUPF工程:', JSON.stringify(supf, null, 2));
  
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });