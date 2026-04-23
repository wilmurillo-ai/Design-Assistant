/**
 * qos_detail_explore.js - 探索 QoS 服务质量控制页面
 * 找到 maxbrUl, maxbrDl, gbrUl, gbrDl 在哪里设置
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { project: 'XW_SUPF_5_1_2_4', headed: true };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  return opts;
}

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
  const opts = parseArgs();
  const browser = await chromium.launch({ headless: !opts.headed, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);

  // 导航到 QoS 服务质量控制页面
  console.log('\n🌐 导航到 QoS 配置页面...');
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  console.log(`   URL: ${page.url()}`);

  // 打印页面所有文字
  const pageText = await page.evaluate(() => document.body.innerText);
  console.log('\n📄 页面内容（前3000字符）:');
  console.log(pageText.substring(0, 3000));

  // 获取所有输入字段
  const inputs = await page.evaluate(() => {
    const result = [];
    document.querySelectorAll('input, select, textarea').forEach(el => {
      if (el.name || el.id) {
        result.push({
          tag: el.tagName,
          name: el.name,
          id: el.id,
          type: el.type,
          value: el.value,
          placeholder: el.placeholder
        });
      }
    });
    return result;
  });
  console.log('\n📋 输入字段:');
  inputs.forEach(i => console.log(`  ${i.tag} [${i.type}] name="${i.name}" id="${i.id}" value="${i.value}"`));

  // 获取表格内容（如果有的话）
  const tableData = await page.evaluate(() => {
    const tables = document.querySelectorAll('.layui-table, table');
    const result = [];
    tables.forEach((tbl, idx) => {
      const headers = [];
      tbl.querySelectorAll('thead th').forEach(th => headers.push(th.textContent.trim()));
      const rows = [];
      tbl.querySelectorAll('tbody tr').forEach(tr => {
        const cells = [];
        tr.querySelectorAll('td').forEach(td => cells.push(td.textContent.trim()));
        if (cells.length > 0) rows.push(cells);
      });
      if (headers.length > 0 || rows.length > 0) {
        result.push({ idx, headers, rows });
      }
    });
    return result;
  });

  console.log('\n📊 表格:');
  tableData.forEach(t => {
    console.log(`  表格${t.idx}: headers=${JSON.stringify(t.headers)}`);
    t.rows.slice(0, 10).forEach(r => console.log(`    row: ${JSON.stringify(r)}`));
  });

  // 获取 layui-table 的确切内容（layui框架）
  const layuiTable = await page.evaluate(() => {
    const tables = document.querySelectorAll('.layui-table');
    const result = [];
    tables.forEach((tbl, ti) => {
      const headers = [];
      tbl.querySelectorAll('thead th').forEach(th => headers.push(th.textContent.trim()));
      const rows = [];
      tbl.querySelectorAll('tbody tr').forEach(tr => {
        const cells = Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim());
        rows.push(cells);
      });
      result.push({ ti, headers, rows });
    });
    return result;
  });

  if (layuiTable.length > 0) {
    console.log('\n📊 Layui表格:');
    layuiTable.forEach(t => {
      console.log(`  表格${t.ti}: headers=${JSON.stringify(t.headers)}`);
      t.rows.slice(0, 20).forEach(r => console.log(`    ${JSON.stringify(r)}`));
    });
  }

  // 获取所有按钮
  const buttons = await page.evaluate(() => {
    const btns = [];
    document.querySelectorAll('button, a.layui-btn, .layui-btn').forEach(b => {
      if (b.textContent.trim()) {
        btns.push({ text: b.textContent.trim(), href: b.href || '', onclick: b.getAttribute('onclick') || '' });
      }
    });
    return btns;
  });
  console.log('\n🔘 按钮:');
  buttons.forEach(b => console.log(`  "${b.text}" href=${b.href} onclick=${b.onclick}`));

  // 截图
  await page.screenshot({ path: 'qos_detail.png', fullPage: true });
  console.log('\n📸 截图已保存: qos_detail.png');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
