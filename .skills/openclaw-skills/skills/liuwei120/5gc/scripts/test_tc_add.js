/**
 * test_tc_add.js - 单测 TC (Traffic Control) 添加
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

  const testTcId = 'tc_regtest_' + Date.now();
  
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/trafficCtl/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(5000);
  
  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('❌ 未找到 layui-layer-iframe2'); await browser.close(); return; }
  console.log('✅ 找到 layui-layer-iframe2:', frame.url());
  await page.waitForTimeout(2000);
  
  // 填写 tcId
  await frame.locator('input[name="tcId"]').fill(testTcId);
  console.log('✅ 填写 tcId');
  
  // 使用 JS 方式设置 select（layui 的 select 可能被隐藏但JS可以设值）
  const selectResult = await frame.evaluate(() => {
    const sel = document.querySelector('select[name="flowStatus"]');
    if (sel) {
      sel.value = 'ENABLED-UPLINK';
      sel.dispatchEvent(new Event('change', { bubbles: true }));
      return { found: true, value: sel.value };
    }
    return { found: false };
  });
  console.log('flowStatus select 结果:', JSON.stringify(selectResult));
  
  // 提交
  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log('✅ 提交完成');
  
  // 验证
  const rows = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.layui-table tbody tr')).map(row =>
      Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
    );
  });
  const found = rows.find(r => r[2] === testTcId);
  if (found) {
    console.log(`\n🎉 TC创建成功! tcId=${found[2]}, flowStatus=${found[3]}`);
  } else {
    console.log(`\n❌ TC ${testTcId} 未找到`);
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });