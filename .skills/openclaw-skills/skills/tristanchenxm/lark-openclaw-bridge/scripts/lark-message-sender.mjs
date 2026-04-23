/**
 * lark-message-sender.mjs
 * Outbound Lark messaging: send text / image messages and inject into OpenClaw session.
 */

import fs, { createReadStream } from 'node:fs';
import FormData from 'form-data';
import fetch from 'node-fetch';
import { getTenantToken, getLarkClient } from './lib/lark-auth.mjs';
import { log, logError } from './lib/logger.mjs';

// ─── Reaction ─────────────────────────────────────────────────────

async function addReaction(messageId) {
  try {
    await getLarkClient().im.v1.messageReaction.create({
      path: { message_id: messageId },
      data: { reaction_type: { emoji_type: 'OnIt' } },
    });
    log('[REACTION] Added reaction to', messageId);
  } catch (e) {
    logError('[WARN] Failed to add reaction:', e.message, e.response?.data || '');
  }
}

// ─── Image Upload ─────────────────────────────────────────────────

async function uploadImage(filePath, token) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  const formData = new FormData();
  formData.append('image_type', 'message');
  formData.append('image', createReadStream(filePath));

  const response = await fetch('https://open.larksuite.com/open-apis/im/v1/images', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, ...formData.getHeaders() },
    body: formData,
  });

  const data = await response.json();
  if (data.code !== 0) throw new Error(`Upload failed: ${data.msg || 'Unknown error'}`);
  return data.data.image_key;
}

// ─── Send Message ─────────────────────────────────────────────────

async function sendMessage(chatId, text, msgType = 'text', imageKey = null, threadInfo = {}, inject = true) {
  const { threadId, rootId, parentId, botMentioned, chatType, replyToId } = threadInfo;
  // Priority: threadId > quote-reply (group: mentioned/parentId; p2p: parentId) > main chat
  const isThreadReply = !!threadId;
  const isGroup = chatType === 'group';
  const shouldQuoteReply = !isThreadReply && !!replyToId
    && (isGroup ? (botMentioned || !!parentId) : !!parentId);
  log('[SENDER] Sending to', chatId, 'type:', msgType,
    isThreadReply ? `[thread:${threadId.slice(0, 8)}]` : shouldQuoteReply ? `[quote:${replyToId.slice(0, 8)}]` : '');

  const token = await getTenantToken();
  if (!token) throw new Error('Failed to get tenant token');

  const receiveIdType = chatId.startsWith('ou_') ? 'open_id' : 'chat_id';
  const messageBody = msgType === 'image' && imageKey
    ? { receive_id: chatId, msg_type: 'image', content: JSON.stringify({ image_key: imageKey }) }
    : { receive_id: chatId, msg_type: 'text', content: JSON.stringify({ text }) };

  let larkResponse;

  if (isThreadReply) {
    log('[SENDER] Replying in thread, root_id:', rootId);
    const replyData = { ...messageBody, reply_in_thread: true };
    delete replyData.receive_id;
    larkResponse = await fetch(
      `https://open.larksuite.com/open-apis/im/v1/messages/${rootId}/reply`,
      { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(replyData) },
    );
  } else if (shouldQuoteReply) {
    log('[SENDER] Quote-reply to message:', replyToId);
    const replyData = { ...messageBody };
    delete replyData.receive_id;
    larkResponse = await fetch(
      `https://open.larksuite.com/open-apis/im/v1/messages/${replyToId}/reply`,
      { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(replyData) },
    );
  } else {
    larkResponse = await fetch(
      `https://open.larksuite.com/open-apis/im/v1/messages?receive_id_type=${receiveIdType}`,
      { method: 'POST', headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }, body: JSON.stringify(messageBody) },
    );
  }

  const larkData = await larkResponse.json();
  if (larkData.code !== 0) throw new Error(`Lark API error: ${larkData.msg || larkData.code}`);

  const messageId = larkData.data.message_id;
  log('[SENDER] Lark message sent:', messageId);

  if (!inject) return { larkMessageId: messageId, injected: false };

  // Inject into OpenClaw session so the agent knows what was sent
  const resolvedChatId = larkData.data.chat_id || chatId;
  if (resolvedChatId !== chatId) log('[SENDER] Resolved ou_xxx to chat_id:', resolvedChatId);

  const agentId = process.env.OPENCLAW_AGENT_ID || 'main';
  const sessionKey = `agent:${agentId}:lark:${resolvedChatId}`;

  try {
    const { execSync } = await import('node:child_process');
    const escaped = JSON.stringify({ sessionKey, message: text }).replace(/'/g, "'\\''");
    execSync(
      `openclaw gateway call chat.inject --params '${escaped}'`,
      { timeout: 5000, stdio: 'pipe' },
    );
    log('[SENDER] Injected into OpenClaw session:', sessionKey);
    return { larkMessageId: messageId, injected: true };
  } catch (injectErr) {
    logError('[SENDER] Failed to inject into OpenClaw:', injectErr.message);
    return { larkMessageId: messageId, injected: false, error: injectErr.message };
  }
}

// ─── Send Image ───────────────────────────────────────────────────

async function sendImage(chatId, imagePath, caption = '') {
  log('[SENDER] Uploading image for', chatId);
  const token = await getTenantToken();
  if (!token) throw new Error('Failed to get tenant token');

  const imageKey = await uploadImage(imagePath, token);
  log('[SENDER] Image uploaded, key:', imageKey);

  return sendMessage(chatId, caption || '[Image]', 'image', imageKey);
}

export { addReaction, uploadImage, sendMessage, sendImage };
