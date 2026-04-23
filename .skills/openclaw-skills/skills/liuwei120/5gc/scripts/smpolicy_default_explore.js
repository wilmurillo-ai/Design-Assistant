/**
 * smpolicy_default_explore.js - 探索 smpolicy/default 页面
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

  // 导航到 smpolicy/default/index
  console.log('\n🌐 导航到 smpolicy/default/index...');
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  console.log(`   URL: ${page.url()}`);
  
  // 获取页面内容
  const pageText = await page.evaluate(() => document.body.innerText);
  console.log('\n📄 页面内容（前4000字符）:');
  console.log(pageText.substring(0, 4000));
  
  // 获取所有输入字段
  const inputs = await page.evaluate(() => {
    const result = [];
    document.querySelectorAll('input, select, textarea').forEach(el => {
      if (el.name || el.id) {
        result.push({ tag: el.tagName, name: el.name, type: el.type, value: el.value });
      }
    });
    return result;
  });
  console.log('\n📋 输入字段:');
  inputs.forEach(i => console.log(`  ${i.tag} [${i.type}] name="${i.name}" value="${i.value}"`));
  
  // 获取layui表格
  const tables = await page.evaluate(() => {
    const result = [];
    document.querySelectorAll('.layui-table').forEach((tbl, idx) => {
      const headers = Array.from(tbl.querySelectorAll('thead th')).map(th => th.textContent.trim());
      const rows = Array.from(tbl.querySelectorAll('tbody tr')).map(tr => 
        Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
      );
      result.push({ idx, headers, rows });
    });
    return result;
  });
  
  console.log('\n📊 表格:');
  tables.forEach(t => {
    console.log(`  表格${t.idx}: headers=${JSON.stringify(t.headers)}`);
    t.rows.slice(0, 10).forEach(r => console.log(`    ${JSON.stringify(r)}`));
  });
  
  // 获取所有按钮
  const buttons = await page.evaluate(() => {
    const result = [];
    document.querySelectorAll('button, .layui-btn').forEach(b => {
      if (b.textContent.trim()) result.push(b.textContent.trim());
    });
    return [...new Set(result)];
  });
  console.log('\n🔘 按钮:', buttons);
  
  // 截图
  await page.screenshot({ path: 'smpolicy_default.png', fullPage: true });
  console.log('\n📸 截图: smpolicy_default.png');
  
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
