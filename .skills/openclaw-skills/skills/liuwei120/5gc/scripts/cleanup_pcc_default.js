/**
 * cleanup_partial.js - 清理中间状态
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

async function deleteByName(page, url, targetName) {
  await page.goto(url, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const found = await page.evaluate((name) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.trim() === name) {
          const links = row.querySelectorAll('a');
          for (const l of links) {
            if (l.textContent.trim() === '删除') { l.click(); return true; }
          }
        }
      }
    }
    return false;
  }, targetName);
  if (found) {
    await page.waitForTimeout(1500);
    try { await page.locator('.layui-layer-btn0').click(); await page.waitForTimeout(2000); } catch(e) {}
    console.log(`  ✅ 已删除 ${targetName}`);
  } else {
    console.log(`  ℹ️ ${targetName} 不存在`);
  }
}

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, 'XW_SUPF_SN4_5_2_8');

  console.log('🗑️ 清理...');
  await deleteByName(page, `${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, 'pcc_default');
  await deleteByName(page, `${globalBaseUrl}/sim_5gc/smpolicy/default/index`, 'sm_policy_default');
  // 也清理旧的
  await deleteByName(page, `${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, 'pcc_qos1');
  await deleteByName(page, `${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, 'qos1');
  await deleteByName(page, `${globalBaseUrl}/sim_5gc/predfPolicy/trafficCtl/index`, 'tc1');

  console.log('\n✅ 完成');
  await browser.close();
}
main().catch(e => { console.error(e); process.exit(1); });