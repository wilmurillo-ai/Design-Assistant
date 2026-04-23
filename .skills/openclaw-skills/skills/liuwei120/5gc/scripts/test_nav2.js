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
  await page.evaluate(function(name) {
    var rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
    for (var i = 0; i < rows.length; i++) {
      var cells = rows[i].querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === name) {
        var icon = cells[1].querySelector('.iconfont');
        if (icon) { icon.click(); return; }
      }
    }
  }, 'XW_SUPF_5_1_2_4');
  await page.waitForTimeout(3000);
  console.log('URL after select:', page.url());
  // Navigate to PCC and wait for pcc2 specifically
  await page.goto('https://192.168.3.89/sim_5gc/predfPolicy/pcc/index', { waitUntil: 'commit', ignoreHTTPSErrors: true });
  try {
    await page.waitForFunction(function() {
      // Check if pcc2 text appears in any table
      return document.body.textContent.includes('pcc2');
    }, { timeout: 15000 });
    console.log('pcc2 appeared!');
  } catch(e) {
    console.log('pcc2 did not appear within timeout');
  }
  await page.waitForTimeout(2000);
  const info = await page.evaluate(function() {
    var rows = document.querySelectorAll('.layui-table tbody tr');
    var result = [];
    for (var i = 0; i < rows.length; i++) {
      var txt = rows[i].textContent.trim();
      if (txt.length > 5) result.push(txt.substring(0, 60));
    }
    return { url: window.location.href, rows: result };
  });
  console.log(JSON.stringify(info, null, 2));
  await browser.close();
})().catch(function(e) { console.error(e.message); });
