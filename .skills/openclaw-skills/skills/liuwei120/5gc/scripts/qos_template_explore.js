/**
 * qos_template_explore.js - 探索 QoS 模板配置页面
 * 查找 maxbrUl, maxbrDl, gbrUl, gbrDl 在哪里设置
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

async function explorePage(page, url, description) {
  console.log(`\n🌐 探索: ${description}`);
  console.log(`   URL: ${url}`);
  await page.goto(url, { waitUntil: 'commit', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const url_ok = page.url();
  console.log(`   当前URL: ${url_ok}`);

  // 获取所有侧边栏链接
  const sidebarLinks = await page.evaluate(() => {
    const links = [];
    document.querySelectorAll('a[href]').forEach(a => {
      if (a.textContent.trim()) {
        links.push({ href: a.href, text: a.textContent.trim().substring(0, 50) });
      }
    });
    return links;
  });
  
  console.log(`   侧边栏链接 (${sidebarLinks.length}个):`);
  sidebarLinks.slice(0, 20).forEach(l => {
    if (l.href.includes('/sim_5gc/') || l.href.includes('/predf')) {
      console.log(`     - ${l.text}: ${l.href}`);
    }
  });

  // 查找包含 maxbr, gbr, qos 的链接
  const qosLinks = sidebarLinks.filter(l => 
    l.text.toLowerCase().includes('qos') || 
    l.text.toLowerCase().includes('maxbr') ||
    l.text.toLowerCase().includes('gbr') ||
    l.href.toLowerCase().includes('qos') ||
    l.href.toLowerCase().includes('maxbr') ||
    l.href.toLowerCase().includes('template')
  );
  
  if (qosLinks.length > 0) {
    console.log('\n   🔍 QoS相关链接:');
    qosLinks.forEach(l => console.log(`     - ${l.text}: ${l.href}`));
  }

  // 在页面文本中搜索关键词
  const pageText = await page.evaluate(() => document.body.innerText);
  const keywords = ['maxbrUl', 'maxbrDl', 'gbrUl', 'gbrDl', 'maxbr', 'gbr', 'qos', 'QoS'];
  console.log('\n   📄 页面文本搜索:');
  keywords.forEach(kw => {
    const regex = new RegExp(kw, 'gi');
    const matches = pageText.match(regex);
    if (matches) {
      console.log(`     "${kw}" 出现 ${matches.length} 次`);
    }
  });
}

async function main() {
  const opts = parseArgs();
  const browser = await chromium.launch({ headless: !opts.headed, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);

  // 探索多个可能包含 QoS 配置的页面
  await explorePage(page, `${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, 'PCC列表');
  await explorePage(page, `${globalBaseUrl}/sim_5gc/predfPolicy/index`, 'Predefined Policy列表');
  await explorePage(page, `${globalBaseUrl}/sim_5gc/qos/index`, 'QoS配置');
  await explorePage(page, `${globalBaseUrl}/sim_5gc/index`, '首页');

  // 尝试查找包含 qos 的所有链接
  console.log('\n\n🔍 深度搜索整个 sidebar...');
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  
  const allLinks = await page.evaluate(() => {
    const links = [];
    document.querySelectorAll('a[href]').forEach(a => {
      if (a.href && a.textContent.trim()) {
        links.push({ href: a.href, text: a.textContent.trim() });
      }
    });
    return links;
  });

  // 过滤可能相关的链接
  const relevant = allLinks.filter(l => 
    l.href.includes('qos') || 
    l.href.includes('pcc') || 
    l.href.includes('predf') ||
    l.href.includes('template') ||
    l.href.includes('config')
  );

  console.log('\n相关链接:');
  relevant.forEach(l => console.log(`  ${l.text}: ${l.href}`));

  // 保存截图
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'commit', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'qos_explore.png', fullPage: true });
  console.log('\n📸 截图已保存: qos_explore.png');

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
