#!/usr/bin/env node

const path = require('path');
const { spawnSync } = require('child_process');
const QRCode = require('qrcode');

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

function printUsage() {
  const usage = `
Usage:
 node path/to/fit-converter/scripts/run-flow.js \\
 --type <type> \\
 --destination <destination> \\
 --address <email> \\
 [--zip-file <path>] \\
 [--account <value>] \\
 [--password <value>] \\
 [--do-mode <trial|do>] \\
 [--fit-code <value>] \\
 [--client-mode <PC|weixin|H5>] \\
 [--client-openid <value>] \\
 [--interval-ms 3000] \\
 [--max-attempts 120] \\
 [--base-url <url>] \\
 [--include-qr-data]

Examples:
  node path/to/fit-converter/scripts/run-flow.js --do-mode trial --type huawei --destination garmin --address user@example.com --zip-file "D:/data/demo.zip"
  node path/to/fit-converter/scripts/run-flow.js --type zepp_sync --destination strava --address user@example.com --account demo --password secret
`;

  process.stderr.write(usage.trimStart());
  process.stderr.write('\n');
}

const _logs = [];

function log(msg) {
  const entry = `[fitconverter] ${msg}`;
  _logs.push(entry);
  process.stderr.write(`${entry}\n`);
}

function collectLogs(jsonResult) {
  if (jsonResult && Array.isArray(jsonResult.logs)) {
    _logs.push(...jsonResult.logs);
  }
}

function exitWithJson(payload, exitCode) {
  payload.logs = _logs;
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(exitCode);
}

function runNodeScript(scriptPath, scriptArgs) {
  const result = spawnSync(process.execPath, [scriptPath, ...scriptArgs], {
    cwd: process.cwd(),
    encoding: 'utf8',
  });

  return {
    status: result.status === null ? 1 : result.status,
    stdout: result.stdout || '',
    stderr: result.stderr || '',
    error: result.error || null,
  };
}

function parseJsonOutput(stdout) {
  const trimmed = stdout.trim();
  if (!trimmed) {
    return null;
  }

  try {
    return JSON.parse(trimmed);
  } catch (error) {
    return null;
  }
}

function argsToList(args) {
  const list = [];

  Object.entries(args).forEach(([key, value]) => {
    if (value === undefined || value === null || value === false) {
      return;
    }

    list.push(`--${key}`);
    if (value !== true && value !== 'true') {
      list.push(String(value));
    }
  });

  return list;
}

async function renderTerminalQr(codeUrl) {
  if (!codeUrl) {
    return null;
  }

  try {
    return await QRCode.toString(codeUrl, {
      type: 'terminal',
      small: true,
    });
  } catch (error) {
    return null;
  }
}

async function main() {
  const rawArgs = process.argv.slice(2);
  const args = parseArgs(rawArgs);

  if (args.help === 'true') {
    printUsage();
    process.exit(0);
  }

  const submitScript = path.join(__dirname, 'submit-convert.js');
  const pollScript = path.join(__dirname, 'poll-payment.js');

  const submitArgs = [...rawArgs];
  // 默认包含 QR data URL，除非明确指定 --skip-qr
  const skipQr = args['skip-qr'] === 'true';
  if (!skipQr && !('include-qr-data' in args)) {
    submitArgs.push('--include-qr-data');
  }

  log('[flow] Step 1/2: submitting conversion request...');
  const submitRun = runNodeScript(submitScript, submitArgs);

  if (submitRun.stderr) {
    process.stderr.write(submitRun.stderr);
  }

  if (submitRun.error) {
    exitWithJson({
      status: 'error',
      user_message: '提交脚本执行失败',
      step: 'submit',
      error: {
        message: submitRun.error.message,
      },
    }, 5);
  }

  const submitResult = parseJsonOutput(submitRun.stdout);
  if (!submitResult) {
    log('[flow] submit script returned no parsable JSON');
    exitWithJson({
      status: 'error',
      user_message: '提交脚本未返回可解析的 JSON',
      step: 'submit',
      raw_stdout: submitRun.stdout,
      raw_stderr: submitRun.stderr,
    }, submitRun.status || 5);
  }

  collectLogs(submitResult);

  if (submitRun.status !== 0) {
    log(`[flow] submit failed with exit code ${submitRun.status}`);
    exitWithJson({
      ...submitResult,
      step: 'submit',
    }, submitRun.status);
  }

  const paymentSummary = submitResult.payment_summary || {};
  const orderId = paymentSummary.orderId || null;

  if (submitResult.status !== 'payment_required' || !orderId) {
    exitWithJson({
      ...submitResult,
      step: 'submit',
    }, 0);
  }

  log(`[flow] Step 1/2 complete: orderId=${orderId}`);
  if (paymentSummary.code_url) {
    log(`[flow] payment code_url: ${paymentSummary.code_url}`);
    const terminalQr = await renderTerminalQr(paymentSummary.code_url);
    if (terminalQr) {
      log('[flow] payment QR (terminal render):');
      process.stderr.write(terminalQr);
      if (!terminalQr.endsWith('\n')) {
        process.stderr.write('\n');
      }
    }
  }
  if (paymentSummary.h5_url) {
    log(`[flow] payment h5_url: ${paymentSummary.h5_url}`);
  }
  log('[flow] Step 2/2: waiting for payment confirmation...');

  const pollArgs = argsToList({
    'order-id': orderId,
    'base-url': args['base-url'],
    'interval-ms': args['interval-ms'],
    'max-attempts': args['max-attempts'],
  });

  const pollRun = runNodeScript(pollScript, pollArgs);

  if (pollRun.stderr) {
    process.stderr.write(pollRun.stderr);
  }

  if (pollRun.error) {
    exitWithJson({
      status: 'error',
      user_message: '支付轮询脚本执行失败',
      step: 'poll',
      submit_result: submitResult,
      error: {
        message: pollRun.error.message,
      },
    }, 5);
  }

  const pollResult = parseJsonOutput(pollRun.stdout);
  if (!pollResult) {
    log('[flow] poll script returned no parsable JSON');
    exitWithJson({
      status: 'error',
      user_message: '支付轮询脚本未返回可解析的 JSON',
      step: 'poll',
      submit_result: submitResult,
      raw_stdout: pollRun.stdout,
      raw_stderr: pollRun.stderr,
    }, pollRun.status || 5);
  }

  collectLogs(pollResult);
  log(`[flow] done: status=${pollResult.status}`);

  exitWithJson({
    status: pollResult.status,
    user_message: pollResult.user_message,
    step: 'done',
    submit_result: submitResult,
    poll_result: pollResult,
  }, pollRun.status);
}

main();
