import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { createInterface } from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';

import { getDataRootCandidates, getPromptPath, resolvePackagePath } from './runtime_paths';
import { toPositiveInteger } from './save_store';
import { isRecord } from './world_state_utils';

type KimiChatCompletionResponse = {
  choices: Array<{
    message?: {
      content?: string;
    };
  }>;
};

export type KimiClientConfig = {
  apiKey: string;
  baseUrl: string;
  model: string;
  timeoutMs: number;
  maxTokens: number;
  enableCanonGuardian: boolean;
};

type AppConfig = {
  apiKey?: string;
  baseUrl?: string;
  model?: string;
  timeoutMs?: number;
  maxTokens?: number;
  enableCanonGuardian?: boolean;
};

const DEFAULT_MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1";
const DEFAULT_MOONSHOT_MODEL = "kimi-k2.5";
const DEFAULT_TIMEOUT_MS = 120000;
const DEFAULT_MAX_TOKENS = 2048;
const DEFAULT_ENABLE_CANON_GUARDIAN = true;
const APP_CONFIG_PATHS = getDataRootCandidates().map(root => join(root, "config.json"));

export async function loadPromptFile(filePath: string): Promise<string> {
  return await readFile(resolvePackagePath(filePath), 'utf-8');
}

export async function loadGenesisPrompt(): Promise<string> {
  try {
    return await readFile(getPromptPath('genesis_engine_prompt.md'), 'utf-8');
  } catch {
    return `# 【创世者协议 v1.0】
你是一位古老的创世者——"墨言"...
[完整Prompt内容]`;
  }
}

async function loadAppConfig(): Promise<AppConfig> {
  for (const configPath of APP_CONFIG_PATHS) {
    try {
      const raw = await readFile(configPath, 'utf-8');
      const parsed = JSON.parse(raw) as unknown;
      if (!isRecord(parsed)) {
        continue;
      }

      return {
        apiKey: typeof parsed.apiKey === "string" && parsed.apiKey.trim().length > 0 ? parsed.apiKey.trim() : undefined,
        baseUrl: typeof parsed.baseUrl === "string" && parsed.baseUrl.trim().length > 0 ? parsed.baseUrl.trim() : undefined,
        model: typeof parsed.model === "string" && parsed.model.trim().length > 0 ? parsed.model.trim() : undefined,
        timeoutMs: toPositiveInteger(parsed.timeoutMs, DEFAULT_TIMEOUT_MS),
        maxTokens: toPositiveInteger(parsed.maxTokens, DEFAULT_MAX_TOKENS),
        enableCanonGuardian: typeof parsed.enableCanonGuardian === "boolean"
          ? parsed.enableCanonGuardian
          : DEFAULT_ENABLE_CANON_GUARDIAN
      };
    } catch {
      continue;
    }
  }

  return {};
}

async function saveAppConfig(config: AppConfig): Promise<string | null> {
  for (const configPath of APP_CONFIG_PATHS) {
    try {
      await mkdir(dirname(configPath), { recursive: true });
      await writeFile(configPath, JSON.stringify(config, null, 2), 'utf-8');
      return configPath;
    } catch {
      continue;
    }
  }

  return null;
}

function parseBooleanFlag(value: string | undefined, fallback: boolean): boolean {
  if (typeof value !== "string") {
    return fallback;
  }

  const normalized = value.trim().toLowerCase();
  if (["1", "true", "yes", "on"].includes(normalized)) {
    return true;
  }
  if (["0", "false", "no", "off"].includes(normalized)) {
    return false;
  }
  return fallback;
}

async function validateKimiApiKey(
  apiKey: string,
  baseUrl: string,
  model: string,
  timeoutMs: number
): Promise<{ valid: boolean; authFailed: boolean; message?: string }> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), Math.min(timeoutMs, 15000));

  try {
    const usedBaseUrl = baseUrl.replace(/\/+$/, "");
    const response = await fetch(`${usedBaseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      signal: controller.signal,
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: "你是一个认证校验助手。" },
          { role: "user", content: "请只回复 OK" }
        ],
        max_tokens: 8,
        thinking: { type: "disabled" }
      })
    });

    if (response.status === 401) {
      return {
        valid: false,
        authFailed: true,
        message: "已保存的 API Key 无效或已过期，请输入新的 Key。"
      };
    }

    if (!response.ok) {
      const errorText = await response.text();
      return {
        valid: false,
        authFailed: false,
        message: `暂时无法校验 API Key：${response.status} ${response.statusText}\n${errorText}`
      };
    }

    return { valid: true, authFailed: false };
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      return {
        valid: false,
        authFailed: false,
        message: "API Key 校验超时，请检查网络或稍后重试。"
      };
    }

    return {
      valid: false,
      authFailed: false,
      message: `暂时无法校验 API Key：${String(error)}`
    };
  } finally {
    clearTimeout(timeoutId);
  }
}

function resolveBaseConfig(savedConfig: AppConfig) {
  const baseUrl = process.env.MOONSHOT_BASE_URL?.trim() || savedConfig.baseUrl || DEFAULT_MOONSHOT_BASE_URL;
  const model = process.env.MOONSHOT_MODEL?.trim() || savedConfig.model || DEFAULT_MOONSHOT_MODEL;
  const timeoutMs = toPositiveInteger(process.env.MOONSHOT_TIMEOUT_MS, savedConfig.timeoutMs || DEFAULT_TIMEOUT_MS);
  const maxTokens = toPositiveInteger(process.env.MOONSHOT_MAX_TOKENS, savedConfig.maxTokens || DEFAULT_MAX_TOKENS);
  const enableCanonGuardian = parseBooleanFlag(
    process.env.MOONSHOT_ENABLE_CANON_GUARDIAN,
    typeof savedConfig.enableCanonGuardian === "boolean"
      ? savedConfig.enableCanonGuardian
      : DEFAULT_ENABLE_CANON_GUARDIAN
  );

  return {
    baseUrl,
    model,
    timeoutMs,
    maxTokens,
    enableCanonGuardian
  };
}

export async function getKimiClientConfigNonInteractive(): Promise<KimiClientConfig> {
  const savedConfig = await loadAppConfig();
  const baseConfig = resolveBaseConfig(savedConfig);
  const envKey = process.env.MOONSHOT_API_KEY?.trim();
  const savedKey = savedConfig.apiKey?.trim();
  let apiKey = envKey || savedKey;

  if (!apiKey) {
    throw new Error("未提供 Kimi API Key。请通过 MOONSHOT_API_KEY 或本地配置文件提供。");
  }

  if (envKey && savedKey && envKey !== savedKey) {
    const envValidation = await validateKimiApiKey(envKey, baseConfig.baseUrl, baseConfig.model, baseConfig.timeoutMs);
    if (!envValidation.valid) {
      apiKey = savedKey;
    }
  }

  return {
    apiKey,
    ...baseConfig
  };
}

export async function hasConfiguredKimiApiKey(): Promise<boolean> {
  const savedConfig = await loadAppConfig();
  return Boolean(process.env.MOONSHOT_API_KEY?.trim() || savedConfig.apiKey);
}

export async function isConfiguredKimiApiKeyUsable(): Promise<boolean> {
  const savedConfig = await loadAppConfig();
  const { baseUrl, model, timeoutMs } = resolveBaseConfig(savedConfig);
  const apiKey = process.env.MOONSHOT_API_KEY?.trim() || savedConfig.apiKey;
  if (!apiKey) {
    return false;
  }

  const envKey = process.env.MOONSHOT_API_KEY?.trim();
  const savedKey = savedConfig.apiKey?.trim();

  if (envKey) {
    const envValidation = await validateKimiApiKey(envKey, baseUrl, model, timeoutMs);
    if (envValidation.valid) {
      return true;
    }
  }

  if (savedKey) {
    const savedValidation = await validateKimiApiKey(savedKey, baseUrl, model, timeoutMs);
    return savedValidation.valid;
  }

  return false;
}

export async function configureKimiApiKey(apiKey: string): Promise<string> {
  const trimmed = apiKey.trim();
  if (!trimmed) {
    throw new Error("API Key 不能为空。");
  }

  const savedConfig = await loadAppConfig();
  const { baseUrl, model, timeoutMs, maxTokens, enableCanonGuardian } = resolveBaseConfig(savedConfig);
  const validation = await validateKimiApiKey(trimmed, baseUrl, model, timeoutMs);
  if (!validation.valid) {
    throw new Error(validation.message || "API Key 校验失败，请确认后重试。");
  }

  process.env.MOONSHOT_API_KEY = trimmed;
  await saveAppConfig({
    ...savedConfig,
    apiKey: trimmed,
    baseUrl,
    model,
    timeoutMs,
    maxTokens,
    enableCanonGuardian
  });

  return "Kimi API Key 已保存并验证通过。";
}

export async function getKimiClientConfig(): Promise<KimiClientConfig> {
  const savedConfig = await loadAppConfig();
  const { baseUrl, model, timeoutMs, maxTokens, enableCanonGuardian } = resolveBaseConfig(savedConfig);
  const resolvedKey = process.env.MOONSHOT_API_KEY?.trim() || savedConfig.apiKey;
  const validatedSavedKey = resolvedKey
    ? await validateKimiApiKey(resolvedKey, baseUrl, model, timeoutMs)
    : { valid: false, authFailed: false as const };

  const rl = createInterface({ input, output });
  if (resolvedKey && !validatedSavedKey.valid && validatedSavedKey.message) {
    console.log(`\n[系统] ${validatedSavedKey.message}`);
  }

  const promptText = validatedSavedKey.valid
    ? "已检测到可用的 Kimi API Key。直接回车继续使用，或输入新的 Key 覆盖："
    : "请输入 Kimi API Key（输入会回显，输入新值后会保存到本地配置文件）：";
  const entered = (await rl.question(promptText)).trim();
  rl.close();

  if (entered.length === 0 && validatedSavedKey.valid && resolvedKey) {
    return { apiKey: resolvedKey, baseUrl, model, timeoutMs, maxTokens, enableCanonGuardian };
  }

  if (entered.length === 0) {
    throw new Error("未提供 API Key，无法进行真实调用");
  }

  const validatedEnteredKey = await validateKimiApiKey(entered, baseUrl, model, timeoutMs);
  if (!validatedEnteredKey.valid) {
    throw new Error(validatedEnteredKey.message || "API Key 校验失败，请确认后重试");
  }

  process.env.MOONSHOT_API_KEY = entered;
  const savedPath = await saveAppConfig({
    ...savedConfig,
    apiKey: entered,
    baseUrl,
    model,
    timeoutMs,
    maxTokens,
    enableCanonGuardian
  });
  if (!savedPath) {
    console.log("警告：当前环境没有可写配置目录，本次仅在当前进程中使用该 API Key。");
  }
  return { apiKey: entered, baseUrl, model, timeoutMs, maxTokens, enableCanonGuardian };
}

export async function kimiChatJson<T>(
  client: KimiClientConfig,
  systemPrompt: string,
  userContent: string | Record<string, unknown>,
  maxTokensOverride?: number
): Promise<T> {
  const userMessage = typeof userContent === "string" ? userContent : JSON.stringify(userContent);
  const usedBaseUrl = client.baseUrl.replace(/\/+$/, "");
  const maxAttempts = 2;
  let lastError: unknown;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), client.timeoutMs);

    try {
      const response = await fetch(`${usedBaseUrl}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${client.apiKey}`
        },
        signal: controller.signal,
        body: JSON.stringify({
          model: client.model,
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userMessage }
          ],
          max_tokens: maxTokensOverride ?? client.maxTokens,
          response_format: { type: "json_object" },
          thinking: { type: "disabled" }
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        if (response.status === 401) {
          throw new Error(
            `Kimi API 认证失败(401): ${response.statusText}\n` +
              `- 请确认你使用的是“新生成且未撤销”的 API Key（不要把 Key 发到聊天里）\n` +
              `- 当前请求地址: ${usedBaseUrl}/chat/completions\n` +
              `- 当前默认服务地址: ${DEFAULT_MOONSHOT_BASE_URL}\n` +
              `${errorText}`
          );
        }

        if ((response.status === 429 || response.status >= 500) && attempt < maxAttempts) {
          console.log(`Kimi API 第 ${attempt} 次请求失败（${response.status}），准备重试...`);
          lastError = new Error(`Kimi API 请求失败: ${response.status} ${response.statusText}\n${errorText}`);
          continue;
        }

        throw new Error(`Kimi API 请求失败: ${response.status} ${response.statusText}\n${errorText}`);
      }

      const data = (await response.json()) as KimiChatCompletionResponse;
      const content = data.choices?.[0]?.message?.content;
      if (typeof content !== "string" || content.length === 0) {
        throw new Error("Kimi API 返回内容为空或格式不符合预期");
      }

      try {
        return JSON.parse(content) as T;
      } catch {
        throw new Error(`Kimi 返回了无法解析的 JSON：\n${content}`);
      }
    } catch (error) {
      lastError = error;
      const isAbortError = error instanceof Error && error.name === "AbortError";
      const isNetworkError = error instanceof TypeError;

      if ((isAbortError || isNetworkError) && attempt < maxAttempts) {
        console.log(`Kimi API 第 ${attempt} 次请求超时或网络异常，准备重试...`);
        continue;
      }

      if (isAbortError) {
        throw new Error(`Kimi API 请求超时（${client.timeoutMs}ms），请检查网络或稍后重试`);
      }

      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  throw lastError instanceof Error ? lastError : new Error(String(lastError));
}
