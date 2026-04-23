#!/usr/bin/env node

const axios = require('axios');

function parseArgs(argv) {
  const args = {};

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      continue;
    }

    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      args[key] = 'true';
      continue;
    }

    args[key] = next;
    i += 1;
  }

  return args;
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

const _logs = [];

function log(msg) {
  const entry = `[fitconverter] ${msg}`;
  _logs.push(entry);
  process.stderr.write(`${entry}\n`);
}

function exitWithJson(payload, exitCode) {
  payload.logs = _logs;
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(exitCode);
}

function printUsage() {
  const usage = `
Usage:
  node path/to/fit-converter/scripts/poll-payment.js \\
    --order-id <id> \\
    [--base-url <url>] \\
    [--interval-ms <milliseconds>] \\
    [--max-attempts <number>] \\
    [--quiet]
`;

  process.stderr.write(usage.trimStart());
  process.stderr.write('\n');
}

function formatElapsedMs(elapsedMs) {
  const totalSeconds = Math.floor(elapsedMs / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}m${String(seconds).padStart(2, '0')}s`;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help === 'true') {
    printUsage();
    process.exit(0);
  }

  const orderId = args['order-id'];
  const baseUrl = (args['base-url'] || 'https://www.fitconverter.com').replace(/\/$/, '');
  const intervalMs = Number(args['interval-ms'] || 3000);
  const maxAttempts = Number(args['max-attempts'] || 120);
  const quiet = args.quiet === 'true';

  if (!orderId) {
    exitWithJson({
      status: 'missing_inputs',
      user_message: '缺少 orderId，无法查询支付状态',
      order_id: null,
    }, 2);
  }

  if (!Number.isFinite(intervalMs) || intervalMs <= 0) {
    exitWithJson({
      status: 'error',
      user_message: 'interval-ms 必须是正整数',
      order_id: orderId,
    }, 3);
  }

  if (!Number.isFinite(maxAttempts) || maxAttempts <= 0) {
    exitWithJson({
      status: 'error',
      user_message: 'max-attempts 必须是正整数',
      order_id: orderId,
    }, 3);
  }

  const startedAt = Date.now();

  if (!quiet) {
    log(`[poll] start: orderId=${orderId}, interval=${intervalMs}ms, maxAttempts=${maxAttempts}`);
  }

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const response = await axios.post(`${baseUrl}/api/payStatusQuery`, {
        orderId,
      }, {
        timeout: 30000,
      });

      const payload = response.data || {};
      const tradeState = payload.data && payload.data.trade_state ? payload.data.trade_state : null;
      const elapsed = formatElapsedMs(Date.now() - startedAt);

      if (tradeState === 'NOTPAY') {
        if (!quiet) {
          log(`[poll] [${attempt}/${maxAttempts}] trade_state=NOTPAY elapsed=${elapsed}, waiting ${intervalMs}ms`);
        }

        if (attempt === maxAttempts) {
          exitWithJson({
            status: 'payment_required',
            user_message: '支付尚未完成，已达到最大轮询次数',
            order_id: orderId,
            attempts: attempt,
            trade_state: tradeState,
            raw_response: payload,
          }, 4);
        }

        await sleep(intervalMs);
        continue;
      }

      if (tradeState === 'SUCCESS') {
        if (!quiet) {
          log(`[poll] [${attempt}/${maxAttempts}] trade_state=SUCCESS elapsed=${elapsed}`);
        }

        exitWithJson({
          status: 'submitted',
          user_message: '提交成功，转换结果随后将以邮件形式通知',
          order_id: orderId,
          attempts: attempt,
          trade_state: tradeState,
          raw_response: payload,
        }, 0);
      }

      if (tradeState) {
        if (!quiet) {
          log(`[poll] [${attempt}/${maxAttempts}] trade_state=${tradeState} elapsed=${elapsed}`);
        }

        exitWithJson({
          status: 'error',
          user_message: `支付流程结束，当前状态为 ${tradeState}`,
          order_id: orderId,
          attempts: attempt,
          trade_state: tradeState,
          raw_response: payload,
        }, 5);
      }

      if (!quiet) {
        log(`[poll] [${attempt}/${maxAttempts}] trade_state=UNKNOWN elapsed=${elapsed}`);
      }

      exitWithJson({
        status: 'error',
        user_message: '支付状态查询返回了无法识别的结果',
        order_id: orderId,
        attempts: attempt,
        trade_state: tradeState,
        raw_response: payload,
      }, 5);
    } catch (error) {
      if (!quiet) {
        log(`[poll] [${attempt}/${maxAttempts}] poll_error=${error.message}`);
      }

      exitWithJson({
        status: 'error',
        user_message: '支付状态查询失败',
        order_id: orderId,
        error: {
          message: error.message,
          response_status: error.response ? error.response.status : null,
          response_data: error.response ? error.response.data : null,
        },
      }, 5);
    }
  }
}

main();
