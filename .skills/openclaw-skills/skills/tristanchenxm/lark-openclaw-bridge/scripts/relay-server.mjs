/**
 * relay-server.mjs
 * Central relay service — deploy on jvs (172.16.240.1)
 *
 * Lark sends all webhooks here. Bridges connect via WebSocket and receive
 * their messages. Handles URL verification challenges directly.
 *
 * Routes (internal — nginx strips /lark/ prefix):
 *   POST /webhook/:appId   — Lark event callbacks (external: /lark/webhook/:appId)
 *   GET  /health            — health check
 *   GET  /status            — connected bridges overview (requires RELAY_STATUS_TOKEN)
 *   GET  /logs              — real-time log viewer (SSE, requires RELAY_STATUS_TOKEN)
 *   GET  /openclaw-config   — provision arouter key + return openclaw.json (requires ?appId=)
 *   WS   /bridge            — bridge WebSocket connections (external: /lark/bridge)
 *
 * Env:
 *   RELAY_PORT                — HTTP/WS port (default: 18787)
 *   RELAY_SECRET              — shared secret bridges must present to connect
 *   RELAY_STATUS_TOKEN        — token for GET /status (optional, defaults to RELAY_SECRET)
 *   RELAY_CLUSTER_WORKERS     — number of cluster workers (0 or unset = single-process)
 *   AROUTER_ADMIN_URL         — arouter admin API base URL (default: http://localhost:18785)
 *   AROUTER_ADMIN_TOKEN       — admin Bearer token for arouter key provisioning
 *   AROUTER_DEPARTMENT_ID     — department ID for new API keys (default: 1)
 *   SSO_JWT_SECRET            — HS256 secret used by auth-link to sign SSO tokens (required for /openclaw-config)
 */

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import cluster from 'node:cluster';
import { fileURLToPath } from 'node:url';
import { WebSocketServer } from 'ws';
import { config as dotenvConfig } from 'dotenv';
import { jwtVerify } from 'jose';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Load .env from the project root (one level up from scripts/)
dotenvConfig({ path: path.resolve(__dirname, '../.env') });

const PORT           = Number(process.env.RELAY_PORT || 18787);
const RELAY_SECRET   = process.env.RELAY_SECRET || '';
const STATUS_TOKEN   = process.env.RELAY_STATUS_TOKEN || RELAY_SECRET;
const WORKER_COUNT   = Number(process.env.RELAY_CLUSTER_WORKERS) || 0;
// Admin API is on a separate port (18794)
// Accept both new (AROUTER_*) and legacy (OPENROUTER_*) env var names
const AROUTER_ADMIN_URL     = process.env.AROUTER_ADMIN_URL    || process.env.OPENROUTER_ADMIN_URL    || 'http://localhost:18786';
const AROUTER_ADMIN_TOKEN   = process.env.AROUTER_ADMIN_TOKEN  || process.env.OPENROUTER_ADMIN_TOKEN  || '';
// Default department ID to assign new API keys to (must exist in arouter DB)
const AROUTER_DEPARTMENT_ID = Number(process.env.AROUTER_DEPARTMENT_ID || process.env.OPENROUTER_DEPARTMENT_ID || 1);
const USE_CLUSTER  = WORKER_COUNT > 1;
// SSO JWT secret — must match the secret used by auth-link to sign tokens.
const SSO_JWT_SECRET = process.env.SSO_JWT_SECRET || '';

// ─── Shared: perMessageDeflate config ────────────────────────────

const perMessageDeflateOpts = {
  zlibDeflateOptions: { chunkSize: 1024, memLevel: 7, level: 3 },
  zlibInflateOptions: { chunkSize: 10 * 1024 },
  threshold: 1024,
  concurrencyLimit: 10,
  serverNoContextTakeover: true,
};

// ─── Log Ring Buffer + SSE ───────────────────────────────────────

const LOG_BUFFER_SIZE = 500;
const logRing = new Array(LOG_BUFFER_SIZE);
let logRingHead  = 0;
let logRingCount = 0;
const sseClients = new Set();

function pushLog(level, msg) {
  const entry = { ts: new Date().toISOString(), level, msg };
  logRing[logRingHead] = entry;
  logRingHead = (logRingHead + 1) % LOG_BUFFER_SIZE;
  if (logRingCount < LOG_BUFFER_SIZE) logRingCount++;
  const line = `data: ${JSON.stringify(entry)}\n\n`;
  for (const client of sseClients) {
    const res = client.res || client;
    const filterAppId = client.filterAppId || '';
    if (filterAppId && !entry.msg?.includes(filterAppId)) continue;
    try { res.write(line); } catch { sseClients.delete(client); }
  }
}

function* iterLogBuffer() {
  if (logRingCount === 0) return;
  const start = logRingCount < LOG_BUFFER_SIZE ? 0 : logRingHead;
  for (let i = 0; i < logRingCount; i++) {
    yield logRing[(start + i) % LOG_BUFFER_SIZE];
  }
}

function log(...args)      {
  const msg = args.join(' ');
  console.log(new Date().toISOString(), '[RELAY]', msg);
  pushLog('info', msg);
}
function logError(...args) {
  const msg = args.join(' ');
  console.error(new Date().toISOString(), '[RELAY][ERROR]', msg);
  pushLog('error', msg);
}

// ─── Shared: HTTP route handlers ─────────────────────────────────

function handleInstallSh(req, res) {
  const scriptPath = path.resolve(__dirname, '../install.sh');
  if (!fs.existsSync(scriptPath)) {
    res.writeHead(404); res.end('install.sh not found');
    return;
  }
  res.writeHead(200, {
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Disposition': 'inline; filename="install.sh"',
    'Cache-Control': 'no-cache',
  });
  fs.createReadStream(scriptPath).pipe(res);
  log('[INSTALL.SH] downloaded from', req.socket.remoteAddress);
}

function handleHealth(res, bridgeCount) {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status: 'ok',
    bridges: bridgeCount,
    uptime: process.uptime(),
  }));
}

function handleLogsRoute(req, res) {
  const params = new URL(req.url, 'http://localhost').searchParams;
  const token  = params.get('token') || req.headers['x-status-token'];
  if (STATUS_TOKEN && token !== STATUS_TOKEN) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>Lark Relay Logs</title>
<style>body{font-family:monospace;background:#111;color:#ccc;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
form{display:flex;flex-direction:column;gap:8px;background:#1e1e1e;padding:24px;border-radius:8px}
input{padding:8px;background:#2a2a2a;border:1px solid #444;color:#fff;border-radius:4px}
button{padding:8px;background:#4a90d9;border:none;color:#fff;border-radius:4px;cursor:pointer}</style></head>
<body><form onsubmit="location.href='/logs?token='+document.getElementById('t').value;return false">
<div style="color:#fff;font-size:14px">🔐 Lark Relay — Access Token</div>
<input id="t" type="password" placeholder="Enter token" autofocus>
<button type="submit">Enter</button></form></body></html>`);
    return;
  }

  const format = params.get('format');
  const filterAppId = params.get('appId') || '';

  const matchesFilter = (entry) => {
    if (!filterAppId) return true;
    return entry.msg?.includes(filterAppId);
  };

  if (format !== 'html') {
    res.writeHead(200, {
      'Content-Type':  'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection':    'keep-alive',
      'X-Accel-Buffering': 'no',
    });
    for (const entry of iterLogBuffer()) {
      if (matchesFilter(entry)) res.write(`data: ${JSON.stringify(entry)}\n\n`);
    }
    const filteredClient = { res, filterAppId };
    sseClients.add(filteredClient);
    req.on('close', () => sseClients.delete(filteredClient));
    return;
  }

  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(LOG_VIEWER_HTML);
}

const LOG_VIEWER_HTML = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Lark Relay Logs</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0d1117; color: #e6edf3; font-family: 'SF Mono', 'Fira Code', monospace; font-size: 13px; display: flex; flex-direction: column; height: 100vh; }
  #header { background: #161b22; padding: 12px 16px; border-bottom: 1px solid #30363d; display: flex; align-items: center; gap: 12px; }
  #header h1 { font-size: 14px; font-weight: 600; color: #58a6ff; }
  #status { font-size: 12px; color: #8b949e; margin-left: auto; }
  #controls { display: flex; gap: 8px; }
  button { padding: 4px 10px; background: #21262d; border: 1px solid #30363d; color: #e6edf3; border-radius: 4px; cursor: pointer; font-size: 12px; }
  button:hover { background: #30363d; }
  #log { flex: 1; overflow-y: auto; padding: 8px 0; }
  .line { padding: 2px 16px; line-height: 1.6; white-space: pre-wrap; word-break: break-all; }
  .line:hover { background: #161b22; }
  .ts { color: #8b949e; user-select: none; }
  .info .tag { color: #3fb950; }
  .error .tag { color: #f85149; }
  #tail-btn.active { background: #1f6feb; border-color: #388bfd; }
  #live-btn.active { background: #1a7f37; border-color: #2ea043; }
</style></head>
<body>
<div id="header">
  <h1>🦞 Lark Relay Logs</h1>
  <div id="status">Connecting…</div>
  <div id="controls">
    <button id="clear-btn" onclick="document.getElementById('log').innerHTML=''">Clear</button>
    <button id="tail-btn" class="active" onclick="toggleTail()">Tail ✓</button>
    <button id="live-btn" class="active" onclick="toggleLive()">Live ✓</button>
  </div>
</div>
<div id="log"></div>
<script>
  let tail = true;
  let live = true;
  let es = null;
  const logEl = document.getElementById('log');
  const statusEl = document.getElementById('status');
  const token = new URLSearchParams(location.search).get('token') || '';

  function toggleTail() {
    tail = !tail;
    document.getElementById('tail-btn').className = tail ? 'active' : '';
    document.getElementById('tail-btn').textContent = tail ? 'Tail ✓' : 'Tail';
  }

  function toggleLive() {
    live = !live;
    document.getElementById('live-btn').className = live ? 'active' : '';
    document.getElementById('live-btn').textContent = live ? 'Live ✓' : 'Live';
    if (live) connect(); else disconnect();
  }

  function connect() {
    if (es) { es.close(); es = null; }
    const basePath = location.pathname.replace(/\/logs$/, '');
    es = new EventSource(basePath + '/logs?token=' + encodeURIComponent(token));
    es.onopen = () => { statusEl.textContent = '● Connected'; statusEl.style.color = '#3fb950'; };
    es.onmessage = (e) => { try { appendLine(JSON.parse(e.data)); } catch {} };
    es.onerror = () => { statusEl.textContent = '● Disconnected'; statusEl.style.color = '#f85149'; };
  }

  function disconnect() {
    if (es) { es.close(); es = null; }
    statusEl.textContent = '○ Paused';
    statusEl.style.color = '#8b949e';
  }

  function appendLine(entry) {
    const d = document.createElement('div');
    d.className = 'line ' + (entry.level || 'info');
    d.innerHTML = '<span class="ts">' + entry.ts + '</span> <span class="tag">[' + (entry.level || 'info').toUpperCase() + ']</span> ' + escHtml(entry.msg);
    logEl.appendChild(d);
    if (tail) logEl.scrollTop = logEl.scrollHeight;
  }

  function escHtml(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  connect();
</script>
</body></html>`;

// ─── Shared: WebSocket connection handler ────────────────────────

function handleWsConnection(ws, req, bridges) {
  const url    = new URL(req.url, 'http://localhost');
  const appId  = url.searchParams.get('appId');
  const secret = url.searchParams.get('secret');

  if (!appId) {
    ws.close(4000, 'Missing appId');
    return;
  }
  if (RELAY_SECRET && secret !== RELAY_SECRET) {
    ws.close(4001, 'Unauthorized');
    logError(`[AUTH FAIL] appId=${appId} from ${req.socket.remoteAddress}`);
    return;
  }

  if (bridges.has(appId)) {
    const prev = bridges.get(appId);
    log(`[RECONNECT] appId=${appId} — closing old connection`);
    prev.ws.close(4010, 'Replaced by new connection');
  }

  const entry = { ws, appId, connectedAt: new Date() };
  bridges.set(appId, entry);
  log(`[CONNECTED] appId=${appId} from ${req.socket.remoteAddress} (total: ${bridges.size})`);

  ws.send(JSON.stringify({ type: 'connected', appId }));

  ws.on('message', (raw) => {
    try {
      const msg = JSON.parse(raw);
      if (msg.type === 'ping') {
        ws.send(JSON.stringify({ type: 'pong' }));
      }
    } catch { /* ignore malformed */ }
  });

  ws.on('close', (code, reason) => {
    if (bridges.get(appId)?.ws === ws) {
      bridges.delete(appId);
      log(`[DISCONNECTED] appId=${appId} code=${code} reason=${reason?.toString() || ''} (total: ${bridges.size})`);
    }
  });

  ws.on('error', (err) => {
    logError(`[WS ERROR] appId=${appId}:`, err.message);
  });
}

// ─── JWT verification (HS256, verified against SSO_JWT_SECRET) ───

/**
 * Verifies a JWT signed by auth-link and returns its payload.
 * Throws if the signature is invalid, the token is expired, or
 * SSO_JWT_SECRET is not configured.
 * @param {string} token
 * @returns {Promise<import('jose').JWTPayload>}
 */
async function verifyJwtPayload(token) {
  if (!SSO_JWT_SECRET) {
    throw new Error('SSO_JWT_SECRET is not configured');
  }
  const secret = new TextEncoder().encode(SSO_JWT_SECRET);
  const { payload } = await jwtVerify(token, secret);
  return payload;
}

// ─── Shared: OpenClaw config provisioner (arouter) ───────────────

async function handleOpenClawConfig(req, res) {
  const params = new URL(req.url, 'http://localhost').searchParams;
  const appId  = params.get('appId') || '';

  if (!appId) {
    res.writeHead(400, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'appId is required' }));
    return;
  }

  // SSO token is required — anonymous key provisioning is not allowed.
  const authHeader = req.headers['authorization'] || '';
  if (!authHeader.startsWith('Bearer ')) {
    res.writeHead(401, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Authorization required: please complete Lark SSO login' }));
    return;
  }
  let ssoPayload;
  try {
    ssoPayload = await verifyJwtPayload(authHeader.slice(7));
  } catch (err) {
    const isConfig = err.message === 'SSO_JWT_SECRET is not configured';
    res.writeHead(isConfig ? 503 : 401, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: isConfig ? 'SSO verification unavailable' : 'Invalid or expired SSO token' }));
    return;
  }
  if (!ssoPayload.name && !ssoPayload.email) {
    res.writeHead(401, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'SSO token missing identity claims' }));
    return;
  }
  const createdBy = [ssoPayload.name, ssoPayload.email].filter(Boolean).join(' ');

  // Provision a new API key from arouter admin API
  let apiKey = '';
  if (AROUTER_ADMIN_TOKEN) {
    try {
      const provisionRes = await fetch(`${AROUTER_ADMIN_URL}/admin/keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${AROUTER_ADMIN_TOKEN}`,
        },
        body: JSON.stringify({
          name: `lark-bridge:${appId}`,
          app_id: appId,
          department_id: AROUTER_DEPARTMENT_ID,
          token_limit: 1000000,
          ...(createdBy ? { created_by: createdBy } : {}),
        }),
      });
      if (provisionRes.ok) {
        const data = await provisionRes.json();
        apiKey = data.api_key || '';
        log(`[CONFIG] Provisioned arouter key for appId=${appId} prefix=${data.key_prefix}`);
      } else {
        const err = await provisionRes.text();
        log(`[CONFIG] Failed to provision key for appId=${appId}: ${provisionRes.status} ${err}`);
      }
    } catch (e) {
      log(`[CONFIG] Failed to provision arouter key for appId=${appId}: ${e.message}`);
    }
  } else {
    log(`[CONFIG] AROUTER_ADMIN_TOKEN not set — skipping key provisioning for appId=${appId}`);
  }

  // Build openclaw.json structure
  // NOTE: apiKey is NOT stored in openclaw.json — it goes into auth-profiles.json
  // (see install.sh for how the key is written to the credential store)
  const config = {
    ...(apiKey ? { _provisionedApiKey: apiKey } : {}),
    models: {
      mode: 'merge',
      providers: {
        arouter: {
          baseUrl: 'https://oc.atomecorp.net/arouter/v1',
          api: 'openai-completions',
          authHeader: true,
          models: [
            {
              id: 'deepseek-v3-2-251201',
              name: 'DeepSeek V3 (Default)',
              input: ['text'],
              cost: { input: 1.0, output: 2.0 },
              contextWindow: 64000,
              maxTokens: 8192,
            },
            {
              id: 'doubao-seed-2-0-lite-260215',
              name: 'Doubao Seed 2.0 Lite (Fast)',
              input: ['text'],
              cost: { input: 0.6, output: 3.6, cacheRead: 0.12 },
              contextWindow: 32000,
              maxTokens: 4096,
            },
            {
              id: 'doubao-seed-2-0-pro-260215',
              name: 'Doubao Seed 2.0 Pro (Smart)',
              input: ['text'],
              cost: { input: 3.2, output: 16.0, cacheRead: 0.64 },
              contextWindow: 32000,
              maxTokens: 4096,
            },
            {
              id: 'doubao-seed-2-0-code-preview-260215',
              name: 'Doubao Seed 2.0 Code (Pro)',
              input: ['text'],
              cost: { input: 3.2, output: 16.0, cacheRead: 0.64 },
              contextWindow: 32000,
              maxTokens: 4096,
            },
          ],
        },
      },
    },
    auth: {
      profiles: {
        'arouter:default': {
          provider: 'arouter',
          mode: 'api_key',
        },
      },
    },
    agents: {
      defaults: {
        model: { primary: 'arouter/deepseek-v3-2-251201' },
      },
    },
  };

  log(`[CONFIG] Served openclaw-config for appId=${appId}${apiKey ? ' (with key)' : ' (no key — AROUTER_ADMIN_TOKEN not set)'}`);

  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(config, null, 2));
}

// ─── Shared: Webhook handler ─────────────────────────────────────

async function handleWebhook(req, res, appId, getBridge) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  let data;
  let rawBody;
  try {
    rawBody = Buffer.concat(chunks).toString('utf8');
    data = JSON.parse(rawBody);
  } catch {
    res.writeHead(400); res.end('Invalid JSON');
    return;
  }

  if (data.type === 'url_verification') {
    const responseBody = JSON.stringify({ challenge: data.challenge });
    log(`[CHALLENGE] appId=${appId}`);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(responseBody);
    return;
  }

  const bridge = getBridge(appId);
  if (!bridge) {
    logError(`[NO BRIDGE] appId=${appId} -- no bridge connected`);
    res.writeHead(200); res.end('ok');
    return;
  }

  res.writeHead(200); res.end('ok');

  try {
    const eventType = data.header?.event_type || data.type || 'unknown';
    log(`[ROUTED] appId=${appId} event=${eventType} schema=${data.schema || 'v1'}`);
    bridge.ws.send('{"type":"lark_event","payload":' + rawBody + '}');
  } catch (err) {
    logError(`[SEND FAIL] appId=${appId}:`, err.message);
  }
}

// ═════════════════════════════════════════════════════════════════
// Single-Process Mode (default, RELAY_CLUSTER_WORKERS=0 or unset)
// ═════════════════════════════════════════════════════════════════

function startSingleProcess() {
  /** @type {Map<string, { ws: import('ws').WebSocket, connectedAt: Date, appId: string }>} */
  const bridges = new Map();

  const server = http.createServer(async (req, res) => {
    if (req.method === 'GET' && req.url === '/install.sh') {
      handleInstallSh(req, res);
      return;
    }
    if (req.method === 'GET' && req.url === '/health') {
      handleHealth(res, bridges.size);
      return;
    }
    if (req.method === 'GET' && req.url?.startsWith('/status')) {
      const token = new URL(req.url, 'http://localhost').searchParams.get('token')
        || req.headers['x-status-token'];
      if (STATUS_TOKEN && token !== STATUS_TOKEN) {
        res.writeHead(401, { 'Content-Type': 'text/plain' });
        res.end('Unauthorized');
        return;
      }
      const list = [...bridges.entries()].map(([appId, b]) => ({
        appId,
        connectedAt: b.connectedAt.toISOString(),
        uptimeSeconds: Math.floor((Date.now() - b.connectedAt) / 1000),
      }));
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ bridges: list, total: list.length }));
      return;
    }
    if (req.method === 'GET' && req.url?.startsWith('/logs')) {
      handleLogsRoute(req, res);
      return;
    }
    if (req.method === 'GET' && req.url?.startsWith('/openclaw-config')) {
      await handleOpenClawConfig(req, res);
      return;
    }
    const webhookMatch = req.method === 'POST' && req.url?.match(/^\/webhook\/([^/?]+)/);
    if (webhookMatch) {
      await handleWebhook(req, res, webhookMatch[1], (id) => bridges.get(id));
      return;
    }
    res.writeHead(404); res.end('Not found');
  });

  const wss = new WebSocketServer({ server, path: '/bridge', perMessageDeflate: perMessageDeflateOpts });
  wss.on('connection', (ws, req) => handleWsConnection(ws, req, bridges));

  if (!RELAY_SECRET) {
    console.warn('[WARN] RELAY_SECRET not set — all bridges can connect without auth');
  }

  server.listen(PORT, '0.0.0.0', () => {
    log(`Relay server started on port ${PORT} (single-process)`);
    log(`  Lark webhook: POST /webhook/{appId}  (external: /lark/webhook/{appId})`);
    log(`  Bridge WS:    ws://host:${PORT}/bridge?appId=&secret=  (external: /lark/bridge)`);
    log(`  Health:       GET  /health`);
    log(`  Status:       GET  /status?token=`);
    log(`  Logs:         GET  /logs?token=&format=html`);
    log(`  Config:       GET  /openclaw-config?appId=`);
  });

  function shutdown() {
    log('Shutting down');
    for (const [, b] of bridges) b.ws.close(1001, 'Server shutting down');
    server.close(() => process.exit(0));
  }
  process.on('SIGTERM', shutdown);
  process.on('SIGINT',  shutdown);
}

// ═════════════════════════════════════════════════════════════════
// Cluster Master
// ═════════════════════════════════════════════════════════════════

function startMaster() {
  const workers = [];
  /** @type {Map<string, import('node:cluster').Worker>} appId -> worker that owns it */
  const appIdToWorker = new Map();
  let nextWorkerIdx = 0;  // round-robin for new WS upgrades

  // Spawn workers
  for (let i = 0; i < WORKER_COUNT; i++) {
    const worker = cluster.fork();
    workers.push(worker);
    setupWorkerIPC(worker);
  }

  log(`Cluster master started — ${WORKER_COUNT} workers`);

  function setupWorkerIPC(worker) {
    worker.on('message', (msg) => {
      switch (msg.type) {
        case 'bridge_registered':
          appIdToWorker.set(msg.appId, worker);
          break;
        case 'bridge_unregistered':
          if (appIdToWorker.get(msg.appId) === worker) {
            appIdToWorker.delete(msg.appId);
          }
          break;
        case 'log':
          pushLog(msg.level, msg.msg);
          if (msg.level === 'error') {
            console.error(new Date().toISOString(), '[RELAY]', msg.msg);
          } else {
            console.log(new Date().toISOString(), '[RELAY]', msg.msg);
          }
          break;
        case 'status_response':
          resolveStatusRequest(msg.requestId, msg.bridges);
          break;
        case 'webhook_no_bridge':
          logError(`[NO BRIDGE] appId=${msg.appId} -- no bridge connected`);
          break;
      }
    });
  }

  // Worker crash recovery
  let shuttingDown = false;
  cluster.on('exit', (deadWorker, code, signal) => {
    log(`[CLUSTER] Worker ${deadWorker.process.pid} died (code=${code} signal=${signal})`);
    // Remove dead worker's appIds
    for (const [appId, w] of appIdToWorker) {
      if (w === deadWorker) appIdToWorker.delete(appId);
    }
    if (shuttingDown) return;
    log(`[CLUSTER] Restarting worker…`);
    const idx = workers.indexOf(deadWorker);
    const replacement = cluster.fork();
    if (idx >= 0) workers[idx] = replacement;
    else workers.push(replacement);
    setupWorkerIPC(replacement);
  });

  // Status request aggregation
  const pendingStatusRequests = new Map();
  let statusRequestId = 0;

  function resolveStatusRequest(requestId, bridgeList) {
    const pending = pendingStatusRequests.get(requestId);
    if (!pending) return;
    pending.results.push(...bridgeList);
    pending.remaining--;
    if (pending.remaining <= 0) {
      clearTimeout(pending.timer);
      pending.resolve(pending.results);
      pendingStatusRequests.delete(requestId);
    }
  }

  function collectStatus() {
    return new Promise((resolve) => {
      const reqId = ++statusRequestId;
      const aliveWorkers = workers.filter(w => !w.isDead());
      if (aliveWorkers.length === 0) { resolve([]); return; }
      const pending = {
        results: [],
        remaining: aliveWorkers.length,
        resolve,
        timer: setTimeout(() => {
          pendingStatusRequests.delete(reqId);
          resolve(pending.results);
        }, 2000),
      };
      pendingStatusRequests.set(reqId, pending);
      for (const w of aliveWorkers) {
        try { w.send({ type: 'status_request', requestId: reqId }); } catch {
          pending.remaining--;
        }
      }
      if (pending.remaining <= 0) {
        clearTimeout(pending.timer);
        pendingStatusRequests.delete(reqId);
        resolve(pending.results);
      }
    });
  }

  // Pick worker for a given appId (prefer existing owner, else round-robin)
  function pickWorker(appId) {
    const existing = appIdToWorker.get(appId);
    if (existing && !existing.isDead()) return existing;
    const aliveWorkers = workers.filter(w => !w.isDead());
    if (aliveWorkers.length === 0) return null;
    const worker = aliveWorkers[nextWorkerIdx % aliveWorkers.length];
    nextWorkerIdx = (nextWorkerIdx + 1) % aliveWorkers.length;
    return worker;
  }

  // HTTP server (master owns all HTTP, including webhook body reading)
  const server = http.createServer(async (req, res) => {
    if (req.method === 'GET' && req.url === '/install.sh') {
      handleInstallSh(req, res);
      return;
    }
    if (req.method === 'GET' && req.url === '/health') {
      handleHealth(res, appIdToWorker.size);
      return;
    }
    if (req.method === 'GET' && req.url?.startsWith('/status')) {
      const token = new URL(req.url, 'http://localhost').searchParams.get('token')
        || req.headers['x-status-token'];
      if (STATUS_TOKEN && token !== STATUS_TOKEN) {
        res.writeHead(401, { 'Content-Type': 'text/plain' });
        res.end('Unauthorized');
        return;
      }
      const bridgeList = await collectStatus();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ bridges: bridgeList, total: bridgeList.length }));
      return;
    }
    if (req.method === 'GET' && req.url?.startsWith('/logs')) {
      handleLogsRoute(req, res);
      return;
    }
    const webhookMatch = req.method === 'POST' && req.url?.match(/^\/webhook\/([^/?]+)/);
    if (webhookMatch) {
      const appId = webhookMatch[1];
      const chunks = [];
      for await (const chunk of req) chunks.push(chunk);
      let rawBody;
      try {
        rawBody = Buffer.concat(chunks).toString('utf8');
        const data = JSON.parse(rawBody);
        // Handle challenge in master (no bridge needed)
        if (data.type === 'url_verification') {
          log(`[CHALLENGE] appId=${appId}`);
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ challenge: data.challenge }));
          return;
        }
      } catch {
        res.writeHead(400); res.end('Invalid JSON');
        return;
      }

      // Ack Lark immediately
      res.writeHead(200); res.end('ok');

      // Forward to worker
      const worker = appIdToWorker.get(appId);
      if (worker && !worker.isDead()) {
        try { worker.send({ type: 'webhook_forward', appId, rawBody }); } catch {
          logError(`[SEND FAIL] appId=${appId}: worker IPC error`);
        }
      } else {
        logError(`[NO BRIDGE] appId=${appId} -- no bridge connected`);
      }
      return;
    }
    res.writeHead(404); res.end('Not found');
  });

  // WebSocket upgrade: hand off TCP socket to target worker
  server.on('upgrade', (req, socket, head) => {
    const url = new URL(req.url, 'http://localhost');
    if (url.pathname !== '/bridge') {
      socket.destroy();
      return;
    }

    const appId = url.searchParams.get('appId');
    const secret = url.searchParams.get('secret');

    // Fail-fast auth in master
    if (!appId) {
      socket.write('HTTP/1.1 400 Bad Request\r\n\r\n');
      socket.destroy();
      return;
    }
    if (RELAY_SECRET && secret !== RELAY_SECRET) {
      logError(`[AUTH FAIL] appId=${appId} from ${req.socket.remoteAddress}`);
      socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
      socket.destroy();
      return;
    }

    const worker = pickWorker(appId);
    if (!worker) {
      socket.write('HTTP/1.1 503 Service Unavailable\r\n\r\n');
      socket.destroy();
      return;
    }

    try {
      worker.send({
        type: 'ws_upgrade',
        appId,
        secret,
        remoteAddress: req.socket.remoteAddress,
        headers: req.headers,
        url: req.url,
        head: head.toString('base64'),
      }, socket);
    } catch (err) {
      logError(`[UPGRADE FAIL] appId=${appId}: ${err.message}`);
      socket.destroy();
    }
  });

  if (!RELAY_SECRET) {
    console.warn('[WARN] RELAY_SECRET not set — all bridges can connect without auth');
  }

  server.listen(PORT, '0.0.0.0', () => {
    log(`Relay server started on port ${PORT} (cluster: ${WORKER_COUNT} workers)`);
    log(`  Lark webhook: POST /webhook/{appId}  (external: /lark/webhook/{appId})`);
    log(`  Bridge WS:    ws://host:${PORT}/bridge?appId=&secret=  (external: /lark/bridge)`);
    log(`  Health:       GET  /health`);
    log(`  Status:       GET  /status?token=`);
    log(`  Logs:         GET  /logs?token=&format=html`);
    log(`  Config:       GET  /openclaw-config?appId=`);
  });

  function shutdown() {
    if (shuttingDown) return;
    shuttingDown = true;
    log('Shutting down cluster…');
    for (const w of workers) {
      if (!w.isDead()) {
        try { w.send({ type: 'shutdown' }); } catch { /* already gone */ }
      }
    }
    setTimeout(() => {
      for (const w of workers) {
        if (!w.isDead()) w.process.kill('SIGKILL');
      }
      server.close(() => process.exit(0));
    }, 5000);
  }
  process.on('SIGTERM', shutdown);
  process.on('SIGINT',  shutdown);
}

// ═════════════════════════════════════════════════════════════════
// Entry Point
// ═════════════════════════════════════════════════════════════════

if (USE_CLUSTER && cluster.isPrimary) {
  startMaster();
} else if (USE_CLUSTER) {
  await import('./relay-worker.mjs');
} else {
  startSingleProcess();
}
