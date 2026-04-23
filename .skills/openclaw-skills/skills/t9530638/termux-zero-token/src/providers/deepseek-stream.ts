/**
 * DeepSeek Web Stream - 從手機 Chrome 獲取 credentials 後調用 DeepSeek API
 */

import type { StreamFn } from "@mariozechner/pi-agent-core";
import {
  createAssistantMessageEventStream,
  type AssistantMessage,
  type AssistantMessageEvent,
  type TextContent,
} from "@mariozechner/pi-ai";

interface DeepSeekMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

interface DeepSeekChatRequest {
  model: string;
  messages: DeepSeekMessage[];
  stream?: boolean;
  temperature?: number;
  max_tokens?: number;
}

interface DeepSeekChatResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: {
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }[];
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

/**
 * 從 cookies 中提取 device_id
 */
function extractDeviceId(cookies: string): string {
  const match = cookies.match(/did=([^;]+)/);
  return match ? match[1] : "";
}

/**
 * 創建 DeepSeek Web Stream 函數
 */
export function createDeepseekWebStreamFn(cookieOrJson: string): StreamFn {
  let cookie: string;
  let userAgent = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36";
  
  try {
    const parsed = JSON.parse(cookieOrJson);
    if (typeof parsed === "string") {
      cookie = parsed;
    } else {
      cookie = parsed.cookie || "";
      userAgent = parsed.userAgent || userAgent;
    }
  } catch {
    cookie = cookieOrJson;
  }

  const deviceId = extractDeviceId(cookie);

  return async (model, context, options) => {
    const stream = createAssistantMessageEventStream();
    
    // 構建 messages
    const messages: DeepSeekMessage[] = [];
    
    // 系統 prompt
    const systemPrompt = (context as unknown as { systemPrompt?: string }).systemPrompt;
    if (systemPrompt) {
      messages.push({ role: "system", content: systemPrompt });
    }
    
    // 歷史 messages
    const history = context.messages || [];
    for (const m of history) {
      const role = (m.role as string) === "toolResult" ? "user" : (m.role as string);
      if (role === "user" || role === "assistant") {
        messages.push({ role, content: m.content as string });
      }
    }

    // 當前 prompt
    const lastMessage = (context as unknown as { lastMessage?: string }).lastMessage || "";
    if (lastMessage) {
      messages.push({ role: "user", content: lastMessage });
    }

    try {
      // 發送到 DeepSeek API
      const response = await fetch("https://api.deepseek.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Cookie": cookie,
          "User-Agent": userAgent,
          "Authorization": "Bearer ", // 使用 cookie，不需要 token
          "Origin": "https://chat.deepseek.com",
          "Referer": "https://chat.deepseek.com/",
        },
        body: JSON.stringify({
          model: model || "deepseek-chat",
          messages,
          stream: false,
          temperature: 0.7,
          max_tokens: 4096,
        } as DeepSeekChatRequest),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`DeepSeek API error: ${response.status} - ${error}`);
      }

      const data: DeepSeekChatResponse = await response.json();
      
      const content = data.choices[0]?.message?.content || "";
      
      // 發送 content 事件
      stream.push({
        type: "content",
        content: [{ type: "text", text: content } as TextContent],
      } as AssistantMessageEvent);

      // 完成
      stream.push({ type: "done" } as AssistantMessageEvent);
      
    } catch (error) {
      stream.push({
        type: "error",
        error: error instanceof Error ? error.message : "Unknown error",
      } as AssistantMessageEvent);
      stream.push({ type: "done" } as AssistantMessageEvent);
    }

    return stream;
  };
}