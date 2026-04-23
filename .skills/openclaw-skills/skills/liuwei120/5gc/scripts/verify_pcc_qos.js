/**
 * verify_pcc_qos.js - 验证 pcc_default_test 的 QoS 值
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

  // 导航到 PCC 列表
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 找到 pcc_default_test 的行
  const pccRow = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 10 && cells[2].textContent.trim() === 'pcc_default_test') {
        return {
          id: cells[1].textContent.trim(),
          qosId: cells[3].textContent.trim(),
          precedence: cells[4].textContent.trim(),
        };
      }
    }
    return null;
  });

  if (pccRow) {
    console.log('\n📋 pcc_default_test 信息:');
    console.log(`   ID: ${pccRow.id}`);
    console.log(`   qosId(使用的QoS模板): ${pccRow.qosId}`);
    console.log(`   precedence: ${pccRow.precedence}`);
  }

  // 导航到 QoS 列表查看 qos3 的详细信息
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 找到 qos3
  const qosRow = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.trim() === 'qos3') {
          // 返回整行
          return Array.from(cells).map(c => c.textContent.trim());
        }
      }
    }
    return null;
  });

  if (qosRow) {
    console.log('\n📋 qos3 QoS模板信息:');
    console.log(`   qosId: ${qosRow[1]}`);
    console.log(`   5qi: ${qosRow[2]}`);
    console.log(`   maxbrUl: ${qosRow[3]}`);
    console.log(`   maxbrDl: ${qosRow[4]}`);
    console.log(`   gbrUl: ${qosRow[5]}`);
    console.log(`   gbrDl: ${qosRow[6]}`);
    
    // 验证值
    const expected = { maxbrUl: '10000000', maxbrDl: '20000000', gbrUl: '5000000', gbrDl: '5000000' };
    const actual = { maxbrUl: qosRow[3], maxbrDl: qosRow[4], gbrUl: qosRow[5], gbrDl: qosRow[6] };
    
    console.log('\n✅ 验证结果:');
    let allMatch = true;
    for (const [key, val] of Object.entries(expected)) {
      const match = actual[key] === val;
      console.log(`   ${key}: 期望=${val}, 实际=${actual[key]} ${match ? '✅' : '❌'}`);
      if (!match) allMatch = false;
    }
    
    if (allMatch) {
      console.log('\n🎉 所有 QoS 参数配置正确！');
    }
  }

  await page.screenshot({ path: 'verify_result.png', fullPage: true });
  console.log('\n📸 截图: verify_result.png');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
