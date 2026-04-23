/**
 * smpolicy-dnn-add-skill.js - DNN Smpolicy 添加工具
 *
 * 用法：
 *   node smpolicy-dnn-add-skill.js --project XW_SUPF_5_1_2_4 --name dnn_policy1 --dnn internet
 *   node smpolicy-dnn-add-skill.js --project XW_SUPF_5_1_2_4 --name dnn_policy1 --dnn internet --pcc-rules pcc2
 *
 * 参数：
 *   --project       工程名（默认 XW_S5GC_1）
 *   --name          DNN策略名称（必填）
 *   --dnn           DNN值（必填）
 *   --sst           sNssai SST（默认 1）
 *   --sd            sNssai SD（默认 111111）
 *   --sess-rules    会话规则（xm-select，多个逗号分隔）
 *   --pcc-rules     PCC规则（xm-select，多个逗号分隔）
 *   --pra-rules     PRA规则（xm-select，可选）
 *   --ref-qos-timer reflectiveQoSTimer 值（秒）
 *   --headed        显示浏览器窗口
 *
 * 添加页：/sim_5gc/smpolicy/dnn/edit（layui-layer-iframe2）
 * xm-select: sessRules=idx0, pccRules=idx1, praRules=idx2
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    project: 'XW_S5GC_1',
    name: null, dnn: null,
    sst: '1', sd: '111111',
    sessRules: null, pccRules: null, praRules: null,
    refQosTimer: null,
    headed: false,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--name') opts.name = args[++i];
    else if (args[i] === '--dnn') opts.dnn = args[++i];
    else if (args[i] === '--sst') opts.sst = args[++i];
    else if (args[i] === '--sd') opts.sd = args[++i];
    else if (args[i] === '--sess-rules') opts.sessRules = args[++i];
    else if (args[i] === '--pcc-rules') opts.pccRules = args[++i];
    else if (args[i] === '--pra-rules') opts.praRules = args[++i];
    else if (args[i] === '--ref-qos-timer') opts.refQosTimer = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }
  if (!opts.name) { console.error('❌ 缺少 --name 参数'); process.exit(1); }
  if (!opts.dnn) { console.error('❌ 缺少 --dnn 参数'); process.exit(1); }
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

/**
 * 在 xm-select 下拉中选择一个选项（点击切换）
 */
async function xmSelectChooseOne(target, page, index, value) {
  if (!value) return;

  await target.evaluate((idx) => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[idx]) inputs[idx].parentElement.click();
  }, index);
  await page.waitForTimeout(1000);

  const clicked = await target.evaluate((text) => {
    const opts = document.querySelectorAll('.xm-option');
    for (const opt of opts) {
      if (opt.textContent.trim() === text) {
        opt.click();
        return true;
      }
    }
    return false;
  }, value);

  if (clicked) {
    console.log(`   ✅ xm-select[${index}] = ${value}`);
  } else {
    console.log(`   ⚠️ xm-select[${index}] 未找到: ${value}`);
  }

  await page.waitForTimeout(500);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
}

async function xmSelectChooseMultiple(target, page, index, values) {
  if (!values) return;
  for (const item of values.split(',').map(s => s.trim()).filter(Boolean)) {
    await xmSelectChooseOne(target, page, index, item);
  }
}

async function main() {
  const opts = parseArgs();
  const browser = await chromium.launch({ headless: !opts.headed, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);

  // 导航到 DNN smpolicy 列表
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/dnn/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  console.log('✅ 到达 DNN Smpolicy 列表页');

  // 添加弹窗
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(3000);

  const frame = page.frame('layui-layer-iframe2');
  if (!frame) { console.error('❌ 未找到弹窗iframe'); process.exit(1); }
  await frame.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2000);
  console.log(`✅ 进入弹窗iframe: ${frame.url()}`);

  // ① 填写文本字段
  const textFields = [
    { name: 'name', value: opts.name },
    { name: 'dnn', value: opts.dnn },
    { name: 'sNssai[sst]', value: opts.sst },
    { name: 'sNssai[sd]', value: opts.sd },
  ];
  if (opts.refQosTimer) {
    textFields.push({ name: 'smPolicyDecision[reflectiveQoSTimer]', value: opts.refQosTimer });
  }

  for (const f of textFields) {
    const loc = frame.locator(`[name="${f.name}"]`).first();
    if (await loc.count() > 0) {
      await loc.fill(String(f.value));
      console.log(`   ✅ ${f.name} = "${f.value}"`);
    }
  }

  // ② xm-select（sessRules=idx0, pccRules=idx1, praRules=idx2）
  const sessDisplay = await frame.evaluate(() => document.querySelectorAll('input.xm-select-default')[0]?.parentElement?.textContent || '');
  if (!sessDisplay.includes('暂无数据')) {
    await xmSelectChooseMultiple(frame, page, 0, opts.sessRules);
  }

  await xmSelectChooseMultiple(frame, page, 1, opts.pccRules);

  const praDisplay = await frame.evaluate(() => document.querySelectorAll('input.xm-select-default')[2]?.parentElement?.textContent || '');
  if (!praDisplay.includes('暂无数据')) {
    await xmSelectChooseMultiple(frame, page, 2, opts.praRules);
  }

  // ③ 提交
  await frame.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log('✅ 已提交');

  // ④ 验证
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/dnn/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const added = await page.evaluate((targetName) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 8 && cells[2].textContent.trim() === targetName) {
        return {
          name: cells[2].textContent.trim(),
          dnn: cells[3].textContent.trim(),
          sst: cells[4].textContent.trim(),
          sd: cells[5].textContent.trim(),
          pccRules: cells[7].textContent.trim(),
        };
      }
    }
    return null;
  }, opts.name);

  if (added) {
    console.log('\n📋 验证结果:');
    console.log(`   name     = ${added.name} ${added.name === opts.name ? '✅' : '❌'}`);
    console.log(`   dnn      = ${added.dnn} ${added.dnn === opts.dnn ? '✅' : '❌'}`);
    console.log(`   sst/sd   = ${added.sst}/${added.sd}`);
    console.log(`   pccRules = ${added.pccRules}`);
  } else {
    console.log('\n❌ 未在列表中找到创建的 DNN Smpolicy');
  }

  console.log('\n✅ 完成');
  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
