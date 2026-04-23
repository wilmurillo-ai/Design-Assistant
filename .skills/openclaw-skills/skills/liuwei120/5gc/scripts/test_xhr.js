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
  // Try fetching the PCC list API directly (no auth cookies needed in same context)
  const apiData = await page.evaluate(async function() {
    try {
      // First get CSRF token from page
      const token = document.querySelector('meta[name="csrf-token"]') ||
                    document.querySelector('input[name="_token"]');
      const tokenVal = token ? token.content || token.value : '';
      const resp = await fetch('/predfPolicy/pcc/index', {
        headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRF-TOKEN': tokenVal }
      });
      return { status: resp.status, url: resp.url, contentType: resp.headers.get('content-type') };
    } catch(e) { return { error: e.message }; }
  });
  console.log('API response:', JSON.stringify(apiData));
  // Alternative: use XHR
  const xhrData = await page.evaluate(function() {
    return new Promise(function(resolve) {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/predfPolicy/pcc/index', true);
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) resolve({ status: xhr.status, len: xhr.responseText.length, url: xhr.responseURL });
      };
      xhr.send();
      setTimeout(function() { resolve({ timeout: true }); }, 5000);
    });
  });
  console.log('XHR response:', JSON.stringify(xhrData));
  await browser.close();
})().catch(function(e) { console.error(e.message); });
