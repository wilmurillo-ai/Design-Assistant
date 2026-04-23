/**
 * pcc_qos_explore.js - 探索 PCC 规则的编辑页面，找到 QoS 字段
 * 
 * 用法：node pcc_qos_explore.js --project XW_SUPF_5_1_2_4 --pcc-id pcc_test_maxbr001
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { project: 'XW_S5GC_1', pccId: null, headed: true };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--pcc-id') opts.pccId = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  if (!opts.pccId) { console.error('❌ 缺少 --pcc-id'); process.exit(1); }
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
  if (!clicked) {
    console.log('❌ 未找到工程'); process.exit(1);
  }
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

  // 去PCC列表页
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'commit', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 找到目标PCC规则的数字ID
  const pccIdResult = await page.evaluate((targetPccId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      // cells[1] = ID, cells[2] = pccRuleId
      if (cells.length >= 5 && cells[2].textContent.trim() === targetPccId) {
        return cells[1].textContent.trim();
      }
    }
    return null;
  }, opts.pccId);

  if (!pccIdResult) {
    console.log(`❌ 未找到PCC规则: ${opts.pccId}`);
    await browser.close();
    return;
  }
  console.log(`✅ 找到PCC规则 ID=${pccIdResult}`);

  // 导航到编辑页
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/edit/${pccIdResult}`, { waitUntil: 'commit', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 打印所有输入字段
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

  console.log('\n📋 页面所有输入字段:');
  inputs.forEach(i => {
    console.log(`  ${i.tag} [${i.type}] name="${i.name}" id="${i.id}" value="${i.value}" placeholder="${i.placeholder}"`);
  });

  // 查找与 maxbr/gbr 相关的字段
  const qosFields = await page.evaluate(() => {
    const allText = document.body.innerText.toLowerCase();
    const keywords = ['maxbr', 'gbr', 'ul', 'dl', 'qos'];
    const result = {};
    
    document.querySelectorAll('input, select, textarea').forEach(el => {
      const name = (el.name || '').toLowerCase();
      const id = (el.id || '').toLowerCase();
      for (const kw of keywords) {
        if (name.includes(kw) || id.includes(kw)) {
          result[name || id] = el.value || '（空）';
        }
      }
    });
    return result;
  });

  console.log('\n🔍 与QoS相关的字段:');
  if (Object.keys(qosFields).length > 0) {
    Object.entries(qosFields).forEach(([k, v]) => console.log(`  ${k} = ${v}`));
  } else {
    console.log('  未找到匹配的字段');
  }

  // 保存截图
  await page.screenshot({ path: 'pcc_qos_explore.png', fullPage: true });
  console.log('\n📸 截图已保存: pcc_qos_explore.png');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
