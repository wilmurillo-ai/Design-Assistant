/**
 * smpolicy_default_edit.js - 编辑 sm_policy_default 的 pccRules
 * 添加 pcc_default_test 到默认规则
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
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-issues'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  // 导航到 smpolicy/default/index
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  console.log('✅ 到达 smpolicy/default/index');

  // 点击"编辑"按钮（第一个）
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    if (rows.length > 0) {
      const editBtn = rows[0].querySelector('a');
      if (editBtn) editBtn.click();
    }
  });
  await page.waitForTimeout(3000);
  console.log('✅ 点击了编辑按钮');
  console.log(`   当前URL: ${page.url()}`);

  // 检查是否有弹窗iframe
  const hasIframe = await page.locator('iframe[name="layui-layer-iframe2"]').count();
  console.log(`   弹窗iframe数量: ${hasIframe}`);

  if (hasIframe > 0) {
    const frame = page.frame('layui-layer-iframe2');
    console.log('✅ 进入弹窗iframe');
    
    // 获取iframe内容
    const iframeText = await frame.evaluate(() => document.body.innerText);
    console.log('\n📄 iframe内容:');
    console.log(iframeText.substring(0, 3000));
    
    // 获取所有输入字段
    const inputs = await frame.evaluate(() => {
      const result = [];
      document.querySelectorAll('input, select, textarea').forEach(el => {
        if (el.name || el.id) {
          result.push({ tag: el.tagName, name: el.name, type: el.type, value: el.value });
        }
      });
      return result;
    });
    console.log('\n📋 iframe输入字段:');
    inputs.forEach(i => console.log(`  ${i.tag} [${i.type}] name="${i.name}" value="${i.value}"`));
    
    // 查找pccRules相关的字段
    const pccInputs = inputs.filter(i => i.name && (i.name.includes('pcc') || i.name.includes('Pcc')));
    console.log('\n🔍 pccRules相关字段:', pccInputs);
    
    // 截图
    await page.screenshot({ path: 'smpolicy_edit.png' });
    console.log('\n📸 截图: smpolicy_edit.png');
  } else {
    // 没有弹窗，可能直接显示了编辑表单
    console.log('   未发现iframe，当前页面编辑');
    const pageText = await page.evaluate(() => document.body.innerText);
    console.log('\n📄 页面内容:');
    console.log(pageText.substring(0, 3000));
    
    await page.screenshot({ path: 'smpolicy_edit_no_iframe.png' });
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
