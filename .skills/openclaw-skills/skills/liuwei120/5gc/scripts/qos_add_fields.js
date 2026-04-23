/**
 * qos_add_fields.js - 检查添加表单的实际字段名
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
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  // 去添加页
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(2000);

  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.log('❌ 未找到iframe'); await browser.close(); return; }

  // 打印所有输入字段（带label/placeholder）
  const fields = await frame.evaluate(() => {
    const result = [];
    // 找所有有name属性的input
    document.querySelectorAll('input[name], select[name], textarea[name]').forEach(el => {
      // 获取label
      const id = el.id || el.name;
      const label = el.closest('.layui-form-item')?.querySelector('.layui-form-label')?.textContent || 
                    el.closest('label')?.textContent ||
                    el.closest('.layui-select')?.previousElementSibling?.textContent || '';
      result.push({
        tag: el.tagName,
        name: el.name,
        id: el.id,
        type: el.type,
        value: el.value,
        label: label.trim()
      });
    });
    return result;
  });

  console.log('\n📋 表单字段:');
  fields.forEach(f => console.log(`  ${f.tag} [${f.type}] name="${f.name}" label="${f.label}" value="${f.value}"`));

  // 也打印表格形式的字段
  const tableFields = await frame.evaluate(() => {
    const result = [];
    // 找所有 layui-form-item
    document.querySelectorAll('.layui-form-item').forEach(item => {
      const label = item.querySelector('.layui-form-label')?.textContent?.trim() || '';
      const input = item.querySelector('input[name]');
      if (input) {
        result.push({ name: input.name, label, value: input.value, type: input.type });
      }
    });
    return result;
  });

  console.log('\n📋 表格字段 (layui-form-item):');
  tableFields.forEach(f => console.log(`  name="${f.name}" label="${f.label}" value="${f.value}"`));

  await page.screenshot({ path: 'qos_add_form.png' });
  console.log('\n📸 截图: qos_add_form.png');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
