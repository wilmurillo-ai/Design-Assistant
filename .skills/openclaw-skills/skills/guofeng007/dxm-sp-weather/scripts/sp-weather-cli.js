#!/usr/bin/env node
'use strict';

console.error('DEBUG: Loading sp-weather-cli.js');
const crypto = require('crypto');
console.error('DEBUG: crypto loaded, SSL_OP_LEGACY_SERVER_CONNECT =', crypto.constants.SSL_OP_LEGACY_SERVER_CONNECT);
const fs = require('fs');
const os = require('os');
const path = require('path');
const http = require('http');
const https = require('https');
const { spawnSync } = require('child_process');

const CONFIG_PATH = path.join(process.env.CLAUDE_SKILL_DIR || __dirname, 'sp-weather-config.json');
const BASE_URL = process.env.SP_WEATHER_BASE || 'https://www.dxmpay.com';
const SKILL_ID = '6143ff36-82e6-4d96-468a-e299dd478554';

// ─── Config ──────────────────────────────────────────────────────────────────

function readConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    }
  } catch (e) {}
  return null;
}

function generateKeys() {
  const { privateKey, publicKey } = crypto.generateKeyPairSync('ec', {
    namedCurve: 'prime256v1', // secp256r1
  });
  const pubKeyDer = publicKey.export({ type: 'spki', format: 'der' });
  // uid = hex(SHA-256(publicKey.getEncoded())).substring(0, 32)
  const uid = crypto.createHash('sha256').update(pubKeyDer).digest('hex').substring(0, 32);
  return {
    uid,
    publicKeyB64: pubKeyDer.toString('base64'),
    publicKeyPem: publicKey.export({ type: 'spki', format: 'pem' }),
    privateKeyPem: privateKey.export({ type: 'pkcs8', format: 'pem' }),
  };
}

// AES-256-GCM: uid → SHA-256(uid) 作为 32 字节密钥
function _uidKey(uid) {
  return crypto.createHash('sha256').update(uid).digest();
}

function encryptField(plaintext, uid) {
  const key = _uidKey(uid);
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const encrypted = Buffer.concat([cipher.update(plaintext, 'utf8'), cipher.final()]);
  const authTag = cipher.getAuthTag();
  return `${iv.toString('base64')}:${authTag.toString('base64')}:${encrypted.toString('base64')}`;
}

function decryptField(encryptedStr, uid) {
  const key = _uidKey(uid);
  const [ivB64, authTagB64, ciphertextB64] = encryptedStr.split(':');
  const iv = Buffer.from(ivB64, 'base64');
  const authTag = Buffer.from(authTagB64, 'base64');
  const ciphertext = Buffer.from(ciphertextB64, 'base64');
  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAuthTag(authTag);
  return decipher.update(ciphertext) + decipher.final('utf8');
}

function ensureConfig() {
  const config = readConfig();
  if (!config || !config.uid || !config.registered) {
    output({ success: false, message: '用户未注册，请先运行: userConfig' });
    process.exit(1);
  }
  config.publicKeyB64 = decryptField(config.publicKeyB64, config.uid);
  config.publicKeyPem = decryptField(config.publicKeyPem, config.uid);
  config.privateKeyPem = decryptField(config.privateKeyPem, config.uid);
  return config;
}

// ─── HTTP ─────────────────────────────────────────────────────────────────────

async function httpRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const lib = urlObj.protocol === 'https:' ? https : http;
    const reqOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: options.headers || {},
    };

    // Fix for Node.js 22+ OpenSSL 3.x TLS renegotiation issue
    if (urlObj.protocol === 'https:') {
      try {
        reqOptions.secureOptions = crypto.constants.SSL_OP_LEGACY_SERVER_CONNECT;
      } catch (e) {
        console.error('Warning: could not set secureOptions:', e.message);
      }
    }

    // 打印请求信息
    console.error('[REQUEST]', reqOptions.method, url);
    console.error('[REQUEST HEADERS]', JSON.stringify(reqOptions.headers));
    if (options.body) console.error('[REQUEST BODY]', options.body);

    const req = lib.request(reqOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        // 打印响应信息
        console.error('[RESPONSE STATUS]', res.statusCode);
        console.error('[RESPONSE HEADERS]', JSON.stringify(res.headers));
        console.error('[RESPONSE BODY]', data);
        resolve({ status: res.statusCode, body: data });
      });
    });
    req.on('error', reject);
    if (options.body) req.write(options.body);
    req.end();
  });
}

// ─── Signing ──────────────────────────────────────────────────────────────────

// 递归按 key 排序对象
function sortKeysRecursive(obj) {
  if (Array.isArray(obj)) return obj.map(sortKeysRecursive);
  if (obj !== null && typeof obj === 'object') {
    return Object.fromEntries(
      Object.keys(obj).sort().map((k) => [k, sortKeysRecursive(obj[k])])
    );
  }
  return obj;
}

// 注册签名: timestamp + "\n" + public_key_b64
function signRegistration(timestamp, publicKeyB64, privateKeyPem) {
  const message = `${timestamp}\n${publicKeyB64}`;
  const signer = crypto.createSign('SHA256');
  signer.update(message, 'utf8');
  return signer.sign(privateKeyPem, 'base64');
}

// API 请求签名: timestamp + "\n" + sortedJson(bodyWithoutSign)
function signApiBody(timestamp, bodyObj, privateKeyPem) {
  const bodyWithoutSign = Object.assign({}, bodyObj);
  delete bodyWithoutSign.sign;
  const sortedJson = JSON.stringify(sortKeysRecursive(bodyWithoutSign));
  const message = `${timestamp}\n${sortedJson}`;
  console.error('[SIGN MESSAGE]', message);
  const signer = crypto.createSign('SHA256');
  signer.update(message, 'utf8');
  return signer.sign(privateKeyPem, 'base64');
}

// 构造带签名的 POST body（timestamp 为毫秒字符串）
function buildSignedPostBody(params, privateKeyPem) {
  const timestamp = String(Date.now());
  const bodyObj = Object.assign({}, params, { timestamp });
  const sign = signApiBody(timestamp, bodyObj, privateKeyPem);
  return JSON.stringify(Object.assign({}, bodyObj, { sign }));
}

// 构造带签名的 GET URL（query params 转为 JSON 对象签名）
function buildSignedGetUrl(baseUrl, params, privateKeyPem) {
  const timestamp = String(Date.now());
  const allParams = Object.assign({}, params, { timestamp });
  const sortedJson = JSON.stringify(sortKeysRecursive(allParams));
  const message = `${timestamp}\n${sortedJson}`;
  console.error('[SIGN MESSAGE]', message);
  const signer = crypto.createSign('SHA256');
  signer.update(message, 'utf8');
  const sign = signer.sign(privateKeyPem, 'base64');
  const qs = new URLSearchParams(Object.assign({}, allParams, { sign })).toString();
  return `${baseUrl}?${qs}`;
}

// ─── QR Code ─────────────────────────────────────────────────────────────────

const { showQRCode } = require('./qrcode.min');

// ─── Arg parser ───────────────────────────────────────────────────────────────

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      result[key] = args[i + 1] !== undefined && !args[i + 1].startsWith('--')
        ? args[++i]
        : true;
    }
  }
  return result;
}

function output(data) {
  console.log(JSON.stringify(data, null, 2));
}

// ─── Commands ─────────────────────────────────────────────────────────────────

async function cmdUserConfig() {
  const config = readConfig();
  if (config && config.uid && config.registered) {
    output({ success: true, action: 'exists', uid: config.uid });
    return;
  }

  // 生成 EC 密钥对
  const keys = generateKeys();
  const timestamp = String(Date.now());
  const sign = signRegistration(timestamp, keys.publicKeyB64, keys.privateKeyPem);

  const body = JSON.stringify({
    public_key_b64: keys.publicKeyB64,
    timestamp,
    sign,
  });

  let res;
  try {
    res = await httpRequest(`${BASE_URL}/api/skill/client/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
      body,
    });
  } catch (e) {
    output({ success: false, message: `注册请求失败: ${e.message}` });
    process.exit(1);
    return;
  }

  let data;
  try { data = JSON.parse(res.body); } catch (_) { data = res.body; }

  if (res.status !== 200) {
    output({ success: false, message: '注册失败', status: res.status, data });
    process.exit(1);
    return;
  }

  // 保存到本地（敏感字段用 uid 派生的 AES-256-GCM 密钥加密）
  const configToSave = {
    uid: keys.uid,
    publicKeyB64: encryptField(keys.publicKeyB64, keys.uid),
    publicKeyPem: encryptField(keys.publicKeyPem, keys.uid),
    privateKeyPem: encryptField(keys.privateKeyPem, keys.uid),
    registered: true,
    registeredAt: new Date().toISOString(),
  };
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(configToSave, null, 2));
  output({ success: true, action: 'registered', uid: keys.uid, configPath: CONFIG_PATH, serverResponse: data });
}

async function cmdQueryWeather(args) {
  const config = ensureConfig();
  const { date, city } = parseArgs(args);

  if (!city) {
    output({ success: false, needCity: true, message: '请提供城市名称（--city 北京）' });
    process.exit(1);
    return;
  }

  const queryDate = date || new Date().toISOString().split('T')[0];
  const payload = { date: queryDate, city };

  const params = {
    skill_id: SKILL_ID,
    uid: config.uid,
    payload,
  };
  const body = buildSignedPostBody(params, config.privateKeyPem);

  let res;
  try {
    res = await httpRequest(`${BASE_URL}/api/skill/invoke`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
      body,
    });
  } catch (e) {
    output({ success: false, message: `连接天气服务失败: ${e.message}` });
    process.exit(1);
    return;
  }

  let data;
  try { data = JSON.parse(res.body); } catch (_) { data = res.body; }
   // data.payUrl = "https://www.baidu.com"
  if (data && data.payUrl) {
    process.stderr.write('\n⚠️  余额不足，请使用微信扫码付费：\n');
     showQRCode(data.payUrl);
    output({ success: false, payRequired: true, payUrl: data.payUrl, message: '余额不足，请扫码充值后重试' });
    process.exit(1);
    return;
  }

  if (res.status !== 200) {
    output({ success: false, status: res.status, data });
    process.exit(1);
    return;
  }

  output({ success: true, date: queryDate, city, data });
}

async function cmdQueryOrders(args) {
  const config = ensureConfig();
  const { page = '1', pageSize = '20' } = parseArgs(args);
  const url = buildSignedGetUrl(
    `${BASE_URL}/api/skill/orders`,
    { uid: config.uid, page, page_size: pageSize },
    config.privateKeyPem
  );

  let res;
  try { res = await httpRequest(url); } catch (e) {
    output({ success: false, message: `请求失败: ${e.message}` }); process.exit(1); return;
  }
  let data;
  try { data = JSON.parse(res.body); } catch (_) { data = res.body; }
  output({ success: res.status === 200, data });
}

async function cmdQueryOrder(args) {
  const config = ensureConfig();
  const { orderId } = parseArgs(args);
  if (!orderId) {
    output({ success: false, message: '请提供订单ID（--orderId SP202603192029449B6A4893）' });
    process.exit(1); return;
  }
  const url = buildSignedGetUrl(
    `${BASE_URL}/api/skill/orders/${encodeURIComponent(orderId)}`,
    { uid: config.uid },
    config.privateKeyPem
  );

  let res;
  try { res = await httpRequest(url); } catch (e) {
    output({ success: false, message: `请求失败: ${e.message}` }); process.exit(1); return;
  }
  let data;
  try { data = JSON.parse(res.body); } catch (_) { data = res.body; }
  output({ success: res.status === 200, data });
}

async function cmdQueryQuota() {
  const config = ensureConfig();
  const url = buildSignedGetUrl(
    `${BASE_URL}/api/skill/quota`,
    { uid: config.uid, skill_id: SKILL_ID },
    config.privateKeyPem
  );

  let res;
  try { res = await httpRequest(url); } catch (e) {
    output({ success: false, message: `请求失败: ${e.message}` }); process.exit(1); return;
  }
  let data;
  try { data = JSON.parse(res.body); } catch (_) { data = res.body; }
  output({ success: res.status === 200, data });
}

async function cmdQueryPurchaseDetail() {
  const config = ensureConfig();
  const url = buildSignedGetUrl(
    `${BASE_URL}/api/skill/purchase/detail`,
    { uid: config.uid, skill_id: SKILL_ID },
    config.privateKeyPem
  );

  let res;
  try { res = await httpRequest(url); } catch (e) {
    output({ success: false, message: `请求失败: ${e.message}` }); process.exit(1); return;
  }
  let data;
  try { data = JSON.parse(res.body); } catch (_) { data = res.body; }
  output({ success: res.status === 200, data });
}

async function cmdQueryCallLogs(args) {
  const config = ensureConfig();
  const { page = '1', pageSize = '20' } = parseArgs(args);
  const url = buildSignedGetUrl(
    `${BASE_URL}/api/skill/call-logs`,
    { uid: config.uid, skill_id: SKILL_ID, page, page_size: pageSize },
    config.privateKeyPem
  );

  let res;
  try { res = await httpRequest(url); } catch (e) {
    output({ success: false, message: `请求失败: ${e.message}` }); process.exit(1); return;
  }
  let data;
  try { data = JSON.parse(res.body); } catch (_) { data = res.body; }
  output({ success: res.status === 200, data });
}

// ─── Main ─────────────────────────────────────────────────────────────────────

const [, , command, ...args] = process.argv;

const COMMANDS = {
  userConfig: cmdUserConfig,
  queryWeather: cmdQueryWeather,
  queryOrders: cmdQueryOrders,
  queryOrder: cmdQueryOrder,
  queryQuota: cmdQueryQuota,
  queryPurchaseDetail: cmdQueryPurchaseDetail,
  queryCallLogs: cmdQueryCallLogs,
};

(async () => {
  if (!command || !COMMANDS[command]) {
    output({
      success: false,
      message: `未知命令: ${command || '(无)'}`,
      available: Object.keys(COMMANDS),
    });
    process.exit(1);
  }
  await COMMANDS[command](args);
})().catch((err) => {
  output({ success: false, error: err.message });
  process.exit(1);
});
