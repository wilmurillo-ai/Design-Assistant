#!/usr/bin/env node
'use strict';
/**
 * CouponClaw — 每日推送开关管理
 * 用法:
 *   node scripts/push-toggle.js on  <userId> [--morning 09:00] [--region all] [--channel telegram] [--lang zh|en]
 *   node scripts/push-toggle.js off <userId>
 *   node scripts/push-toggle.js status <userId>
 */

const fs = require('fs');
const path = require('path');

const USERS_DIR = path.join(__dirname, '..', 'data', 'users');
const ALLOWED_CHANNELS = new Set(['telegram', 'feishu', 'slack', 'discord']);
const ALLOWED_REGIONS = new Set(['cn', 'us', 'uk', 'au', 'sea', 'all']);
const ALLOWED_LANGS = new Set(['zh', 'en']);

function sanitizeId(v) {
  if (typeof v !== 'string' || !/^[a-zA-Z0-9_-]{1,128}$/.test(v)) {
    console.error('❌ 无效 userId'); process.exit(1);
  }
  return v;
}
function safeUserPath(u) {
  const r = path.resolve(USERS_DIR, u + '.json');
  if (!r.startsWith(path.resolve(USERS_DIR) + path.sep)) {
    console.error('❌ 非法路径'); process.exit(1);
  }
  return r;
}
function loadUser(u) {
  const f = safeUserPath(u);
  return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : {};
}
function saveUser(u, data) {
  fs.mkdirSync(USERS_DIR, { recursive: true });
  fs.writeFileSync(safeUserPath(u), JSON.stringify(data, null, 2), 'utf8');
}

const [action, rawId, ...rest] = process.argv.slice(2);

if (!action || !rawId) {
  console.log('用法: node scripts/push-toggle.js on|off|status <userId> [options]');
  process.exit(0);
}

const userId = sanitizeId(rawId);

if (action === 'status') {
  const user = loadUser(userId);
  if (!user.push) {
    console.log(`[${userId}] 推送未开启`);
  } else {
    console.log(`[${userId}] 推送已开启 | 时间: ${user.push.morning} | 地区: ${user.push.region} | 语言: ${user.push.lang} | 渠道: ${user.push.channel}`);
  }
  process.exit(0);
}

if (action === 'off') {
  const user = loadUser(userId);
  delete user.push;
  saveUser(userId, user);
  console.log(`[${userId}] 每日优惠推送已关闭`);
  process.exit(0);
}

if (action === 'on') {
  const morningIdx = rest.indexOf('--morning');
  const rawMorning = morningIdx !== -1 ? rest[morningIdx + 1] : '09:00';
  const morning = /^\d{2}:\d{2}$/.test(rawMorning) ? rawMorning : '09:00';

  const regionIdx = rest.indexOf('--region');
  const rawRegion = regionIdx !== -1 ? rest[regionIdx + 1] : 'all';
  const region = ALLOWED_REGIONS.has(rawRegion) ? rawRegion : 'all';

  const channelIdx = rest.indexOf('--channel');
  const rawChannel = channelIdx !== -1 ? rest[channelIdx + 1] : 'telegram';
  const channel = ALLOWED_CHANNELS.has(rawChannel) ? rawChannel : 'telegram';

  const langIdx = rest.indexOf('--lang');
  const rawLang = langIdx !== -1 ? rest[langIdx + 1] : 'zh';
  const lang = ALLOWED_LANGS.has(rawLang) ? rawLang : 'zh';

  const user = loadUser(userId);
  user.push = { morning, region, channel, lang, enabledAt: new Date().toISOString() };
  saveUser(userId, user);

  const cronCmd = `node scripts/daily-deals.js --region ${region} --lang ${lang}`;
  console.log(`[${userId}] 每日优惠推送已开启`);
  console.log(`推送时间: ${morning} | 地区: ${region} | 渠道: ${channel} | 语言: ${lang}`);
  console.log(`\n请在 openclaw cron 中添加以下任务：`);
  console.log(`openclaw cron add --schedule "0 ${morning.split(':')[1]} ${morning.split(':')[0]} * * *" --cmd "${cronCmd}" --target ${userId} --channel ${channel}`);
  process.exit(0);
}

console.error(`未知操作: ${action}`);
process.exit(1);
