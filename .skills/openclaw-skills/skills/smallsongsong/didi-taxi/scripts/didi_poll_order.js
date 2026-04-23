#!/usr/bin/env node
/**
 * 滴滴打车订单单次探测脚本（cron 调用版）
 *
 * 用法:
 *   node scripts/didi_poll_order.js --order-id "ORDER_ID" --job-id "JOB_ID"
 *
 * 功能:
 *   - 单次查询订单状态（由 cron job 每30秒调用一次）
 *   - status=0:    输出匹配中状态
 *   - status=1:    输出司机已接单 + 查询司机位置
 *   - status=2~12: 输出终态信息 + 通过 JOB_ID 自动清理任务
 *
 * 调试模式:
 *   DIDI_DEBUG=1 node scripts/didi_poll_order.js --order-id "ORDER_ID" --job-id "JOB_ID"
 */

import { spawn } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { existsSync, readFileSync, mkdirSync, appendFileSync } from 'fs';
import { homedir } from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const DEBUG = process.env.DIDI_DEBUG === '1';

// 状态描述映射
const STATUS_DESCRIPTIONS = {
  0: "匹配中",
  1: "司机已接单",
  2: "司机已到达",
  3: "未知（-）",
  4: "行程开始",
  5: "订单完成",
  6: "订单已被系统取消",
  7: "订单已被取消",
  8: "未知（-）",
  9: "未知（-）",
  10: "未知（-）",
  11: "客服关闭订单",
  12: "未能完成服务",
};

// 终止状态
const TERMINAL_STATES = new Set([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);

// ─── 工具函数 ────────────────────────────────────────────────────────────────

function debug(msg) {
  if (DEBUG) process.stderr.write(`[DEBUG] ${msg}\n`);
}

function writeLog(orderId, msg) {
  try {
    const logDir = join(__dirname, '..', 'tmp', 'didi_orders');
    if (!existsSync(logDir)) mkdirSync(logDir, { recursive: true });
    const ts = new Date().toISOString();
    appendFileSync(join(logDir, `${orderId}.txt`), `[${ts}] ${msg}\n`);
  } catch (e) {
    debug(`writeLog failed: ${e.message}`);
  }
}

function parseArgs(argv) {
  const result = {};
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (!arg.startsWith('--')) continue;
    const key = arg.slice(2);
    if (i + 1 < argv.length && !argv[i + 1].startsWith('--')) {
      result[key] = argv[++i];
    } else {
      result[key] = true;
    }
  }
  return result;
}

/**
 * 获取 DIDI_MCP_KEY
 * 优先级: 环境变量 > ~/.openclaw/openclaw.json > /data/.clawdbot/openclaw.json
 */
function getDidiMcpKey() {
  let key = process.env.DIDI_MCP_KEY;
  if (key && key.trim()) return key.trim();

  const configPaths = [
    `${homedir()}/.openclaw/openclaw.json`,
    '/data/.clawdbot/openclaw.json',
  ];

  for (const configPath of configPaths) {
    try {
      if (existsSync(configPath)) {
        const config = JSON.parse(readFileSync(configPath, 'utf8'));
        key = config?.skills?.entries?.['didi-taxi']?.apiKey;
        if (key && key.trim()) {
          debug(`DIDI_MCP_KEY from ${configPath}`);
          return key.trim();
        }
      }
    } catch (e) {
      debug(`Failed to read config from ${configPath}: ${e.message}`);
    }
  }
  return null;
}

function execCommand(cmd, args) {
  return new Promise((resolve, reject) => {
    const proc = spawn(cmd, args, {
      stdio: ['ignore', 'pipe', 'pipe'],
      timeout: 30000,
    });
    let stdout = '';
    let stderr = '';
    proc.stdout.on('data', (d) => { stdout += d.toString(); });
    proc.stderr.on('data', (d) => { stderr += d.toString(); });
    proc.on('close', (code) => {
      debug(`${cmd} exit code: ${code}`);
      if (stderr) debug(`${cmd} stderr: ${stderr.trim()}`);
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        reject(new Error(stderr.trim() || `${cmd} exited with code ${code}`));
      }
    });
    proc.on('error', reject);
  });
}

/**
 * 解析 mcporter 输出（兼容标准 JSON 和 JS 对象字面量两种格式）
 *
 * mcporter 实际输出格式不稳定：
 *   - 标准 JSON：  {"content":[...],"structuredContent":{...}}
 *   - JS 对象字面量：{content:[{type:'text',text:'...'}],structuredContent:{statusCode:7,...}}
 *
 * 返回 { structured, contentText }
 *   structured:  structuredContent 对象（含 statusCode / statusText 等字段）
 *   contentText: content[0].text 字符串（可选，用于展示）
 */
function parseMcporterJson(stdout) {
  const text = stdout.trim();

  // ── 尝试 1：标准 JSON ──
  // 兼容两种格式：直接 {structuredContent, content} 或 {result: {structuredContent, content}}
  try {
    const data = JSON.parse(text);
    const payload = data.result ?? data;
    return {
      structured: payload.structuredContent || {},
      contentText: (payload.content?.[0]?.text || '').trim(),
    };
  } catch (_) {
    debug('JSON.parse failed, falling back to JS object literal parser');
  }

  // ── 尝试 2：JS 对象字面量（mcporter 实际输出格式）──
  // 用括号计数提取完整 structuredContent 块，避免嵌套 } 截断
  try {
    const scKeyIdx = text.indexOf('structuredContent');
    if (scKeyIdx !== -1) {
      const braceStart = text.indexOf('{', scKeyIdx);
      if (braceStart !== -1) {
        let depth = 0, inStr = false, strChar = '', end = -1;
        for (let i = braceStart; i < text.length; i++) {
          const c = text[i];
          if (inStr) {
            if (c === '\\') { i++; continue; }
            if (c === strChar) inStr = false;
          } else {
            if (c === '"' || c === "'") { inStr = true; strChar = c; }
            else if (c === '{') depth++;
            else if (c === '}') { depth--; if (depth === 0) { end = i; break; } }
          }
        }
        if (end !== -1) {
          let scStr = text.slice(braceStart, end + 1);
          // 处理 Node.js inspect 输出的 [Object]/[Array] 占位符（嵌套超过2层时出现）
          scStr = scStr.replace(/\[Object\]/g, '{}');
          scStr = scStr.replace(/\[Array\]/g, '[]');
          // 给无引号的 key 加双引号（如 statusCode: → "statusCode":）
          scStr = scStr.replace(/([{,]\s*)([\w]+)\s*:/g, '$1"$2":');
          // 单引号 → 双引号
          scStr = scStr.replace(/'([^']*)'/g, '"$1"');
          const structured = JSON.parse(scStr);
          debug(`JS object literal parsed: statusCode=${structured.statusCode}`);
          return { structured, contentText: '' };
        }
      }
    }
  } catch (e2) {
    debug(`JS object literal parsing failed: ${e2.message}`);
  }

  // ── 尝试 3：正则兜底，仅提取关键字段 ──
  const statusCodeMatch = text.match(/statusCode\s*:\s*(\d+)/);
  const statusTextMatch = text.match(/statusText\s*:\s*['"]?([^'"\n,}]+)['"]?/);
  const structured = {};
  if (statusCodeMatch) structured.statusCode = parseInt(statusCodeMatch[1], 10);
  if (statusTextMatch) structured.statusText = statusTextMatch[1].trim();
  debug(`Regex fallback: statusCode=${structured.statusCode}, statusText=${structured.statusText}`);
  return { structured, contentText: '' };
}

// ─── API 调用 ────────────────────────────────────────────────────────────────

async function queryOrder(orderId, mcpUrl) {
  const { stdout } = await execCommand('mcporter', [
    'call', mcpUrl,
    'taxi_query_order',
    '--args', JSON.stringify({ order_id: orderId }),
    '--output', 'json',
  ]);
  debug(`queryOrder stdout: ${stdout}`);
  // 记录原始输出，用于排查解析问题
  writeLog(orderId, `queryOrder raw stdout: ${stdout.trim()}`);
  return parseMcporterJson(stdout);
}

async function getDriverLocation(orderId, mcpUrl) {
  const { stdout } = await execCommand('mcporter', [
    'call', mcpUrl,
    'taxi_get_driver_location',
    '--args', JSON.stringify({ order_id: orderId }),
    '--output', 'json',
  ]);
  debug(`getDriverLocation stdout: ${stdout}`);
  return parseMcporterJson(stdout);
}

async function removeCronJob(jobId) {
  try {
    await execCommand('openclaw', ['cron', 'remove', jobId]);
    console.log(`🧹 任务已自动清理（${jobId}）`);
  } catch (e) {
    console.log(`⚠️ 自动清理任务失败（${jobId}）: ${e.message}`);
  }
}

// ─── 主函数 ──────────────────────────────────────────────────────────────────

async function main() {
  const parsed = parseArgs(process.argv.slice(2));
  const ORDER_ID = parsed['order-id'];
  const JOB_ID = parsed['job-id'];

  if (!ORDER_ID) {
    process.stderr.write('Error: --order-id is required\n');
    process.exit(1);
  }
  if (!JOB_ID) {
    process.stderr.write('Error: --job-id is required\n');
    process.exit(1);
  }

  // 获取 MCP Key
  const mcpKey = getDidiMcpKey();
  if (!mcpKey) {
    console.log(`❌ 未配置 DIDI_MCP_KEY，无法查询订单`);
    console.log(`💡 请访问 https://mcp.didichuxing.com/api?tap=api 获取 API Key`);
    process.exit(1);
  }
  const mcpUrl = `https://mcp.didichuxing.com/mcp-servers?key=${mcpKey}`;

  // 查询订单
  let orderResult;
  try {
    orderResult = await queryOrder(ORDER_ID, mcpUrl);
  } catch (e) {
    console.log(`🚖 订单: ${ORDER_ID}`);
    console.log(`❌ 查询失败: ${e.message}`);
    writeLog(ORDER_ID, `ERROR: 查询失败: ${e.message}`);
    process.exit(1);
  }

  const statusCode = orderResult.structured.statusCode;

  if (statusCode === undefined || statusCode === null) {
    console.log(`🚖 订单: ${ORDER_ID}`);
    console.log(`⚠️ 无法获取订单状态，请稍后重试`);
    writeLog(ORDER_ID, `WARN: 无法获取订单状态`);
    process.exit(1);
  }

  const statusText = STATUS_DESCRIPTIONS[statusCode] ?? `状态(${statusCode})`;
  writeLog(ORDER_ID, `STATUS: ${statusCode} - ${statusText}`);

  // ── status=0：匹配中 ──
  if (statusCode === 0) {
    console.log(`🚖 订单: ${ORDER_ID}`);
    console.log(`📊 状态: ${statusText} (${statusCode})`);
    console.log(`⏳ 正在为您匹配司机，请稍候...`);
    console.log(`🔁 继续跟踪中`);

  // ── status=1：司机已接单 ──
  } else if (statusCode === 1) {
    console.log(`🚖 订单: ${ORDER_ID}`);
    console.log(`📊 状态: ${statusText} (${statusCode})`);

    const driver = orderResult.structured.driver;
    const map = orderResult.structured.map;

    // 记录原始结构，用于排查 distanceKm/driver 字段是否存在
    writeLog(ORDER_ID, `STATUS=1 raw structured: ${JSON.stringify(orderResult.structured)}`);
    writeLog(ORDER_ID, `STATUS=1 driver=${JSON.stringify(driver)}, map=${JSON.stringify(map)}`);

    if (driver) {
      console.log(`👤 司机：${driver.name} | ${driver.carModel} | ${driver.carPlate}`);
      console.log(`📞 电话：${driver.phone}`);
    }

    if (map && map.distanceKm && map.eta) {
      console.log(`📍 距上车点还有 ${map.distanceKm} 公里，约 ${map.eta} 分钟到达`);
      writeLog(ORDER_ID, `DRIVER: distance=${map.distanceKm}km, eta=${map.eta}min`);
    } else {
      writeLog(ORDER_ID, `DRIVER: map.distanceKm/eta 不存在，降级调用 taxi_get_driver_location`);
      // 兜底：使用 taxi_get_driver_location 获取原始坐标
      try {
        const { structured: driverData } = await getDriverLocation(ORDER_ID, mcpUrl);
        writeLog(ORDER_ID, `getDriverLocation raw: ${JSON.stringify(driverData)}`);
        if (driverData.latitude && driverData.longitude) {
          console.log(`📍 司机正在向您驶来：纬度 ${driverData.latitude}，经度 ${driverData.longitude}`);
          writeLog(ORDER_ID, `DRIVER: lat=${driverData.latitude}, lng=${driverData.longitude}`);
        }
      } catch (e) {
        debug(`getDriverLocation failed: ${e.message}`);
        console.log(`📍 司机位置：暂时无法获取`);
      }
    }

    console.log(`🔁 继续跟踪中`);

  // ── 终态：status=2~12 ──
  } else if (TERMINAL_STATES.has(statusCode)) {
    console.log(`🚖 订单: ${ORDER_ID}`);
    console.log(`📊 状态: ${statusText} (${statusCode})`);
    if (statusCode === 2) {
      console.log(`✅ 司机已到达上车点，请前往上车！`);
    } else {
      console.log(`✅ 订单已结束`);
    }
    writeLog(ORDER_ID, `TERMINAL: 订单终态，任务清理`);
    await removeCronJob(JOB_ID);

  // ── 未知状态 ──
  } else {
    console.log(`🚖 订单: ${ORDER_ID}`);
    console.log(`📊 状态: 未知 (${statusCode})`);
    console.log(`🔁 继续跟踪中`);
  }

  process.exit(0);
}

main().catch((err) => {
  process.stderr.write(`Fatal error: ${err.message}\n`);
  process.exit(1);
});
