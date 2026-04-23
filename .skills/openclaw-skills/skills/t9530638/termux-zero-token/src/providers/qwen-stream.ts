/**
 * Qwen Web Stream - 從手機 Chrome 獲取 credentials 後調用 Qwen API
 */

import type { StreamFn } from "@mariozechner/pi-agent-core";
import {
  createAssistantMessageEventStream,
  type AssistantMessageEvent,
  type TextContent,
} from "@mariozechner/pi-ai";

interface QwenMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

interface QwenChatRequest {
  model: string;
  input: {
    messages: QwenMessage[];
  };
  parameters: {
    temperature?: number;
    max_tokens?: number;
    result_format?: string;
  };
}

interface QwenChatResponse {
  output: {
    choices: {
      finish_reason: string;
      message: {
        role: string;
        content: string;
      };
    }[];
  };
  usage?: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
  request_id: string;
}

/**
 * 創建 Qwen Web Stream 函數
 */
export function createQwenWebStreamFn(cookieOrJson: string): StreamFn {
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

  // 從 cookie 提取 auth token
  function extractAuthToken(cookie: string): string {
    const match = cookie.match(/auth_token=([^;]+)/);
    return match ? match[1] : "";
  }

  return async (model, context, options) => {
    const stream = createAssistantMessageEventStream();
    
    const messages: QwenMessage[] = [];
    
    const systemPrompt = (context as unknown as { systemPrompt?: string }).systemPrompt;
    if (systemPrompt) {
      messages.push({ role: "system", content: systemPrompt });
    }
    
    const history = context.messages || [];
    for (const m of history) {
      const role = (m.role as string) === "toolResult" ? "user" : (m.role as string);
      if (role === "user" || role === "assistant") {
        messages.push({ role, content: m.content as string });
      }
    }

    const lastMessage = (context as unknown as { lastMessage?: string }).lastMessage || "";
    if (lastMessage) {
      messages.push({ role: "user", content: lastMessage });
    }

    try {
      const authToken = extractAuthToken(cookie);
      
      const response = await fetch("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${authToken}`,
          "X-DashScope-Referer": "https://qwen.chat/",
          "X-DashScope-Api-Version": "2024-11-01",
        },
        body: JSON.stringify({
          model: model || "qwen-turbo",
          input: { messages },
          parameters: {
            temperature: 0.7,
            max_tokens: 4096,
            result_format: "message",
          },
        } as QwenChatRequest),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Qwen API error: ${response.status} - ${error}`);
      }

      const data: QwenChatResponse = await response.json();
      const content = data.output?.choices[0]?.message?.content || "";
      
      stream.push({
        type: "content",
        content: [{ type: "text", text: content } as TextContent],
      } as AssistantMessageEvent);

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