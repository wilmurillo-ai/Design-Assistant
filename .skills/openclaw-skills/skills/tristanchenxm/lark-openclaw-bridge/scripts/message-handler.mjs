/**
 * message-handler.mjs
 * Batch message processing: combines queued Lark messages, calls OpenClaw gateway
 * asynchronously, and sends the reply back to Lark.
 */

import crypto from 'node:crypto';
import os from 'node:os';
import { sendMessage, addReaction } from './lark-message-sender.mjs';
import { combineBatchMessages } from './lib/message-formatter.mjs';
import { getChatLabel } from './lib/lark-reader.mjs';
import { log, logError } from './lib/logger.mjs';
import { isAuthError, tryRefreshKey } from './lib/key-refresh.mjs';

const CONTROL_MESSAGES = new Set(['NO', 'NO_REPLY', 'HEARTBEAT_OK']);

function uuid() { return crypto.randomUUID(); }

function openClawConfigPath() {
  const raw = process.env.OPENCLAW_CONFIG_PATH || '~/.openclaw/openclaw.json';
  return raw.replace(/^~/, os.homedir());
}

// ─── Multi-reply parser ────────────────────────────────────────────

function parseMultiReplies(text) {
  const replies = [];
  const parts = text.split(/\[REPLY\]:\s*/);
  for (const part of parts.slice(1)) {
    const newlineIdx = part.indexOf('\n');
    if (newlineIdx === -1) continue;
    const messageId = part.slice(0, newlineIdx).trim();
    const content = part.slice(newlineIdx).trim();
    if (messageId && content) replies.push({ messageId, content });
  }
  return replies;
}

// ─── OpenClaw Gateway ─────────────────────────────────────────────

async function askOpenClaw({ message, sessionKey, sessionLabel }, chatId, messageId, threadInfo = {}, messageMap = null, threadMap = null, _retried = false) {
  const { spawn } = await import('node:child_process');
  const params = { message, sessionKey, idempotencyKey: uuid(), ...(sessionLabel ? { label: sessionLabel } : {}) };
  const escaped = JSON.stringify(params).replace(/'/g, "'\\''");
  const cmd = `openclaw gateway call agent --params '${escaped}' --expect-final --json --timeout 600000`;

  log('[OPENCLAW] Starting for chat:', chatId);

  let completed = false;
  let result = '';
  let error = null;
  let stdout = '';
  let stderr = '';

  await new Promise(resolve => {
    const proc = spawn('sh', ['-c', cmd], {
      env: {
        ...process.env,
        OPENCLAW_CONFIG_PATH: openClawConfigPath(),
        PATH: process.env.PATH || '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin',
      },
    });

    proc.stdout.on('data', d => { stdout += d.toString(); });
    proc.stderr.on('data', d => { stderr += d.toString(); });

    // Add emoji reaction if still processing after 30s
    setTimeout(() => { if (!completed) addReaction(messageId); }, 30000);

    // Send message if still processing after 3 mins
    setTimeout(() => {
      if (!completed) sendMessage(chatId,
        '[System] The task is still running in the background — it may take longer than expected. You\'ll receive the result once it\'s done.',
        'text', null, threadInfo, false,
      ).catch(e => logError('[OPENCLAW] Failed to send timeout message:', e.message));
    }, 180000);

    proc.on('close', (code) => {
      completed = true;
      if (code === 0) {
        try {
          const lines = stdout.split('\n');
          const jsonStart = lines.findIndex(l => l.trim().startsWith('{'));
          if (jsonStart >= 0) {
            const response = JSON.parse(lines.slice(jsonStart).join('\n'));
            const payloads = response.result?.payloads || [];
            if (payloads.length > 0) result = payloads[payloads.length - 1]?.text || '';
          }
        } catch (e) {
          error = `Parse error: ${e.message}`;
          logError('[OPENCLAW] Parse error:', e.message);
        }
        log('[OPENCLAW] Raw result:', result || '(empty)');
      } else {
        error = `Process exited with code ${code}: ${stderr.substring(0, 200) || '(no stderr)'}`;
        logError('[OPENCLAW] Process failed, code:', code, 'stderr:', stderr.substring(0, 200));
        log('[OPENCLAW] Raw stdout:', stdout.substring(0, 500) || '(empty)');
      }
      resolve();
    });
  });

  // Auto-refresh: if the failure is an auth error and we haven't retried yet,
  // rotate the key and re-run the same request transparently.
  if (!_retried && isAuthError(stdout, stderr)) {
    logError('[OPENCLAW] Auth failure detected — attempting automatic key refresh...');
    const refreshed = await tryRefreshKey(log, logError);
    if (refreshed) {
      log('[OPENCLAW] Key refreshed — retrying request for chat:', chatId);
      return askOpenClaw({ message, sessionKey, sessionLabel }, chatId, messageId, threadInfo, messageMap, threadMap, true);
    }
    logError('[OPENCLAW] Key refresh failed — reporting error to user');
  }

  const trimmed = (result || '').trim();
  const isNoReply = !result
    || (result || '').trimEnd().endsWith('NO_REPLY')
    || CONTROL_MESSAGES.has(trimmed);

  if (result && !isNoReply) {
    // Try multi-reply format first
    const multiReplies = parseMultiReplies(result);
    if (multiReplies.length > 0 && (messageMap || threadMap)) {
      log('[OPENCLAW] Parsed', multiReplies.length, 'reply block(s)');
      for (const { messageId: replyId, content } of multiReplies) {
        const byMessage = messageMap?.get(replyId);
        const byThread  = threadMap?.get(replyId);
        if (byMessage) {
          const { chatId: msgChatId, chatType } = byMessage;
          await sendMessage(msgChatId, content, 'text', null, {
            chatType, replyToId: replyId, parentId: replyId,
          }, false).catch(e => logError('[OPENCLAW] Failed to send reply:', e.message));
        } else if (byThread) {
          const { chatId: msgChatId, threadId, rootId } = byThread;
          await sendMessage(msgChatId, content, 'text', null, {
            threadId, rootId,
          }, false).catch(e => logError('[OPENCLAW] Failed to send thread reply:', e.message));
        } else {
          logError('[OPENCLAW] Unknown id in [REPLY]:', replyId);
        }
      }
    } else {
      await sendMessage(chatId, result, 'text', null, threadInfo, false)
        .catch(e => logError('[OPENCLAW] Failed to send result:', e.message));
    }
  } else if (isNoReply && result) {
    log('[OPENCLAW] Not sending reply (NO_REPLY detected)');
  } else if (error) {
    const isTimeout = stderr.includes('gateway timeout');
    const errorMsg = isTimeout
      ? '[System] The task is taking too long to complete. Please wait a moment and ask for the result again. '
      : `[System] Task failed: ${error}`;
    await sendMessage(chatId, errorMsg, 'text', null, threadInfo, false)
      .catch(e => logError('[OPENCLAW] Failed to send error:', e.message));
  }

  log('[OPENCLAW] Process completed for chat:', chatId, 'success:', !error);
}

// ─── Batch Processor ─────────────────────────────────────────────

async function processBatchedMessages(sessionKey, batch) {
  if (batch.length === 0) return;

  const messageMap = new Map(batch.map(msg => [msg.messageId, msg]));
  const threadMap  = new Map(batch.filter(m => m.threadId).map(msg => [msg.threadId, msg]));
  let combinedMessage = combineBatchMessages(batch);

  if (batch.length > 1) {
    combinedMessage = `[Batch: ${batch.length} messages. Reply to any subset (or none) using this exact format:]
[REPLY]: <message_id>   ← quote-reply to a specific message
<reply content>

[REPLY]: <thread_id>    ← reply in thread
<reply content>

---
${combinedMessage}`;
  }

  log(`[BATCH] Combined ${batch.length} messages (${combinedMessage.length} chars)`);
  log(`[BATCH] ${combinedMessage}`);

  const { chatId, messageId, threadId, rootId, parentId, botMentioned, chatType } = batch[0];
  const sessionLabel = await getChatLabel(chatId);
  await askOpenClaw(
    { message: combinedMessage, sessionKey, sessionLabel },
    chatId, messageId,
    { threadId, rootId, parentId, botMentioned, chatType, replyToId: messageId },
    messageMap,
    threadMap,
  );
  log('[BATCH] Async processing started');
}

export { processBatchedMessages };
