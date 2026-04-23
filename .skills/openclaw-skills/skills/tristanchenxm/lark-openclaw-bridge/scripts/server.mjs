/**
 * server.mjs
 * Entry point: validates config, starts the HTTP server, wires up all routes.
 *
 * Routes:
 *   GET  /health         — health check
 *   GET  /chat-info      — basic chat info by sessionKey
 *   GET  /session-info   — full session info with member list
 *   POST /proactive      — send a message or image to a Lark chat
 *   POST /webhook        — receives Lark event callbacks
 */

import dotenv from 'dotenv';
dotenv.config();

import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import { log, logError } from './lib/logger.mjs';
import { MessageQueue } from './lib/message-queue.mjs';
import { processBatchedMessages } from './message-handler.mjs';
import { handleMessageEvent } from './lark-event-handler.mjs';
import { sendMessage, sendImage } from './lark-message-sender.mjs';
import { getChatInfo, getSessionInfo } from './lib/lark-reader.mjs';
import { startRelayClient } from './relay-client.mjs';

// ─── Config ───────────────────────────────────────────────────────

const APP_ID               = process.env.LARK_APP_ID;
const WEBHOOK_PORT         = Number(process.env.WEBHOOK_PORT || 18780);
const RELAY_SERVER_URL     = process.env.RELAY_SERVER_URL || '';   // e.g. ws://relay.atomecorp.net:8080/bridge
const RELAY_SECRET         = process.env.RELAY_SECRET || '';
const VERIFICATION_TOKEN   = process.env.LARK_VERIFICATION_TOKEN || '';
const OPENCLAW_CONFIG_PATH = (process.env.OPENCLAW_CONFIG_PATH || '~/.openclaw/openclaw.json')
  .replace(/^~/, os.homedir());

function validateConfig() {
  if (!process.env.LARK_APP_ID) {
    logError('[FATAL] LARK_APP_ID environment variable is required');
    process.exit(1);
  }
  if (!process.env.LARK_APP_SECRET) {
    logError('[FATAL] LARK_APP_SECRET environment variable is required');
    process.exit(1);
  }

  // Try primary path, fall back to legacy path
  let configPath = OPENCLAW_CONFIG_PATH;
  if (!fs.existsSync(configPath)) {
    const legacy = `${os.homedir()}/.clawdbot/clawdbot.json`;
    if (fs.existsSync(legacy)) {
      configPath = legacy;
    } else {
      logError('[FATAL] OpenClaw config not found:', configPath);
      process.exit(1);
    }
  }

  const clawdConfig = JSON.parse(fs.readFileSync(configPath, 'utf8').trim());
  if (!clawdConfig?.gateway?.auth?.token) {
    logError('[FATAL] gateway.auth.token missing in OpenClaw config');
    process.exit(1);
  }
}

// ─── Auto-discover bot open_id ────────────────────────────────────

async function ensureBotOpenId() {
  if (process.env.LARK_APP_OPEN_ID) return; // already set

  try {
    const tokenRes = await fetch('https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ app_id: process.env.LARK_APP_ID, app_secret: process.env.LARK_APP_SECRET }),
    });
    const { tenant_access_token } = await tokenRes.json();

    const botRes = await fetch('https://open.larksuite.com/open-apis/bot/v3/info', {
      headers: { Authorization: `Bearer ${tenant_access_token}` },
    });
    const { bot } = await botRes.json();

    if (bot?.open_id) {
      process.env.LARK_APP_OPEN_ID = bot.open_id;
      if (bot.app_name) process.env.LARK_BOT_NAME = bot.app_name;

      // Persist to .env so it survives restarts
      const envPath = new URL('../.env', import.meta.url).pathname;
      if (fs.existsSync(envPath)) {
        const envContent = fs.readFileSync(envPath, 'utf8');
        const additions = [];
        if (!envContent.includes('LARK_APP_OPEN_ID')) additions.push(`LARK_APP_OPEN_ID=${bot.open_id}`);
        if (bot.app_name && !envContent.includes('LARK_BOT_NAME')) additions.push(`LARK_BOT_NAME=${bot.app_name}`);
        if (additions.length) {
          fs.appendFileSync(envPath, '\n' + additions.join('\n') + '\n');
          log(`[OK] Auto-discovered bot info: ${bot.open_id} / ${bot.app_name || 'unknown'} (saved to .env)`);
        }
      }
    }
  } catch (err) {
    logError('[WARN] Failed to auto-discover bot open_id:', err.message);
  }
}

await ensureBotOpenId();

// ─── Message Queue ────────────────────────────────────────────────

const messageQueue = new MessageQueue({
  batchProcessor: (sessionKey, batch) => processBatchedMessages(sessionKey, batch),
  logger:         { log, logError },
});

// ─── HTTP Server ──────────────────────────────────────────────────

const server = http.createServer(async (req, res) => {
  const clientIp = req.headers['x-forwarded-for'] || req.headers['x-real-ip'] || req.socket.remoteAddress;
  const isLocal  = clientIp === '127.0.0.1' || clientIp === '::1' || clientIp === '::ffff:127.0.0.1';

  // GET /health
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', appId: APP_ID, supportedTypes: ['text', 'post', 'image', 'file'] }));
    return;
  }

  // GET /chat-info?sessionKey=...
  if (req.method === 'GET' && req.url?.startsWith('/chat-info')) {
    const sessionKey = new URL(req.url, `http://localhost`).searchParams.get('sessionKey');
    if (!sessionKey) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'sessionKey parameter required' }));
      return;
    }
    const chatId = sessionKey.split(':').at(-1);
    if (!chatId.startsWith('oc_') && !chatId.startsWith('ou_')) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid sessionKey format' }));
      return;
    }
    try {
      const chatInfo = await getChatInfo(chatId);
      log('[CHAT-INFO] Retrieved info for:', chatId, '-', chatInfo.name || '[private chat]');
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: true, sessionKey, chatId,
        chatInfo: {
          name: chatInfo.name, chatType: chatInfo.chat_type, chatMode: chatInfo.chat_mode,
          ownerId: chatInfo.owner_id, userCount: chatInfo.user_count, botCount: chatInfo.bot_count,
          description: chatInfo.description, avatar: chatInfo.avatar,
        },
      }));
    } catch (err) {
      logError('[CHAT-INFO] Error:', err.message);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  // GET /session-info?sessionKey=...  (full info with member list)
  if (req.method === 'GET' && req.url?.startsWith('/session-info')) {
    const sessionKey = new URL(req.url, `http://localhost`).searchParams.get('sessionKey');
    if (!sessionKey) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'sessionKey parameter required' }));
      return;
    }
    try {
      const data = await getSessionInfo(sessionKey);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, ...data }));
    } catch (err) {
      logError('[SESSION-INFO] Error:', err.message);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  // POST /proactive  — send message or image
  if (req.method === 'POST' && req.url === '/proactive') {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    let payload;
    try { payload = JSON.parse(Buffer.concat(chunks).toString('utf8')); }
    catch { res.writeHead(400, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ error: 'Invalid JSON' })); return; }

    const { chatId, text, imagePath, rootId, threadId, parentId } = payload;

    if (!chatId || (!text && !imagePath)) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'chatId and (text or imagePath) required' }));
      return;
    }

    try {
      const threadInfo = (parentId || rootId || threadId) ? { parentId, rootId, threadId } : {};
      const result = imagePath
        ? await sendImage(chatId, imagePath, text)
        : await sendMessage(chatId, text, 'text', null, threadInfo);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, ...result }));
    } catch (err) {
      logError('[PROACTIVE] Error:', err.message);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  // POST /webhook  — Lark event callbacks (exact match only)
  if (req.method === 'POST' && req.url === '/webhook') {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    let data;
    try { data = JSON.parse(Buffer.concat(chunks).toString('utf8')); }
    catch { res.writeHead(400); res.end('Invalid JSON'); return; }

    // URL verification challenge (no token check required)
    if (data.type === 'url_verification') {
      log('[OK] URL verification challenge received');
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ challenge: data.challenge }));
      return;
    }

    // Verification token check (mandatory for public requests)
    if (!isLocal) {
      if (!VERIFICATION_TOKEN) {
        log('[SECURITY] LARK_VERIFICATION_TOKEN not configured, rejecting public request from IP:', clientIp);
        res.writeHead(403, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Forbidden' }));
        return;
      }
      const requestToken = data.header?.token || data.token;
      if (requestToken !== VERIFICATION_TOKEN) {
        log('[SECURITY] Invalid Verification Token from IP:', clientIp);
        res.writeHead(403, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Forbidden' }));
        return;
      }
    }

    log('[EVENT]', data.type || data.header?.event_type || 'unknown');

    // Schema 2.0 event
    if (data.schema === '2.0' && data.header?.event_type === 'im.message.receive_v1') {
      res.writeHead(200); res.end('ok');
      handleMessageEvent(data.event, messageQueue);
      return;
    }

    // Legacy schema 1.0 event
    if (data.event?.type === 'message') {
      res.writeHead(200); res.end('ok');
      handleMessageEvent({
        message: {
          chat_id:      data.event.open_chat_id,
          message_id:   data.event.open_message_id,
          message_type: data.event.msg_type,
          content:      data.event.msg_type === 'text'
            ? JSON.stringify({ text: data.event.text_without_at_bot || data.event.text })
            : null,
          chat_type: data.event.chat_type,
          mentions:  data.event.open_id ? [{ id: data.event.open_id }] : [],
        },
      }, messageQueue);
      return;
    }

    // Unsupported event type
    log('[WARN] Unsupported event type received:', data.type || data.header?.event_type || 'unknown');
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Unsupported event type' }));
    return;
  }

  res.writeHead(404); res.end('Not found');
});

// ─── Startup / Shutdown ───────────────────────────────────────────

function gracefulShutdown(signal) {
  log(`[OK] Received ${signal}, shutting down`);
  server.close(() => { log('[OK] Server closed'); process.exit(0); });
}

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT',  () => gracefulShutdown('SIGINT'));

validateConfig();

// ─── Relay Mode ───────────────────────────────────────────────────

if (RELAY_SERVER_URL) {
  // Relay mode: receive Lark events via WebSocket from central relay server.
  // Local HTTP server still runs for proactive sends, health, chat-info, etc.
  log('[OK] Relay mode enabled — connecting to relay server');

  startRelayClient({
    appId:    APP_ID,
    secret:   RELAY_SECRET,
    relayUrl: RELAY_SERVER_URL,
    onEvent(data) {
      // Verification Token check (mandatory for all relay events)
      if (!VERIFICATION_TOKEN) {
        log('[RELAY SECURITY] LARK_VERIFICATION_TOKEN not configured, dropping relay event');
        return;
      }
      const requestToken = data.header?.token || data.token;
      if (requestToken !== VERIFICATION_TOKEN) {
        log('[RELAY EVENT] verification token mismatch, dropping event');
        return;
      }

      log('[RELAY EVENT]', data.header?.event_type || data.type || 'unknown');

      if (data.schema === '2.0' && data.header?.event_type === 'im.message.receive_v1') {
        handleMessageEvent(data.event, messageQueue);
        return;
      }
      if (data.event?.type === 'message') {
        handleMessageEvent({
          message: {
            chat_id:      data.event.open_chat_id,
            message_id:   data.event.open_message_id,
            message_type: data.event.msg_type,
            content:      data.event.msg_type === 'text'
              ? JSON.stringify({ text: data.event.text_without_at_bot || data.event.text })
              : null,
            chat_type: data.event.chat_type,
            mentions:  data.event.open_id ? [{ id: data.event.open_id }] : [],
          },
        }, messageQueue);
      }
    },
  });
}

// ─── Start HTTP Server ────────────────────────────────────────────

server.listen(WEBHOOK_PORT, '0.0.0.0', () => {
  log('[OK] Lark webhook bridge started');
  log(`    App ID:       ${APP_ID}`);
  log(`    Port:         ${WEBHOOK_PORT}`);
  log(`    Mode:         ${RELAY_SERVER_URL ? 'relay (' + RELAY_SERVER_URL + ')' : 'direct webhook'}`);
  if (!RELAY_SERVER_URL) {
    log(`    Webhook:      POST /webhook`);
  }
  log(`    Proactive:    POST /proactive`);
  log(`    Chat info:    GET  /chat-info?sessionKey=...`);
  log(`    Session info: GET  /session-info?sessionKey=...`);
  log(`    Health:       GET  /health`);
  log('');
  log('  ** PRIVACY: Chat content is logged locally for DEBUG purposes only. The server and gateway do not record any chat content. **');
});

