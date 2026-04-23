/**
 * smpolicy-cell-add-skill.js - Cell Smpolicy 添加技能
 *
 * 用法：
 *   node smpolicy-cell-add-skill.js --project XW_SUPF_5_1_2_4 --name cell_policy_test
 *     --node-id 0x00001 --node-id-len 28 --cell-id 0x00001 [--headed]
 *
 * 参数：
 *   --project      工程名（默认 XW_S5GC_1）
 *   --name         策略名称（必填）
 *   --node-id      Node ID（必填）
 *   --node-id-len  Node ID Len（默认 28）
 *   --cell-id      Cell ID（必填）
 *   --headed       显示浏览器
 *
 * 添加页：/sim_5gc/smpolicy/cell/edit（iframe弹窗）
 */
const { chromium } = require('playwright');
const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { project: 'XW_S5GC_1', name: null, nodeId: null, nodeIdLen: '28', cellId: null, headed: false };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--name') opts.name = args[++i];
    else if (args[i] === '--node-id') opts.nodeId = args[++i];
    else if (args[i] === '--node-id-len') opts.nodeIdLen = args[++i];
    else if (args[i] === '--cell-id') opts.cellId = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  if (!opts.name || !opts.nodeId || !opts.cellId) { console.error('❌ 缺少必要参数 (--name, --node-id, --cell-id)'); process.exit(1); }
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
  const frame = await openAddDialog(page, `${globalBaseUrl}/sim_5gc/smpolicy/cell/index`);

  const fields = [
    { name: 'name', value: opts.name },
    { name: 'node_id', value: opts.nodeId },
    { name: 'node_id_len', value: opts.nodeIdLen },
    { name: 'cell_id', value: opts.cellId },
  ];
  for (const f of fields) {
    const loc = frame.locator(`[name="${f.name}"]`);
    if (await loc.count() > 0) { await loc.fill(String(f.value)); console.log(`   ✅ ${f.name} = "${f.value}"`); }
  }

  const submitBtn = frame.locator('button:has-text("提交"), button:has-text("保存")');
  await submitBtn.click();
  console.log('   ✅ 已提交');
  await new Promise(r => setTimeout(r, 3000));

  console.log('\n✅ Cell Smpolicy 添加完成');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
