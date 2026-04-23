/**
 * GLM Web Stream - 從手機 Chrome 獲取 credentials 後調用 GLM API
 */

import type { StreamFn } from "@mariozechner/pi-agent-core";
import {
  createAssistantMessageEventStream,
  type AssistantMessageEvent,
  type TextContent,
} from "@mariozechner/pi-ai";

interface GLMMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

interface GLMChatRequest {
  model: string;
  messages: GLMMessage[];
  stream?: boolean;
  temperature?: number;
  max_tokens?: number;
}

interface GLMChatResponse {
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
 * 創建 GLM Web Stream 函數
 */
export function createGlmWebStreamFn(cookieOrJson: string): StreamFn {
  let cookie: string;
  let userAgent = "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36";
  
  try {
    const parsed = JSON.parse(cookieOrJson);
    if (typeof parsed === "string") {
      cookie = parsed.cookie;
    } else {
      cookie = parsed.cookie || "";
      userAgent = parsed.userAgent || userAgent;
    }
  } catch {
    cookie = cookieOrJson;
  }

  return async (model, context, options) => {
    const stream = createAssistantMessageEventStream();
    
    const messages: GLMMessage[] = [];
    
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
      const response = await fetch("https://open.bigmodel.cn/api/paas/v4/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Cookie": cookie,
          "User-Agent": userAgent,
          "Origin": "https://chatglm.cn",
          "Referer": "https://chatglm.cn/",
        },
        body: JSON.stringify({
          model: model || "glm-4-flash",
          messages,
          stream: false,
          temperature: 0.7,
          max_tokens: 4096,
        } as GLMChatRequest),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`GLM API error: ${response.status} - ${error}`);
      }

      const data: GLMChatResponse = await response.json();
      const content = data.choices[0]?.message?.content || "";
      
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