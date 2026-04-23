/**
 * debug_qos_add.js - 探索 QoS 添加页面结构
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

  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  console.log('QoS列表页 URL:', page.url());
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(5000);

  console.log('点击后 URL:', page.url());
  console.log('layui-layer弹窗数量:', await page.locator('.layui-layer').count());

  // 获取所有frames
  const allFrames = page.frames();
  console.log('\n所有frames:');
  for (const f of allFrames) {
    console.log(`  name="${f.name()}", url="${f.url()}"`);
  }

  // 找到layui-layer-iframe2（QoS编辑页）
  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('❌ 未找到 layui-layer-iframe2'); await browser.close(); return; }
  console.log('✅ 找到 layui-layer-iframe2:', frame.url());

  await page.waitForTimeout(2000);

  const inputs = await frame.evaluate(() => {
    return Array.from(document.querySelectorAll('input[name], select[name]')).map(inp => ({
      name: inp.name || '',
      tag: inp.tagName,
      type: inp.type || '',
      placeholder: inp.placeholder || '',
      value: inp.value ? inp.value.substring(0, 30) : ''
    }));
  });
  console.log('\niframe内字段:', JSON.stringify(inputs, null, 2));

  const btns = await frame.evaluate(() => {
    return Array.from(document.querySelectorAll('button, .layui-btn')).map(b => b.textContent.trim()).filter(t => t);
  });
  console.log('iframe内按钮:', JSON.stringify(btns));

  await page.screenshot({ path: 'qos_add_popup.png', fullPage: true });
  console.log('截图: qos_add_popup.png');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });