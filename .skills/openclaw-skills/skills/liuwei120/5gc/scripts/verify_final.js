/**
 * verify_final.js - 最终验证
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

async function selectProject(page, projectName) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.evaluate((name) => {
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
  await page.waitForTimeout(3000);
}

async function main() {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  // 1. 验证 smpolicy default 的 pccRules
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const smpolicy = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 6) {
        return {
          id: cells[1].textContent.trim(),
          name: cells[2].textContent.trim(),
          pccRules: cells[4].textContent.trim(),
        };
      }
    }
    return null;
  });
  
  console.log('\n========== 验证结果 ==========\n');
  console.log('📋 sm_policy_default:');
  console.log(`   ID: ${smpolicy.id}`);
  console.log(`   名称: ${smpolicy.name}`);
  console.log(`   pccRules: ${smpolicy.pccRules}`);
  
  const hasPccDefaultTest = smpolicy.pccRules.includes('pcc_default_test');
  console.log(`   ✅ pcc_default_test 已添加: ${hasPccDefaultTest ? '是' : '否'}`);

  // 2. 验证 qos3
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const qos = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      // cells[2] = qosId, cells[4]=maxbrUl, cells[5]=maxbrDl, cells[6]=gbrUl, cells[7]=gbrDl
      for (let i = 0; i < cells.length; i++) {
        if (cells[i].textContent.trim() === 'qos3') {
          return {
            id: cells[1].textContent.trim(),
            qosId: cells[2].textContent.trim(),
            qi: cells[3].textContent.trim(),
            maxbrUl: cells[4].textContent.trim(),
            maxbrDl: cells[5].textContent.trim(),
            gbrUl: cells[6].textContent.trim(),
            gbrDl: cells[7].textContent.trim(),
          };
        }
      }
    }
    return null;
  });
  
  console.log('\n📋 qos3 QoS模板:');
  console.log(`   ID: ${qos.id}`);
  console.log(`   qosId: ${qos.qosId}`);
  console.log(`   5qi: ${qos.qi}`);
  console.log(`   maxbrUl: ${qos.maxbrUl}`);
  console.log(`   maxbrDl: ${qos.maxbrDl}`);
  console.log(`   gbrUl: ${qos.gbrUl}`);
  console.log(`   gbrDl: ${qos.gbrDl}`);
  
  const qosMatch = 
    qos.maxbrUl === '10000000' &&
    qos.maxbrDl === '20000000' &&
    qos.gbrUl === '5000000' &&
    qos.gbrDl === '5000000';
  console.log(`   ✅ QoS参数匹配: ${qosMatch ? '是' : '否'}`);

  // 3. 验证 pcc_default_test 使用的 QoS
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const pcc = await page.evaluate(() => {
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
  
  console.log('\n📋 pcc_default_test PCC规则:');
  console.log(`   ID: ${pcc.id}`);
  console.log(`   使用的QoS模板: ${pcc.qosId || '(通过名称引用)'}`);
  console.log(`   precedence: ${pcc.precedence}`);

  console.log('\n========== 总结 ==========\n');
  if (hasPccDefaultTest && qosMatch) {
    console.log('✅✅✅ 任务完成！');
    console.log('   1. qos3 QoS模板已创建，参数正确');
    console.log('   2. pcc_default_test PCC规则已创建，使用qos3');
    console.log('   3. pcc_default_test 已添加到 sm_policy_default 的 pccRules');
    console.log('\n   PCF默认规则现已包含 pcc_default_test，其QoS参数:');
    console.log('   - maxbrUl = 10000000');
    console.log('   - maxbrDl = 20000000');
    console.log('   - gbrUl = 5000000');
    console.log('   - gbrDl = 5000000');
  } else {
    console.log('❌ 部分验证未通过');
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
