/**
 * force_fix.js - 强制删除并重建 qos3
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
  await page.evaluate((n) => {
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) {
        cells[1].querySelector('.iconfont').click();
      }
    });
  }, name);
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${name}" 已选`);
}

async function main() {
  const browser = await chromium.launch({ headless: false, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();
  await login(page);
  await selectProject(page, 'XW_SUPF_5_1_2_4');

  // ── 1. 删除 qos3 ──────────────────────────────────────────
  console.log('\n🗑️ Step 1: 删除旧 qos3...');
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 强制显示所有行并删除
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.trim() === 'qos3') {
          const deleteBtn = Array.from(row.querySelectorAll('a')).find(a => a.textContent.trim() === '删除');
          if (deleteBtn) {
            deleteBtn.click();
            return;
          }
        }
      }
    }
  });
  await page.waitForTimeout(1500);

  // 确认删除
  const confirmBtn = page.locator('.layui-layer-btn0');
  if (await confirmBtn.count() > 0) {
    await confirmBtn.click();
    await page.waitForTimeout(2000);
    console.log('   ✅ 已确认删除 qos3');
  } else {
    console.log('   ⚠️ 未找到确认按钮，qos3 可能不存在');
  }

  // ── 2. 重新创建 qos3 ─────────────────────────────────────
  console.log('\n📦 Step 2: 创建新 qos3 (5qi=8)...');
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(2000);

  const frame = page.frame('layui-layer-iframe2');
  await frame.waitForLoadState('domcontentloaded');

  // 填写所有字段
  await frame.locator('input[name="qosId"]').fill('qos3');
  await frame.locator('input[name="5qi"]').fill('8');
  await frame.locator('input[name="maxbrUl"]').fill('10000000');
  await frame.locator('input[name="maxbrDl"]').fill('20000000');
  await frame.locator('input[name="gbrUl"]').fill('5000000');
  await frame.locator('input[name="gbrDl"]').fill('5000000');
  console.log('   已填写所有字段: qosId=qos3, 5qi=8, maxbrUl=10000000, maxbrDl=20000000, gbrUl=5000000, gbrDl=5000000');

  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log('   ✅ 已提交');

  // ── 3. 验证 qos3 的 5qi ───────────────────────────────────
  console.log('\n🔍 Step 3: 验证 qos3 数据...');
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const qos3Data = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (let i = 0; i < cells.length; i++) {
        if (cells[i].textContent.trim() === 'qos3') {
          return Array.from(cells).map((c, idx) => idx + ':' + c.textContent.trim()).join(' | ');
        }
      }
    }
    return 'qos3 未找到';
  });
  console.log('   ' + qos3Data);

  // 解析并验证
  const qiMatch = qos3Data.match(/3:(\d+)/);
  if (qiMatch && qiMatch[1] === '8') {
    console.log('\n✅✅✅ qos3.5qi = 8（正确！）');
  } else {
    console.log(`\n❌ qos3.5qi = ${qiMatch ? qiMatch[1] : '未知'}（期望 8）`);
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
