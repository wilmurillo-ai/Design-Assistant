/**
 * test_qos_single.js - 单测 qos-add-skill
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

  const testQosId = 'qos_regtest_' + Date.now();
  
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  console.log('到达QoS列表页');
  
  // 点击添加
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(5000);
  
  // 获取frame
  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('❌ 未找到 layui-layer-iframe2'); await browser.close(); return; }
  console.log('✅ 找到frame:', frame.url());
  
  // 填写
  await frame.locator('input[name="qosId"]').fill(testQosId);
  await frame.locator('input[name="5qi"]').fill('9');
  await frame.locator('input[name="maxbrUl"]').fill('10000000');
  await frame.locator('input[name="maxbrDl"]').fill('20000000');
  await frame.locator('input[name="gbrUl"]').fill('5000000');
  await frame.locator('input[name="gbrDl"]').fill('5000000');
  console.log('✅ 填写完成');
  
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
  const found = rows.find(r => r[2] === testQosId);
  if (found) {
    console.log(`\n🎉 QoS模板创建成功!`);
    console.log(`  qosId=${found[2]}, 5qi=${found[3]}, maxbrUl=${found[4]}, maxbrDl=${found[5]}, gbrUl=${found[6]}, gbrDl=${found[7]}`);
  } else {
    console.log(`\n❌ QoS模板 ${testQosId} 未找到`);
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });