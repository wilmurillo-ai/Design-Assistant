const { chromium } = require('playwright');
(async()=>{
  const browser = await chromium.launch({headless:true,args:['--no-sandbox','--ignore-certificate-errors','--disable-dev-shm-usage','--no-proxy-server','--proxy-server=direct://','--proxy-bypass-list=*']});
  const context = await browser.newContext({ignoreHTTPSErrors:true, viewport:{width:1440,height:900}});
  const page = await context.newPage();
  const base='https://192.168.3.89';
  await page.goto(base+'/login',{waitUntil:'commit', timeout:20000});
  await page.waitForTimeout(3000);
  await page.getByRole('textbox',{name:'E-Mail地址'}).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox',{name:'密码'}).fill('dotouch');
  const remember=page.getByRole('checkbox',{name:'记住我'});
  if (await remember.count()) await remember.check().catch(()=>{});
  await page.getByRole('button',{name:'登录'}).click();
  await page.waitForTimeout(5000);
  await page.goto(base+'/sim_5gc/project/index',{waitUntil:'commit', timeout:20000});
  await page.waitForTimeout(5000);
  const result = await page.evaluate(()=>({
    title: document.title,
    rows: document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').length,
    hasSearch: !!document.querySelector('input[name="project_search_name"]'),
    url: location.href
  }));
  console.log(JSON.stringify(result));
  await browser.close();
})().catch(e=>{ console.error(e.stack||e.message); process.exit(1); });
