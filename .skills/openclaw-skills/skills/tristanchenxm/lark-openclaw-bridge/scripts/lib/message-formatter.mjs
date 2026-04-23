/**
 * Format a single message with JSON metadata header + content body.
 *
 * @param {object} msg      - Internal message object
 * @param {object} rawEvent - Original Lark event
 * @returns {string}
 */
export function formatMessage(msg, rawEvent) {
  const createTimeMs = rawEvent?.message?.create_time || String(msg.timestamp);
  const date = new Date(parseInt(createTimeMs));

  // Convert to UTC+8 (Asia/Shanghai)
  const utc8Date = new Date(date.getTime() + 8 * 60 * 60 * 1000);

  const year  = utc8Date.getUTCFullYear();
  const month = String(utc8Date.getUTCMonth() + 1).padStart(2, '0');
  const day   = String(utc8Date.getUTCDate()).padStart(2, '0');
  const hours = String(utc8Date.getUTCHours()).padStart(2, '0');
  const mins  = String(utc8Date.getUTCMinutes()).padStart(2, '0');
  const secs  = String(utc8Date.getUTCSeconds()).padStart(2, '0');
  const createTimeStr = `${year}-${month}-${day}T${hours}:${mins}:${secs}+08:00`;

  const rawMetadata = {
    message_id:      msg.messageId,
    chat_type:       msg.chatType,
    sender_open_id:  rawEvent?.sender?.sender_id?.open_id,
    sender_user_id:  rawEvent?.sender?.sender_id?.user_id,
    bot_open_id:     process.env.LARK_APP_OPEN_ID || undefined,
    bot_name:        process.env.LARK_BOT_NAME || undefined,
    mentioned_you:    msg.botMentioned,
    hint:            msg.mentionsOthers ? 'Not mentioned.' : undefined,
    create_time:     createTimeStr,
    root_id:         msg.rootId,
    parent_id:       msg.parentId,
    thread_id:       msg.threadId,
    parent_content:  msg.parentContent,
  };

  const metadata = Object.fromEntries(
    Object.entries(rawMetadata).filter(([, v]) => v !== '' && v !== null && v !== undefined)
  );

  const userId = rawEvent?.sender?.sender_id?.user_id || rawEvent?.sender?.sender_id?.open_id || 'unknown';
  return `${JSON.stringify(metadata)}\n[${userId}]: ${msg.text}`;
}

/**
 * Combine a batch of messages into a single string (separated by 2 blank lines).
 *
 * @param {object[]} batch
 * @returns {string}
 */
export function combineBatchMessages(batch) {
  if (batch.length === 0) return '';
  if (batch.length === 1) return formatMessage(batch[0], batch[0].rawEvent);
  return batch.map(msg => formatMessage(msg, msg.rawEvent)).join('\n\n\n');
}

