/**
 * qos_verify.js - 验证 qos3 是否创建成功
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

async function selectProject(page, projectName) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  const clicked = await page.evaluate((name) => {
    const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === name) {
        const icon = cells[1].querySelector('.iconfont');
        if (icon) { icon.click(); return true; }
      }
    }
    return false;
  }, projectName);
  if (!clicked) { console.log('❌ 未找到工程'); process.exit(1); }
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${projectName}" 已选`);
}

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  // 去QoS列表页
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 搜索 qos3
  const qos3Exists = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.trim() === 'qos3') {
          return true;
        }
      }
    }
    return false;
  });

  console.log(`\n${qos3Exists ? '✅ qos3 已存在！' : '❌ qos3 不存在'}`);

  // 找到 qos3 的行
  const qos3Row = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (let i = 0; i < cells.length; i++) {
        if (cells[i].textContent.trim() === 'qos3') {
          // 返回这一行的所有单元格内容
          return Array.from(cells).map(c => c.textContent.trim());
        }
      }
    }
    return null;
  });

  if (qos3Row) {
    console.log('\n📋 qos3 行内容:');
    console.log(JSON.stringify(qos3Row));
  }

  await page.screenshot({ path: 'qos_verify.png', fullPage: true });
  console.log('\n📸 截图: qos_verify.png');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
