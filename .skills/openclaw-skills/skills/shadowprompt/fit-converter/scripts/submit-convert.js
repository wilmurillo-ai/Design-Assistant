#!/usr/bin/env node
const os = require('os');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const QRCode = require('qrcode');

const FILE_CONVERT_PAYMENT = 19.9;
const SYNC_CONVERT_PAYMENT = 29.9;
const TRIAL_CONVERT_PAYMENT = 0.1;

const FILE_TYPE_LIST = [
  'huawei',
  'zepp',
  'xiaomi',
  'vivo',
  'keep',
  'samsung',
  'dongdong',
  'kml',
  'gpx',
  'tcx',
  'fit',
];

const SYNC_PASSWORD_TYPE_LIST = [
  'zepp_sync',
  'keep_sync',
  'codoon_sync',
  'xingzhe_sync',
  'garmin_sync_coros',
];

const SYNC_CODE_TYPE_LIST = ['joyrun_sync'];

const MOCK_LOGIN_TYPE_LIST = [
  'zepp_sync',
  'keep_sync',
  'codoon_sync',
  'joyrun_sync',
  'rqrun_sync',
  'xingzhe_sync',
  'garmin_sync_coros',
];

const DIY_TYPE_LIST = [
  ...FILE_TYPE_LIST,
  ...SYNC_PASSWORD_TYPE_LIST,
  ...SYNC_CODE_TYPE_LIST,
].filter((item) => item !== 'rqrun_sync');

const DESTINATION_LIST = [
  'coros',
  'garmin',
  'strava',
  'rqrun',
  'huawei',
  'keep',
  'shuzixindong',
  'xingzhe',
  'igpsport',
  'onelap',
  'fit',
  'tcx',
  'gpx',
  'kml',
];

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
Usage: node path/to/fit-converter/scripts/submit-convert.js \\
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
  [--base-url <url>] \\
  [--skip-qr] \\
  [--qr-output <path>]

Examples:
  node path/to/fit-converter/scripts/submit-convert.js --type huawei --destination garmin --address user@example.com --zip-file ./demo.zip
  node path/to/fit-converter/scripts/submit-convert.js --type zepp_sync --destination strava --address user@example.com --account demo --password secret
  node path/to/fit-converter/scripts/submit-convert.js --type huawei --destination garmin --address user@example.com --zip-file "D:/data/demo.zip" --qr-output ./weixinPayQr.png
`;

  process.stderr.write(usage.trimStart());
  process.stderr.write('\n');
}

const _logs = [];

function log(msg) {
  const entry = `[fitconverter] ${msg}`;
  _logs.push(entry);
  console.log(entry);
  process.stderr.write(`${entry}\n`);
}

function exitWithJson(payload, exitCode) {
  payload.logs = _logs;
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(exitCode);
}

function isValidEmail(email) {
  return /([A-Za-z0-9]+([_.][A-Za-z0-9]+)*@([A-Za-z0-9-]+\.)+[A-Za-z]{2,6})/i.test(email);
}

function isTruthyFlag(value) {
  return value === true || value === 'true';
}

function getPaymentAmount(type, doMode) {
  if (doMode === 'trial') {
    return TRIAL_CONVERT_PAYMENT;
  }

  if (MOCK_LOGIN_TYPE_LIST.includes(type)) {
    return SYNC_CONVERT_PAYMENT;
  }

  return FILE_CONVERT_PAYMENT;
}

function collectMissingFields(args) {
  const missing = [];
  const type = args.type;

  if (!type) {
    missing.push('type');
  }
  if (!args.destination) {
    missing.push('destination');
  }
  if (!args.address) {
    missing.push('address');
  }

  if (FILE_TYPE_LIST.includes(type) && !args['zip-file']) {
    missing.push('zip_file');
  }

  if (SYNC_PASSWORD_TYPE_LIST.includes(type)) {
    if (!args.account) {
      missing.push('account');
    }
    if (!args.password) {
      missing.push('password');
    }
  }

  if (SYNC_CODE_TYPE_LIST.includes(type)) {
    if (!args.account) {
      missing.push('account');
    }
    if (!args.password) {
      missing.push('password');
    }
  }

  return missing;
}

function buildRequestSummary(args, baseUrl) {
  return {
    baseUrl,
    type: args.type || null,
    destination: args.destination || null,
    address: args.address || null,
    doMode: args['do-mode'] || 'trial',
    clientMode: args['client-mode'] || 'PC',
    hasZipFile: Boolean(args['zip-file']),
    hasAccount: Boolean(args.account),
    hasPassword: Boolean(args.password),
  };
}

function normalizeZipFileArg(rawPath) {
  if (!rawPath) {
    return {
      rawPath,
      normalizedPath: rawPath,
      resolvedPath: null,
      hasLikelyBashWindowsPathIssue: false,
    };
  }

  let normalizedPath = rawPath;

  if (/^\/[a-zA-Z]\//.test(normalizedPath)) {
    normalizedPath = `${normalizedPath[1]}:/${normalizedPath.slice(3)}`;
  }

  if (/^[a-zA-Z]:\//.test(normalizedPath)) {
    normalizedPath = normalizedPath.replace(/\//g, path.sep);
  }

  const hasLikelyBashWindowsPathIssue =
    /^[a-zA-Z]:[^\\/]/.test(rawPath) && !/^[a-zA-Z]:\//.test(rawPath);

  return {
    rawPath,
    normalizedPath,
    resolvedPath: path.resolve(normalizedPath),
    hasLikelyBashWindowsPathIssue,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (isTruthyFlag(args.help)) {
    printUsage();
    process.exit(0);
  }

  const baseUrl = (args['base-url'] || 'https://www.fitconverter.com').replace(/\/$/, '');
  const doMode = args['do-mode'] || 'trial';
  const clientMode = args['client-mode'] || 'PC';
  const fitCode = args['fit-code'] || '';
  const fileName = args['file-name'] || `trial_${Date.now()}`;
  const paymentAmount = getPaymentAmount(args.type, doMode);
  const missingFields = collectMissingFields(args);
  const requestSummary = buildRequestSummary(args, baseUrl);
  const zipFileInfo = normalizeZipFileArg(args['zip-file']);
  let qrOutput = args['qr-output'];

  log(`[submit] type=${args.type} destination=${args.destination} address=${args.address} doMode=${doMode}`);

  if (missingFields.length > 0) {
    log(`[submit] missing fields: ${missingFields.join(', ')}`);
    exitWithJson({
      status: 'missing_inputs',
      user_message: '缺少必要参数，无法提交转换任务',
      missing_fields: missingFields,
      request_summary: requestSummary,
    }, 2);
  }

  if (!DIY_TYPE_LIST.includes(args.type)) {
    log(`[submit] unsupported type: ${args.type}`);
    exitWithJson({
      status: 'unsupported_flow',
      user_message: '当前数据源不支持自助转换，请走人工转换流程',
      missing_fields: [],
      request_summary: requestSummary,
    }, 3);
  }

  if (!DESTINATION_LIST.includes(args.destination)) {
    exitWithJson({
      status: 'error',
      user_message: '不支持的目标平台',
      missing_fields: [],
      request_summary: requestSummary,
    }, 4);
  }

  if (!isValidEmail(args.address)) {
    exitWithJson({
      status: 'error',
      user_message: '请正确填写转换结果接收邮箱地址',
      missing_fields: [],
      request_summary: requestSummary,
    }, 4);
  }

  if (clientMode === 'H5') {
    exitWithJson({
      status: 'unsupported_flow',
      user_message: 'H5 模式不支持当前自助提交流程',
      missing_fields: [],
      request_summary: requestSummary,
    }, 3);
  }

  const formData = new FormData();
  formData.append('clientMode', clientMode);
  formData.append('clientOpenID', args['client-openid'] || '');

  if (FILE_TYPE_LIST.includes(args.type)) {
    if (!fs.existsSync(zipFileInfo.resolvedPath)) {
      const helpMessage = zipFileInfo.hasLikelyBashWindowsPathIssue
        ? '检测到 Windows 路径在 bash 中被转义了。请改用 "D:/path/to/file.zip" 或 "/d/path/to/file.zip"。'
        : '请检查 zip 文件路径是否正确，并在包含空格或特殊字符时使用引号。';

      exitWithJson({
        status: 'error',
        user_message: 'zip 文件不存在',
        help_message: helpMessage,
        missing_fields: [],
        request_summary: {
          ...requestSummary,
          zipFile: {
            raw: zipFileInfo.rawPath,
            normalized: zipFileInfo.normalizedPath,
            resolved: zipFileInfo.resolvedPath,
          },
        },
      }, 4);
    }

    log(`[submit] zip file resolved: ${zipFileInfo.resolvedPath}`);
    formData.append('zip_file', fs.createReadStream(zipFileInfo.resolvedPath));
  }

  formData.append('type', args.type);
  formData.append('address', args.address);
  formData.append('destination', args.destination);
  formData.append('fileName', fileName);
  formData.append('fitCode', fitCode);
  formData.append('account', args.account || 'OpenClaw');
  formData.append('password', args.password || '');
  formData.append('paid', String(paymentAmount));
  formData.append('payment', 'wechat');
  formData.append('recordMode', doMode === 'trial' ? `trial_${fitCode}` : 'prd');

  log(`[submit] posting to ${baseUrl}/api/convertSubmit ...`);

  try {
    const response = await axios.post(`${baseUrl}/api/convertSubmit`, formData, {
      timeout: 600000,
      headers: formData.getHeaders(),
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
    });

    const res = response.data || {};
    log(`[submit] server responded: code=${res.code}`);

    if (res.code === 1) {
      const result = {
        status: 'payment_required',
        user_message: '校验通过，请完成支付以触发服务器自动转换',
        missing_fields: [],
        request_summary: requestSummary,
        payment_summary: {
          orderId: res.orderId || null,
          amount: typeof res.paid === 'number' ? res.paid / 100 : null,
          qr_image_path: res.wxPayImgUrl,
          payment_channel: 'wechat',
          next_step: 'none',
        },
        raw_response: res,
      };

      if (res.data && res.data.code_url) {
        result.payment_summary.next_step = 'scan_qr';
        result.payment_summary.code_url = res.data.code_url;
        log(`[submit] payment created: orderId=${res.orderId}, code_url available`);

        if (!isTruthyFlag(args['skip-qr'])) {
          log(`[submit] generating QR code ...`);
          const qrDataUrl = await QRCode.toDataURL(res.data.code_url);
          const qrBase64 = qrDataUrl.split(',')[1];
          result.payment_summary.qr_data_url = qrDataUrl;

          // 如果未指定--qr-output，则保存二维码图片至/root/.openclaw/media/fitId_xxx.png
          if (!qrOutput) {
            const mediaDir = path.join(os.homedir(), '.openclaw', 'media');
            if (!fs.existsSync(mediaDir)) {
              fs.mkdirSync(mediaDir, { recursive: true });
            }
            qrOutput = `${mediaDir}/${res.orderId}.png`;
          }
          const qrBuffer = Buffer.from(qrBase64, 'base64');
          fs.writeFileSync(qrOutput, qrBuffer);
          result.payment_summary.qr_image_local_path = qrOutput;
          log(`[submit] QR code saved to ${qrOutput}`);

          log(`[submit] QR code ready (data url length=${qrDataUrl.length})`);
        }
      } else if (res.data && res.data.h5_url) {
        result.payment_summary.next_step = 'open_h5_url';
        result.payment_summary.h5_url = res.data.h5_url;
      } else if (res.data && res.data.prepay_id) {
        result.payment_summary.next_step = 'invoke_wechat_pay';
        result.payment_summary.wechat_payload = res.extraData || null;
      } else {
        result.status = 'error';
        result.user_message = '支付初始化成功，但未返回可用的支付信息';
        result.payment_summary.next_step = 'none';
        process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
        process.exit(5);
      }

      process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
      process.exit(0);
    }

    if (res.code === 0) {
      log(`[submit] validation failed: ${res.message || 'unknown reason'}`);
      const message = res.message
        ? `提交的${res.message}，请按照说明重新整理后上传`
        : '提交压缩包结构不正确，请按照说明重新整理后上传';

      exitWithJson({
        status: 'validation_failed',
        user_message: message,
        missing_fields: [],
        request_summary: requestSummary,
        raw_response: res,
      }, 6);
    }

    exitWithJson({
      status: 'error',
      user_message: '其它异常',
      missing_fields: [],
      request_summary: requestSummary,
      raw_response: res,
    }, 5);
  } catch (error) {
    log(`[submit] request error: ${error.message}`);
    exitWithJson({
      status: 'error',
      user_message: '出错啦',
      missing_fields: [],
      request_summary: requestSummary,
      error: {
        message: error.message,
        response_status: error.response ? error.response.status : null,
        response_data: error.response ? error.response.data : null,
      },
    }, 5);
  }
}

main();
