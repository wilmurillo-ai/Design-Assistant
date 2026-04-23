/**
 * debug_tc.js - 探索 Traffic Control 添加页字段
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

  // 查看 TC 列表
  console.log('\n📋 TC列表:');
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/trafficCtl/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const tcList = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    const list = [];
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      list.push(Array.from(cells).map(c => c.textContent.trim()));
    });
    return list;
  });
  console.log(JSON.stringify(tcList, null, 2));

  // 查看 TC 添加页字段
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);
  
  const frame = page.frame('layui-layer-iframe2');
  if (frame) {
    const fields = await frame.evaluate(() => {
      const result = [];
      document.querySelectorAll('.layui-form-item').forEach(item => {
        const label = item.querySelector('.layui-form-label')?.textContent?.trim() || '';
        const input = item.querySelector('input[name]');
        if (input) result.push({ label, name: input.name, value: input.value });
      });
      return result;
    });
    console.log('\n📋 TC添加页字段:');
    fields.forEach(f => console.log(`  "${f.label}" -> name="${f.name}"`));
  }

  // 查看 PCC 列表已有数据（如果有）
  console.log('\n📋 PCC列表:');
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const pccList = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    const list = [];
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 8) list.push(Array.from(cells).map(c => c.textContent.trim()));
    });
    return list;
  });
  console.log(JSON.stringify(pccList, null, 2));

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });