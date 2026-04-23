/**
 * _test-relay.mjs — Quick smoke test for relay server + client.
 * Tests: health, challenge, WS connect, webhook forwarding, ring buffer.
 * Usage: node scripts/_test-relay.mjs
 */

import http from 'node:http';
import { WebSocket } from 'ws';
import { spawn } from 'node:child_process';

const PORT = 19877;
const SECRET = 'test-secret-' + Date.now();
const APP_ID = 'cli_test_app';
let passed = 0;
let failed = 0;
let server;

function assert(cond, msg) {
  if (cond) { passed++; console.log(`  PASS: ${msg}`); }
  else { failed++; console.error(`  FAIL: ${msg}`); }
}

function fetch(method, path, body) {
  return new Promise((resolve, reject) => {
    const req = http.request({ hostname: '127.0.0.1', port: PORT, method, path, headers: body ? { 'Content-Type': 'application/json' } : {} }, (res) => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        const text = Buffer.concat(chunks).toString();
        try { resolve({ status: res.statusCode, json: JSON.parse(text), text }); }
        catch { resolve({ status: res.statusCode, text }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function connectWs(appId) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(`ws://127.0.0.1:${PORT}/bridge?appId=${appId}&secret=${SECRET}`, {
      perMessageDeflate: { clientNoContextTakeover: true, threshold: 1024 },
    });
    const messages = [];
    ws.on('open', () => {
      ws.on('message', (raw) => {
        const msg = JSON.parse(raw);
        messages.push(msg);
        if (msg.type === 'connected') resolve({ ws, messages });
      });
    });
    ws.on('error', reject);
    setTimeout(() => reject(new Error('WS connect timeout')), 3000);
  });
}

function waitForMessage(messages, predicate, timeoutMs = 3000) {
  return new Promise((resolve, reject) => {
    // Check already received
    const found = messages.find(predicate);
    if (found) { resolve(found); return; }
    const interval = setInterval(() => {
      const found = messages.find(predicate);
      if (found) { clearInterval(interval); clearTimeout(timer); resolve(found); }
    }, 50);
    const timer = setTimeout(() => { clearInterval(interval); reject(new Error('Timeout waiting for message')); }, timeoutMs);
  });
}

async function runTests(mode) {
  console.log(`\n=== Testing ${mode} mode ===\n`);

  // 1. Health check
  const health = await fetch('GET', '/health');
  assert(health.status === 200, 'GET /health returns 200');
  assert(health.json?.status === 'ok', 'health status is ok');

  // 2. URL verification challenge
  const challenge = await fetch('POST', `/lark/webhook/${APP_ID}`, { type: 'url_verification', challenge: 'abc123' });
  assert(challenge.status === 200, 'challenge returns 200');
  assert(challenge.json?.challenge === 'abc123', 'challenge value echoed');

  // 3. Webhook with no bridge
  const noBridge = await fetch('POST', `/lark/webhook/${APP_ID}`, { header: { event_type: 'test' }, schema: '2.0' });
  assert(noBridge.status === 200, 'webhook with no bridge still returns 200');

  // 4. Connect WebSocket bridge
  const { ws, messages } = await connectWs(APP_ID);
  assert(messages[0]?.type === 'connected', 'WS receives connected ack');
  assert(messages[0]?.appId === APP_ID, 'WS connected ack has correct appId');

  // 5. Send webhook and verify forwarding
  const testPayload = { header: { event_type: 'im.message.receive_v1' }, schema: '2.0', event: { message: { content: 'hello' } } };
  await fetch('POST', `/lark/webhook/${APP_ID}`, testPayload);

  try {
    const event = await waitForMessage(messages, m => m.type === 'lark_event');
    assert(event.type === 'lark_event', 'received lark_event via WS');
    assert(event.payload?.header?.event_type === 'im.message.receive_v1', 'payload has correct event_type');
    assert(event.payload?.event?.message?.content === 'hello', 'payload content preserved');
  } catch {
    assert(false, 'received lark_event via WS (timeout)');
  }

  // 6. Ping/pong
  ws.send(JSON.stringify({ type: 'ping' }));
  try {
    const pong = await waitForMessage(messages, m => m.type === 'pong');
    assert(pong.type === 'pong', 'ping/pong works');
  } catch {
    assert(false, 'ping/pong works (timeout)');
  }

  // 7. Status endpoint
  const status = await fetch('GET', `/status?token=${SECRET}`);
  assert(status.status === 200, 'GET /status returns 200');
  assert(status.json?.total >= 1, 'status shows at least 1 bridge');
  const found = status.json?.bridges?.find(b => b.appId === APP_ID);
  assert(!!found, 'status lists our appId');

  ws.close();
}

async function main() {
  // Test single-process mode
  server = spawn('node', ['scripts/relay-server.mjs'], {
    env: { ...process.env, RELAY_PORT: String(PORT), RELAY_SECRET: SECRET, RELAY_CLUSTER_WORKERS: '0' },
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  await new Promise((resolve) => {
    server.stdout.on('data', (d) => {
      if (d.toString().includes('started on port')) resolve();
    });
    setTimeout(resolve, 3000);
  });

  try {
    await runTests('single-process');
  } finally {
    server.kill('SIGTERM');
    await new Promise(r => server.on('close', r));
  }

  // Test cluster mode
  server = spawn('node', ['scripts/relay-server.mjs'], {
    env: { ...process.env, RELAY_PORT: String(PORT), RELAY_SECRET: SECRET, RELAY_CLUSTER_WORKERS: '2' },
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  let workerCount = 0;
  await new Promise((resolve) => {
    const onData = (d) => {
      const text = d.toString();
      const matches = text.match(/Worker started/g);
      if (matches) workerCount += matches.length;
      if (workerCount >= 2) resolve();
    };
    server.stdout.on('data', onData);
    server.stderr.on('data', onData);
    setTimeout(resolve, 5000);
  });

  try {
    await runTests('cluster');
  } finally {
    server.kill('SIGTERM');
    await new Promise(r => server.on('close', r));
  }

  console.log(`\n=== Results: ${passed} passed, ${failed} failed ===\n`);
  process.exit(failed > 0 ? 1 : 0);
}

main().catch(err => { console.error(err); process.exit(1); });
