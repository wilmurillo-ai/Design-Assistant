/**
 * full_flow.js - 完整流程：创建QoS模板 → 创建PCC规则 → 添加到默认规则
 *
 * 逻辑：
 *   1. 如果用户指定了5qi/maxbr-ul/maxbr-dl/gbr-ul/gbr-dl → 用用户指定的
 *   2. 如果用户没指定 → 自动选择（5qi自动选一个不同的，参数用默认值）
 *   3. 创建QoS模板 → 创建PCC规则 → 添加到sm_policy_default
 *
 * 用法:
 *   node full_flow.js --project XW_SUPF_5_1_2_4 --qos-id qos3 --maxbr-ul 10000000 --maxbr-dl 20000000 --gbr-ul 5000000 --gbr-dl 5000000 [--5qi 8] [--headed]
 */
const { chromium } = require('playwright');

const globalBaseUrl = 'https://192.168.3.89';

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    project: 'XW_S5GC_1',
    qosId: null,
    // 用户指定的值（null表示未指定，使用默认值）
    qi: null,
    maxbrUl: null,
    maxbrDl: null,
    gbrUl: null,
    gbrDl: null,
    priority: '',
    headed: false,
  };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--project' || args[i] === '-p') opts.project = args[++i];
    else if (args[i] === '--qos-id') opts.qosId = args[++i];
    else if (args[i] === '--5qi') opts.qi = args[++i];
    else if (args[i] === '--maxbr-ul') opts.maxbrUl = args[++i];
    else if (args[i] === '--maxbr-dl') opts.maxbrDl = args[++i];
    else if (args[i] === '--gbr-ul') opts.gbrUl = args[++i];
    else if (args[i] === '--gbr-dl') opts.gbrDl = args[++i];
    else if (args[i] === '--priority') opts.priority = args[++i];
    else if (args[i] === '--headed') opts.headed = true;
  }

  if (!opts.qosId) {
    console.error('❌ 缺少必要参数: --qos-id');
    console.error('   示例: node full_flow.js --project XW_SUPF_5_1_2_4 --qos-id qos3 --maxbr-ul 10000000 --maxbr-dl 20000000 --gbr-ul 5000000 --gbr-dl 5000000');
    process.exit(1);
  }

  // 如果用户指定了maxbr/gbr，必须全部指定
  const hasBr = [opts.maxbrUl, opts.maxbrDl, opts.gbrUl, opts.gbrDl].some(v => v !== null);
  const allBr = [opts.maxbrUl, opts.maxbrDl, opts.gbrUl, opts.gbrDl].every(v => v !== null);
  if (hasBr && !allBr) {
    console.error('❌ maxbr-ul, maxbr-dl, gbr-ul, gbr-dl 需要同时指定或都不指定');
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

// 获取已使用的5qi列表
async function getUsed5qis(page) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  const usedQis = await page.evaluate(() => {
    const qis = new Set();
    document.querySelectorAll('.layui-table tbody tr').forEach(row => {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 4) {
        const qi = parseInt(cells[3].textContent.trim());
        if (!isNaN(qi)) qis.add(qi);
      }
    });
    return [...qis];
  });
  return usedQis;
}

function autoSelect5qi(usedQis) {
  const candidates = [8, 9, 6, 5, 4, 3, 2, 1];
  for (const c of candidates) {
    if (!usedQis.includes(c)) return c;
  }
  return 8;
}

function autoFillParams() {
  // 默认参数（如果用户没指定）
  return {
    maxbrUl: '10000000',
    maxbrDl: '20000000',
    gbrUl: '5000000',
    gbrDl: '5000000',
  };
}

// 删除已有的QoS模板（如果存在）
async function deleteQosIfExists(page, qosId) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const exists = await page.evaluate((targetId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (const cell of cells) {
        if (cell.textContent.trim() === targetId) {
          return true;
        }
      }
    }
    return false;
  }, qosId);

  if (!exists) {
    console.log(`   ℹ️ QoS模板 ${qosId} 不存在，无需删除`);
    return false;
  }

  // 点击删除
  await page.evaluate((targetId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (let i = 0; i < cells.length; i++) {
        if (cells[i].textContent.trim() === targetId) {
          const deleteBtn = row.querySelector('a:has-text("删除")');
          if (deleteBtn) { deleteBtn.click(); return; }
        }
      }
    }
  }, qosId);

  await page.waitForTimeout(2000);
  // 确认删除（如果有确认框）
  try {
    const confirmBtn = page.locator('.layui-layer-btn0');
    if (await confirmBtn.count() > 0) {
      await confirmBtn.click();
      await page.waitForTimeout(2000);
    }
  } catch(e) {}
  console.log(`   ✅ 已删除旧 QoS模板 ${qosId}`);
  return true;
}

// 删除已有的PCC规则（如果存在）
async function deletePccIfExists(page, pccId) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  const exists = await page.evaluate((targetId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === targetId) {
        return true;
      }
    }
    return false;
  }, pccId);

  if (!exists) {
    console.log(`   ℹ️ PCC规则 ${pccId} 不存在，无需删除`);
    return false;
  }

  await page.evaluate((targetId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 3 && cells[2].textContent.trim() === targetId) {
        const deleteBtn = row.querySelector('a:has-text("删除")');
        if (deleteBtn) { deleteBtn.click(); return; }
      }
    }
  }, pccId);

  await page.waitForTimeout(2000);
  try {
    const confirmBtn = page.locator('.layui-layer-btn0');
    if (await confirmBtn.count() > 0) {
      await confirmBtn.click();
      await page.waitForTimeout(2000);
    }
  } catch(e) {}
  console.log(`   ✅ 已删除旧 PCC规则 ${pccId}`);
  return true;
}

// 添加QoS模板
async function addQos(page, opts) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(2000);

  const iframe = page.locator('iframe[name="layui-layer-iframe2"]');
  if (await iframe.count() > 0) {
    const frame = page.frame('layui-layer-iframe2');
    await fillQosForm(frame, opts);
  } else {
    await fillQosForm(page, opts);
  }
}

async function fillQosForm(page, opts) {
  await page.waitForTimeout(2000);
  await page.locator('input[name="qosId"]').first().fill(opts.qosId);
  console.log(`   qosId = ${opts.qosId}`);
  await page.locator('input[name="5qi"]').first().fill(opts.qi);
  console.log(`   5qi = ${opts.qi}`);
  await page.locator('input[name="maxbrUl"]').first().fill(opts.maxbrUl);
  console.log(`   maxbrUl = ${opts.maxbrUl}`);
  await page.locator('input[name="maxbrDl"]').first().fill(opts.maxbrDl);
  console.log(`   maxbrDl = ${opts.maxbrDl}`);
  await page.locator('input[name="gbrUl"]').first().fill(opts.gbrUl);
  console.log(`   gbrUl = ${opts.gbrUl}`);
  await page.locator('input[name="gbrDl"]').first().fill(opts.gbrDl);
  console.log(`   gbrDl = ${opts.gbrDl}`);
  await page.locator('button:has-text("提交")').first().click();
  await page.waitForTimeout(3000);
}

// 添加PCC规则
async function xmSelectChoose(frame, index, optionText) {
  await frame.evaluate((idx) => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[idx]) inputs[idx].parentElement.click();
  }, index);
  await frame.waitForTimeout(1000);
  await frame.evaluate((text) => {
    const opts = document.querySelectorAll('.xm-option.show-icon');
    for (const opt of opts) {
      if (opt.textContent.trim() === text) {
        opt.click();
        return;
      }
    }
  }, optionText);
  await frame.waitForTimeout(500);
}

async function addPcc(page, opts) {
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/pcc/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  await page.locator('button:has-text("添加")').click();
  await page.waitForTimeout(2000);

  const frame = page.frameLocator('iframe[name="layui-layer-iframe2"]');
  const f = frame.locator('iframe').contentFrame() ? frame.locator('iframe').contentFrame() : page.frame('layui-layer-iframe2');
  
  // 直接用 evaluate 在 frame 里操作
  const frameEl = await page.frame('layui-layer-iframe2');
  await frameEl.waitForLoadState('domcontentloaded');
  await frameEl.locator('input[name="pccRuleId"]').fill(opts.pccId);
  await frameEl.locator('input[name="precedence"]').fill('10');
  console.log(`   pccRuleId = ${opts.pccId}, precedence = 10`);
  
  // 选择QoS（第0个xm-select）
  await xmSelectChoose(frameEl, 0, opts.qosId);
  
  // 按Escape关闭下拉
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
  
  await frameEl.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
}

// 添加PCC规则到 sm_policy_default
async function addPccToSmpolicy(page, pccId) {
  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);

  // 点击编辑
  await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    if (rows.length > 0) {
      rows[0].querySelector('a').click();
    }
  });
  await page.waitForTimeout(3000);

  const frameEl = await page.frame('layui-layer-iframe2');
  await frameEl.waitForLoadState('domcontentloaded');

  // 检查是否已经添加过
  const alreadySelected = await frameEl.evaluate((targetId) => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs.length >= 2) {
      const parent = inputs[1].parentElement;
      return parent.textContent.includes(targetId);
    }
    return false;
  }, pccId);

  if (alreadySelected) {
    console.log(`   ℹ️ ${pccId} 已在pccRules中，跳过`);
    await page.keyboard.press('Escape');
    return;
  }

  // 点击 pccRules 下拉（第1个xm-select）
  await frameEl.evaluate(() => {
    const inputs = document.querySelectorAll('input.xm-select-default');
    if (inputs[1]) inputs[1].parentElement.click();
  });
  await frameEl.waitForTimeout(1000);
  
  await frameEl.evaluate((text) => {
    const opts = document.querySelectorAll('.xm-option.show-icon');
    for (const opt of opts) {
      if (opt.textContent.trim() === text) {
        opt.click();
        return;
      }
    }
  }, pccId);

  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
  
  await frameEl.locator('button:has-text("提交")').click();
  await page.waitForTimeout(3000);
  console.log(`   ✅ 已添加 ${pccId} 到 pccRules`);
}

async function main() {
  const opts = parseArgs();
  const pccId = `pcc_${opts.qosId}`;
  
  // 参数处理
  const defaults = autoFillParams();
  const params = {
    qosId: opts.qosId,
    qi: opts.qi,
    maxbrUl: opts.maxbrUl || defaults.maxbrUl,
    maxbrDl: opts.maxbrDl || defaults.maxbrDl,
    gbrUl: opts.gbrUl || defaults.gbrUl,
    gbrDl: opts.gbrDl || defaults.gbrDl,
  };

  const browser = await chromium.launch({ headless: !opts.headed, args: ['--no-sandbox', '--ignore-certificate-errors', '--disable-dev-shm-usage', '--no-proxy-server', '--proxy-server=direct://', '--proxy-bypass-list=*'] });
  const ctx = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1920, height: 1080 } });
  const page = await ctx.newPage();

  await login(page);
  await selectProject(page, opts.project);

  // 自动确定5qi
  if (params.qi === null) {
    console.log('\n📋 检测已有QoS模板的5qi...');
    const usedQis = await getUsed5qis(page);
    console.log(`   已使用5qi: ${usedQis.join(', ')}`);
    params.qi = String(autoSelect5qi(usedQis));
    console.log(`   ✅ 自动选择 5qi = ${params.qi}`);
  } else {
    console.log(`\n📋 用户指定 5qi = ${params.qi}`);
  }

  // 显示最终参数
  console.log('\n📋 最终参数:');
  console.log(`   qosId   = ${params.qosId}`);
  console.log(`   5qi     = ${params.qi}`);
  console.log(`   maxbrUl = ${params.maxbrUl}`);
  console.log(`   maxbrDl = ${params.maxbrDl}`);
  console.log(`   gbrUl   = ${params.gbrUl}`);
  console.log(`   gbrDl   = ${params.gbrDl}`);

  // 清理旧数据
  console.log('\n🗑️ 清理旧数据...');
  await deleteQosIfExists(page, opts.qosId);
  await deletePccIfExists(page, pccId);

  // 创建QoS
  console.log('\n📦 创建QoS模板...');
  await addQos(page, params);

  // 创建PCC规则
  console.log('\n📦 创建PCC规则...');
  await addPcc(page, { ...params, pccId });

  // 添加到 sm_policy_default
  console.log('\n📦 添加到 sm_policy_default...');
  await addPccToSmpolicy(page, pccId);

  // 验证
  console.log('\n📋 验证结果...');
  await page.goto(`${globalBaseUrl}/sim_5gc/predfPolicy/qos/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const qosRow = await page.evaluate((targetId) => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      for (let i = 0; i < cells.length; i++) {
        if (cells[i].textContent.trim() === targetId) {
          return Array.from(cells).map(c => c.textContent.trim());
        }
      }
    }
    return null;
  }, opts.qosId);

  if (qosRow) {
    console.log(`\n✅ qos3 已创建: 5qi=${qosRow[3]}, maxbrUl=${qosRow[4]}, maxbrDl=${qosRow[5]}, gbrUl=${qosRow[6]}, gbrDl=${qosRow[7]}`);
  }

  await page.goto(`${globalBaseUrl}/sim_5gc/smpolicy/default/index`, { waitUntil: 'networkidle', ignoreHTTPSErrors: true });
  await page.waitForTimeout(3000);
  
  const smpolicy = await page.evaluate(() => {
    const rows = document.querySelectorAll('.layui-table tbody tr');
    for (const row of rows) {
      const cells = row.querySelectorAll('td');
      if (cells.length >= 6) {
        return cells[4].textContent.trim();
      }
    }
    return '';
  });

  console.log(`\n✅ sm_policy_default pccRules = ${smpolicy}`);

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
