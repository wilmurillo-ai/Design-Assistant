/**
 * smpolicy-tac-add-skill.js - TAC Smpolicy 添加技能
 *
 * 用法：
 *   node smpolicy-tac-add-skill.js --project XW_SUPF_5_1_2_4 --name tac_policy_test --tac 000100 [--headed]
 *
 * 参数：
 *   --project   工程名（默认 XW_S5GC_1）
 *   --name      策略名称（必填）
 *   --tac       TAC值，只能填纯数字（必填）
 *   --headed    显示浏览器
 *
 * 添加页：/sim_5gc/smpolicy/tac/edit（iframe弹窗，仅name+tac两个字段）
 */
const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { project: 'XW_S5GC_1', name: null, tac: null, headed: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--name') opts.name = args[++i];
    else if (args[i] === '--tac') opts.tac = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  if (!opts.name || !opts.tac) { console.error('❌ 缺少 --name 或 --tac'); process.exit(1); }
  if (!/^\d+$/.test(opts.tac)) { console.error('❌ TAC必须全是数字'); process.exit(1); }
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
    for (let p = 2; p <= 10; p++) {
      const nextBtn = document.querySelector('.jsgrid-pager a.jsgrid-pager-next');
      if (!nextBtn) break;
      nextBtn.click();
      await new Promise(r => setTimeout(r, 1000));
      const found = page.evaluate((n) => {
        const rows = document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row');
        for (const row of rows) {
          const cells = row.querySelectorAll('td');
          if (cells.length >= 3 && cells[2].textContent.trim() === n) {
            const icon = cells[1].querySelector('.iconfont');
            if (icon) { icon.click(); return true; }
          }
        }
        return false;
      }, projectName);
      if (found) break;
    }
  }
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${projectName}" 已选`);
}

async function openAddDialog(page, listUrl) {
  await page.goto(listUrl, { waitUntil: 'commit', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    for (const b of btns) { if (b.textContent.trim().includes('添加')) { b.click(); return; } }
  });
  await page.waitForFunction(() => Array.from(document.querySelectorAll('iframe')).some(f => f.src && f.src.includes('/edit')), { timeout: 10000 });
  await page.waitForTimeout(2000);
  const iframeSrc = await page.evaluate(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    for (const f of iframes) { if (f.src && f.src.includes('/edit')) return f.src; }
    return null;
  });
  console.log('✅ 弹窗已打开:', iframeSrc);
  await page.waitForTimeout(2000);
  const frame = page.frames().find(f => f.url().includes('/edit'));
  if (!frame) throw new Error('无法获取iframe');
  await new Promise(r => setTimeout(r, 2000));
  return frame;
}

async function main() {
  const opts = parseArgs();
  const browser = await chromium.launch({ headless: !opts.headed, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);
  const frame = await openAddDialog(page, `${globalBaseUrl}/sim_5gc/smpolicy/tac/index`);

  const nameLoc = frame.locator('[name="name"]');
  const tacLoc = frame.locator('[name="tac"]');
  if (await nameLoc.count() > 0) { await nameLoc.fill(opts.name); console.log(`   ✅ name = "${opts.name}"`); }
  if (await tacLoc.count() > 0) { await tacLoc.fill(opts.tac); console.log(`   ✅ tac = "${opts.tac}"`); }

  const submitBtn = frame.locator('button:has-text("提交"), button:has-text("保存")');
  await submitBtn.click();
  console.log('   ✅ 已提交');
  await new Promise(r => setTimeout(r, 3000));

  console.log('\n✅ TAC Smpolicy 添加完成');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
