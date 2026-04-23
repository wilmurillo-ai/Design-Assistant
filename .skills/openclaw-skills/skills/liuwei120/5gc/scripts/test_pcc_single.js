/**
 * test_pcc_single.js - 单测 pcc-add-skill 的添加流程
 */
const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';

async function login(page) {
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000, waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  try { await page.locator('input[name="email"]').first().waitFor({ state: 'visible', timeout: 5000 }); } catch(e) {}
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);
  console.log('✅ 登录成功');
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
  console.log(`✅ 工程 "${name}" 已选`);
}

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  const testPccId = 'pcc_regtest_' + Date.now();
  
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  console.log('PCC列表页 URL:', page.url());
  console.log('弹窗数量:', await page.locator('.layui-layer').count());
  
  // 点击添加
  await page.locator('button:has-text("添加")').click();
  
  // 等待 URL 变化（主框架跳转到 /predfPolicy/pcc/edit）
  await page.waitForFunction(() => window.location.href.includes('/predfPolicy/pcc/edit'), { timeout: 10000 });
  await page.waitForTimeout(3000);
  
  console.log('点击后 URL:', page.url());
  console.log('弹窗数量:', await page.locator('.layui-layer').count());
  
  // 检查页面上的iframe
  const iframes = await page.locator('iframe').all();
  for (const iframe of iframes) {
    console.log(`  iframe: name="${await iframe.getAttribute('name')}", src="${await iframe.getAttribute('src')}"`);
  }
  
  // PCC 编辑页是主框架直接跳转，表单直接在主页面上
  // 但是 URL 显示的是 /predfPolicy/pcc/edit，这意味着表单可能在某个地方
  // 尝试查找表单
  const bodyText = await page.evaluate(() => document.body.innerText.substring(0, 500));
  console.log('\n页面内容（前500字）:', bodyText);
  
  // 查找input
  const inputs = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('input[name]')).map(inp => ({
      name: inp.name || '',
      type: inp.type || '',
      value: inp.value ? inp.value.substring(0, 30) : ''
    }));
  });
  console.log('\n页面input:', JSON.stringify(inputs));
  
  await page.screenshot({ path: 'pcc_add_page.png', fullPage: true });
  console.log('截图: pcc_add_page.png');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });