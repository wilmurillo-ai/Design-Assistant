/**
 * regression_check.js - 全面检查工程 XW_SUPF_5_1_2_4 的当前配置状态
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

async function getTableData(page, url) {
  await page.goto(url, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  return await page.evaluate(() => {
    const headers = Array.from(document.querySelectorAll('.layui-table thead th')).map((th, i) => i + ':' + th.textContent.trim());
    const rows = Array.from(document.querySelectorAll('.layui-table tbody tr')).map(row =>
      Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
    );
    return { headers, rows };
  });
}

async function main() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  console.log('========================================');
  console.log('工程 XW_SUPF_5_1_2_4 配置状态');
  console.log('========================================\n');

  // 1. PCF 列表
  const pcf = await getTableData(page, `${globalBaseUrl}/sim_5gc/pcf/index`);
  console.log('📋 PCF列表:');
  if (pcf.rows.length > 0) {
    console.log(`  表头: ${pcf.headers.filter(h => !h.startsWith('0:')).join(', ')}`);
    pcf.rows.forEach(r => {
      if (r.some(c => c.trim())) console.log(`  ${r.filter(c => c.trim()).join(' | ')}`);
    });
  } else { console.log('  无数据'); }

  // 2. PCF 编辑弹窗（查看 default_smpolicy 等）
  console.log('\n📋 PCF编辑弹窗（default_smpolicy配置）:');
  await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    if (rows.length > 0) {
      const links = rows[0].querySelectorAll('a');
      for (const l of links) { if (l.textContent.trim() === '编辑') { l.click(); return; } }
    }
  });
  await page.waitForTimeout(3000);
  const frame = page.frame('layui-layer-iframe2');
  if (frame) {
    const pcfEditData = await frame.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('input.xm-select-default')).map((inp, i) => ({
        idx: i, value: inp.value, display: inp.parentElement.textContent.substring(0, 80)
      }));
      const selects = Array.from(document.querySelectorAll('select[name]')).map(s => s.name + '=' + s.value);
      return { inputs, selects };
    });
    console.log('  xm-select:', JSON.stringify(pcfEditData.inputs));
  }

  // 3. smpolicy/default
  const smp = await getTableData(page, `${globalBaseUrl}/sim_5gc/smpolicy/default/index`);
  console.log('\n📋 smpolicy/default:');
  if (smp.rows.length > 0) {
    smp.rows.forEach(r => {
      if (r.some(c => c.trim())) console.log(`  ID=${r[1]} | name=${r[2]} | pccRules=${r[4]} | sessRules=${r[3]}`);
    });
  } else { console.log('  无数据'); }

  // 4. QoS 模板
  const qos = await getTableData(page, `${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`);
  console.log('\n📋 QoS模板:');
  if (qos.rows.length > 0) {
    qos.rows.forEach(r => {
      if (r[2]) console.log(`  qosId=${r[2]} | 5qi=${r[3]} | maxbrUl=${r[4]} | maxbrDl=${r[5]} | gbrUl=${r[6]} | gbrDl=${r[7]}`);
    });
  } else { console.log('  无数据'); }

  // 5. TC 模板
  const tc = await getTableData(page, `${globalBaseUrl}/sim_5gc/predfPolicy/trafficCtl/index`);
  console.log('\n📋 Traffic Control模板:');
  if (tc.rows.length > 0) {
    tc.rows.forEach(r => {
      if (r[2]) console.log(`  tcId=${r[2]} | flowStatus=${r[3]}`);
    });
  } else { console.log('  无数据'); }

  // 6. PCC 规则
  const pcc = await getTableData(page, `${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`);
  console.log('\n📋 PCC规则:');
  if (pcc.rows.length > 0) {
    pcc.rows.forEach(r => {
      if (r[2]) console.log(`  pccRuleId=${r[2]} | precedence=${r[4]} | refQosData=${r[5]} | refTcData=${r[6]} | refChgData=${r[7]}`);
    });
  } else { console.log('  无数据'); }

  console.log('\n========================================');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });