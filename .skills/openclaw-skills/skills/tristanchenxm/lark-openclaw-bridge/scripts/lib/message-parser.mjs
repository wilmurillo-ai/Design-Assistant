/**
 * Parse MEDIA: tags from a message string.
 *
 * @param {string} content
 * @returns {{ text: string, mediaPath: string|null }}
 */
export function parseMedia(content) {
  const mediaRegex = /MEDIA:([^\s]+)/;
  const match = content.match(mediaRegex);
  if (match) {
    const mediaPath = match[1];
    const text = content.replace(mediaRegex, '').trim();
    return { text, mediaPath };
  }
  return { text: content, mediaPath: null };
}

/**
 * Parse Lark post (rich text) message content.
 *
 * @param {string|object} content - Raw content field from Lark message
 * @returns {{ texts: string[], imageKeys: string[] }}
 */
export function parsePostContent(content) {
  const texts = [];
  const imageKeys = [];

  try {
    const parsed = typeof content === 'string' ? JSON.parse(content) : content;

    let contentBlocks = null;

    if (parsed.content && Array.isArray(parsed.content)) {
      contentBlocks = parsed.content;
    } else {
      for (const key of ['zh_cn', 'en_us', 'ja_jp', 'default']) {
        if (parsed[key]?.content) {
          contentBlocks = parsed[key].content;
          break;
        }
      }
    }

    if (!contentBlocks) return { texts, imageKeys };

    for (const paragraph of contentBlocks) {
      if (!Array.isArray(paragraph)) continue;
      for (const element of paragraph) {
        if (element.tag === 'text' && element.text) {
          texts.push(element.text);
        } else if (element.tag === 'img' && element.image_key) {
          imageKeys.push(element.image_key);
        } else if (element.tag === 'a' && element.text) {
          texts.push(element.href ? `[${element.text}](${element.href})` : element.text);
        }
      }
    }
  } catch {
    // Return empty result on parse failure
  }

  return { texts, imageKeys };
}

/**
 * Extract display text from a single Lark card element (recursive).
 *
 * @param {object} element
 * @returns {string}
 */
export function extractElementText(element) {
  if (!element || typeof element !== 'object') return '';

  const tag = element.tag;

  if (tag === 'text' && typeof element.text === 'string') return element.text;

  if (tag === 'a') {
    const linkText = element.text || element.href || '';
    if (element.href && linkText !== element.href) return `${linkText} (${element.href})`;
    return linkText;
  }

  if (element.text?.content) return element.text.content;
  if (typeof element.text === 'string') return element.text;
  if (element.content && typeof element.content === 'string') return element.content;

  if (tag === 'markdown' || tag === 'md') return element.content || '';

  if (tag === 'div') {
    if (element.text) {
      if (typeof element.text === 'string') return element.text;
      if (element.text.content) return element.text.content;
    }
    if (element.fields) {
      return element.fields.map(f => {
        if (f.text?.content) return f.text.content;
        if (typeof f.text === 'string') return f.text;
        return '';
      }).filter(Boolean).join(' | ');
    }
  }

  if (tag === 'note' && element.elements) {
    return element.elements.map(extractElementText).filter(Boolean).join(' ');
  }

  if (tag === 'action' && element.actions) {
    const labels = element.actions
      .map(a => a.text?.content || a.text)
      .filter(Boolean);
    if (labels.length > 0) return `[Buttons]: ${labels.join(', ')}`;
  }

  if (tag === 'column_set' && element.columns) {
    return element.columns.map(col => extractElementText(col)).filter(Boolean).join(' | ');
  }

  if (tag === 'column' && element.elements) {
    return element.elements.map(extractElementText).filter(Boolean).join('\n');
  }

  if (tag === 'hr') return '';

  if (Array.isArray(element.fields)) {
    return element.fields.map(extractElementText).filter(Boolean).join('\n');
  }

  if (Array.isArray(element.elements)) {
    return element.elements.map(extractElementText).filter(Boolean).join('\n');
  }

  return '';
}

/**
 * Extract plain-text summary from a Lark interactive card message.
 *
 * @param {object} cardContent
 * @returns {string}
 */
export function extractCardText(cardContent) {
  const parts = [];

  try {
    if (cardContent.config) parts.push('[Card with config]');

    if (cardContent.header?.title) {
      const title =
        cardContent.header.title.content ||
        cardContent.header.title.text ||
        cardContent.header.title;
      if (typeof title === 'string') parts.push(`Title: ${title}`);
    }

    if (cardContent.header?.template) {
      parts.push(`Template: ${cardContent.header.template}`);
    }

    if (Array.isArray(cardContent.elements)) {
      for (const element of cardContent.elements) {
        if (Array.isArray(element)) {
          for (const subElement of element) {
            const text = extractElementText(subElement);
            if (text) parts.push(text);
          }
        } else {
          const text = extractElementText(element);
          if (text) parts.push(text);
        }
      }
    }

    if (cardContent.card_link?.url) {
      parts.push(`Link: ${cardContent.card_link.url}`);
    }

    if (parts.length === 0) {
      for (const [key, value] of Object.entries(cardContent)) {
        if (typeof value === 'string' && value.length > 0 && value.length < 500) {
          parts.push(`${key}: ${value}`);
        }
      }
    }
  } catch {
    // Return best-effort result
  }

  if (parts.length === 0) {
    const compactJson = JSON.stringify(cardContent, null, 2);
    if (compactJson.length < 1000) return `[Card]\n${compactJson}`;
    return `[Card] Fields: ${Object.keys(cardContent).join(', ')}`;
  }

  return `[Card]\n${parts.join('\n')}`;
}
