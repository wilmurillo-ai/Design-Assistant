/**
 * lark-reader.mjs
 * All read operations against the Lark API:
 *   - Media download (images, files)
 *   - Message content fetching (parent messages, merge-forward)
 *   - Chat / user info (for HTTP endpoints and session injection)
 */

import fs from 'node:fs';
import os from 'node:os';
import fetch from 'node-fetch';
import { getTenantToken, getLarkClient } from './lark-auth.mjs';
import { parsePostContent, extractCardText } from './message-parser.mjs';
import { log, logError } from './logger.mjs';

function tempFileDir() {
  return `${os.homedir()}/clawd/tmp/lark-files/`;
}

// ─── Media Download ───────────────────────────────────────────────

async function downloadResource(resourceKey, messageId, type = 'image', fileName = null) {
  try {
    const token = await getTenantToken();
    if (!token) return null;

    const url = `https://open.larksuite.com/open-apis/im/v1/messages/${messageId}/resources/${resourceKey}?type=${type}`;
    const res = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });

    if (!res.ok) {
      logError(`[WARN] ${type} download failed:`, res.status, resourceKey);
      return null;
    }

    const buffer = Buffer.from(await res.arrayBuffer());
    const base64 = buffer.toString('base64');
    const contentType = res.headers.get('content-type')
      || (type === 'image' ? 'image/png' : 'application/octet-stream');

    const fileExt = fileName?.split('.').pop() || contentType.split('/')[1] || 'bin';
    const safeFileName = fileName || `${messageId}_${resourceKey.slice(0, 8)}.${fileExt}`;
    const dir = tempFileDir();
    await fs.promises.mkdir(dir, { recursive: true });
    const filePath = `${dir}${safeFileName}`;

    await fs.promises.writeFile(filePath, buffer);
    log(`[DOWNLOAD] Saved ${type} to: ${filePath}`);

    return { base64, contentType, filePath, fileName: safeFileName };
  } catch (e) {
    logError(`[ERROR] ${type} download error:`, e.message);
    return null;
  }
}

async function downloadImage(imageKey, messageId) {
  return downloadResource(imageKey, messageId, 'image');
}

// ─── Message Content Fetching ─────────────────────────────────────

async function getParentMessageContent(messageId) {
  try {
    const client = getLarkClient();
    const result = await client.im.v1.message.get({ path: { message_id: messageId } });

    const message = result.data?.items?.[0];
    if (!message) {
      log('[PARENT] Message not found:', messageId);
      return null;
    }

    const { msg_type: msgType, body } = message;

    if (msgType === 'text') {
      const content = JSON.parse(body.content || '{}');
      return content.text || null;
    }

    if (msgType === 'post') {
      const content = JSON.parse(body.content || '{}');
      const texts = [];
      for (const line of content.zh_cn?.content || []) {
        for (const el of line) {
          if (el.tag === 'text' && el.text) texts.push(el.text);
        }
      }
      return texts.join(' ') || null;
    }

    if (msgType === 'interactive') {
      const content = JSON.parse(body.content || '{}');
      return extractCardText(content) || null;
    }

    return `[${msgType} message]`;
  } catch (e) {
    log('[PARENT] Failed to get message:', messageId, e.message);
    return null;
  }
}

async function getMergeForwardContent(messageId) {
  try {
    const token = await getTenantToken();
    if (!token) return null;

    const res = await fetch(`https://open.larksuite.com/open-apis/im/v1/messages/${messageId}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });

    if (!res.ok) {
      logError('[WARN] Get message failed:', res.status, messageId);
      return null;
    }

    const data = await res.json();
    if (data.code !== 0) {
      logError('[WARN] Get message error:', data.msg || data.code);
      return null;
    }

    const items = data.data?.items;
    if (!Array.isArray(items) || items.length === 0) {
      log('[WARN] No sub-messages found in merge_forward');
      return [];
    }

    const subMessages = items.map(item => {
      const { msg_type: msgType } = item;
      let text = '';

      if (msgType === 'text') {
        try { text = JSON.parse(item.body?.content || '{}').text || ''; } catch {}
      } else if (msgType === 'post') {
        const { texts } = parsePostContent(item.body?.content || '{}');
        text = texts.join(' ');
      } else if (msgType === 'interactive') {
        try { text = extractCardText(JSON.parse(item.body?.content || '{}')); } catch { text = '[Card]'; }
      } else {
        text = msgType === 'image' ? '[Image]' : `[${msgType}]`;
      }

      return {
        messageId: item.message_id,
        msgType,
        text,
        sender: item.sender?.sender_id?.user_id || item.sender?.sender_id?.open_id || 'unknown',
        createTime: item.create_time,
      };
    });

    log('[MERGE_FORWARD] Retrieved', subMessages.length, 'sub-messages');
    return subMessages;
  } catch (e) {
    logError('[ERROR] Get merge forward content error:', e.message);
    return null;
  }
}

// ─── Chat / User Info ─────────────────────────────────────────────

async function getChatInfo(chatId) {
  const token = await getTenantToken();
  const res = await fetch(
    `https://open.larksuite.com/open-apis/im/v1/chats/${chatId}?user_id_type=open_id`,
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
  const data = await res.json();
  if (data.code === 0) return data.data;
  throw new Error(`Failed to get chat info: ${data.msg}`);
}

async function getChatMembers(chatId) {
  const token = await getTenantToken();
  const members = [];
  let pageToken = '';

  do {
    const url = `https://open.larksuite.com/open-apis/im/v1/chats/${chatId}/members`
      + `?member_id_type=open_id&page_size=50${pageToken ? `&page_token=${pageToken}` : ''}`;
    const res = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
    const data = await res.json();
    if (data.code !== 0) throw new Error(`Failed to get members: ${data.msg}`);
    members.push(...data.data.items);
    pageToken = data.data.page_token || '';
  } while (pageToken);

  return members;
}

async function getUserInfo(openId) {
  const token = await getTenantToken();
  const res = await fetch(
    `https://open.larksuite.com/open-apis/contact/v3/users/${openId}`
      + `?user_id_type=open_id&department_id_type=open_department_id`,
    { headers: { 'Authorization': `Bearer ${token}` } },
  );
  const data = await res.json();
  if (data.code === 0) return data.data.user;
  throw new Error(`Failed to get user info: ${data.msg}`);
}

const chatLabelCache = new Map(); // chatId -> { label, expiresAt }
const CHAT_LABEL_TTL = 24 * 60 * 60 * 1000;

async function getChatLabel(chatId) {
  const cached = chatLabelCache.get(chatId);
  if (cached && cached.expiresAt > Date.now()) return cached.label;

  try {
    const chatInfo = await getChatInfo(chatId);
    let label;
    if (chatInfo.chat_mode === 'p2p') {
      const botOpenId = process.env.LARK_APP_OPEN_ID || '';
      const members = await getChatMembers(chatId);
      const other = members.find(m => m.member_id !== botOpenId);
      if (other) {
        try {
          const userInfo = await getUserInfo(other.member_id);
          label = userInfo.name || userInfo.en_name || other.name || chatId;
        } catch {
          label = other.name || chatId;
        }
      } else {
        label = chatId;
      }
    } else {
      label = chatInfo.name || chatId;
    }
    chatLabelCache.set(chatId, { label, expiresAt: Date.now() + CHAT_LABEL_TTL });
    return label;
  } catch (e) {
    logError('[WARN] getChatLabel failed:', e.message);
    return chatId;
  }
}

async function getSessionInfo(sessionKey) {
  const parts = sessionKey.split(':');
  const chatId = parts[parts.length - 1];

  if (!chatId.startsWith('oc_') && !chatId.startsWith('ou_')) {
    throw new Error('Invalid sessionKey: expected Lark chat/user ID');
  }

  const chatInfo = await getChatInfo(chatId);
  const members = await getChatMembers(chatId);

  let userName = null;
  if (chatInfo.chat_mode === 'p2p') {
    const botOpenId = process.env.LARK_APP_OPEN_ID || '';
    const other = members.find(m => m.member_id !== botOpenId);
    if (other) {
      try {
        const userInfo = await getUserInfo(other.member_id);
        userName = userInfo.name || userInfo.en_name || other.name;
      } catch (err) {
        logError(`[WARN] Failed to fetch user name: ${err.message}`);
        userName = other.name || null;
      }
    }
  }

  return { sessionKey, chatId, chatInfo, members, userName };
}

export {
  downloadResource,
  downloadImage,
  getParentMessageContent,
  getMergeForwardContent,
  getChatInfo,
  getChatLabel,
  getSessionInfo,
};
