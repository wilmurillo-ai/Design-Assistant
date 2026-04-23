/**
 * fix_pcc_qos.js - 在 PCC 编辑模式下修复 refQosData（qos1）
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

  // 直接打开 PCC 编辑页 ID=17484
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/edit/17484`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 检查初始状态
  const initial = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('input.xm-select-default')).map((inp, i) => ({ idx: i, value: inp.value }));
  });
  console.log('初始 xm-select:', JSON.stringify(initial));

  // 方法1：用 Playwright locator 直接点击 xm-select 选项
  // 先打开下拉
  await page.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[0]) inputs[0].parentElement.click();
  });
  await page.waitForTimeout(1500);
  
  // 用 Playwright locator 找到可见选项并点击
  // 在页面上查找包含 "qos1" 的选项
  const optionLocator = page.locator('.xm-option.show-icon', { hasText: 'qos1' }).first();
  const optionVisible = await optionLocator.isVisible({ timeout: 3000 }).catch(() => false);
  console.log('qos1 选项可见:', optionVisible);
  
  if (optionVisible) {
    await optionLocator.click();
    console.log('用 locator 点击了 qos1');
    await page.waitForTimeout(1000);
  } else {
    // 备选：用 JS 点击
    const clicked = await page.evaluate(() => {
      const opts = document.querySelectorAll('.xm-option.show-icon');
      for (const opt of opts) {
        if (opt.textContent.trim() === 'qos1') {
          opt.click();
          return true;
        }
      }
      return false;
    });
    console.log('JS 点击 qos1:', clicked ? '成功' : '失败');
  }

  // 再次检查值
  const afterSelect = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('input.xm-select-default')).map((inp, i) => ({ idx: i, value: inp.value }));
  });
  console.log('选择后 xm-select:', JSON.stringify(afterSelect));

  // 提交
  await page.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log('提交后URL:', page.url());

  // 验证
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const result = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 7 && cells[2].textContent.trim() === 'pcc_default') {
        return { refQosData: cells[5].textContent.trim(), refTcData: cells[6].textContent.trim() };
      }
    }
    return null;
  });
  
  console.log('\n📋 验证结果:');
  console.log('   refQosData:', result ? result.refQosData : 'null');
  console.log('   refTcData:', result ? result.refTcData : 'null');
  if (result) {
    console.log(result.refQosData === 'qos1' && result.refTcData === 'tc1' ? '\n🎉 全部正确！' : '\n❌ 仍有问题');
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });