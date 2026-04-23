/**
 * explore_smpolicy_ue.js - 探索 UE Smpolicy 添加页结构
 */
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

  // 选择工程
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

  // 导航到 UE smpolicy 列表
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/ue/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  console.log('UE smpolicy列表页:', page.url());
  console.log('页面内容:', (await page.evaluate(() => document.body.innerText)).substring(0, 500));

  // 点添加按钮
  const addBtn = page.locator('button:has-text("添加")');
  console.log('添加按钮:', await addBtn.count(), '个');
  await addBtn.click();
  await page.waitForTimeout(3000);

  // 检查弹窗iframe
  const frames = page.frames();
  console.log('所有iframe:', frames.map(f => ({ url: f.url(), name: f.name() })));

  const editFrame = frames.find(f => f.url().includes('/edit'));
  if (editFrame) {
    console.log('\n编辑帧 URL:', editFrame.url());
    await editFrame.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 列出所有input/select
    const fields = await editFrame.evaluate(() => {
      const result = [];
      document.querySelectorAll('input[name], select[name], textarea[name]').forEach(el => {
        result.push({ tag: el.tagName, name: el.name, value: el.value, type: el.type || '' });
      });
      return result;
    });
    console.log('\n字段:', JSON.stringify(fields, null, 2));

    // xm-select 状态
    const xmState = await editFrame.evaluate(() => {
      const inputs = document.querySelectorAll('input.xm-select-default');
      return Array.from(inputs).map((inp, i) => ({
        idx: i, name: inp.name, value: inp.value,
        display: inp.parentElement?.textContent?.substring(0, 100)
      }));
    });
    console.log('\nxm-select 状态:', JSON.stringify(xmState, null, 2));

    // 列出所有可点击按钮
    const btns = await editFrame.evaluate(() =>
      Array.from(document.querySelectorAll('button')).map(b => ({ text: b.textContent.trim(), type: b.type }))
    );
    console.log('\n按钮:', JSON.stringify(btns));

    // 截图
    await page.screenshot({ path: 'smpolicy_ue_add.png', fullPage: true });
    console.log('\n截图: smpolicy_ue_add.png');
  } else {
    console.log('未找到 /edit iframe');
    const allIframes = page.frames().map(f => ({ name: f.name(), url: f.url() }));
    console.log('所有frames:', JSON.stringify(allIframes));
    await page.screenshot({ path: 'smpolicy_ue_no_iframe.png', fullPage: true });
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });