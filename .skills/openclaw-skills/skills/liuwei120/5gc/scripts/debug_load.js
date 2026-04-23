const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox','--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: {width:1920,height:1080} });
  const page = await ctx.newPage();
  await page.goto('https://192.168.3.89/login', { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', {name:'E-Mail地址'}).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', {name:'密码'}).fill('dotouch');
  await page.getByRole('button', {name:'登录'}).click();
  await page.waitForTimeout(2500);
  await page.goto('https://192.168.3.89/sim_5gc/project/index', { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.evaluate((name) => {
    const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === name) {
        const icon = cells[1].querySelector('.iconfont');
        if (icon) { icon.click(); return; }
      }
    }
  }, 'XW_SUPF_5_1_2_4');
  await page.waitForTimeout(3000);
  await page.goto('https://192.168.3.89/sim_5gc/load/index', { ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  // Click dedicated edit
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 5 && cells[2].textContent.trim() === 'dedicated') {
        const links = Array.from(cells[5].querySelectorAll('a'));
        const editLink = links.find(l => l.textContent.trim() === '编辑');
        if (editLink) { editLink.click(); return; }
      }
    }
  });
  await page.waitForSelector('.layui-layer', { timeout: 5000 });
  await page.waitForTimeout(1000);
  for (let i = 0; i < 10; i++) {
    const allFrames = await page.frames();
    const frameList = allFrames.map(f => ({ name: f.name(), url: f.url() }));
    const mainFrame = page.mainFrame();
    const mainUrl = mainFrame.url();
    console.log('[' + (i*500) + 'ms] mainFrame=' + mainUrl + ' frames=' + JSON.stringify(frameList));
    if (mainUrl.includes('/load/edit/')) { console.log('FOUND in mainFrame!'); break; }
    await new Promise(r => setTimeout(r, 500));
  }
  // Try getting inputs from main frame
  const mainUrl = page.mainFrame().url();
  console.log('Main frame URL:', mainUrl);
  if (mainUrl.includes('/load/edit/')) {
    const inputs = await page.evaluate(() => {
      const allInputs = document.querySelectorAll('input, textarea');
      return Array.from(allInputs).map(el => ({ tag: el.tagName, name: el.name, val: el.value ? el.value.substring(0, 40) : '[empty]' })).filter(el => el.name);
    });
    console.log('Inputs from main frame:', JSON.stringify(inputs.slice(0, 15), null, 2));
  }
  await browser.close();
})().catch(e => console.error(e.message));
