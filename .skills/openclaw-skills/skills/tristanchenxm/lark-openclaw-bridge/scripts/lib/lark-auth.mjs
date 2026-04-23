import * as Lark from '@larksuiteoapi/node-sdk';
import fetch from 'node-fetch';
import { logError } from './logger.mjs';

// ─── Token Cache ──────────────────────────────────────────────────

let tokenCache = { token: null, expireTime: 0 };

async function getTenantToken() {
  const now = Date.now() / 1000;
  if (tokenCache.token && tokenCache.expireTime > now) {
    return tokenCache.token;
  }

  try {
    const res = await fetch('https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_id: process.env.LARK_APP_ID,
        app_secret: process.env.LARK_APP_SECRET,
      }),
    });
    const data = await res.json();
    if (data.code === 0) {
      tokenCache.token = data.tenant_access_token;
      tokenCache.expireTime = now + data.expire - 60;
      return tokenCache.token;
    }
  } catch (e) {
    logError('[ERROR] Failed to get tenant token:', e.message);
  }
  return null;
}

// ─── Lark SDK Client (lazy singleton) ────────────────────────────

let _client = null;

function getLarkClient() {
  if (!_client) {
    _client = new Lark.Client({
      appId: process.env.LARK_APP_ID,
      appSecret: process.env.LARK_APP_SECRET,
      domain: Lark.Domain.Lark,
      appType: Lark.AppType.SelfBuild,
    });
  }
  return _client;
}

export { getTenantToken, getLarkClient };
