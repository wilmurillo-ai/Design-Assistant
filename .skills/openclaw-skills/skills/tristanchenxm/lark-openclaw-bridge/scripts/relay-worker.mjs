/**
 * relay-worker.mjs
 * Cluster worker — owns WebSocket connections, handles IPC from master.
 *
 * This file is dynamically imported by relay-server.mjs when running in
 * cluster mode (RELAY_CLUSTER_WORKERS > 1). It should NOT be run directly.
 */

import http from 'node:http';
import { WebSocketServer } from 'ws';

const perMessageDeflateOpts = {
  zlibDeflateOptions: { chunkSize: 1024, memLevel: 7, level: 3 },
  zlibInflateOptions: { chunkSize: 10 * 1024 },
  threshold: 1024,
  concurrencyLimit: 10,
  serverNoContextTakeover: true,
};

// ─── Worker logging (sends to master for ring buffer + SSE) ──────

function log(...args) {
  const msg = args.join(' ');
  console.log(new Date().toISOString(), `[RELAY][W${process.pid}]`, msg);
  process.send?.({ type: 'log', level: 'info', msg: `[W${process.pid}] ${msg}` });
}
function logError(...args) {
  const msg = args.join(' ');
  console.error(new Date().toISOString(), `[RELAY][W${process.pid}][ERROR]`, msg);
  process.send?.({ type: 'log', level: 'error', msg: `[W${process.pid}] ${msg}` });
}

// ─── Bridge Registry ─────────────────────────────────────────────

/** @type {Map<string, { ws: import('ws').WebSocket, connectedAt: Date, appId: string }>} */
const bridges = new Map();

// ─── noServer WebSocket Server ───────────────────────────────────

const wss = new WebSocketServer({ noServer: true, perMessageDeflate: perMessageDeflateOpts });

wss.on('connection', (ws, req) => {
  const url   = new URL(req.url, 'http://localhost');
  const appId = url.searchParams.get('appId');

  // Auth already validated by master; appId guaranteed present
  if (bridges.has(appId)) {
    const prev = bridges.get(appId);
    log(`[RECONNECT] appId=${appId} — closing old connection`);
    prev.ws.close(4010, 'Replaced by new connection');
  }

  const entry = { ws, appId, connectedAt: new Date() };
  bridges.set(appId, entry);
  process.send?.({ type: 'bridge_registered', appId });
  log(`[CONNECTED] appId=${appId} from ${req.remoteAddress || req.socket?.remoteAddress || 'unknown'} (total: ${bridges.size})`);

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
      process.send?.({ type: 'bridge_unregistered', appId });
      log(`[DISCONNECTED] appId=${appId} code=${code} reason=${reason?.toString() || ''} (total: ${bridges.size})`);
    }
  });

  ws.on('error', (err) => {
    logError(`[WS ERROR] appId=${appId}:`, err.message);
  });
});

// ─── IPC Message Handler ─────────────────────────────────────────

process.on('message', (msg, socket) => {
  switch (msg.type) {
    case 'ws_upgrade':
      handleUpgrade(msg, socket);
      break;
    case 'webhook_forward':
      forwardWebhook(msg.appId, msg.rawBody);
      break;
    case 'status_request':
      handleStatusRequest(msg.requestId);
      break;
    case 'shutdown':
      gracefulShutdown();
      break;
  }
});

function handleUpgrade(msg, socket) {
  if (!socket || socket.destroyed) return;
  const req = new http.IncomingMessage(socket);
  req.method = 'GET';
  req.headers = msg.headers;
  req.url = msg.url;
  Object.defineProperty(req, 'remoteAddress', { value: msg.remoteAddress });
  const head = msg.head ? Buffer.from(msg.head, 'base64') : Buffer.alloc(0);
  wss.handleUpgrade(req, socket, head, (ws) => {
    wss.emit('connection', ws, req);
  });
}

function forwardWebhook(appId, rawBody) {
  const bridge = bridges.get(appId);
  if (!bridge) {
    process.send?.({ type: 'webhook_no_bridge', appId });
    return;
  }
  try {
    let data;
    try { data = JSON.parse(rawBody); } catch { return; }
    const eventType = data.header?.event_type || data.type || 'unknown';
    log(`[ROUTED] appId=${appId} event=${eventType} schema=${data.schema || 'v1'}`);
    bridge.ws.send('{"type":"lark_event","payload":' + rawBody + '}');
  } catch (err) {
    logError(`[SEND FAIL] appId=${appId}:`, err.message);
  }
}

function handleStatusRequest(requestId) {
  const bridgeList = [...bridges.entries()].map(([appId, b]) => ({
    appId,
    connectedAt: b.connectedAt.toISOString(),
    uptimeSeconds: Math.floor((Date.now() - b.connectedAt) / 1000),
    workerId: process.pid,
  }));
  process.send?.({ type: 'status_response', requestId, bridges: bridgeList });
}

function gracefulShutdown() {
  log('Worker shutting down…');
  for (const [, b] of bridges) {
    b.ws.close(1001, 'Server shutting down');
  }
  wss.close(() => {
    process.exit(0);
  });
}

log('Worker started');
