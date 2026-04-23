/**
 * lark-event-handler.mjs
 * Parses incoming Lark webhook message events and enqueues them for batch processing.
 */

import { parsePostContent, extractCardText } from './lib/message-parser.mjs';
import { downloadImage, downloadResource, getParentMessageContent, getMergeForwardContent } from './lib/lark-reader.mjs';
import { log, logError } from './lib/logger.mjs';

const CONTROL_MESSAGES = new Set(['NO', 'NO_REPLY', 'HEARTBEAT_OK']);

// ─── Main Event Handler ───────────────────────────────────────────

async function handleMessageEvent(event, messageQueue) {
  try {
    log('[RAW_EVENT]', JSON.stringify(event, null, 2));

    const message   = event?.message;
    const sender    = event?.sender;
    const chatId    = message?.chat_id;
    const messageId = message?.message_id;
    const msgType   = message?.message_type;
    const chatType  = message?.chat_type;
    const rootId    = message?.root_id   || '';
    const parentId  = message?.parent_id || '';
    const threadId  = message?.thread_id || '';

    const senderType   = sender?.sender_type || '';
    const senderUserId = sender?.sender_id?.user_id || '';

    if (!chatId) return;
    if (senderType === 'app') return;

    log('[MSG]', msgType, messageId, 'from', senderUserId, threadId ? `thread:${threadId.slice(0, 8)}` : '');
    log('[THREAD_DEBUG] rootId:', rootId, 'parentId:', parentId, 'threadId:', threadId);

    // ─── Parse message content ────────────────────────────────────
    let text = '';
    let images = [];

    if (msgType === 'text') {
      try { text = (JSON.parse(message.content)?.text || '').trim(); } catch { return; }

    } else if (msgType === 'post') {
      const { texts, imageKeys } = parsePostContent(message.content);
      text = texts.join(' ').trim();
      for (const key of imageKeys) {
        const img = await downloadImage(key, messageId);
        if (img) images.push(img);
      }
      log('[POST] text:', text.substring(0, 50), 'images:', images.length);

    } else if (msgType === 'image') {
      try {
        const { image_key: key } = JSON.parse(message.content || '{}');
        if (key) {
          const img = await downloadImage(key, messageId);
          if (img) images.push(img);
        }
      } catch (e) { logError('[ERROR] Image parse error:', e.message); }
      text = '[User sent an image]';

    } else if (msgType === 'file') {
      let fileName = 'unknown';
      try {
        const { file_key: key, file_name: name } = JSON.parse(message.content || '{}');
        fileName = name || 'unknown';
        if (key) {
          const file = await downloadResource(key, messageId, 'file', fileName);
          if (file) images.push(file);
        }
      } catch (e) { logError('[ERROR] File parse error:', e.message); }
      text = `[User sent a file: ${fileName}]`;

    } else if (msgType === 'interactive') {
      try {
        const cardContent = JSON.parse(message.content || '{}');
        log('[CARD] Raw card structure:', JSON.stringify(cardContent, null, 2));
        text = extractCardText(cardContent);
        log('[CARD] Extracted text:', text);
      } catch (e) {
        logError('[ERROR] Card parse error:', e.message);
        text = '[User sent a card message - parse error]';
      }

    } else if (msgType === 'merge_forward') {
      try {
        log('[MERGE_FORWARD] Detected merged forward message:', messageId);
        const subMessages = await getMergeForwardContent(messageId);
        text = subMessages?.length
          ? `[User forwarded ${subMessages.length} messages]\n\n`
            + subMessages.map((m, i) => `--- Message ${i + 1} ---\n${m.text || '[Empty]'}`).join('\n\n')
          : '[User forwarded messages - unable to retrieve content]';
        if (subMessages?.length) log('[MERGE_FORWARD] Extracted', subMessages.length, 'sub-messages');
      } catch (e) {
        logError('[ERROR] Merge forward parse error:', e.message);
        text = '[User forwarded messages - parse error]';
      }

    } else {
      log('[SKIP] Unsupported message type:', msgType);
      return;
    }

    if (!text && images.length === 0) return;

    log('[SENDER]', senderUserId);

    // ─── Mention detection (all chat types) ───────────────────────
    let botMentioned = false;
    const mentions = Array.isArray(message?.mentions) ? message.mentions : [];
    const appOpenId = process.env.LARK_APP_OPEN_ID || '';

    if (mentions.length > 0) {
      botMentioned = mentions.some(m => m.id?.open_id === appOpenId);
      mentions.forEach((m, i) => {
        const isBot = m.id?.open_id === appOpenId;
        const openId = m.id?.open_id || '';
        const name   = isBot ? (process.env.LARK_BOT_NAME || 'YOU') : (m.name || m.id?.user_id || 'unknown');
        const replacement = `<at open_id='${openId}'>${name}</at>`;
        text = text.replace(`@_user_${i + 1}`, replacement);
      });
      text = text.replace(/\s+/g, ' ').trim();
    }

    // ─── Group chat filter ─────────────────────────────────────────
    if (chatType === 'group') {
      if (!botMentioned && images.length === 0 && (!text || CONTROL_MESSAGES.has(text))) return;
    }

    // ─── Build queue entry ────────────────────────────────────────
    const agentId    = process.env.OPENCLAW_AGENT_ID || 'main';
    const sessionKey = `agent:${agentId}:lark:${chatId}`;
    const messageText = text || '[No text content]';

    log('[MSG_DATA]', chatType, `(${senderUserId})`, 'text:', messageText.substring(0, 50),
      'attachments:', images.length, rootId ? '[in-thread]' : '');
    log('[SESSION]', sessionKey);

    let parentContent = null;
    if (parentId) {
      log('[PARENT] Fetching parent message:', parentId);
      parentContent = await getParentMessageContent(parentId);
      if (parentContent) log('[PARENT] Retrieved:', parentContent.substring(0, 100));
    }

    const mentionsOthers = mentions.length > 0 && !botMentioned;

    messageQueue.add(sessionKey, {
      messageId,
      chatId,
      chatType,
      threadId,
      rootId,
      parentId,
      parentContent,
      botMentioned,
      mentionsOthers,
      text: messageText,
      originalText: text || '[No text content]',
      attachments: images.map(img => ({ mimeType: img.contentType, content: img.base64 })),
      timestamp: Date.now(),
      rawEvent: event,
    });

  } catch (e) {
    logError('[ERROR] handleMessageEvent:', e);
  }
}

export { handleMessageEvent };
