/**
 * Termux Zero Token - 連接手機 Chrome 獲取 AI 調用 credentials
 * 
 * 設計原理：
 * 1. 通過 ADB port forward 連接手機 Chrome CDP
 * 2. 捕獲已登入 AI 網站的 cookies/session
 * 3. 使用這些 credentials 調用 AI API
 */

import { chromium, type Browser, type BrowserContext, type Page } from "playwright-core";
import * as fs from "node:fs";
import * as path from "node:path";
import * as https from "node:https";
import * as http from "node:http";

// 配置文件路徑
const CONFIG_DIR = path.join(process.env.HOME || "", ".openclaw", "zero-token");
const CREDENTIALS_FILE = path.join(CONFIG_DIR, "credentials.json");

// 支持的 AI 提供商
export const PROVIDERS = {
  "deepseek-web": {
    name: "DeepSeek",
    url: "https://chat.deepseek.com",
    cookieDomains: ["deepseek.com", "chat.deepseek.com"],
    apiEndpoint: "https://api.deepseek.com/v1/chat/completions",
    models: ["deepseek-chat", "deepseek-reasoner"],
  },
  "kimi-web": {
    name: "Kimi",
    url: "https://kimi.moonshot.cn",
    cookieDomains: ["kimi.moonshot.cn", "moonshot.cn"],
    apiEndpoint: "https://api.moonshot.cn/v1/chat/completions",
    models: ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
  },
  "qwen-web": {
    name: "Qwen",
    url: "https://qwen.chat",
    cookieDomains: ["qwen.chat", "tongyi.aliyun.com"],
    apiEndpoint: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
    models: ["qwen-turbo", "qwen-plus", "qwen-max"],
  },
  "glm-web": {
    name: "GLM",
    url: "https://chatglm.cn",
    cookieDomains: ["chatglm.cn", "zhipuai.com.cn"],
    apiEndpoint: "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    models: ["glm-4-flash", "glm-4-plus", "glm-4"],
  },
  "claude-web": {
    name: "Claude",
    url: "https://claude.ai",
    cookieDomains: ["claude.ai", "anthropic.com"],
    apiEndpoint: null, // 需要特殊處理
    models: ["claude-3-5-sonnet", "claude-3-haiku"],
  },
  "chatgpt-web": {
    name: "ChatGPT",
    url: "https://chat.openai.com",
    cookieDomains: ["chat.openai.com", "openai.com"],
    apiEndpoint: null, // 需要特殊處理
    models: ["gpt-4", "gpt-4o"],
  },
} as const;

export type ProviderId = keyof typeof PROVIDERS;

export interface Credentials {
  provider: ProviderId;
  cookies: string;
  bearer?: string;
  userAgent?: string;
  expiresAt?: number;
}

export interface ChromeConnection {
  browser: Browser;
  context: BrowserContext;
  cdpUrl: string;
}

/**
 * 確保配置目錄存在
 */
function ensureConfigDir(): void {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
}

/**
 * 保存 credentials
 */
export function saveCredentials(creds: Credentials): void {
  ensureConfigDir();
  const all = loadAllCredentials();
  all[creds.provider] = creds;
  fs.writeFileSync(CREDENTIALS_FILE, JSON.stringify(all, null, 2));
  console.log(`✅ Saved credentials for ${creds.provider}`);
}

/**
 * 加載所有 credentials
 */
export function loadAllCredentials(): Record<ProviderId, Credentials> {
  ensureConfigDir();
  if (!fs.existsSync(CREDENTIALS_FILE)) {
    return {} as Record<ProviderId, Credentials>;
  }
  try {
    return JSON.parse(fs.readFileSync(CREDENTIALS_FILE, "utf-8"));
  } catch {
    return {} as Record<ProviderId, Credentials>;
  }
}

/**
 * 加載特定 provider 的 credentials
 */
export function loadCredentials(provider: ProviderId): Credentials | null {
  const all = loadAllCredentials();
  return all[provider] || null;
}

/**
 * 連接到手機 Chrome（通過 localhost:9222）
 * 假設 ADB port forward 已經設置
 */
export async function connectToPhoneChrome(
  cdpUrl: string = "http://127.0.0.1:9222"
): Promise<ChromeConnection> {
  console.log(`📱 Connecting to Chrome at ${cdpUrl}...`);
  
  // 獲取 WebSocket URL
  const wsUrl = await getChromeWebSocketUrl(cdpUrl);
  if (!wsUrl) {
    throw new Error("Failed to get Chrome WebSocket URL. Make sure ADB port forward is set up.");
  }
  
  const browser = await chromium.connectOverCDP(wsUrl);
  const context = browser.contexts()[0] || await browser.newContext();
  
  return { browser, context, cdpUrl };
}

/**
 * 獲取 Chrome WebSocket URL
 */
async function getChromeWebSocketUrl(cdpUrl: string): Promise<string | null> {
  try {
    const response = await fetch(`${cdpUrl}/json/version`);
    const data = await response.json();
    return data.webSocketDebuggerUrl;
  } catch (error) {
    console.error("Failed to connect to Chrome:", error);
    return null;
  }
}

/**
 * 從 Chrome 獲取特定網站的 cookies
 */
export async function captureProviderCookies(
  context: BrowserContext,
  provider: ProviderId
): Promise<string> {
  const config = PROVIDERS[provider];
  const domains = config.cookieDomains;
  
  const cookies = await context.cookies(
    domains.map(d => `https://${d}`)
  );
  
  // 轉換為 cookie 字符串
  const cookieStr = cookies.map(c => `${c.name}=${c.value}`).join("; ");
  return cookieStr;
}

/**
 * 檢查 provider 是否已登入
 */
export async function checkProviderLogin(
  context: BrowserContext,
  provider: ProviderId
): Promise<boolean> {
  const config = PROVIDERS[provider];
  const pages = context.pages();
  
  // 查找相關頁面
  const providerPage = pages.find(p => 
    config.cookieDomains.some(d => p.url().includes(d))
  );
  
  if (!providerPage) {
    return false;
  }
  
  // 檢查 cookies
  const cookies = await context.cookies(
    config.cookieDomains.map(d => `https://${d}`)
  );
  
  return cookies.length > 0;
}

/**
 * 從手機 Chrome 導入特定 provider 的 credentials
 */
export async function importProviderCredentials(
  provider: ProviderId,
  cdpUrl: string = "http://127.0.0.1:9222"
): Promise<void> {
  const connection = await connectToPhoneChrome(cdpUrl);
  
  try {
    // 檢查是否已登入
    const isLoggedIn = await checkProviderLogin(connection.context, provider);
    
    if (!isLoggedIn) {
      console.log(`⚠️ ${provider} not logged in. Please login in Chrome first.`);
      console.log(`   Open ${PROVIDERS[provider].url} in your phone Chrome and login.`);
      return;
    }
    
    // 捕獲 cookies
    const cookies = await captureProviderCookies(connection.context, provider);
    
    // 保存
    const credentials: Credentials = {
      provider,
      cookies,
      userAgent: connection.context.options?.userAgent,
      expiresAt: Date.now() + 7 * 24 * 60 * 60 * 1000, // 7 days
    };
    
    saveCredentials(credentials);
    console.log(`✅ Imported credentials for ${provider}`);
    
  } finally {
    await connection.browser.close();
  }
}

/**
 * 列出所有已配置的 providers
 */
export function listProviders(): { provider: ProviderId; configured: boolean }[] {
  const all = loadAllCredentials();
  return Object.keys(PROVIDERS).map(p => ({
    provider: p as ProviderId,
    configured: !!all[p as ProviderId],
  }));
}

/**
 * 測試特定 provider 的 credentials 是否有效
 */
export async function testCredentials(provider: ProviderId): Promise<boolean> {
  const creds = loadCredentials(provider);
  if (!creds) {
    console.log(`❌ No credentials for ${provider}`);
    return false;
  }
  
  // 這裡可以添加實際的 API 測試
  console.log(`✅ Credentials found for ${provider}`);
  console.log(`   Cookies: ${creds.cookies.substring(0, 50)}...`);
  
  return true;
}