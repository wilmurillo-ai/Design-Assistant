/**
 * key-refresh.mjs
 * Detects arouter "api key is inactive" failures and transparently rotates
 * the local API key by calling POST /v1/token/refresh.
 *
 * Credentials are stored in two files that the openclaw CLI reads on every
 * invocation, so updating them takes effect on the next subprocess call:
 *   ~/.openclaw/agents/main/agent/auth-profiles.json  (key under profiles['arouter:default'].key)
 *   ~/.openclaw/agents/main/agent/models.json          (key under providers.arouter.apiKey)
 */

import fs from 'node:fs';
import os from 'node:os';

const HOME             = os.homedir();
const AUTH_PROFILES    = `${HOME}/.openclaw/agents/main/agent/auth-profiles.json`;
const MODELS_JSON      = `${HOME}/.openclaw/agents/main/agent/models.json`;

// Minimum interval between refresh attempts — prevents thundering-herd when
// several concurrent requests all fail with auth errors simultaneously.
const MIN_REFRESH_INTERVAL_MS = 30_000;

let _refreshing   = false;
let _lastRefreshAt = 0;

/**
 * Reads the current arouter API key and base URL from local openclaw config.
 * @returns {{ key: string|null, baseUrl: string|null }}
 */
export function readArouterCredentials() {
  let key = null;
  try {
    const p = JSON.parse(fs.readFileSync(AUTH_PROFILES, 'utf8'));
    key = p?.profiles?.['arouter:default']?.key ?? null;
  } catch { /* file missing or malformed — key stays null */ }

  let baseUrl = null;
  try {
    const m = JSON.parse(fs.readFileSync(MODELS_JSON, 'utf8'));
    baseUrl = m?.providers?.arouter?.baseUrl ?? null;
  } catch { /* same */ }

  return { key, baseUrl };
}

/**
 * Writes a fresh API key into both credential files.
 * @param {string} newKey
 */
export function writeNewKey(newKey) {
  // auth-profiles.json
  let authProfiles = { version: 1, profiles: {}, usageStats: {} };
  try { authProfiles = JSON.parse(fs.readFileSync(AUTH_PROFILES, 'utf8')); } catch {}
  authProfiles.profiles = authProfiles.profiles ?? {};
  authProfiles.profiles['arouter:default'] = {
    ...(authProfiles.profiles['arouter:default'] ?? {}),
    type: 'api_key',
    provider: 'arouter',
    key: newKey,
  };
  fs.writeFileSync(AUTH_PROFILES, JSON.stringify(authProfiles, null, 2));

  // models.json — apiKey field (used by openclaw CLI directly)
  let models = {};
  try { models = JSON.parse(fs.readFileSync(MODELS_JSON, 'utf8')); } catch {}
  models.providers = models.providers ?? {};
  models.providers.arouter = models.providers.arouter ?? {};
  models.providers.arouter.apiKey = newKey;
  fs.writeFileSync(MODELS_JSON, JSON.stringify(models, null, 2));
}

/**
 * Returns true if the subprocess output indicates an arouter auth failure.
 * @param {string} stdout
 * @param {string} stderr
 */
export function isAuthError(stdout, stderr) {
  const text = (stdout + '\n' + stderr).toLowerCase();
  return text.includes('api key is inactive')
      || text.includes('authentication_error')
      || text.includes('invalid api key');
}

/**
 * Attempts to rotate the arouter key by calling POST /v1/token/refresh.
 * Writes the new key to local config files on success.
 *
 * Returns true if the key was successfully refreshed, false otherwise.
 * Concurrent calls within MIN_REFRESH_INTERVAL_MS are debounced — the second
 * caller gets false immediately so only one refresh races to the server.
 *
 * @param {(msg: string) => void} log
 * @param {(msg: string) => void} logError
 * @returns {Promise<boolean>}
 */
export async function tryRefreshKey(log, logError) {
  const now = Date.now();
  if (_refreshing || now - _lastRefreshAt < MIN_REFRESH_INTERVAL_MS) {
    log('[KEY-REFRESH] Refresh already in progress or too recent — skipping');
    return false;
  }

  _refreshing    = true;
  _lastRefreshAt = now;

  try {
    const { key: currentKey, baseUrl } = readArouterCredentials();
    if (!currentKey) {
      logError('[KEY-REFRESH] No API key found in local config — cannot refresh');
      return false;
    }
    if (!baseUrl) {
      logError('[KEY-REFRESH] No arouter baseUrl found in models.json — cannot refresh');
      return false;
    }

    // baseUrl is e.g. "https://oc.atomecorp.net/arouter/v1"
    // refresh endpoint lives at the same base: /v1/token/refresh
    const refreshUrl = baseUrl.replace(/\/+$/, '') + '/token/refresh';
    log(`[KEY-REFRESH] Requesting new key from ${refreshUrl}`);

    const res = await fetch(refreshUrl, {
      method: 'POST',
      headers: { Authorization: `Bearer ${currentKey}` },
    });

    if (!res.ok) {
      logError(`[KEY-REFRESH] Server returned HTTP ${res.status}`);
      return false;
    }

    const data = await res.json();
    if (!data.api_key) {
      logError('[KEY-REFRESH] Response missing api_key field');
      return false;
    }

    writeNewKey(data.api_key);
    log(`[KEY-REFRESH] New key written to local config (app_id=${data.app_id ?? '?'})`);
    return true;
  } catch (err) {
    logError(`[KEY-REFRESH] Failed: ${err.message}`);
    return false;
  } finally {
    _refreshing = false;
  }
}
