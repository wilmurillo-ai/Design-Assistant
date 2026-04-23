/**
 * debug_tc_add.js - 调试 TC 创建
 */
const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';

async function login(page) {
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);
}

async function selectProject(page, name) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.locator('input[name="project_search_name"]').fill(name);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  await page.evaluate((n) => {
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) cells[1].querySelector('.iconfont').click();
    });
  }, name);
  await page.waitForTimeout(3000);
}

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, 'XW_SUPF_SN4_5_2_8');

  // 去 TC 列表页
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/trafficCtl/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  console.log('TC列表页URL:', page.url());
  console.log('TC列表页内容（前500字）:', (await page.evaluate(() => document.body.innerText)).substring(0, 500));

  // 点添加按钮
  const addBtn = page.locator('button:has-text("添加")');
  console.log('\n添加按钮数量:', await addBtn.count());
  await addBtn.click();
  await page.waitForTimeout(3000);
  
  // 检查是否有iframe弹窗
  const iframeCount = await page.locator('iframe[name="layui-layer-iframe2"]').count();
  console.log('iframe数量:', iframeCount);
  
  if (iframeCount > 0) {
    const frame = page.frame('layui-layer-iframe2');
    console.log('iframe URL:', frame.url());
    
    // 等待 iframe 内容加载
    await frame.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);
    
    // 打印 iframe 内容
    const frameText = await frame.evaluate(() => document.body.innerText);
    console.log('\niframe内容:', frameText.substring(0, 1000));
    
    // 找所有input
    const inputs = await frame.evaluate(() => {
      const result = [];
      document.querySelectorAll('input[name], select[name], textarea[name]').forEach(el => {
        result.push({ tag: el.tagName, name: el.name, value: el.value, type: el.type });
      });
      return result;
    });
    console.log('\niframe输入字段:', JSON.stringify(inputs, null, 2));
    
    // 尝试填写
    const tcIdInput = frame.locator('input[name="tcId"]').first();
    console.log('\ntcId input 数量:', await tcIdInput.count());
    if (await tcIdInput.count() > 0) {
      await tcIdInput.fill('tc1');
      console.log('已填写 tcId=tc1');
      
      // 点提交
      const submitBtn = frame.locator('button:has-text("提交")').first();
      console.log('提交按钮数量:', await submitBtn.count());
      await submitBtn.click();
      await page.waitForTimeout(3000);
      
      console.log('\n提交后URL:', page.url());
      
      // 检查TC列表
      await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/trafficCtl/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
      await page.waitForTimeout(3000);
      
      const tcRows = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('.layui-table tbody tr')).map(row => {
          return Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim());
        });
      });
      console.log('\nTC列表行数:', tcRows.length);
      console.log('TC列表:', JSON.stringify(tcRows));
    } else {
      // 没有tcId input，说明可能还在iframe里但DOM不同
      console.log('未找到tcId input，检查是否直接嵌入页面...');
      const directInputs = await page.evaluate(() => {
        const result = [];
        document.querySelectorAll('input[name]').forEach(el => {
          result.push({ name: el.name, value: el.value });
        });
        return result;
      });
      console.log('页面直接input:', JSON.stringify(directInputs));
    }
  } else {
    // 检查页面上的内容
    const pageText = await page.evaluate(() => document.body.innerText);
    console.log('\n无iframe，页面内容:', pageText.substring(0, 500));
  }
  
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });