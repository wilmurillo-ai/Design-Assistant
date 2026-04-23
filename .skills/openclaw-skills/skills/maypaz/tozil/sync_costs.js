/**
 * Tozil cost sync for OpenClaw — pure Node.js, zero shell execution.
 *
 * Implements the same logic as the former sync_costs.sh:
 *   - Byte-offset tracking per session file (no duplicates, no mtime races)
 *   - Atomic offset commits (only after all API batches succeed)
 *   - Batched HTTPS POST to Tozil API
 *   - Input validation matching the original bash guards
 */

import {
  existsSync, mkdirSync, readdirSync, statSync,
  openSync, readSync, closeSync,
  readFileSync, writeFileSync,
} from 'node:fs';
import { join, basename, dirname } from 'node:path';
import { homedir } from 'node:os';
import { request as httpsRequest } from 'node:https';
import { URL } from 'node:url';

const HOME = homedir();

// Mirrors the bash regex guards exactly
const API_KEY_REGEX = /^tz_[A-Za-z0-9_-]{16,}$/;
const HTTPS_URL_REGEX = /^https:\/\/[a-zA-Z0-9._-]+/;
const SESSION_ID_REGEX = /^[A-Za-z0-9_-]+$/;

function getConfig() {
  return {
    apiKey:      process.env.TOZIL_API_KEY ?? '',
    baseUrl:     process.env.TOZIL_BASE_URL || 'https://agents.tozil.dev',
    sessionsDir: process.env.OPENCLAW_SESSIONS_DIR || join(HOME, '.openclaw', 'agents', 'main', 'sessions'),
    offsetsDir:  join(HOME, '.openclaw', 'hooks', 'tozil', 'offsets'),
    logFile:     join(HOME, '.openclaw', 'logs', 'tozil-sync.log'),
    batchSize:   Number(process.env.TOZIL_BATCH_SIZE) || 100,
  };
}

// ── Logging ──────────────────────────────────────────────────────────────────

function appendLog(logFile, message) {
  const ts = new Date().toISOString().replace('T', ' ').slice(0, 19);
  try {
    writeFileSync(logFile, `[${ts}] ${message}\n`, { flag: 'a' });
  } catch {
    // Never let logging break the sync
  }
}

// ── Filesystem helpers ────────────────────────────────────────────────────────

function ensureDir(dir) {
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
}

/**
 * Read bytes from `offset` to EOF without loading the full file into memory
 * upfront (mirrors `tail -c +N` semantics).
 */
function readFromOffset(filePath, offset) {
  const fd = openSync(filePath, 'r');
  try {
    const size = statSync(filePath).size;
    if (offset >= size) return '';
    const length = size - offset;
    const buf = Buffer.allocUnsafe(length);
    readSync(fd, buf, 0, length, offset);
    return buf.toString('utf8');
  } finally {
    closeSync(fd);
  }
}

// ── Event extraction ──────────────────────────────────────────────────────────

/**
 * Parse new content for lines that contain a usage entry with cost > 0.
 * Mirrors the jq `select(.message.usage and .message.usage.cost and ...)` filter.
 */
function extractEvents(content, sessionId) {
  const events = [];
  for (const line of content.split('\n')) {
    if (!line.includes('"usage"')) continue;
    let obj;
    try { obj = JSON.parse(line); } catch { continue; }
    const usage = obj?.message?.usage;
    const cost  = usage?.cost;
    if (!usage || !cost || !(cost.total > 0)) continue;
    events.push({
      timestamp:           obj.timestamp,
      model:               obj.message.model,
      provider:            obj.message.provider,
      input_tokens:        usage.input,
      output_tokens:       usage.output,
      cache_read_tokens:   usage.cacheRead  ?? 0,
      cache_write_tokens:  usage.cacheWrite ?? 0,
      total_cost_usd:      cost.total,
      cost_input:          cost.input,
      cost_output:         cost.output,
      cost_cache_read:     cost.cacheRead  ?? 0,
      cost_cache_write:    cost.cacheWrite ?? 0,
      session_id:          sessionId,
    });
  }
  return events;
}

// ── HTTPS ─────────────────────────────────────────────────────────────────────

/**
 * POST `body` as JSON. Retries on connection/timeout errors (not HTTP errors).
 * Enforces TLS 1.2+ and a 30 s hard timeout — mirrors curl flags.
 */
function httpsPost(urlString, body, apiKey, retries = 2, retryDelayMs = 3000) {
  return new Promise((resolve, reject) => {
    const attempt = (attemptsLeft) => {
      const parsed  = new URL(urlString);
      const payload = JSON.stringify(body);

      const req = httpsRequest({
        hostname: parsed.hostname,
        port:     parsed.port || 443,
        path:     parsed.pathname + parsed.search,
        method:   'POST',
        headers:  {
          'Content-Type':   'application/json',
          'Authorization':  `Bearer ${apiKey}`,
          'Content-Length': Buffer.byteLength(payload),
        },
        minVersion: 'TLSv1.2',
        timeout:    30_000,
      }, (res) => {
        let data = '';
        res.on('data', (chunk) => { data += chunk; });
        res.on('end',  ()      => resolve({ statusCode: res.statusCode, body: data }));
      });

      req.on('timeout', () => {
        req.destroy(new Error('Request timed out'));
      });

      req.on('error', (err) => {
        if (attemptsLeft > 0) {
          setTimeout(() => attempt(attemptsLeft - 1), retryDelayMs);
        } else {
          reject(err);
        }
      });

      req.write(payload);
      req.end();
    };

    attempt(retries);
  });
}

// ── Offset commit ─────────────────────────────────────────────────────────────

/**
 * Write staged offsets to their permanent location.
 * Called only after all batches succeed — ensures atomicity.
 */
function commitOffsets(offsetsDir, staged) {
  for (const [sessionId, offset] of staged) {
    try {
      writeFileSync(join(offsetsDir, `${sessionId}.offset`), String(offset));
    } catch {
      // Best-effort; next run will re-process and deduplicate via the API
    }
  }
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Run a full sync cycle. Returns `{ accepted, skipped }` on success.
 * Throws on configuration errors or API failures.
 */
export async function syncCosts() {
  const cfg = getConfig();

  // Validate — mirrors bash guard order
  if (!cfg.apiKey)                        throw new Error('TOZIL_API_KEY not set');
  if (!API_KEY_REGEX.test(cfg.apiKey))    throw new Error('Invalid TOZIL_API_KEY format (expected tz_ prefix + 16+ chars)');
  if (!HTTPS_URL_REGEX.test(cfg.baseUrl)) throw new Error(`TOZIL_BASE_URL must use HTTPS (got: ${cfg.baseUrl})`);
  if (!existsSync(cfg.sessionsDir))       throw new Error(`Sessions dir not found: ${cfg.sessionsDir}`);

  ensureDir(cfg.offsetsDir);
  ensureDir(dirname(cfg.logFile));

  const log = (msg) => appendLog(cfg.logFile, msg);

  log('Starting sync');

  // ── Collect new events using byte-offset tracking ─────────────────────────
  const allEvents    = [];
  const stagedOffsets = new Map(); // sessionId → new byte offset

  let filenames;
  try {
    filenames = readdirSync(cfg.sessionsDir).filter((f) => f.endsWith('.jsonl'));
  } catch (err) {
    throw new Error(`Cannot read sessions dir: ${cfg.sessionsDir} — ${err.message}`);
  }

  for (const filename of filenames) {
    if (filename.includes('.reset.')) continue;

    const sessionId = basename(filename, '.jsonl');

    if (!SESSION_ID_REGEX.test(sessionId)) {
      log(`Warning: Skipping file with unsafe session ID: ${sessionId}`);
      continue;
    }

    const filePath = join(cfg.sessionsDir, filename);

    let fileSize;
    try { fileSize = statSync(filePath).size; } catch { continue; }

    // Read committed offset (default 0)
    let currentOffset = 0;
    const offsetFile = join(cfg.offsetsDir, `${sessionId}.offset`);
    if (existsSync(offsetFile)) {
      try {
        const raw = readFileSync(offsetFile, 'utf8').trim();
        if (/^\d+$/.test(raw)) currentOffset = Number(raw);
      } catch { /* keep 0 */ }
    }

    if (currentOffset >= fileSize) continue; // No new bytes

    let newContent;
    try { newContent = readFromOffset(filePath, currentOffset); } catch { continue; }

    const events = extractEvents(newContent, sessionId);
    allEvents.push(...events);

    stagedOffsets.set(sessionId, fileSize);
  }

  if (allEvents.length === 0) {
    log('No new events found');
    commitOffsets(cfg.offsetsDir, stagedOffsets);
    return { accepted: 0, skipped: 0 };
  }

  log(`Found ${allEvents.length} events to sync`);

  // ── Send to Tozil API in batches ──────────────────────────────────────────
  const totalBatches  = Math.ceil(allEvents.length / cfg.batchSize);
  let   totalAccepted = 0;
  let   totalSkipped  = 0;

  for (let i = 0; i < allEvents.length; i += cfg.batchSize) {
    const batchNum = Math.floor(i / cfg.batchSize) + 1;
    const batch    = allEvents.slice(i, i + cfg.batchSize);

    let response;
    try {
      response = await httpsPost(
        `${cfg.baseUrl}/api/v1/track/bulk`,
        batch,
        cfg.apiKey,
      );
    } catch (err) {
      throw new Error(`Batch ${batchNum}/${totalBatches} failed: connection error — ${err.message}`);
    }

    if (response.statusCode === 200) {
      let parsed = {};
      try { parsed = JSON.parse(response.body); } catch { /* use defaults */ }
      const accepted = parsed.accepted ?? 0;
      const skipped  = parsed.skipped  ?? 0;
      totalAccepted += accepted;
      totalSkipped  += skipped;
      log(`Batch ${batchNum}/${totalBatches}: ${accepted} accepted, ${skipped} skipped`);
    } else {
      throw new Error(`Batch ${batchNum}/${totalBatches} failed (HTTP ${response.statusCode}): ${response.body}`);
    }
  }

  log(`Sync complete: ${totalAccepted} accepted, ${totalSkipped} skipped`);

  // Commit byte offsets only after every batch has succeeded
  commitOffsets(cfg.offsetsDir, stagedOffsets);

  return { accepted: totalAccepted, skipped: totalSkipped };
}
