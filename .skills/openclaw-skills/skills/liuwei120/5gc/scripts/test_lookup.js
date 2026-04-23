const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox','--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: {width:1920,height:1080} });
  const page = await ctx.newPage();

  // Login
  await page.goto('https://192.168.3.89/login', { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', {name:'E-Mail地址'}).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', {name:'密码'}).fill('dotouch');
  await page.getByRole('button', {name:'登录'}).click();
  await page.waitForTimeout(2500);
  console.log('Logged in');

  // Select project
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
  console.log('Project selected, URL:', page.url());

  // Navigate to PCC
  await page.goto('https://192.168.3.89/sim_5gc/predfPolicy/pcc/index', { waitUntil: 'commit', ignoreHTTPSErrors: true });

  // Wait for pcc2 text
  try {
    await page.waitForFunction(function() {
      return document.body.textContent.includes('pcc2');
    }, { timeout: 15000 });
    console.log('pcc2 found in body!');
  } catch(e) {
    console.log('pcc2 NOT found in body within timeout');
    await browser.close();
    return;
  }

  // Now query DOM
  await page.waitForTimeout(3000);
  const result = await page.evaluate(function() {
    var tables = document.querySelectorAll('.layui-table');
    var info = [];
    for (var ti = 0; ti < tables.length; ti++) {
      var table = tables[ti];
      var rows = table.querySelectorAll('tbody tr');
      info.push('TABLE ' + ti + ': ' + rows.length + ' rows');
      for (var ri = 0; ri < rows.length; ri++) {
        var row = rows[ri];
        var cells = row.querySelectorAll('td');
        var txt = '  row' + ri + ' cells=' + cells.length + ': ';
        for (var ci = 0; ci < cells.length; ci++) {
          txt += '[' + ci + ']="' + cells[ci].textContent.trim().substring(0, 15) + '" ';
        }
        info.push(txt);
      }
    }
    return info.join('\n');
  });
  console.log('DOM structure:\n' + result);

  // Now try the exact query from the skill
  const lookup = await page.evaluate(function(targetId) {
    var tables = document.querySelectorAll('.layui-table');
    for (var ti = 0; ti < tables.length; ti++) {
      var table = tables[ti];
      var rows = table.querySelectorAll('tbody tr');
      for (var ri = 0; ri < rows.length; ri++) {
        var row = rows[ri];
        var cells = row.querySelectorAll('td');
        if (cells.length < 9) continue;
        var c0 = cells[0].textContent.trim();
        var c1 = cells[1].textContent.trim();
        if (c1 === targetId) return { found: true, id: c0 };
      }
    }
    return { found: false };
  }, 'pcc2');
  console.log('Lookup result:', JSON.stringify(lookup));

  await browser.close();
})().catch(function(e) { console.error(e.message); });
