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
  await page.goto('https://192.168.3.89/sim_5gc/predfPolicy/pcc/index', { ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  // Click pcc2 edit link
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      if (row.textContent.includes('pcc2') && row.textContent.includes('编辑')) {
        const links = Array.from(row.querySelectorAll('a'));
        const editLink = links.find(l => l.textContent.trim() === '编辑');
        if (editLink) { editLink.click(); return; }
      }
    }
  });
  await page.waitForSelector('.layui-layer', { timeout: 5000 });
  await page.waitForTimeout(500);
  for (let i = 0; i < 15; i++) {
    const frameInfo = await page.evaluate(() => {
      const iframe = document.querySelector('.layui-layer iframe');
      if (!iframe) return { src: 'no iframe' };
      return { name: iframe.name, id: iframe.id, src: iframe.getAttribute('src'), laySrc: iframe.getAttribute('lay-src') };
    });
    const allFrames = await page.frames();
    const frameList = allFrames.map(f => ({ name: f.name(), url: f.url() }));
    console.log('[' + (i*500) + 'ms] iframe=' + JSON.stringify(frameInfo) + ' frames=' + JSON.stringify(frameList));
    if (frameInfo.src && frameInfo.src.includes('/predfPolicy/pcc/edit/')) { console.log('FOUND!'); break; }
    await new Promise(r => setTimeout(r, 500));
  }
  await browser.close();
})().catch(e => console.error(e.message));
