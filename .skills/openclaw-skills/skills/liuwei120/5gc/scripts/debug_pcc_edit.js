/**
 * debug_pcc_edit.js - 探索 PCC 添加页的完整字段结构
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
  await page.locator('input[name="project_search_name"]').fill(name);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
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

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, 'XW_SUPF_SN4_5_2_8');

  // 去 PCC 列表
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);
  
  await page.waitForFunction(() => window.location.href.includes('/predfPolicy/pcc/edit'), { timeout: 10000 });
  await page.waitForTimeout(3000);

  // 打印页面内容
  const pageText = await page.evaluate(() => document.body.innerText);
  console.log('\n📄 PCC添加页内容:');
  console.log(pageText.substring(0, 3000));

  // 打印所有字段
  const fields = await page.evaluate(() => {
    const result = [];
    document.querySelectorAll('.layui-form-item').forEach(item => {
      const label = item.querySelector('.layui-form-label')?.textContent?.trim() || '';
      const input = item.querySelector('input[name]');
      const select = item.querySelector('select[name]');
      if (input) {
        result.push({ label, name: input.name, value: input.value, type: input.type });
      } else if (select) {
        result.push({ label, name: select.name });
      }
    });
    return result;
  });
  
  console.log('\n📋 表单字段 (layui-form-item):');
  fields.forEach(f => console.log(`  "${f.label}" -> name="${f.name}" value="${f.value || ''}"`));

  // xm-select 数量和显示文本
  const xmSelects = await page.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    return Array.from(inputs).map((inp, idx) => {
      const parent = inp.parentElement;
      return { idx, display: parent.textContent.substring(0, 200) };
    });
  });
  
  console.log('\n📋 xm-select 下拉列表:');
  xmSelects.forEach(s => console.log(`  [${s.idx}]: ${s.display}`));

  // 尝试点击每个 xm-select 看选项
  for (let i = 0; i < xmSelects.length; i++) {
    await page.evaluate((idx) => {
      const inputs = document.querySelectorAll('input.xm-select-default');
      if (inputs[idx]) inputs[idx].parentElement.click();
    }, i);
    await page.waitForTimeout(1000);
    
    const options = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.xm-option.show-icon')).map(o => o.textContent.trim());
    });
    
    console.log(`\n  xm-select[${i}] 选项:`, JSON.stringify(options));
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
  }

  await page.screenshot({ path: 'pcc_add_debug.png', fullPage: true });
  console.log('\n📸 截图: pcc_add_debug.png');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });