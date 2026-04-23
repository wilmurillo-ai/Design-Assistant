/**
 * pcf_smpolicy_explore.js - 探索 PCF Smpolicy 页面
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

  // 探索 PCF 列表
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
  console.log(`\n找到 ${pcfList.length} 个 PCF:`, pcfList);

  // 点击第一个 PCF 的编辑
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
  console.log(`PCF编辑弹窗URL: ${page.url()}`);

  // 切换到iframe
  const frame = page.frame('layui-layer-iframe2');
  if (frame) {
    console.log('✅ 进入弹窗iframe');
    
    // 获取iframe内容
    const iframeContent = await frame.evaluate(() => ({
      url: window.location.href,
      title: document.title,
      text: document.body.innerText.substring(0, 3000)
    }));
    console.log('\n📄 iframe内容:');
    console.log(iframeContent.text);
    
    // 查找smpolicy相关的链接
    const links = await frame.evaluate(() => {
      const result = [];
      document.querySelectorAll('a[href]').forEach(a => {
        if (a.textContent.trim()) result.push({ text: a.textContent.trim(), href: a.href });
      });
      return result;
    });
    
    console.log('\n🔗 iframe内所有链接:');
    links.forEach(l => console.log(`  "${l.text}": ${l.href}`));
    
    // 查找包含smpolicy的链接
    const smpolicyLinks = links.filter(l => 
      l.href.includes('smpolicy') || 
      l.text.includes('smpolicy') ||
      l.text.includes('Smpolicy') ||
      l.text.includes('默认')
    );
    
    if (smpolicyLinks.length > 0) {
      console.log('\n🔍 smpolicy相关链接:');
      smpolicyLinks.forEach(l => console.log(`  "${l.text}": ${l.href}`));
    }
  }

  // 截图
  await page.screenshot({ path: 'pcf_edit.png', fullPage: true });
  console.log('\n📸 截图: pcf_edit.png');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
