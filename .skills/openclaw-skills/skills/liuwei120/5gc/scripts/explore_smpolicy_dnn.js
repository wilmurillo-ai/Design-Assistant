const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await page.goto(`${globalBaseUrl}/login`, { ignoreHTTPSErrors: true, timeout: 15000 });
  await page.waitForTimeout(1500);
  await page.getByRole('textbox', { name: 'E-Mail地址' }).fill('dotouch@dotouch.com.cn');
  await page.getByRole('textbox', { name: '密码' }).fill('dotouch');
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(2500);

  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.locator('input[name="project_search_name"]').fill('XW_SUPF_5_1_2_4');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  await page.evaluate(() => {
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === 'XW_SUPF_5_1_2_4') cells[1].querySelector('.iconfont').click();
    });
  });
  await page.waitForTimeout(3000);

  // 探索 DNN 列表页
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/dnn/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  console.log('DNN列表页:', page.url());

  // 点添加
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);

  const frames = page.frames();
  const editFrame = frames.find(f => f.url().includes('/edit'));
  if (editFrame) {
    await editFrame.waitForLoadState('domcontentloaded');
    console.log('编辑帧:', editFrame.url());
    const fields = await editFrame.evaluate(() => {
      const result = [];
      document.querySelectorAll('input[name], select[name]').forEach(el => result.push({ name: el.name, value: el.value }));
      return result;
    });
    console.log('字段:', JSON.stringify(fields));
    const xmState = await editFrame.evaluate(() => {
      const inputs = document.querySelectorAll('input.xm-select-default');
      return Array.from(inputs).map((inp, i) => ({ idx: i, display: inp.parentElement?.textContent?.substring(0, 80) }));
    });
    console.log('xm-select:', JSON.stringify(xmState));
    const btns = await editFrame.evaluate(() => Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim()));
    console.log('按钮:', btns);
  }

  // 关闭弹窗，探索编辑页
  await page.keyboard.press('Escape');
  await page.waitForTimeout(1000);

  // 找已有记录看能否编辑
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/dnn/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const rows = await page.evaluate(() => {
    const result = [];
    document.querySelectorAll('.layui-table tbody tr').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 8) result.push({ id: cells[1].textContent.trim(), name: cells[2].textContent.trim(), dnn: cells[3].textContent.trim() });
    });
    return result;
  });
  console.log('\n现有DNN策略:', JSON.stringify(rows.slice(0, 3)));

  if (rows.length > 0) {
    // 直接访问编辑页
    await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/dnn/edit/${rows[0].id}`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
    await page.waitForTimeout(3000);
    console.log('\n编辑页URL:', page.url());
    console.log('页面内容:', (await page.evaluate(() => document.body.innerText)).substring(0, 500));
    const dnnFrames = page.frames();
    console.log('iframe数量:', dnnFrames.length);
    const dnnFields = await page.evaluate(() => {
      const result = [];
      document.querySelectorAll('input[name], select[name]').forEach(el => result.push({ name: el.name, value: el.value }));
      return result;
    });
    console.log('主页面字段:', JSON.stringify(dnnFields));
    const dnnBtns = await page.evaluate(() => Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim()));
    console.log('主页面按钮:', dnnBtns);
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });