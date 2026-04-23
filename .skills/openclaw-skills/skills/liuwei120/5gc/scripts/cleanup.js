/**
 * cleanup.js - 清理测试数据
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
  console.log('✅ 登录成功');
}

async function selectProject(page, name) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.evaluate((n) => {
    const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) {
        cells[1].querySelector('.iconfont').click();
        return;
      }
    }
  }, name);
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${name}" 已选`);
}

async function deleteByName(page, url, targetId) {
  await page.goto(url, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const found = await page.evaluate((id) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.trim() === id) {
          const btn = row.querySelector('a');
          if (btn && btn.textContent.trim() === '删除') {
            btn.click();
            return true;
          }
        }
      }
    }
    return false;
  }, targetId);
  if (found) {
    await page.waitForTimeout(1500);
    try {
      await page.locator('.layui-layer-btn0').click();
      await page.waitForTimeout(2000);
      console.log(`  ✅ 已删除 ${targetId}`);
    } catch(e) {
      console.log(`  ⚠️ 确认框未出现 ${targetId}`);
    }
  } else {
    console.log(`  ℹ️ ${targetId} 不存在，跳过`);
  }
}

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  console.log('\n🗑️ 清理测试数据...');
  await deleteByName(page, `${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, 'qos3');
  await deleteByName(page, `${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, 'pcc_default_test');

  console.log('\n✅ 清理完成');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
