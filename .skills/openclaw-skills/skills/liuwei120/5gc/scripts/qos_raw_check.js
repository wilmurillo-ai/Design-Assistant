/**
 * qos_raw_check.js - 直接查看 qos3 的原始数据
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
  await page.evaluate((n) => {
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) {
        cells[1].querySelector('.iconfont').click();
      }
    });
  }, name);
  await page.waitForTimeout(3000);
}

async function main() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 打印所有表格
  const tables = await page.evaluate(() => {
    const result = [];
    document.querySelectorAll('.layui-table').forEach((tbl, ti) => {
      const headers = Array.from(tbl.querySelectorAll('thead th')).map((th, i) => i + ':' + th.textContent.trim());
      const rows = Array.from(tbl.querySelectorAll('tbody tr')).map(tr => 
        Array.from(tr.querySelectorAll('td')).map((td, i) => i + ':' + td.textContent.trim())
      );
      if (rows.length > 0) {
        result.push({ ti, headers, rows });
      }
    });
    return result;
  });

  tables.forEach(t => {
    console.log(`\n📊 表格${t.ti}:`);
    console.log('  表头:', t.headers);
    t.rows.forEach(r => {
      const hasQos3 = r.some(c => c.includes('qos3'));
      if (hasQos3) {
        console.log('  ★ qos3行:', r.join(' | '));
      }
    });
  });

  // 直接查找 qos3 的数据
  const qos3Data = await page.evaluate(() => {
    // 方法：直接搜索包含 qos3 的行
    const allRows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of allRows) {
      const cells = row.querySelectorAll('td');
      // 找 qosId 列
      for (let i = 0; i < cells.length; i++) {
        if (cells[i].textContent.trim() === 'qos3') {
          return Array.from(cells).map((c, idx) => idx + '=' + c.textContent.trim());
        }
      }
    }
    return null;
  });
  
  console.log('\n🔍 qos3 直接搜索结果:', qos3Data);

  // 也检查是否是编辑页
  console.log('\n🌐 当前URL:', page.url());
  
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
