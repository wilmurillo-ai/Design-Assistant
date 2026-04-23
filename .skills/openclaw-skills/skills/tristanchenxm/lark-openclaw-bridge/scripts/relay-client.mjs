/**
 * relay-client.mjs
 * WebSocket client — connects the local bridge to the central relay server.
 *
 * Usage (called by server.mjs when RELAY_SERVER_URL is set):
 *   import { startRelayClient } from './relay-client.mjs';
 *   startRelayClient({ appId, secret, relayUrl, onEvent });
 *
 * Env (read by server.mjs, passed in as options):
 *   RELAY_SERVER_URL  — e.g. ws://relay.atomecorp.net:8080/bridge
 *   RELAY_SECRET      — shared secret
 */

import { WebSocket } from 'ws';

const RECONNECT_INITIAL_MS = 2_000;
const RECONNECT_MAX_MS     = 60_000;
const PING_INTERVAL_MS     = 30_000;

function log(...args)      { console.log(new Date().toISOString(), '[RELAY-CLIENT]', ...args); }
function logError(...args) { console.error(new Date().toISOString(), '[RELAY-CLIENT][ERROR]', ...args); }

/**
 * @param {object} opts
 * @param {string} opts.appId       — Lark App ID (used as bridge identifier)
 * @param {string} opts.secret      — shared secret matching relay server's RELAY_SECRET
 * @param {string} opts.relayUrl    — WebSocket base URL, e.g. ws://relay.atomecorp.net:8080/bridge
 * @param {(event: object) => void} opts.onEvent  — called with each lark_event payload
 * @returns {{ stop: () => void }}
 */
export function startRelayClient({ appId, secret, relayUrl, onEvent }) {
  let ws         = null;
  let stopped    = false;
  let pingTimer  = null;
  let retryDelay = RECONNECT_INITIAL_MS;
  let retryTimer = null;

  function buildUrl() {
    const url = new URL(relayUrl);
    url.searchParams.set('appId', appId);
    if (secret) url.searchParams.set('secret', secret);
    return url.toString();
  }

  function connect() {
    if (stopped) return;
    const url = buildUrl();
    log(`Connecting to relay: ${relayUrl} (appId=${appId})`);

    ws = new WebSocket(url, {
      perMessageDeflate: { clientNoContextTakeover: true, threshold: 1024 },
    });

    ws.on('open', () => {
      log('Connected to relay');
      retryDelay = RECONNECT_INITIAL_MS;

      // Heartbeat
      pingTimer = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, PING_INTERVAL_MS);
    });

    ws.on('message', (raw) => {
      let msg;
      try { msg = JSON.parse(raw); } catch { return; }

      if (msg.type === 'connected') {
        log(`Registered as appId=${msg.appId}`);
        return;
      }
      if (msg.type === 'pong') return;

      if (msg.type === 'lark_event') {
        try {
          onEvent(msg.payload);
        } catch (err) {
          logError('onEvent handler threw:', err.message);
        }
        return;
      }

      log('Unknown message type:', msg.type);
    });

    ws.on('close', (code, reason) => {
      clearInterval(pingTimer);
      pingTimer = null;
      if (stopped) return;

      const reasonStr = reason?.toString() || '';
      log(`Disconnected (code=${code} reason=${reasonStr}). Reconnecting in ${retryDelay}ms…`);

      retryTimer = setTimeout(() => {
        retryDelay = Math.min(retryDelay * 2, RECONNECT_MAX_MS);
        connect();
      }, retryDelay);
    });

    ws.on('error', (err) => {
      logError('WebSocket error:', err.message);
      // 'close' event will fire after error, triggering reconnect
    });
  }

  connect();

  return {
    stop() {
      stopped = true;
      clearInterval(pingTimer);
      clearTimeout(retryTimer);
      ws?.close();
    },
  };
}
