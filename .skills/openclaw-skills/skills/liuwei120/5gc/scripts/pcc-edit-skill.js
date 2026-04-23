/**
 * pcc-edit-skill.js - PCC 规则编辑（修改 QoS/TC 绑定）
 *
 * 用法:
 *   node 5gc.js pcc edit --project XW_SUPF_5_1_2_4 --name pcc_default --set-qos qos_high_rate
 *   node 5gc.js pcc edit --project XW_SUPF_5_1_2_4 --name pcc_default --set-qos qos_new --set-tc tc_new
 *
 * 参数:
 *   --project     工程名（默认 XW_S5GC_1）
 *   --name        PCC规则名称（精确匹配，要修改的 PCC）
 *   --set-qos    新的 QoS 模板名称
 *   --set-tc     新的 Traffic Control 名称
 *   --headed      显示浏览器窗口
 *
 * 链路:
 *   PCC列表页 → 找到 PCC 数字ID → 直接导航到 /predfPolicy/pcc/edit/{id}
 *   → 修改 xm-select → 提交
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    project: 'XW_S5GC_1',
    name: null,
    newQos: null,
    newTc: null,
    headed: false,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--name') opts.name = args[++i];
    else if (args[i] === '--set-qos') opts.newQos = args[++i];
    else if (args[i] === '--set-tc') opts.newTc = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  if (!opts.name) {
    console.error('❌ 缺少 --name 参数');
    process.exit(1);
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

async function selectProject(page, name) {
  await page.goto(`${globalBaseUrl}/sim_5gc/project/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(2000);
  await page.locator('input[name="project_search_name"]').fill(name);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);
  const found = await page.evaluate((n) => {
    let result = false;
    document.querySelectorAll('.jsgrid-row, .jsgrid-alt-row').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === n) {
        cells[1].querySelector('.iconfont')?.click();
        result = true;
      }
    });
    return result;
  }, name);
  if (!found) { console.error(`❌ 未找到工程: ${name}`); process.exit(1); }
  await page.waitForTimeout(3000);
  console.log(`✅ 工程 "${name}" 已选`);
}

async function main() {
  const opts = parseArgs();
  const browser = await chromium.launch({ headless: !opts.headed, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);

  // ① 去 PCC 列表页，找到目标 PCC 的数字 ID
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const pccInfo = await page.evaluate((targetName) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 10 && cells[2].textContent.trim() === targetName) {
        return { id: cells[1].textContent.trim(), pccRuleId: cells[2].textContent.trim() };
      }
    }
    return null;
  }, opts.name);

  if (!pccInfo) {
    console.error(`❌ 未找到 PCC: ${opts.name}`);
    process.exit(1);
  }
  console.log(`✅ 找到 PCC "${opts.name}"，数字ID=${pccInfo.id}`);

  // ② 直接导航到编辑页
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/edit/${pccInfo.id}`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  console.log(`   编辑页URL: ${page.url()}`);

  // ③ 修改 refQosData（第0个xm-select）
  if (opts.newQos) {
    // 打开下拉
    await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[0].parentElement.click());
    await page.waitForTimeout(800);

    // 直接点击目标选项（xm-select 切换时自动取消旧的）
    const clicked = await page.evaluate((targetText) => {
      const allOpts = document.querySelectorAll('.xm-option');
      for (const opt of allOpts) {
        if (opt.textContent.trim() === targetText) {
          opt.click();
          return true;
        }
      }
      return false;
    }, opts.newQos);

    if (clicked) {
      console.log(`   ✅ refQosData → ${opts.newQos}`);
    } else {
      console.log(`   ❌ 选项 ${opts.newQos} 未找到`);
    }
    await page.waitForTimeout(500);
  }

  // ④ 修改 refTcData（第1个xm-select）
  if (opts.newTc) {
    await page.evaluate(() => document.querySelectorAll('input.xm-select-default')[1].parentElement.click());
    await page.waitForTimeout(800);

    const clicked = await page.evaluate((targetText) => {
      const allOpts = document.querySelectorAll('.xm-option');
      for (const opt of allOpts) {
        if (opt.textContent.trim() === targetText) {
          opt.click();
          return true;
        }
      }
      return false;
    }, opts.newTc);

    if (clicked) {
      console.log(`   ✅ refTcData → ${opts.newTc}`);
    } else {
      console.log(`   ❌ 选项 ${opts.newTc} 未找到`);
    }
    await page.waitForTimeout(500);
  }

  // 关闭下拉
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // ⑤ 提交
  await page.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log('✅ 已提交');

  // ⑥ 验证
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const updated = await page.evaluate((targetName) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 8 && cells[2].textContent.trim() === targetName) {
        return {
          pccRuleId: cells[2].textContent.trim(),
          precedence: cells[4].textContent.trim(),
          refQosData: cells[5].textContent.trim(),
          refTcData: cells[6].textContent.trim(),
        };
      }
    }
    return null;
  }, opts.name);

  if (updated) {
    console.log('\n📋 验证结果:');
    console.log(`   pccRuleId  = ${updated.pccRuleId}`);
    console.log(`   precedence = ${updated.precedence}`);
    console.log(`   refQosData = ${updated.refQosData} ${opts.newQos ? (updated.refQosData === opts.newQos ? '✅' : '❌') : ''}`);
    console.log(`   refTcData  = ${updated.refTcData} ${opts.newTc ? (updated.refTcData === opts.newTc ? '✅' : '❌') : ''}`);
  }

  await browser.close();
  console.log('\n✅ 完成');
}

main().catch(e => { console.error(e); process.exit(1); });
