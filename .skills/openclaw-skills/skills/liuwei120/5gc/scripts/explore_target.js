/**
 * explore_target.js - 探索 XW_SUPF_SN4_5_2_8 的 PCF 配置
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
  // 使用搜索
  const searchInput = page.locator('input[type="search"], input[placeholder*="搜索"], input[name*="search"], .jsgrid-search input').first();
  await searchInput.fill(name);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  
  const clicked = await page.evaluate((n) => {
    const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) {
        cells[1].querySelector('.iconfont').click();
        return true;
      }
    }
    return false;
  }, name);
  if (!clicked) { console.log('❌ 选择工程失败'); process.exit(1); }
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${name}" 已选`);
}

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, 'XW_SUPF_SN4_5_2_8');

  // 1. 查看 PCF 列表
  console.log('\n📋 PCF 列表:');
  await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const pcfList = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    const pcfs = [];
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 10) {
        pcfs.push({ id: cells[1].textContent.trim(), name: cells[2].textContent.trim() });
      }
    });
    return pcfs;
  });
  console.log(`   找到 ${pcfList.length} 个 PCF:`, JSON.stringify(pcfList));

  // 2. 查看 smpolicy/default
  console.log('\n📋 smpolicy/default:');
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const smpolicyList = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    const list = [];
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 6) {
        list.push({
          id: cells[1].textContent.trim(),
          name: cells[2].textContent.trim(),
          pccRules: cells[4].textContent.trim(),
        });
      }
    });
    return list;
  });
  console.log(`   找到 ${smpolicyList.length} 个默认规则:`, JSON.stringify(smpolicyList));

  // 3. 查看 QoS 模板
  console.log('\n📋 QoS 模板:');
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const qosList = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    const list = [];
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 8) {
        list.push({
          qosId: cells[2].textContent.trim(),
          qi: cells[3].textContent.trim(),
          maxbrUl: cells[4].textContent.trim(),
          maxbrDl: cells[5].textContent.trim(),
        });
      }
    });
    return list;
  });
  console.log(`   找到 ${qosList.length} 个QoS模板:`, JSON.stringify(qosList));

  // 4. 查看 PCC 规则
  console.log('\n📋 PCC 规则:');
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const pccList = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    const list = [];
    rows.forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 6) {
        list.push({
          pccRuleId: cells[2].textContent.trim(),
          precedence: cells[4].textContent.trim(),
          qosId: cells[5].textContent.trim(),
        });
      }
    });
    return list;
  });
  console.log(`   找到 ${pccList.length} 个PCC规则:`, JSON.stringify(pccList));

  // 5. 如果有PCF，查看其编辑弹窗的默认规则配置
  if (pcfList.length > 0) {
    console.log('\n📋 PCF编辑弹窗（查看 default_smpolicy 等）:');
    await page.goto(`${globalBaseUrl}/sim_5gc/pcf/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
    await page.waitForTimeout(2000);
    
    await page.evaluate((targetId) => {
      const rows = document.querySelectorAll('.layui-table tbody tr');
      for (const row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 10 && cells[1].textContent.trim() === targetId) {
          const links = cells[9].querySelectorAll('a');
          for (const link of links) {
            if (link.textContent.trim() === '编辑') { link.click(); return; }
          }
        }
      }
    }, pcfList[0].id);
    
    await page.waitForTimeout(3000);
    const frame = page.frame('layui-layer-iframe2');
    if (frame) {
      const text = await frame.evaluate(() => document.body.innerText);
      console.log(text.substring(0, 1500));
    }
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });