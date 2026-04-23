var __defProp = Object.defineProperty;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __esm = (fn, res) => function __init() {
  return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
};
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};

// src/lib/config.ts
import path from "path";
import fs from "fs";
function getConfig() {
  return { ...defaultConfig };
}
function getCookiePath(platform) {
  const config2 = getConfig();
  return path.join(config2.cookieDir, `${platform}_cookies.json`);
}
function ensureCookieDir() {
  const config2 = getConfig();
  if (!fs.existsSync(config2.cookieDir)) {
    fs.mkdirSync(config2.cookieDir, { recursive: true });
  }
  return config2.cookieDir;
}
var defaultConfig;
var init_config = __esm({
  "src/lib/config.ts"() {
    "use strict";
    defaultConfig = {
      cookieDir: path.join(process.cwd(), "data", "cookies"),
      cookieExpiryDays: 30,
      headless: false,
      timeout: 6e4,
      slowMo: 100
    };
  }
});

// src/lib/cookie-manager.ts
var cookie_manager_exports = {};
__export(cookie_manager_exports, {
  CookieManager: () => CookieManager
});
import fs2 from "fs";
var CookieManager;
var init_cookie_manager = __esm({
  "src/lib/cookie-manager.ts"() {
    "use strict";
    init_config();
    CookieManager = class {
      platform;
      constructor(platform) {
        this.platform = platform;
      }
      /**
       * 保存Cookie
       */
      async saveCookies(cookies) {
        ensureCookieDir();
        const config2 = getConfig();
        const now = /* @__PURE__ */ new Date();
        const expiresAt = new Date(now.getTime() + config2.cookieExpiryDays * 24 * 60 * 60 * 1e3);
        const cookieData = {
          cookies,
          createdAt: now.toISOString(),
          expiresAt: expiresAt.toISOString()
        };
        const cookiePath = getCookiePath(this.platform);
        fs2.writeFileSync(cookiePath, JSON.stringify(cookieData, null, 2), "utf-8");
      }
      /**
       * 读取Cookie
       */
      async loadCookies() {
        const cookiePath = getCookiePath(this.platform);
        if (!fs2.existsSync(cookiePath)) {
          return null;
        }
        try {
          const content = fs2.readFileSync(cookiePath, "utf-8");
          const cookieData = JSON.parse(content);
          if (this.isExpired(cookieData)) {
            await this.clearCookies();
            return null;
          }
          return cookieData;
        } catch (error) {
          console.error(`Failed to load cookies for ${this.platform}:`, error);
          return null;
        }
      }
      /**
       * 检查Cookie是否过期
       */
      isExpired(cookieData) {
        const expiresAt = new Date(cookieData.expiresAt);
        return expiresAt < /* @__PURE__ */ new Date();
      }
      /**
       * 清除Cookie
       */
      async clearCookies() {
        const cookiePath = getCookiePath(this.platform);
        if (fs2.existsSync(cookiePath)) {
          fs2.unlinkSync(cookiePath);
        }
      }
      /**
       * 检查是否存在有效的Cookie
       */
      async hasValidCookies() {
        const cookieData = await this.loadCookies();
        return cookieData !== null && !this.isExpired(cookieData);
      }
      /**
       * 获取Cookie创建时间
       */
      async getCookieInfo() {
        const cookieData = await this.loadCookies();
        if (!cookieData) {
          return null;
        }
        return {
          createdAt: new Date(cookieData.createdAt),
          expiresAt: new Date(cookieData.expiresAt)
        };
      }
    };
  }
});

// src/lib/browser-manager.ts
import { chromium } from "playwright";

// src/types/index.ts
var PLATFORMS = {
  zhihu: {
    name: "zhihu",
    displayName: "\u77E5\u4E4E",
    loginUrl: "https://www.zhihu.com/signin",
    publishUrl: "https://zhuanlan.zhihu.com/write",
    domain: "zhihu.com"
  },
  bilibili: {
    name: "bilibili",
    displayName: "Bilibili",
    loginUrl: "https://passport.bilibili.com/",
    publishUrl: "https://member.bilibili.com/platform/upload/text/edit",
    domain: "bilibili.com"
  },
  baijiahao: {
    name: "baijiahao",
    displayName: "\u767E\u5BB6\u53F7",
    loginUrl: "https://baijiahao.baidu.com/",
    publishUrl: "https://baijiahao.baidu.com/builder/rc/edit",
    domain: "baijiahao.baidu.com"
  },
  toutiao: {
    name: "toutiao",
    displayName: "\u5934\u6761\u53F7",
    loginUrl: "https://mp.toutiao.com/",
    publishUrl: "https://mp.toutiao.com/publish",
    domain: "toutiao.com"
  },
  xiaohongshu: {
    name: "xiaohongshu",
    displayName: "\u5C0F\u7EA2\u4E66",
    loginUrl: "https://www.xiaohongshu.com/",
    publishUrl: "https://creator.xiaohongshu.com/publish/publish",
    domain: "xiaohongshu.com"
  }
};

// src/lib/browser-manager.ts
init_cookie_manager();
init_config();
var BrowserManager = class {
  browser = null;
  context = null;
  page = null;
  platform;
  cookieManager;
  constructor(platform) {
    this.platform = platform;
    this.cookieManager = new CookieManager(platform);
  }
  /**
   * 启动浏览器
   */
  async launch() {
    if (this.browser && this.page) {
      return this.page;
    }
    const config2 = getConfig();
    const platformInfo = PLATFORMS[this.platform];
    this.browser = await chromium.launch({
      headless: config2.headless,
      slowMo: config2.slowMo,
      args: [
        "--disable-blink-features=AutomationControlled",
        "--disable-features=IsolateOrigins,site-per-process"
      ]
    });
    const cookieData = await this.cookieManager.loadCookies();
    const storageState = cookieData ? {
      cookies: cookieData.cookies,
      origins: []
    } : void 0;
    this.context = await this.browser.newContext({
      viewport: { width: 1280, height: 800 },
      userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      storageState
    });
    await this.context.addInitScript(`
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
      });
    `);
    this.page = await this.context.newPage();
    this.page.setDefaultTimeout(config2.timeout);
    return this.page;
  }
  /**
   * 获取当前页面
   */
  getPage() {
    return this.page;
  }
  /**
   * 获取浏览器上下文
   */
  getContext() {
    return this.context;
  }
  /**
   * 保存当前Cookie
   */
  async saveCookies() {
    if (!this.context) {
      throw new Error("Browser context not initialized");
    }
    const state = await this.context.storageState();
    await this.cookieManager.saveCookies(state.cookies);
  }
  /**
   * 导航到登录页面
   */
  async gotoLoginPage() {
    if (!this.page) {
      throw new Error("Page not initialized");
    }
    const platformInfo = PLATFORMS[this.platform];
    await this.page.goto(platformInfo.loginUrl, { waitUntil: "networkidle" });
  }
  /**
   * 导航到发布页面
   */
  async gotoPublishPage() {
    if (!this.page) {
      throw new Error("Page not initialized");
    }
    const platformInfo = PLATFORMS[this.platform];
    console.log("   \u5BFC\u822A\u5230\u53D1\u5E03\u9875\u9762:", platformInfo.publishUrl);
    try {
      await this.page.goto(platformInfo.publishUrl, {
        waitUntil: "domcontentloaded",
        timeout: 3e4
      });
      await this.page.waitForTimeout(2e3);
      const currentUrl = this.page.url();
      console.log("   \u5F53\u524D\u9875\u9762URL:", currentUrl);
      if (this.isOnLoginPage() || currentUrl.includes("login")) {
        console.log("   \u26A0\uFE0F \u68C0\u6D4B\u5230\u672A\u767B\u5F55\uFF0C\u9875\u9762\u5DF2\u8DF3\u8F6C\u5230\u767B\u5F55\u9875\u9762");
        await this.handleBaijiahaoLoginButton();
        return;
      }
      console.log("   \u5BFC\u822A\u5230\u53D1\u5E03\u9875\u9762\u5B8C\u6BD5:", platformInfo.publishUrl);
      if (this.platform === "baijiahao") {
        await this.handleBaijiahaoLoginButton();
      }
    } catch (error) {
      const currentUrl = this.page.url();
      console.log("   \u5BFC\u822A\u8FC7\u7A0B\u4E2D\u51FA\u73B0\u9519\u8BEF\uFF0C\u5F53\u524DURL:", currentUrl);
      if (this.isOnLoginPage() || currentUrl.includes("login")) {
        console.log("   \u26A0\uFE0F \u68C0\u6D4B\u5230\u672A\u767B\u5F55\uFF0C\u9875\u9762\u5DF2\u8DF3\u8F6C\u5230\u767B\u5F55\u9875\u9762");
        await this.handleBaijiahaoLoginButton();
        return;
      }
      throw error;
    }
  }
  /**
   * 处理百家号登录按钮
   * 百家号需要先点击右上角的【登录】按钮才会显示扫码界面
   */
  async handleBaijiahaoLoginButton() {
    if (!this.page) return;
    try {
      await this.page.waitForTimeout(2e3);
      const currentUrl = this.page.url();
      if (!currentUrl.includes("login")) {
        return;
      }
      console.log("   \u68C0\u6D4B\u5230\u767E\u5BB6\u53F7\u767B\u5F55\u9875\u9762\uFF0C\u5C1D\u8BD5\u70B9\u51FB\u767B\u5F55\u6309\u94AE...");
      const loginBtnSelectors = [
        '[data-testid="bjh-login-btn"]',
        // 根据用户提供的HTML
        "button.loginBtn--lZVgU",
        // 类名
        "header button",
        // header 中的 button
        'button:has-text("\u767B\u5F55")',
        // 包含"登录"文字的按钮
        ".loginBtn--lZVgU",
        '[class*="loginBtn"]'
      ];
      for (const selector of loginBtnSelectors) {
        try {
          const loginBtn = await this.page.$(selector);
          if (loginBtn) {
            const isVisible = await loginBtn.isVisible();
            if (isVisible) {
              const btnText = await loginBtn.textContent();
              console.log(`   \u627E\u5230\u767B\u5F55\u6309\u94AE: ${btnText}`);
              await loginBtn.click();
              console.log("   \u2705 \u5DF2\u70B9\u51FB\u767B\u5F55\u6309\u94AE\uFF0C\u7B49\u5F85\u626B\u7801\u754C\u9762...");
              await this.page.waitForTimeout(2e3);
              return;
            }
          }
        } catch {
          continue;
        }
      }
      console.log("   \u672A\u627E\u5230\u767B\u5F55\u6309\u94AE\uFF0C\u53EF\u80FD\u9875\u9762\u5DF2\u53D8\u5316");
    } catch (error) {
      console.log("   \u5904\u7406\u767B\u5F55\u6309\u94AE\u65F6\u51FA\u9519:", error);
    }
  }
  /**
   * 检测当前页面是否在登录页面
   */
  isOnLoginPage() {
    if (!this.page) {
      return false;
    }
    const currentUrl = this.page.url();
    switch (this.platform) {
      case "zhihu":
        return currentUrl.includes("signin") || currentUrl.includes("login");
      case "bilibili":
        return currentUrl.includes("passport");
      case "baijiahao":
        if (currentUrl.includes("login")) {
          return true;
        }
        return false;
      case "toutiao":
        return currentUrl.includes("login") || currentUrl.includes("passport");
      case "xiaohongshu":
        return currentUrl.includes("login") || currentUrl.includes("signup");
      default:
        return false;
    }
  }
  /**
   * 异步检测是否在登录页面（通过检查页面元素）
   * 用于百家号等平台，需要检查页面中是否存在登录按钮
   */
  async isOnLoginPageAsync() {
    if (!this.page) {
      return false;
    }
    await this.page.waitForTimeout(1e3);
    const currentUrl = this.page.url();
    switch (this.platform) {
      case "baijiahao":
        if (currentUrl.includes("login")) {
          return true;
        }
        try {
          const loginBtnSelectors = [
            '[data-testid="bjh-login-btn"]',
            "button.loginBtn--lZVgU",
            "header button",
            'button:has-text("\u767B\u5F55")'
          ];
          for (const selector of loginBtnSelectors) {
            const btn = await this.page.$(selector);
            if (btn) {
              const isVisible = await btn.isVisible();
              if (isVisible) {
                return true;
              }
            }
          }
        } catch {
        }
        return false;
      default:
        return this.isOnLoginPage();
    }
  }
  /**
   * 检测登录是否成功
   * 根据各平台的URL变化和页面特征判断登录状态
   */
  async checkLoginSuccess() {
    if (!this.page) {
      return false;
    }
    const currentUrl = this.page.url();
    switch (this.platform) {
      case "zhihu":
        if (currentUrl.includes("zhihu.com") && !currentUrl.includes("signin") && !currentUrl.includes("login")) {
          try {
            const hasAvatar = await this.page.$('.AppHeader-profile img, .GlobalSideBar-userAvatar, [class*="Avatar"]');
            return hasAvatar !== null;
          } catch {
            return !currentUrl.includes("signin");
          }
        }
        return false;
      case "bilibili":
        if (currentUrl.includes("bilibili.com") && !currentUrl.includes("passport") || currentUrl.includes("member.bilibili.com")) {
          return true;
        }
        return false;
      case "baijiahao":
        if (currentUrl.includes("baijiahao.baidu.com") && !currentUrl.includes("login")) {
          try {
            const hasUserAvatar = await this.page.$('.user-avatar, .user-info, [class*="avatar"]');
            return hasUserAvatar !== null;
          } catch {
            return !currentUrl.includes("login");
          }
        }
        return false;
      case "toutiao":
        if (currentUrl.includes("toutiao.com") && !currentUrl.includes("login") && !currentUrl.includes("passport")) {
          try {
            const hasUserAvatar = await this.page.$('.avatar-wrap, .user-avatar, [class*="avatar"]');
            return hasUserAvatar !== null;
          } catch {
            return !currentUrl.includes("login");
          }
        }
        return false;
      case "xiaohongshu":
        if (currentUrl.includes("xiaohongshu.com") && !currentUrl.includes("login") && !currentUrl.includes("signup")) {
          try {
            const hasUserAvatar = await this.page.$('.user-avatar, [class*="avatar"], [class*="user-info"]');
            return hasUserAvatar !== null;
          } catch {
            return !currentUrl.includes("login");
          }
        }
        return false;
      default:
        return false;
    }
  }
  /**
   * 等待登录成功
   * 使用轮询机制检测登录状态
   */
  async waitForLogin(timeout = 12e4) {
    if (!this.page) {
      throw new Error("Page not initialized");
    }
    const platformInfo = PLATFORMS[this.platform];
    const checkInterval = 2e3;
    const startTime = Date.now();
    console.log(`\u23F3 \u7B49\u5F85 ${platformInfo.displayName} \u767B\u5F55...\uFF08\u8D85\u65F6\u65F6\u95F4: ${timeout / 1e3}\u79D2\uFF09`);
    let dots = 0;
    while (Date.now() - startTime < timeout) {
      const isLoggedIn = await this.checkLoginSuccess();
      if (isLoggedIn) {
        console.log("");
        console.log("\u2705 \u68C0\u6D4B\u5230\u767B\u5F55\u6210\u529F\uFF01");
        await this.saveCookies();
        return true;
      }
      dots = (dots + 1) % 4;
      const dotsStr = ".".repeat(dots);
      process.stdout.write(`\r\u{1F50D} \u68C0\u6D4B\u767B\u5F55\u72B6\u6001\u4E2D${dotsStr}   `);
      await this.page.waitForTimeout(checkInterval);
    }
    console.log("");
    return false;
  }
  /**
   * 检查是否已登录（通过访问发布页面检测）
   */
  async checkLoginStatus() {
    if (!this.page) {
      return false;
    }
    const platformInfo = PLATFORMS[this.platform];
    try {
      await this.page.goto(platformInfo.publishUrl, {
        waitUntil: "domcontentloaded",
        timeout: 3e4
      });
      await this.page.waitForTimeout(2e3);
      const currentUrl = this.page.url();
      if (currentUrl.includes("login") || currentUrl.includes("signin")) {
        return false;
      }
      return true;
    } catch (error) {
      console.error("Failed to check login status:", error);
      return false;
    }
  }
  /**
   * 关闭浏览器
   */
  async close() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.context = null;
      this.page = null;
    }
  }
  /**
   * 截图
   */
  async screenshot(path3) {
    if (!this.page) {
      throw new Error("Page not initialized");
    }
    await this.page.screenshot({ path: path3, fullPage: true });
  }
};

// src/lib/base-adapter.ts
init_cookie_manager();
var BaseAdapter = class {
  platform;
  platformInfo;
  browserManager;
  cookieManager;
  constructor(platform) {
    this.platform = platform;
    this.platformInfo = PLATFORMS[platform];
    this.browserManager = new BrowserManager(platform);
    this.cookieManager = new CookieManager(platform);
  }
  /**
   * 获取平台名称
   */
  getPlatformName() {
    return this.platform;
  }
  /**
   * 获取平台显示名称
   */
  getDisplayName() {
    return this.platformInfo.displayName;
  }
  /**
   * 打开登录页面
   */
  async openLoginPage() {
    await this.browserManager.launch();
    await this.browserManager.gotoLoginPage();
    return `\u8BF7\u5728\u6253\u5F00\u7684\u6D4F\u89C8\u5668\u4E2D\u626B\u7801\u767B\u5F55${this.platformInfo.displayName}\uFF0C\u767B\u5F55\u6210\u529F\u540E\u5C06\u81EA\u52A8\u4FDD\u5B58\u767B\u5F55\u72B6\u6001\u3002`;
  }
  /**
   * 等待登录完成
   */
  async waitForLogin(timeout) {
    const success = await this.browserManager.waitForLogin(timeout);
    if (success) {
      await this.browserManager.close();
    }
    return success;
  }
  /**
   * 检查登录状态
   */
  async checkLoginStatus() {
    const hasCookies = await this.cookieManager.hasValidCookies();
    if (!hasCookies) {
      return false;
    }
    try {
      await this.browserManager.launch();
      const isLoggedIn = await this.browserManager.checkLoginStatus();
      await this.browserManager.close();
      return isLoggedIn;
    } catch (error) {
      await this.browserManager.close();
      return false;
    }
  }
  /**
   * 清除登录状态
   */
  async logout() {
    await this.cookieManager.clearCookies();
  }
  /**
   * 填充文章标题
   */
  async fillTitle(title) {
    throw new Error("fillTitle must be implemented by subclass");
  }
  /**
   * 填充文章内容
   */
  async fillContent(content) {
    throw new Error("fillContent must be implemented by subclass");
  }
  /**
   * 上传封面图片
   */
  async uploadCover(imagePath) {
    throw new Error("uploadCover must be implemented by subclass");
  }
  /**
   * 设置标签
   */
  async setTags(tags) {
    throw new Error("setTags must be implemented by subclass");
  }
  /**
   * 点击发布按钮
   */
  async clickPublish() {
    throw new Error("clickPublish must be implemented by subclass");
  }
  /**
   * 获取发布后的文章链接
   */
  async getArticleUrl() {
    throw new Error("getArticleUrl must be implemented by subclass");
  }
  /**
   * 截图保存当前页面状态
   */
  async screenshot(path3) {
    await this.browserManager.screenshot(path3);
  }
};

// src/lib/cover-image.ts
import path2 from "path";
import fs3 from "fs";
import { fileURLToPath } from "url";
var __filename = fileURLToPath(import.meta.url);
var __dirname = path2.dirname(__filename);
var config = null;
function getConfigPath() {
  return path2.join(__dirname, "..", "..", "config", "cover-image.json");
}
function loadConfig() {
  if (config) {
    return config;
  }
  const configPath = getConfigPath();
  try {
    if (fs3.existsSync(configPath)) {
      const content = fs3.readFileSync(configPath, "utf-8");
      config = JSON.parse(content);
      return config;
    }
  } catch (error) {
    console.error("\u52A0\u8F7D\u914D\u7F6E\u6587\u4EF6\u5931\u8D25:", error);
  }
  return null;
}
function getPexelsApiKey() {
  const cfg = loadConfig();
  return cfg?.pexels?.apiKey || null;
}
var AI_PROMPT_TEMPLATE = `\u4F60\u662F\u4E00\u4E2A\u4E13\u4E1A\u7684\u56FE\u7247\u641C\u7D22\u52A9\u624B\u3002\u8BF7\u6839\u636E\u4EE5\u4E0B\u6587\u7AE0\u6807\u9898\u548C\u5185\u5BB9\uFF0C\u63D0\u53D6\u9002\u5408\u5728 Pexels \u56FE\u7247\u5E93\u641C\u7D22\u7684\u82F1\u6587\u5173\u952E\u8BCD\u3002

\u6587\u7AE0\u6807\u9898\uFF1A{title}
\u6587\u7AE0\u5185\u5BB9\u6458\u8981\uFF1A{content}

\u8981\u6C42\uFF1A
1. \u8FD4\u56DE 2-4 \u4E2A\u82F1\u6587\u5173\u952E\u8BCD\uFF0C\u7528\u7A7A\u683C\u5206\u9694
2. \u5173\u952E\u8BCD\u8981\u80FD\u51C6\u786E\u53CD\u6620\u6587\u7AE0\u4E3B\u9898\uFF0C\u9002\u5408\u641C\u7D22\u76F8\u5173\u914D\u56FE
3. \u4E0D\u8981\u8FD4\u56DE\u4EFB\u4F55\u89E3\u91CA\uFF0C\u53EA\u8FD4\u56DE\u5173\u952E\u8BCD\u672C\u8EAB
4. \u5982\u679C\u6587\u7AE0\u6D89\u53CA\u5177\u4F53\u4EA7\u54C1\u6216\u6280\u672F\uFF0C\u4F7F\u7528\u901A\u7528\u7684\u82F1\u6587\u672F\u8BED
5. \u5173\u952E\u8BCD\u8981\u5177\u4F53\uFF0C\u907F\u514D\u8FC7\u4E8E\u62BD\u8C61

\u793A\u4F8B\uFF1A
- \u6807\u9898"AI\u73A9\u5177\u4EA7\u4E1A\u89C2\u5BDF" -> "smart toys technology artificial intelligence"
- \u6807\u9898"\u7F16\u7A0B\u5165\u95E8\u6307\u5357" -> "programming coding computer technology"
- \u6807\u9898"\u7F8E\u98DF\u63A2\u5E97\u8BB0\u5F55" -> "food restaurant dining cuisine"`;
var AI_PROVIDERS = {
  kimi: {
    name: "Kimi",
    url: "https://api.moonshot.cn/v1/chat/completions",
    defaultModel: "moonshot-v1-8k"
  },
  deepseek: {
    name: "DeepSeek",
    url: "https://api.deepseek.com/v1/chat/completions",
    defaultModel: "deepseek-chat"
  },
  zhipu: {
    name: "\u667A\u8C31 AI",
    url: "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    defaultModel: "glm-4-flash"
  }
};
async function callAIProvider(provider, apiKey, model, prompt) {
  const providerInfo = AI_PROVIDERS[provider];
  try {
    const response = await fetch(providerInfo.url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model,
        messages: [{ role: "user", content: prompt }],
        temperature: 0.3,
        max_tokens: 50
      })
    });
    if (!response.ok) {
      console.error(`${providerInfo.name} \u8C03\u7528\u5931\u8D25:`, response.status);
      return null;
    }
    const result = await response.json();
    const keywords = result.choices?.[0]?.message?.content?.trim();
    if (keywords) {
      console.log(`\u{1F916} ${providerInfo.name} \u63D0\u53D6\u5173\u952E\u8BCD\uFF1A${keywords}`);
      return keywords;
    }
    return null;
  } catch (error) {
    console.error(`${providerInfo.name} \u8C03\u7528\u5931\u8D25:`, error);
    return null;
  }
}
async function extractKeywordsByAI(title, content = "") {
  const cfg = loadConfig();
  const aiConfig = cfg?.ai;
  if (!aiConfig) {
    return null;
  }
  const prompt = AI_PROMPT_TEMPLATE.replace("{title}", title).replace("{content}", content.slice(0, 500) || "\u65E0");
  const priority = cfg?.aiPriority || ["kimi", "deepseek", "zhipu"];
  for (const provider of priority) {
    const providerConfig = aiConfig[provider];
    if (!providerConfig?.apiKey || providerConfig.apiKey === "YOUR_KIMI_API_KEY" || providerConfig.apiKey === "YOUR_DEEPSEEK_API_KEY" || providerConfig.apiKey === "YOUR_ZHIPU_API_KEY" || providerConfig.enabled === false) {
      continue;
    }
    const model = providerConfig.model || AI_PROVIDERS[provider].defaultModel;
    const keywords = await callAIProvider(provider, providerConfig.apiKey, model, prompt);
    if (keywords) {
      return keywords;
    }
  }
  return null;
}
var KEYWORD_MAP = {
  "ai": "artificial intelligence",
  "\u4EBA\u5DE5\u667A\u80FD": "artificial intelligence",
  "\u7F16\u7A0B": "programming coding",
  "\u4EE3\u7801": "coding programming",
  "\u56FE\u7247": "image technology",
  "\u622A\u56FE": "screenshot technology",
  "\u6309\u94AE": "button interface",
  "\u754C\u9762": "interface ui",
  "\u5546\u4E1A": "business",
  "\u4F1A\u8BAE": "meeting",
  "\u5199\u4F5C": "writing",
  "\u8BFB\u4E66": "reading books",
  "\u81EA\u7136": "nature",
  "\u98CE\u666F": "landscape",
  "\u73A9\u5177": "smart toys technology",
  "\u4EA7\u4E1A": "industry technology",
  "\u79D1\u6280": "technology",
  "\u65B0\u4EAE\u70B9": "innovation technology",
  "\u7F8E\u98DF": "food cuisine",
  "\u65C5\u6E38": "travel tourism",
  "\u5065\u8EAB": "fitness exercise",
  "\u97F3\u4E50": "music",
  "\u7535\u5F71": "movie film",
  "\u6E38\u620F": "game gaming",
  "\u6559\u80B2": "education learning",
  "\u91D1\u878D": "finance business",
  "\u533B\u7597": "medical health",
  "\u6C7D\u8F66": "car automotive",
  "\u623F\u4EA7": "real estate house",
  "\u65F6\u5C1A": "fashion style",
  "\u80B2\u513F": "parenting family",
  "\u5BA0\u7269": "pet animal",
  "\u804C\u573A": "workplace career",
  "\u5FC3\u7406": "psychology mind",
  "\u5386\u53F2": "history",
  "\u6587\u5316": "culture",
  "\u4F53\u80B2": "sports",
  "\u65B0\u95FB": "news media"
};
function extractKeywordsLocal(title) {
  const titleLower = title.toLowerCase();
  const keywords = [];
  for (const [cn, en] of Object.entries(KEYWORD_MAP)) {
    if (titleLower.includes(cn) || title.includes(cn)) {
      if (!keywords.includes(en)) {
        keywords.push(en);
      }
    }
  }
  if (keywords.length > 0) {
    return keywords.slice(0, 3).join(" ");
  }
  if (/[\u4e00-\u9fff]/.test(title)) {
    return "technology innovation";
  }
  return title;
}
async function extractKeywords(title, content = "") {
  const aiKeywords = await extractKeywordsByAI(title, content);
  if (aiKeywords) {
    return aiKeywords;
  }
  console.log("\u{1F4CC} \u4F7F\u7528\u672C\u5730\u5173\u952E\u8BCD\u63D0\u53D6...");
  return extractKeywordsLocal(title);
}
async function getCoverForArticle(params) {
  const {
    title = "",
    contentPreview = "",
    keywords,
    orientation = "landscape",
    size = "large2x"
  } = params;
  const apiKey = getPexelsApiKey();
  if (!apiKey) {
    console.error("\u274C Pexels API Key \u672A\u914D\u7F6E");
    return null;
  }
  let finalKeywords;
  if (keywords) {
    finalKeywords = keywords;
    console.log("\u{1F4DD} \u4F7F\u7528\u5916\u90E8\u63D0\u4F9B\u7684\u5173\u952E\u8BCD");
  } else {
    finalKeywords = await extractKeywords(title, contentPreview);
    console.log(`\u{1F4DD} \u6587\u7AE0\u4E3B\u9898\uFF1A${title}`);
  }
  console.log(`\u{1F50D} \u641C\u7D22\u5173\u952E\u8BCD\uFF1A${finalKeywords}`);
  const searchParams = new URLSearchParams({
    query: finalKeywords,
    orientation,
    size: "large",
    per_page: "5",
    page: "1"
  });
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3e4);
    const response = await fetch(`https://api.pexels.com/v1/search?${searchParams}`, {
      headers: {
        "Authorization": apiKey
      },
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (!response.ok) {
      console.error("Pexels API \u8C03\u7528\u5931\u8D25:", response.status);
      return null;
    }
    const data = await response.json();
    const photos = data.photos;
    if (!photos || photos.length === 0) {
      console.log("\u26A0\uFE0F \u672A\u627E\u5230\u76F8\u5173\u56FE\u7247\uFF0C\u4F7F\u7528\u5907\u7528\u5173\u952E\u8BCD\u91CD\u8BD5...");
      return getCoverWithFallback("technology", orientation, size);
    }
    console.log(`
\u2705 \u627E\u5230 ${photos.length} \u5F20\u5019\u9009\u5C01\u9762\u56FE\uFF1A
`);
    photos.forEach((photo, i) => {
      console.log(`\u9009\u9879 ${i + 1}:`);
      console.log(`  \u{1F4F8} \u6444\u5F71\u5E08\uFF1A${photo.photographer}`);
      console.log(`  \u{1F5BC}\uFE0F  \u9884\u89C8\uFF1A${photo.src.medium}`);
      console.log(`  \u{1F517} \u9AD8\u6E05\u56FE\uFF1A${photo.src[size]}`);
      console.log();
    });
    const selected = photos[0];
    console.log(`\u{1F3AF} \u5DF2\u9009\u62E9\u9ED8\u8BA4\u5C01\u9762\uFF08ID: ${selected.id}\uFF09`);
    return selected.src[size] || null;
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      console.error("\u274C API \u8C03\u7528\u8D85\u65F6\uFF0830\u79D2\uFF09");
    } else {
      console.error("\u274C API \u8C03\u7528\u5931\u8D25:", error);
    }
    return null;
  }
}
async function getCoverWithFallback(keyword, orientation, size) {
  const apiKey = getPexelsApiKey();
  if (!apiKey) {
    return null;
  }
  const params = new URLSearchParams({
    query: keyword,
    orientation,
    per_page: "1"
  });
  try {
    const response = await fetch(`https://api.pexels.com/v1/search?${params}`, {
      headers: {
        "Authorization": apiKey
      }
    });
    const data = await response.json();
    if (data.photos && data.photos.length > 0) {
      return data.photos[0].src[size] || null;
    }
  } catch {
  }
  return null;
}

// src/adapters/zhihu.ts
import { tmpdir } from "os";
import { join } from "path";
import { writeFileSync, unlinkSync, existsSync } from "fs";
import { createHash } from "crypto";
var ZhihuAdapter = class extends BaseAdapter {
  tempFiles = [];
  constructor() {
    super("zhihu");
  }
  /**
   * 从 URL 下载图片到临时文件
   */
  async downloadImageToTemp(imageUrl) {
    try {
      console.log(`   \u{1F4E5} \u6B63\u5728\u4E0B\u8F7D\u5C01\u9762\u56FE\u7247...`);
      const response = await fetch(imageUrl);
      if (!response.ok) {
        console.warn(`   \u26A0\uFE0F \u4E0B\u8F7D\u5931\u8D25: HTTP ${response.status}`);
        return null;
      }
      const buffer = Buffer.from(await response.arrayBuffer());
      const hash = createHash("md5").update(imageUrl).digest("hex").slice(0, 8);
      const ext = imageUrl.includes(".png") ? "png" : "jpg";
      const tempPath = join(tmpdir(), `cover-${hash}.${ext}`);
      writeFileSync(tempPath, buffer);
      this.tempFiles.push(tempPath);
      console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0B\u8F7D: ${tempPath}`);
      return tempPath;
    } catch (error) {
      console.warn(`   \u26A0\uFE0F \u4E0B\u8F7D\u5C01\u9762\u56FE\u7247\u5931\u8D25: ${error instanceof Error ? error.message : String(error)}`);
      return null;
    }
  }
  /**
   * 清理临时文件
   */
  cleanupTempFiles() {
    for (const file of this.tempFiles) {
      try {
        if (existsSync(file)) {
          unlinkSync(file);
        }
      } catch {
      }
    }
    this.tempFiles = [];
  }
  /**
   * 发布文章到知乎
   * @param article 文章内容
   * @param testMode 测试模式，为true时不点击发布按钮
   */
  async publish(article, testMode = false) {
    try {
      console.log(`\u{1F680} \u5F00\u59CB\u53D1\u5E03\u6587\u7AE0\u5230\u77E5\u4E4E...`);
      if (testMode) {
        console.log("\u{1F4DD} \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u5C06\u586B\u5199\u6587\u7AE0\u4F46\u4E0D\u53D1\u5E03");
      }
      await this.browserManager.launch();
      const page = this.browserManager.getPage();
      if (!page) {
        throw new Error("Page not initialized");
      }
      console.log("\u{1F4F1} \u5BFC\u822A\u5230\u53D1\u5E03\u9875\u9762...");
      await this.browserManager.gotoPublishPage();
      await page.waitForTimeout(2e3);
      if (this.browserManager.isOnLoginPage()) {
        console.log("\u26A0\uFE0F \u68C0\u6D4B\u5230\u672A\u767B\u5F55\uFF0C\u5F00\u59CB\u767B\u5F55\u6D41\u7A0B...");
        console.log("\u8BF7\u5728\u6D4F\u89C8\u5668\u4E2D\u626B\u7801\u767B\u5F55\u77E5\u4E4E...");
        const loginSuccess = await this.browserManager.waitForLogin(12e4);
        if (!loginSuccess) {
          await this.browserManager.close();
          return {
            success: false,
            platform: this.platform,
            message: "\u767B\u5F55\u8D85\u65F6\uFF0C\u8BF7\u91CD\u8BD5"
          };
        }
        console.log("\u{1F4F1} \u767B\u5F55\u6210\u529F\uFF0C\u7EE7\u7EED\u53D1\u5E03\u6D41\u7A0B...");
        await this.browserManager.gotoPublishPage();
        await page.waitForTimeout(2e3);
      }
      console.log("\u{1F4DD} \u586B\u5145\u6587\u7AE0\u6807\u9898...");
      await this.fillTitle(article.title);
      console.log("\u{1F4DD} \u586B\u5145\u6587\u7AE0\u5185\u5BB9...");
      await this.fillContent(article.content);
      let coverImagePath = null;
      if (article.coverImage) {
        console.log("\u{1F5BC}\uFE0F \u4F7F\u7528\u7528\u6237\u63D0\u4F9B\u7684\u5C01\u9762\u56FE\u7247...");
        if (article.coverImage.startsWith("http")) {
          coverImagePath = await this.downloadImageToTemp(article.coverImage);
        } else {
          coverImagePath = article.coverImage;
        }
      } else {
        console.log("\u{1F5BC}\uFE0F \u672A\u63D0\u4F9B\u5C01\u9762\u56FE\u7247\uFF0C\u6B63\u5728\u81EA\u52A8\u751F\u6210...");
        const coverUrl = await getCoverForArticle({
          title: article.title,
          contentPreview: article.content,
          orientation: "landscape",
          size: "large2x"
        });
        if (coverUrl) {
          coverImagePath = await this.downloadImageToTemp(coverUrl);
        } else {
          console.warn("   \u26A0\uFE0F \u5C01\u9762\u56FE\u7247\u751F\u6210\u5931\u8D25\uFF0C\u5C06\u4E0D\u8BBE\u7F6E\u5C01\u9762");
        }
      }
      if (coverImagePath) {
        console.log("\u{1F4E4} \u4E0A\u4F20\u5C01\u9762\u56FE\u7247...");
        await this.uploadCover(coverImagePath);
      }
      if (article.tags && article.tags.length > 0) {
        console.log("\u{1F3F7}\uFE0F \u8BBE\u7F6E\u6807\u7B7E...");
        await this.setTags(article.tags);
      }
      if (testMode) {
        console.log("");
        console.log("===========================================");
        console.log("\u2705 \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u5DF2\u586B\u5199\u5B8C\u6210\uFF01");
        console.log("\u26A0\uFE0F  \u672A\u70B9\u51FB\u53D1\u5E03\u6309\u94AE\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("===========================================");
        console.log("");
        const screenshotPath = `./test-screenshot-zhihu-${Date.now()}.png`;
        await this.screenshot(screenshotPath);
        console.log(`\u{1F4F8} \u622A\u56FE\u5DF2\u4FDD\u5B58: ${screenshotPath}`);
        await this.browserManager.saveCookies();
        console.log("");
        console.log("\u{1F4A1} \u6D4F\u89C8\u5668\u5C06\u4FDD\u6301\u6253\u5F00\u72B6\u6001\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("   \u68C0\u67E5\u5B8C\u6210\u540E\uFF0C\u8BF7\u624B\u52A8\u5173\u95ED\u6D4F\u89C8\u5668\u7A97\u53E3");
        console.log("");
        return {
          success: true,
          platform: this.platform,
          message: "\u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u5DF2\u586B\u5199\u5B8C\u6210\uFF0C\u672A\u53D1\u5E03",
          testMode: true
        };
      }
      console.log("\u{1F4E4} \u70B9\u51FB\u53D1\u5E03\u6309\u94AE...");
      await this.clickPublish();
      const articleUrl = await this.getArticleUrl();
      await this.browserManager.saveCookies();
      await this.browserManager.close();
      this.cleanupTempFiles();
      return {
        success: true,
        platform: this.platform,
        message: "\u6587\u7AE0\u53D1\u5E03\u6210\u529F",
        url: articleUrl || void 0
      };
    } catch (error) {
      this.cleanupTempFiles();
      await this.browserManager.close();
      return {
        success: false,
        platform: this.platform,
        message: "\u53D1\u5E03\u5931\u8D25",
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
  /**
   * 填充标题
   */
  async fillTitle(title) {
    const page = this.browserManager.getPage();
    if (!page) return;
    const titleSelectors = [
      'textarea[placeholder*="\u6807\u9898"]',
      'textarea[placeholder*="\u8F93\u5165\u6807\u9898"]',
      ".WriteIndex-titleInput textarea",
      ".title-input textarea",
      'textarea[class*="title"]',
      "textarea.Input",
      'input[placeholder*="\u8F93\u5165\u6807\u9898"]',
      'input[placeholder*="\u6807\u9898"]'
    ];
    let titleInput = null;
    for (const selector of titleSelectors) {
      try {
        titleInput = await page.$(selector);
        if (titleInput) {
          console.log(`   \u2705 \u627E\u5230\u6807\u9898\u8F93\u5165\u6846\uFF0C\u4F7F\u7528\u9009\u62E9\u5668: ${selector}`);
          break;
        }
      } catch {
        continue;
      }
    }
    if (!titleInput) {
      console.log("   \u26A0\uFE0F \u9884\u8BBE\u9009\u62E9\u5668\u672A\u627E\u5230\uFF0C\u5C1D\u8BD5\u67E5\u627E\u6240\u6709 textarea/input \u5143\u7D20...");
      const textareas = await page.$$("textarea");
      const inputs = await page.$$('input[type="text"], input:not([type])');
      console.log(`   \u{1F4CB} \u9875\u9762\u5171\u6709 ${textareas.length} \u4E2Atextarea, ${inputs.length} \u4E2Ainput\u5143\u7D20`);
      for (const textarea of textareas) {
        const placeholder = await textarea.getAttribute("placeholder");
        if (placeholder?.includes("\u6807\u9898")) {
          titleInput = textarea;
          console.log(`   \u2705 \u627E\u5230\u6807\u9898\u8F93\u5165\u6846(textarea): placeholder="${placeholder}"`);
          break;
        }
      }
      if (!titleInput) {
        for (const input of inputs) {
          const placeholder = await input.getAttribute("placeholder");
          const className = await input.getAttribute("class");
          if (placeholder?.includes("\u6807\u9898") || className?.toLowerCase().includes("title")) {
            titleInput = input;
            console.log(`   \u2705 \u627E\u5230\u6807\u9898\u8F93\u5165\u6846(input): placeholder="${placeholder}", class="${className}"`);
            break;
          }
        }
      }
    }
    if (titleInput) {
      await titleInput.click();
      await titleInput.fill(title);
      console.log(`   \u{1F4DD} \u6807\u9898\u5DF2\u586B\u5145: ${title}`);
    } else {
      console.error("   \u274C \u672A\u627E\u5230\u6807\u9898\u8F93\u5165\u6846\uFF0C\u5C1D\u8BD5\u4F7F\u7528\u952E\u76D8\u8F93\u5165\u4F5C\u4E3A\u540E\u5907\u65B9\u6848...");
      await page.keyboard.type(title);
      console.log(`   \u26A0\uFE0F \u6807\u9898\u5DF2\u901A\u8FC7\u952E\u76D8\u8F93\u5165: ${title}`);
    }
  }
  /**
   * 填充内容
   */
  async fillContent(content) {
    const page = this.browserManager.getPage();
    if (!page) return;
    const contentSelectors = [
      ".public-DraftEditor-content",
      '.DraftEditor-editorContainer [contenteditable="true"]',
      '[data-contents="true"]',
      ".ql-editor",
      '[contenteditable="true"]'
    ];
    let contentEditor = null;
    for (const selector of contentSelectors) {
      try {
        contentEditor = await page.$(selector);
        if (contentEditor) {
          console.log(`   \u4F7F\u7528\u9009\u62E9\u5668: ${selector}`);
          break;
        }
      } catch {
        continue;
      }
    }
    if (contentEditor) {
      await contentEditor.click();
      await page.waitForTimeout(500);
      await contentEditor.fill("");
      await page.keyboard.type(content, { delay: 10 });
      console.log(`   \u5185\u5BB9\u957F\u5EA6: ${content.length} \u5B57\u7B26`);
    } else {
      console.warn("   \u672A\u627E\u5230\u5185\u5BB9\u7F16\u8F91\u5668\uFF0C\u5C1D\u8BD5\u70B9\u51FB\u9875\u9762\u4E2D\u592E...");
      const viewport = page.viewportSize();
      if (viewport) {
        await page.mouse.click(viewport.width / 2, viewport.height / 2);
        await page.keyboard.type(content, { delay: 10 });
        console.log(`   \u5185\u5BB9\u957F\u5EA6: ${content.length} \u5B57\u7B26`);
      }
    }
  }
  /**
   * 上传封面 - 修复版，上传到右侧封面区域
   */
  async uploadCover(imagePath) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      console.log("   \u{1F50D} \u5BFB\u627E\u5C01\u9762\u4E0A\u4F20\u533A\u57DF...");
      const coverInputSelectors = [
        "input.UploadPicture-input",
        'input[type="file"][accept*=".jpg"], input[type="file"][accept*=".png"]',
        '.UploadPicture-wrapper input[type="file"]',
        "label.UploadPicture-wrapper input"
      ];
      let uploadSuccess = false;
      for (const selector of coverInputSelectors) {
        try {
          const input = await page.$(selector);
          if (input) {
            const isVisible = await input.isVisible().catch(() => false);
            const isHidden = !isVisible;
            console.log(`   \u627E\u5230\u5C01\u9762\u4E0A\u4F20\u8F93\u5165\u6846: ${selector} (visible: ${isVisible})`);
            await input.setInputFiles(imagePath);
            await page.waitForTimeout(2e3);
            console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0A\u4F20\u5230\u5C01\u9762\u533A\u57DF: ${imagePath}`);
            uploadSuccess = true;
            break;
          }
        } catch {
          continue;
        }
      }
      if (!uploadSuccess) {
        const coverAreaSelectors = [
          "label.UploadPicture-wrapper",
          ".css-1i9x2dq",
          "text=\u6DFB\u52A0\u6587\u7AE0\u5C01\u9762",
          "text=\u6DFB\u52A0\u5C01\u9762"
        ];
        for (const selector of coverAreaSelectors) {
          try {
            const area = await page.$(selector);
            if (area) {
              console.log(`   \u627E\u5230\u5C01\u9762\u533A\u57DF: ${selector}`);
              await area.click();
              await page.waitForTimeout(1e3);
              const input = await page.$('input[type="file"]');
              if (input) {
                await input.setInputFiles(imagePath);
                await page.waitForTimeout(2e3);
                console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0A\u4F20\uFF08\u70B9\u51FB\u540E\u4E0A\u4F20\uFF09: ${imagePath}`);
                uploadSuccess = true;
                break;
              }
            }
          } catch {
            continue;
          }
        }
      }
      if (!uploadSuccess) {
        const allInputs = await page.$$('input[type="file"]');
        console.log(`   \u{1F4CB} \u9875\u9762\u5171\u6709 ${allInputs.length} \u4E2A\u6587\u4EF6\u8F93\u5165\u6846`);
        for (const input of allInputs) {
          try {
            const box = await input.boundingBox();
            if (box) {
              console.log(`   \u8F93\u5165\u6846\u4F4D\u7F6E: x=${box.x}, y=${box.y}, width=${box.width}, height=${box.height}`);
              const viewport = page.viewportSize();
              if (viewport && box.x > viewport.width / 2) {
                await input.setInputFiles(imagePath);
                await page.waitForTimeout(2e3);
                console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0A\u4F20\uFF08\u901A\u8FC7\u4F4D\u7F6E\u5224\u65AD\uFF09: ${imagePath}`);
                uploadSuccess = true;
                break;
              }
            }
          } catch {
            continue;
          }
        }
      }
      if (!uploadSuccess) {
        console.warn("   \u26A0\uFE0F \u672A\u80FD\u627E\u5230\u5C01\u9762\u4E0A\u4F20\u533A\u57DF\uFF0C\u8DF3\u8FC7\u5C01\u9762\u4E0A\u4F20");
      }
    } catch (error) {
      console.warn("   \u26A0\uFE0F \u5C01\u9762\u4E0A\u4F20\u5931\u8D25:", error instanceof Error ? error.message : String(error));
    }
  }
  /**
   * 设置标签
   */
  async setTags(tags) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      const topicButtonSelectors = [
        'button:has-text("\u8BDD\u9898")',
        '[class*="topic"] button',
        ".TopicSelectButton",
        '[class*="TagButton"]'
      ];
      for (const selector of topicButtonSelectors) {
        try {
          const button = await page.$(selector);
          if (button) {
            await button.click();
            await page.waitForTimeout(500);
            console.log("   \u70B9\u51FB\u8BDD\u9898\u6309\u94AE\u5C55\u5F00");
            break;
          }
        } catch {
          continue;
        }
      }
      const tagInputSelectors = [
        'input[placeholder*="\u641C\u7D22\u8BDD\u9898"]:visible',
        'input[placeholder*="\u8BDD\u9898"]:visible',
        'input[aria-label*="\u8BDD\u9898"]:visible',
        ".TopicSelector input",
        '[class*="topic"] input:visible'
      ];
      let tagInput = null;
      for (const selector of tagInputSelectors) {
        try {
          tagInput = await page.$(selector);
          if (tagInput) {
            const isVisible = await tagInput.isVisible();
            if (isVisible) {
              console.log(`   \u627E\u5230\u8BDD\u9898\u8F93\u5165\u6846: ${selector}`);
              break;
            }
          }
        } catch {
          continue;
        }
      }
      if (!tagInput) {
        console.warn("   \u672A\u627E\u5230\u53EF\u89C1\u7684\u8BDD\u9898\u8F93\u5165\u6846\uFF0C\u8DF3\u8FC7\u6807\u7B7E\u8BBE\u7F6E");
        return;
      }
      for (const tag of tags.slice(0, 5)) {
        await tagInput.fill(tag);
        await page.waitForTimeout(800);
        const dropdownSelectors = [
          ".Popover-content button",
          '[class*="Popover"] button',
          ".css-ogem9c button"
        ];
        let dropdownVisible = false;
        for (const dropdownSelector of dropdownSelectors) {
          try {
            const dropdown = await page.$(dropdownSelector);
            if (dropdown) {
              const isVisible = await dropdown.isVisible().catch(() => false);
              if (isVisible) {
                console.log(`   \u627E\u5230\u8BDD\u9898\u4E0B\u62C9\u6846\uFF0C\u70B9\u51FB\u7B2C\u4E00\u4E2A\u9009\u9879`);
                await dropdown.click();
                await page.waitForTimeout(500);
                dropdownVisible = true;
                break;
              }
            }
          } catch {
            continue;
          }
        }
        if (!dropdownVisible) {
          await page.keyboard.press("Enter");
          await page.waitForTimeout(500);
        }
      }
      console.log(`   \u6807\u7B7E: ${tags.slice(0, 5).join(", ")}`);
    } catch (error) {
      console.warn("   \u6807\u7B7E\u8BBE\u7F6E\u5931\u8D25\uFF0C\u8DF3\u8FC7:", error instanceof Error ? error.message : String(error));
    }
  }
  /**
   * 点击发布
   */
  async clickPublish() {
    const page = this.browserManager.getPage();
    if (!page) return;
    const publishSelector = 'button:has-text("\u53D1\u5E03"), .publish-button, [class*="publish"]';
    await page.waitForSelector(publishSelector, { timeout: 1e4 });
    await page.click(publishSelector);
    await page.waitForTimeout(3e3);
  }
  /**
   * 获取文章链接
   */
  async getArticleUrl() {
    const page = this.browserManager.getPage();
    if (!page) return null;
    try {
      await page.waitForTimeout(2e3);
      const url = page.url();
      if (url.includes("zhuanlan.zhihu.com/p/")) {
        return url;
      }
      return null;
    } catch {
      return null;
    }
  }
};

// src/adapters/bilibili.ts
import { tmpdir as tmpdir2 } from "os";
import { join as join2 } from "path";
import { writeFileSync as writeFileSync2, unlinkSync as unlinkSync2, existsSync as existsSync2 } from "fs";
import { createHash as createHash2 } from "crypto";
var BilibiliAdapter = class extends BaseAdapter {
  tempFiles = [];
  constructor() {
    super("bilibili");
  }
  /**
   * 获取Bilibili编辑器的iframe定位器
   * Bilibili的发布页面使用iframe加载编辑器，所有编辑元素都在iframe中
   */
  getIframeLocator() {
    const page = this.browserManager.getPage();
    if (!page) {
      throw new Error("Page not initialized");
    }
    return page.frameLocator('iframe[src*="member.bilibili.com/york/read-editor"]');
  }
  /**
   * 从 URL 下载图片到临时文件
   */
  async downloadImageToTemp(imageUrl) {
    try {
      console.log(`   \u{1F4E5} \u6B63\u5728\u4E0B\u8F7D\u5C01\u9762\u56FE\u7247...`);
      const response = await fetch(imageUrl);
      if (!response.ok) {
        console.warn(`   \u26A0\uFE0F \u4E0B\u8F7D\u5931\u8D25: HTTP ${response.status}`);
        return null;
      }
      const buffer = Buffer.from(await response.arrayBuffer());
      const hash = createHash2("md5").update(imageUrl).digest("hex").slice(0, 8);
      const ext = imageUrl.includes(".png") ? "png" : "jpg";
      const tempPath = join2(tmpdir2(), `cover-${hash}.${ext}`);
      writeFileSync2(tempPath, buffer);
      this.tempFiles.push(tempPath);
      console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0B\u8F7D: ${tempPath}`);
      return tempPath;
    } catch (error) {
      console.warn(`   \u26A0\uFE0F \u4E0B\u8F7D\u5C01\u9762\u56FE\u7247\u5931\u8D25: ${error instanceof Error ? error.message : String(error)}`);
      return null;
    }
  }
  /**
   * 清理临时文件
   */
  cleanupTempFiles() {
    for (const file of this.tempFiles) {
      try {
        if (existsSync2(file)) {
          unlinkSync2(file);
        }
      } catch {
      }
    }
    this.tempFiles = [];
  }
  /**
   * 发布文章到Bilibili
   * @param article 文章内容
   * @param testMode 测试模式，为true时不点击发布按钮
   */
  async publish(article, testMode = false) {
    try {
      console.log(`\u{1F680} \u5F00\u59CB\u53D1\u5E03\u6587\u7AE0\u5230Bilibili...`);
      if (testMode) {
        console.log("\u{1F4DD} \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u5C06\u586B\u5199\u6587\u7AE0\u4F46\u4E0D\u53D1\u5E03");
      }
      await this.browserManager.launch();
      const page = this.browserManager.getPage();
      if (!page) {
        throw new Error("Page not initialized");
      }
      console.log("\u{1F4F1} \u5BFC\u822A\u5230\u53D1\u5E03\u9875\u9762...");
      await this.browserManager.gotoPublishPage();
      console.log("   \u7B49\u5F85\u9875\u9762\u52A0\u8F7D...");
      await page.waitForTimeout(3e3);
      if (this.browserManager.isOnLoginPage()) {
        console.log("\u26A0\uFE0F \u68C0\u6D4B\u5230\u672A\u767B\u5F55\uFF0C\u5F00\u59CB\u767B\u5F55\u6D41\u7A0B...");
        console.log("\u8BF7\u5728\u6D4F\u89C8\u5668\u4E2D\u626B\u7801\u767B\u5F55Bilibili...");
        const loginSuccess = await this.browserManager.waitForLogin(12e4);
        if (!loginSuccess) {
          await this.browserManager.close();
          return {
            success: false,
            platform: this.platform,
            message: "\u767B\u5F55\u8D85\u65F6\uFF0C\u8BF7\u91CD\u8BD5"
          };
        }
        console.log("\u{1F4F1} \u767B\u5F55\u6210\u529F\uFF0C\u7EE7\u7EED\u53D1\u5E03\u6D41\u7A0B...");
        await this.browserManager.gotoPublishPage();
        await page.waitForTimeout(3e3);
      }
      console.log("\u{1F50D} \u68C0\u67E5\u9875\u9762\u5143\u7D20...");
      const currentUrl = page.url();
      console.log(`   \u5F53\u524DURL: ${currentUrl}`);
      console.log("\u{1F4DD} \u586B\u5145\u6587\u7AE0\u6807\u9898...");
      await this.fillTitle(article.title);
      console.log("\u{1F4DD} \u586B\u5145\u6587\u7AE0\u5185\u5BB9...");
      await this.fillContent(article.content);
      let coverImagePath = null;
      if (article.coverImage) {
        console.log("\u{1F5BC}\uFE0F \u4F7F\u7528\u7528\u6237\u63D0\u4F9B\u7684\u5C01\u9762\u56FE\u7247...");
        if (article.coverImage.startsWith("http")) {
          coverImagePath = await this.downloadImageToTemp(article.coverImage);
        } else {
          coverImagePath = article.coverImage;
        }
      } else {
        console.log("\u{1F5BC}\uFE0F \u672A\u63D0\u4F9B\u5C01\u9762\u56FE\u7247\uFF0C\u6B63\u5728\u81EA\u52A8\u751F\u6210...");
        const coverUrl = await getCoverForArticle({
          title: article.title,
          contentPreview: article.content,
          orientation: "landscape",
          size: "large2x"
        });
        if (coverUrl) {
          coverImagePath = await this.downloadImageToTemp(coverUrl);
        } else {
          console.warn("   \u26A0\uFE0F \u5C01\u9762\u56FE\u7247\u751F\u6210\u5931\u8D25\uFF0C\u5C06\u4E0D\u8BBE\u7F6E\u5C01\u9762");
        }
      }
      if (coverImagePath) {
        console.log("\u{1F4E4} \u4E0A\u4F20\u5C01\u9762\u56FE\u7247...");
        await this.uploadCover(coverImagePath);
      }
      if (article.tags && article.tags.length > 0) {
        console.log("\u{1F3F7}\uFE0F \u8BBE\u7F6E\u6807\u7B7E...");
        await this.setTags(article.tags);
      }
      if (testMode) {
        console.log("");
        console.log("===========================================");
        console.log("\u2705 \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u5DF2\u586B\u5199\u5B8C\u6210\uFF01");
        console.log("\u26A0\uFE0F  \u672A\u70B9\u51FB\u53D1\u5E03\u6309\u94AE\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("===========================================");
        console.log("");
        const screenshotPath = `./test-screenshot-bilibili-${Date.now()}.png`;
        await this.screenshot(screenshotPath);
        console.log(`\u{1F4F8} \u622A\u56FE\u5DF2\u4FDD\u5B58: ${screenshotPath}`);
        await this.browserManager.saveCookies();
        console.log("");
        console.log("\u{1F4A1} \u6D4F\u89C8\u5668\u5C06\u4FDD\u6301\u6253\u5F00\u72B6\u6001\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("   \u68C0\u67E5\u5B8C\u6210\u540E\uFF0C\u8BF7\u624B\u52A8\u5173\u95ED\u6D4F\u89C8\u5668\u7A97\u53E3");
        console.log("");
        return {
          success: true,
          platform: this.platform,
          message: "\u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u5DF2\u586B\u5199\u5B8C\u6210\uFF0C\u672A\u53D1\u5E03",
          testMode: true
        };
      }
      console.log("\u{1F4E4} \u70B9\u51FB\u53D1\u5E03\u6309\u94AE...");
      await this.clickPublish();
      const articleUrl = await this.getArticleUrl();
      await this.browserManager.saveCookies();
      await this.browserManager.close();
      this.cleanupTempFiles();
      return {
        success: true,
        platform: this.platform,
        message: "\u6587\u7AE0\u53D1\u5E03\u6210\u529F",
        url: articleUrl || void 0
      };
    } catch (error) {
      this.cleanupTempFiles();
      await this.browserManager.close();
      return {
        success: false,
        platform: this.platform,
        message: "\u53D1\u5E03\u5931\u8D25",
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
  /**
   * 填充标题
   */
  async fillTitle(title) {
    const page = this.browserManager.getPage();
    if (!page) {
      console.error("   \u274C \u672A\u83B7\u53D6\u5230\u6709\u6548\u9875\u9762");
      return;
    }
    console.log("   \u7B49\u5F85iframe\u52A0\u8F7D...");
    try {
      const iframeLocator = this.getIframeLocator();
      console.log("   \u7B49\u5F85\u6807\u9898\u8F93\u5165\u6846\u51FA\u73B0...");
      const titleSelectors = [
        "textarea.title-input__inner",
        'textarea[placeholder*="\u6807\u9898"]',
        ".title-input textarea",
        'input[placeholder*="\u6807\u9898"]'
      ];
      let foundSelector = "";
      for (const selector of titleSelectors) {
        try {
          console.log(`   \u5C1D\u8BD5\u9009\u62E9\u5668: ${selector}`);
          const locator = iframeLocator.locator(selector);
          await locator.waitFor({ timeout: 1e4, state: "visible" });
          foundSelector = selector;
          console.log(`   \u2705 \u627E\u5230\u6807\u9898\u8F93\u5165\u6846: ${selector}`);
          break;
        } catch (error) {
          console.log(`   \u274C \u672A\u627E\u5230: ${selector}`);
          continue;
        }
      }
      if (foundSelector) {
        const titleInput = iframeLocator.locator(foundSelector);
        console.log("   \u70B9\u51FB\u6807\u9898\u8F93\u5165\u6846...");
        await titleInput.click({ force: true });
        await page.waitForTimeout(500);
        console.log("   \u6E05\u7A7A\u6807\u9898\u8F93\u5165\u6846...");
        await titleInput.fill("");
        await page.waitForTimeout(300);
        console.log(`   \u8F93\u5165\u6807\u9898: ${title}`);
        await titleInput.fill(title);
        await page.waitForTimeout(500);
        console.log("   \u2705 \u6807\u9898\u586B\u5199\u5B8C\u6210");
      } else {
        console.warn("   \u274C \u672A\u627E\u5230\u6807\u9898\u8F93\u5165\u6846");
      }
    } catch (error) {
      console.error("   \u274C iframe\u64CD\u4F5C\u5931\u8D25:", error);
    }
  }
  /**
   * 填充内容
   */
  async fillContent(content) {
    const page = this.browserManager.getPage();
    if (!page) return;
    console.log("   \u7B49\u5F85iframe\u52A0\u8F7D...");
    try {
      const iframeLocator = this.getIframeLocator();
      console.log("   \u7B49\u5F85\u5185\u5BB9\u7F16\u8F91\u5668\u51FA\u73B0...");
      const contentSelectors = [
        ".tiptap.ProseMirror.eva3-editor",
        '.eva3-editor[contenteditable="true"]',
        '.tiptap[contenteditable="true"]',
        '[contenteditable="true"].ProseMirror',
        ".ql-editor",
        '[contenteditable="true"]'
      ];
      let foundSelector = "";
      for (const selector of contentSelectors) {
        try {
          console.log(`   \u5C1D\u8BD5\u9009\u62E9\u5668: ${selector}`);
          const locator = iframeLocator.locator(selector);
          await locator.waitFor({ timeout: 1e4, state: "visible" });
          foundSelector = selector;
          console.log(`   \u2705 \u627E\u5230\u5185\u5BB9\u7F16\u8F91\u5668: ${selector}`);
          break;
        } catch (error) {
          console.log(`   \u274C \u672A\u627E\u5230: ${selector}`);
          continue;
        }
      }
      if (foundSelector) {
        const contentEditor = iframeLocator.locator(foundSelector);
        console.log("   \u70B9\u51FB\u5185\u5BB9\u7F16\u8F91\u5668...");
        await contentEditor.click({ force: true });
        await page.waitForTimeout(1e3);
        console.log("   \u6E05\u7A7A\u7F16\u8F91\u5668\u5185\u5BB9...");
        await contentEditor.press("Control+A");
        await page.waitForTimeout(300);
        await contentEditor.press("Backspace");
        await page.waitForTimeout(500);
        console.log("   \u5F00\u59CB\u8F93\u5165\u5185\u5BB9...");
        const lines = content.split("\n");
        for (let i = 0; i < lines.length; i++) {
          await contentEditor.type(lines[i], { delay: 20 });
          if (i < lines.length - 1) {
            await contentEditor.press("Enter");
            await page.waitForTimeout(200);
          }
        }
        await page.waitForTimeout(500);
        console.log(`   \u2705 \u5185\u5BB9\u586B\u5199\u5B8C\u6210 (${content.length} \u5B57\u7B26)`);
      } else {
        console.warn("   \u274C \u672A\u627E\u5230\u5185\u5BB9\u7F16\u8F91\u5668");
      }
    } catch (error) {
      console.error("   \u274C iframe\u64CD\u4F5C\u5931\u8D25:", error);
    }
  }
  async uploadCover(imagePath) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      console.log("   \u7B49\u5F85iframe\u52A0\u8F7D...");
      const iframeLocator = this.getIframeLocator();
      console.log("   \u{1F50D} \u5BFB\u627E\u5C01\u9762\u4E0A\u4F20\u533A\u57DF...");
      const formItems = await iframeLocator.locator(".form-item").all();
      console.log(`   \u{1F4CB} \u627E\u5230 ${formItems.length} \u4E2A .form-item \u5143\u7D20`);
      for (const formItem of formItems) {
        try {
          const labelText = await formItem.locator(".form-item-label").textContent();
          if (labelText?.includes("\u81EA\u5B9A\u4E49\u5C01\u9762")) {
            console.log('   \u627E\u5230"\u81EA\u5B9A\u4E49\u5C01\u9762"\u8868\u5355\u9879');
            const switchEl = formItem.locator(".vui_switch--switch");
            const isChecked = await switchEl.getAttribute("aria-checked");
            console.log(`   \u5F00\u5173\u72B6\u6001: aria-checked=${isChecked}`);
            if (isChecked !== "true") {
              console.log("   \u6B63\u5728\u5F00\u542F\u81EA\u5B9A\u4E49\u5C01\u9762\u5F00\u5173...");
              await switchEl.click();
              await page.waitForTimeout(1e3);
              console.log("   \u2705 \u5DF2\u5F00\u542F\u81EA\u5B9A\u4E49\u5C01\u9762\u5F00\u5173");
            } else {
              console.log("   \u2705 \u81EA\u5B9A\u4E49\u5C01\u9762\u5F00\u5173\u5DF2\u5F00\u542F");
            }
            break;
          }
        } catch {
          continue;
        }
      }
      await page.waitForTimeout(1e3);
      const uploadButton = iframeLocator.locator('.upload-button:has-text("\u6DFB\u52A0\u5C01\u9762"), .select-cover .upload-button, .upload-button').first();
      try {
        await uploadButton.waitFor({ timeout: 5e3, state: "visible" });
        console.log("   \u627E\u5230\u5C01\u9762\u4E0A\u4F20\u6309\u94AE");
        console.log('   \u70B9\u51FB"\u6DFB\u52A0\u5C01\u9762"\u6309\u94AE...');
        await uploadButton.click();
        await page.waitForTimeout(1e3);
        const fileInput = iframeLocator.locator('input[type="file"]');
        await fileInput.waitFor({ timeout: 5e3, state: "visible" });
        console.log("   \u9009\u62E9\u6587\u4EF6...");
        await fileInput.setInputFiles(imagePath);
        await page.waitForTimeout(2e3);
        console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0A\u4F20: ${imagePath}`);
        await this.confirmCoverCrop();
        return;
      } catch {
        console.log("   \u672A\u627E\u5230\u5C01\u9762\u4E0A\u4F20\u6309\u94AE");
      }
      console.log("   \u5C1D\u8BD5\u76F4\u63A5\u67E5\u627E\u6587\u4EF6\u8F93\u5165\u6846...");
      const fileInputs = await iframeLocator.locator('input[type="file"]').all();
      console.log(`   \u{1F4CB} \u9875\u9762\u5171\u6709 ${fileInputs.length} \u4E2A\u6587\u4EF6\u8F93\u5165\u6846`);
      for (const input of fileInputs) {
        try {
          await input.setInputFiles(imagePath);
          await page.waitForTimeout(2e3);
          console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0A\u4F20: ${imagePath}`);
          await this.confirmCoverCrop();
          return;
        } catch {
          continue;
        }
      }
      console.warn("   \u26A0\uFE0F \u672A\u80FD\u627E\u5230\u5C01\u9762\u4E0A\u4F20\u533A\u57DF\uFF0C\u8DF3\u8FC7\u5C01\u9762\u4E0A\u4F20");
    } catch (error) {
      console.warn("   \u26A0\uFE0F \u5C01\u9762\u4E0A\u4F20\u5931\u8D25:", error instanceof Error ? error.message : String(error));
    }
  }
  /**
   * 确认封面裁剪对话框
   */
  async confirmCoverCrop() {
    const page = this.browserManager.getPage();
    if (!page) return;
    console.log("   \u7B49\u5F85\u5C01\u9762\u88C1\u526A\u5BF9\u8BDD\u6846...");
    try {
      await page.waitForTimeout(2e3);
      const iframeLocator = this.getIframeLocator();
      const confirmSelectors = [
        '.vui_dialog--footer button.vui_button--blue:has-text("\u786E\u5B9A")',
        '.vui_dialog--footer button:has-text("\u786E\u5B9A")',
        ".vui_dialog--btn-confirm",
        'button.vui_button--blue:has-text("\u786E\u5B9A")'
      ];
      for (const selector of confirmSelectors) {
        try {
          console.log(`   \u5C1D\u8BD5\u9009\u62E9\u5668: ${selector}`);
          const confirmButton = iframeLocator.locator(selector).first();
          await confirmButton.waitFor({ timeout: 5e3, state: "visible" });
          console.log("   \u2705 \u627E\u5230\u786E\u8BA4\u6309\u94AE");
          await confirmButton.click();
          await page.waitForTimeout(1e3);
          console.log("   \u2705 \u5DF2\u70B9\u51FB\u786E\u8BA4\u6309\u94AE");
          return;
        } catch {
          console.log(`   \u274C \u672A\u627E\u5230: ${selector}`);
          continue;
        }
      }
      console.log("   \u672A\u627E\u5230\u5C01\u9762\u88C1\u526A\u5BF9\u8BDD\u6846\uFF0C\u7EE7\u7EED\u6267\u884C");
    } catch (error) {
      console.log("   \u5C01\u9762\u88C1\u526A\u5BF9\u8BDD\u6846\u5904\u7406\u5931\u8D25:", error instanceof Error ? error.message : String(error));
    }
  }
  async setTags(tags) {
    console.log("   \u26A0\uFE0F Bilibili\u5DF2\u6539\u4E3A\u5728\u6B63\u6587\u4E2D\u4F7F\u7528 #\u6807\u7B7E# \u683C\u5F0F\u6DFB\u52A0\u6807\u7B7E");
    console.log(`   \u5EFA\u8BAE\u6807\u7B7E: ${tags.map((t) => `#${t}#`).join(" ")}`);
  }
  async clickPublish() {
    const page = this.browserManager.getPage();
    if (!page) return;
    console.log("   \u7B49\u5F85iframe\u52A0\u8F7D...");
    try {
      const iframeLocator = this.getIframeLocator();
      const publishSelectors = [
        'button.vui_button--blue:has-text("\u53D1\u5E03")',
        'button:has-text("\u53D1\u5E03")',
        ".footer-right button.vui_button--blue"
      ];
      for (const selector of publishSelectors) {
        try {
          console.log(`   \u5C1D\u8BD5\u9009\u62E9\u5668: ${selector}`);
          const button = iframeLocator.locator(selector);
          await button.waitFor({ timeout: 1e4, state: "visible" });
          console.log(`   \u2705 \u627E\u5230\u53D1\u5E03\u6309\u94AE: ${selector}`);
          await button.click();
          await page.waitForTimeout(3e3);
          console.log("   \u2705 \u5DF2\u70B9\u51FB\u53D1\u5E03\u6309\u94AE");
          return;
        } catch (error) {
          console.log(`   \u274C \u672A\u627E\u5230: ${selector}`);
          continue;
        }
      }
      console.warn("   \u26A0\uFE0F \u672A\u627E\u5230\u53D1\u5E03\u6309\u94AE");
    } catch (error) {
      console.error("   \u274C iframe\u64CD\u4F5C\u5931\u8D25:", error);
    }
  }
  async getArticleUrl() {
    const page = this.browserManager.getPage();
    if (!page) return null;
    try {
      await page.waitForTimeout(2e3);
      const url = page.url();
      if (url.includes("bilibili.com/read/")) {
        return url;
      }
      return null;
    } catch {
      return null;
    }
  }
};

// src/adapters/baijiahao.ts
import { tmpdir as tmpdir3 } from "os";
import { join as join3 } from "path";
import { writeFileSync as writeFileSync3, unlinkSync as unlinkSync3, existsSync as existsSync3 } from "fs";
import { createHash as createHash3 } from "crypto";
var BaijiahaoAdapter = class extends BaseAdapter {
  tempFiles = [];
  constructor() {
    super("baijiahao");
  }
  /**
   * 从 URL 下载图片到临时文件
   */
  async downloadImageToTemp(imageUrl) {
    try {
      console.log(`   \u{1F4E5} \u6B63\u5728\u4E0B\u8F7D\u5C01\u9762\u56FE\u7247...`);
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3e4);
      const response = await fetch(imageUrl, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      if (!response.ok) {
        console.warn(`   \u26A0\uFE0F \u4E0B\u8F7D\u5931\u8D25: HTTP ${response.status}`);
        return null;
      }
      const buffer = Buffer.from(await response.arrayBuffer());
      const hash = createHash3("md5").update(imageUrl).digest("hex").slice(0, 8);
      const ext = imageUrl.includes(".png") ? "png" : "jpg";
      const tempPath = join3(tmpdir3(), `cover-${hash}.${ext}`);
      writeFileSync3(tempPath, buffer);
      this.tempFiles.push(tempPath);
      console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0B\u8F7D: ${tempPath}`);
      return tempPath;
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        console.warn(`   \u26A0\uFE0F \u4E0B\u8F7D\u5C01\u9762\u56FE\u7247\u8D85\u65F6\uFF0830\u79D2\uFF09`);
      } else {
        console.warn(`   \u26A0\uFE0F \u4E0B\u8F7D\u5C01\u9762\u56FE\u7247\u5931\u8D25: ${error instanceof Error ? error.message : String(error)}`);
      }
      return null;
    }
  }
  /**
   * 清理临时文件
   */
  cleanupTempFiles() {
    for (const file of this.tempFiles) {
      try {
        if (existsSync3(file)) {
          unlinkSync3(file);
        }
      } catch {
      }
    }
    this.tempFiles = [];
  }
  /**
   * 关闭百家号新手引导/确认框
   * 百家号在打开发布页面时可能会显示以下确认框：
   * 1. "新增风险检测" 确认框 - 点击 "我知道了" 按钮关闭
   * 2. "AI工具收起" 说明框 - 点击右上角 [x] 关闭按钮关闭
   */
  async closeTourDialogs() {
    const page = this.browserManager.getPage();
    if (!page) return;
    console.log("   \u{1F50D} \u68C0\u67E5\u662F\u5426\u6709\u65B0\u624B\u5F15\u5BFC/\u786E\u8BA4\u6846...");
    try {
      await page.waitForTimeout(1e3);
      let hasDialog = true;
      let maxAttempts = 5;
      let attempt = 0;
      while (hasDialog && attempt < maxAttempts) {
        attempt++;
        hasDialog = false;
        const tourContent = await page.$(".cheetah-tour-content");
        if (tourContent) {
          console.log(`   \u53D1\u73B0\u786E\u8BA4\u6846 (\u5C1D\u8BD5 ${attempt}/${maxAttempts})`);
          const allButtons = await page.$$("div.cheetah-tour-buttons > button");
          if (allButtons.length > 0) {
            console.log(`   \u627E\u5230 ${allButtons.length} \u4E2A\u6309\u94AE`);
            for (let i = allButtons.length - 1; i >= 0; i--) {
              const btn = allButtons[i];
              const isVisible = await btn.isVisible();
              if (isVisible) {
                const btnText = await btn.textContent();
                console.log(`   \u70B9\u51FB\u6309\u94AE [${i + 1}]: ${btnText}`);
                await btn.click();
                await page.waitForTimeout(500);
                hasDialog = true;
                break;
              }
            }
            if (hasDialog) continue;
          }
          const closeBtn = await page.$("button.cheetah-tour-close");
          if (closeBtn) {
            const isVisible = await closeBtn.isVisible();
            if (isVisible) {
              console.log("   \u70B9\u51FB\u5173\u95ED\u6309\u94AE [x]");
              await closeBtn.click();
              await page.waitForTimeout(500);
              hasDialog = true;
              continue;
            }
          }
        }
        const otherDialogs = await page.$$('.cheetah-modal-content, .cheetah-dialog, [role="dialog"]');
        for (const dialog of otherDialogs) {
          const isVisible = await dialog.isVisible();
          if (isVisible) {
            const closeBtn = await dialog.$('button[class*="close"], .cheetah-modal-close, .close-btn');
            if (closeBtn) {
              console.log("   \u5173\u95ED\u5176\u4ED6\u5BF9\u8BDD\u6846");
              await closeBtn.click();
              await page.waitForTimeout(500);
              hasDialog = true;
              break;
            }
          }
        }
        try {
          const tipDialogs = await page.$$('.cheetah-modal-wrap, [class*="modal"]');
          for (const dialog of tipDialogs) {
            const isVisible = await dialog.isVisible();
            if (isVisible) {
              const titleEl = await dialog.$('.cheetah-modal-title, [class*="title"]');
              const title = titleEl ? await titleEl.textContent() : "";
              const content = await dialog.textContent();
              if (title?.includes("\u63D0\u793A") || content?.includes("\u683C\u5F0F\u4E0D\u6B63\u786E") || content?.includes("\u9519\u8BEF")) {
                console.log(`   \u53D1\u73B0\u9519\u8BEF\u63D0\u793A\u6846: ${title || "\u63D0\u793A"}`);
                const confirmBtn = await dialog.$('button:has-text("\u786E\u8BA4"), button:has-text("\u786E\u5B9A"), .cheetah-btn-primary');
                if (confirmBtn) {
                  await confirmBtn.click();
                  console.log("   \u70B9\u51FB\u786E\u8BA4\u6309\u94AE\u5173\u95ED\u63D0\u793A\u6846");
                  await page.waitForTimeout(500);
                  hasDialog = true;
                  break;
                }
                const closeBtn = await dialog.$('button[class*="close"], .cheetah-modal-close');
                if (closeBtn) {
                  await closeBtn.click();
                  console.log("   \u70B9\u51FB\u5173\u95ED\u6309\u94AE\u5173\u95ED\u63D0\u793A\u6846");
                  await page.waitForTimeout(500);
                  hasDialog = true;
                  break;
                }
              }
            }
          }
        } catch {
        }
      }
      if (attempt > 1) {
        console.log("   \u2705 \u786E\u8BA4\u6846\u5DF2\u5904\u7406\u5B8C\u6210");
      } else {
        console.log("   \u2705 \u672A\u53D1\u73B0\u786E\u8BA4\u6846");
      }
    } catch (error) {
      console.log("   \u26A0\uFE0F \u5904\u7406\u786E\u8BA4\u6846\u65F6\u51FA\u9519:", error instanceof Error ? error.message : String(error));
    }
  }
  /**
   * 处理错误提示框
   * 用于处理发布过程中出现的各种错误提示
   */
  async handleErrorDialogs() {
    const page = this.browserManager.getPage();
    if (!page) return false;
    let handled = false;
    try {
      const errorSelectors = [
        ".cheetah-modal-wrap",
        ".cheetah-modal-content",
        '[class*="modal"]',
        '[role="dialog"]'
      ];
      for (const selector of errorSelectors) {
        const dialogs = await page.$$(selector);
        for (const dialog of dialogs) {
          const isVisible = await dialog.isVisible();
          if (!isVisible) continue;
          const text = await dialog.textContent();
          if (text?.includes("\u683C\u5F0F\u4E0D\u6B63\u786E") || text?.includes("\u89C6\u9891") || text?.includes("\u9519\u8BEF") || text?.includes("\u5931\u8D25") || text?.includes("\u63D0\u793A")) {
            console.log(`   \u53D1\u73B0\u9519\u8BEF\u63D0\u793A: ${text?.substring(0, 50)}...`);
            const confirmBtn = await dialog.$('button:has-text("\u786E\u8BA4"), button:has-text("\u786E\u5B9A"), .cheetah-btn-primary, button');
            if (confirmBtn) {
              const btnText = await confirmBtn.textContent();
              console.log(`   \u70B9\u51FB\u6309\u94AE\u5173\u95ED\u63D0\u793A: ${btnText}`);
              await confirmBtn.click();
              await page.waitForTimeout(500);
              handled = true;
              break;
            }
            const closeBtn = await dialog.$('button[class*="close"], .cheetah-modal-close, [class*="close"]');
            if (closeBtn) {
              await closeBtn.click();
              console.log("   \u70B9\u51FB\u5173\u95ED\u6309\u94AE");
              await page.waitForTimeout(500);
              handled = true;
              break;
            }
          }
        }
        if (handled) break;
      }
    } catch (error) {
      console.log("   \u5904\u7406\u9519\u8BEF\u63D0\u793A\u6846\u65F6\u51FA\u9519:", error);
    }
    return handled;
  }
  /**
   * 发布文章到百家号
   * @param article 文章内容
   * @param testMode 测试模式，为true时不点击发布按钮
   */
  async publish(article, testMode = false) {
    try {
      console.log(`\u{1F680} \u5F00\u59CB\u53D1\u5E03\u6587\u7AE0\u5230\u767E\u5BB6\u53F7...`);
      if (testMode) {
        console.log("\u{1F4DD} \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u5C06\u586B\u5199\u6587\u7AE0\u4F46\u4E0D\u53D1\u5E03");
      }
      await this.browserManager.launch();
      const page = this.browserManager.getPage();
      if (!page) {
        throw new Error("Page not initialized");
      }
      console.log("\u{1F4F1} \u5BFC\u822A\u5230\u53D1\u5E03\u9875\u9762...");
      await this.browserManager.gotoPublishPage();
      await page.waitForTimeout(2e3);
      const isOnLoginPage = await this.browserManager.isOnLoginPageAsync();
      if (isOnLoginPage) {
        console.log("\u26A0\uFE0F \u68C0\u6D4B\u5230\u672A\u767B\u5F55\uFF0C\u5F00\u59CB\u767B\u5F55\u6D41\u7A0B...");
        console.log("\u8BF7\u5728\u6D4F\u89C8\u5668\u4E2D\u626B\u7801\u767B\u5F55\u767E\u5BB6\u53F7...");
        const loginSuccess = await this.browserManager.waitForLogin(12e4);
        if (!loginSuccess) {
          await this.browserManager.close();
          return {
            success: false,
            platform: this.platform,
            message: "\u767B\u5F55\u8D85\u65F6\uFF0C\u8BF7\u91CD\u8BD5"
          };
        }
        console.log("\u{1F4F1} \u767B\u5F55\u6210\u529F\uFF0C\u7EE7\u7EED\u53D1\u5E03\u6D41\u7A0B...");
        await this.browserManager.gotoPublishPage();
      }
      console.log("   \u7B49\u5F85\u7F16\u8F91\u5668\u52A0\u8F7D...");
      await page.waitForSelector("#ueditor", { timeout: 1e4 });
      await this.closeTourDialogs();
      console.log("\u{1F4DD} \u586B\u5145\u6587\u7AE0\u6807\u9898...");
      await this.fillTitle(article.title);
      console.log("\u{1F4DD} \u586B\u5145\u6587\u7AE0\u5185\u5BB9...");
      await this.fillContent(article.content);
      let coverImagePath = null;
      if (article.coverImage) {
        console.log("\u{1F5BC}\uFE0F \u4F7F\u7528\u7528\u6237\u63D0\u4F9B\u7684\u5C01\u9762\u56FE\u7247...");
        if (article.coverImage.startsWith("http")) {
          coverImagePath = await this.downloadImageToTemp(article.coverImage);
        } else {
          coverImagePath = article.coverImage;
        }
      } else {
        console.log("\u{1F5BC}\uFE0F \u672A\u63D0\u4F9B\u5C01\u9762\u56FE\u7247\uFF0C\u6B63\u5728\u81EA\u52A8\u751F\u6210...");
        const coverUrl = await getCoverForArticle({
          title: article.title,
          contentPreview: article.content,
          orientation: "landscape",
          size: "large2x"
        });
        if (coverUrl) {
          coverImagePath = await this.downloadImageToTemp(coverUrl);
        } else {
          console.warn("   \u26A0\uFE0F \u5C01\u9762\u56FE\u7247\u751F\u6210\u5931\u8D25\uFF0C\u5C06\u4E0D\u8BBE\u7F6E\u5C01\u9762");
        }
      }
      if (coverImagePath) {
        console.log("\u{1F4E4} \u4E0A\u4F20\u5C01\u9762\u56FE\u7247...");
        await this.uploadCover(coverImagePath);
        await this.handleErrorDialogs();
      }
      if (article.summary) {
        console.log("\u{1F4DD} \u586B\u5199\u6587\u7AE0\u6458\u8981...");
        await this.fillSummary(article.summary);
      }
      if (article.category) {
        console.log("\u{1F4C1} \u9009\u62E9\u6587\u7AE0\u5206\u7C7B...");
        await this.selectCategory(article.category);
      }
      if (article.tags && article.tags.length > 0) {
        console.log("\u{1F3F7}\uFE0F \u8BBE\u7F6E\u6807\u7B7E...");
        await this.setTags(article.tags);
      }
      if (testMode) {
        console.log("");
        console.log("===========================================");
        console.log("\u2705 \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u5DF2\u586B\u5199\u5B8C\u6210\uFF01");
        console.log("\u26A0\uFE0F  \u672A\u70B9\u51FB\u53D1\u5E03\u6309\u94AE\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("===========================================");
        console.log("");
        const screenshotPath = `./test-screenshot-baijiahao-${Date.now()}.png`;
        await this.screenshot(screenshotPath);
        console.log(`\u{1F4F8} \u622A\u56FE\u5DF2\u4FDD\u5B58: ${screenshotPath}`);
        await this.browserManager.saveCookies();
        console.log("");
        console.log("\u{1F4A1} \u6D4F\u89C8\u5668\u5C06\u4FDD\u6301\u6253\u5F00\u72B6\u6001\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("   \u68C0\u67E5\u5B8C\u6210\u540E\uFF0C\u8BF7\u624B\u52A8\u5173\u95ED\u6D4F\u89C8\u5668\u7A97\u53E3");
        console.log("");
        return {
          success: true,
          platform: this.platform,
          message: "\u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u5DF2\u586B\u5199\u5B8C\u6210\uFF0C\u672A\u53D1\u5E03",
          testMode: true
        };
      }
      console.log("\u{1F4E4} \u70B9\u51FB\u53D1\u5E03\u6309\u94AE...");
      await this.clickPublish();
      const articleUrl = await this.getArticleUrl();
      await this.browserManager.saveCookies();
      await this.browserManager.close();
      this.cleanupTempFiles();
      return {
        success: true,
        platform: this.platform,
        message: "\u6587\u7AE0\u53D1\u5E03\u6210\u529F",
        url: articleUrl || void 0
      };
    } catch (error) {
      this.cleanupTempFiles();
      await this.browserManager.close();
      return {
        success: false,
        platform: this.platform,
        message: "\u53D1\u5E03\u5931\u8D25",
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
  async fillTitle(title) {
    const page = this.browserManager.getPage();
    if (!page) return;
    console.log("   \u67E5\u627E\u6807\u9898\u8F93\u5165\u6846...");
    const titleSelectors = [
      '#bjhNewsTitle [contenteditable="true"]',
      '#bjhNewsTitle .input-box [contenteditable="true"]',
      '[data-testid="news-title-input"] [contenteditable="true"]',
      '#newsTextArea [contenteditable="true"]'
    ];
    for (const selector of titleSelectors) {
      try {
        console.log(`   \u5C1D\u8BD5\u9009\u62E9\u5668: ${selector}`);
        const titleInput = await page.$(selector);
        if (titleInput) {
          const isVisible = await titleInput.isVisible();
          if (isVisible) {
            console.log(`   \u2705 \u627E\u5230\u6807\u9898\u8F93\u5165\u6846: ${selector}`);
            await titleInput.click();
            await page.waitForTimeout(300);
            await page.keyboard.press("Control+A");
            await page.waitForTimeout(200);
            await page.keyboard.press("Backspace");
            await page.waitForTimeout(300);
            await page.keyboard.type(title, { delay: 50 });
            await page.waitForTimeout(500);
            console.log(`   \u2705 \u6807\u9898\u586B\u5199\u5B8C\u6210: ${title}`);
            return;
          }
        }
      } catch (error) {
        console.log(`   \u9009\u62E9\u5668 ${selector} \u5931\u8D25:`, error);
        continue;
      }
    }
    console.warn("   \u274C \u672A\u627E\u5230\u6807\u9898\u8F93\u5165\u6846");
  }
  async fillContent(content) {
    const page = this.browserManager.getPage();
    if (!page) return;
    console.log("   \u67E5\u627E\u5185\u5BB9\u7F16\u8F91\u5668...");
    try {
      const iframeElement = await page.$('iframe[id*="editor"]');
      if (iframeElement) {
        console.log("   \u627E\u5230\u7F16\u8F91\u5668 iframe");
        const frame = await iframeElement.contentFrame();
        if (frame) {
          console.log("   \u5728 iframe \u4E2D\u67E5\u627E\u7F16\u8F91\u533A\u57DF...");
          const body = await frame.$("body.view");
          if (body) {
            console.log("   \u2705 \u627E\u5230\u5185\u5BB9\u7F16\u8F91\u5668 (iframe body)");
            await body.click();
            await page.waitForTimeout(500);
            const lines = content.split("\n");
            for (let i = 0; i < lines.length; i++) {
              const line = lines[i];
              for (let j = 0; j < line.length; j++) {
                const char = line[j];
                if (char == "#") {
                  await page.keyboard.type(char, { delay: 100 });
                  await page.keyboard.press("Escape");
                  await page.waitForTimeout(100);
                } else {
                  await page.keyboard.type(char, { delay: 10 });
                }
              }
              if (i < lines.length - 1) {
                await page.keyboard.press("Enter");
                await page.waitForTimeout(200);
              }
            }
            console.log(`   \u2705 \u5185\u5BB9\u586B\u5199\u5B8C\u6210 (${content.length} \u5B57\u7B26)`);
            return;
          }
        }
      }
    } catch (error) {
      console.log("   iframe \u65B9\u5F0F\u5931\u8D25\uFF0C\u5C1D\u8BD5\u5176\u4ED6\u65B9\u5F0F...");
    }
    const contentSelectors = [
      "#editor",
      '[contenteditable="true"]',
      ".editor-content",
      ".ql-editor",
      ".ProseMirror",
      ".public-DraftEditor-content",
      ".edui-editor-iframeholder iframe"
    ];
    for (const selector of contentSelectors) {
      try {
        console.log(`   \u5C1D\u8BD5\u9009\u62E9\u5668: ${selector}`);
        const contentEditor = await page.$(selector);
        if (contentEditor) {
          const isVisible = await contentEditor.isVisible();
          if (isVisible) {
            console.log(`   \u2705 \u627E\u5230\u5185\u5BB9\u7F16\u8F91\u5668: ${selector}`);
            await contentEditor.click();
            await page.waitForTimeout(500);
            await page.keyboard.press("Control+A");
            await page.waitForTimeout(300);
            await page.keyboard.press("Backspace");
            await page.waitForTimeout(500);
            const lines = content.split("\n");
            for (let i = 0; i < lines.length; i++) {
              await page.keyboard.type(lines[i], { delay: 10 });
              if (i < lines.length - 1) {
                await page.keyboard.press("Enter");
                await page.waitForTimeout(200);
              }
            }
            console.log(`   \u2705 \u5185\u5BB9\u586B\u5199\u5B8C\u6210 (${content.length} \u5B57\u7B26)`);
            return;
          }
        }
      } catch {
        continue;
      }
    }
    console.warn("   \u274C \u672A\u627E\u5230\u5185\u5BB9\u7F16\u8F91\u5668");
  }
  async uploadCover(imagePath) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      console.log("   \u{1F50D} \u5BFB\u627E\u5C01\u9762\u4E0A\u4F20\u533A\u57DF...");
      await page.waitForTimeout(1e3);
      const coverTriggerSelectors = [
        "._93c3fe2a3121c388-item",
        // 封面项容器
        "._73a3a52aab7e3a36-default",
        // 封面默认区域
        "._73a3a52aab7e3a36-content",
        // 封面内容区域
        '[class*="list"] [class*="item"]',
        // 通用列表项
        ".bjh-news-cover-add",
        '[class*="cover-add"]',
        '[class*="cover"] [class*="add"]',
        ".cover-upload",
        ".cover-selector",
        '#bjhNewsCover [class*="add"]',
        "#bjhNewsCover .cheetah-btn",
        "#bjhNewsCover button"
      ];
      let clickedTrigger = false;
      for (const selector of coverTriggerSelectors) {
        try {
          const triggers = await page.$$(selector);
          console.log(`   \u67E5\u627E\u9009\u62E9\u5668 ${selector}, \u627E\u5230 ${triggers.length} \u4E2A\u5143\u7D20`);
          for (const trigger of triggers) {
            const isVisible = await trigger.isVisible();
            if (isVisible) {
              const text = await trigger.textContent();
              console.log(`   \u5143\u7D20\u6587\u672C: ${text?.substring(0, 30)}`);
              if (text?.includes("\u9009\u62E9\u5C01\u9762") || text?.includes("\u5C01\u9762") || text?.includes("\u6DFB\u52A0")) {
                console.log(`   \u2705 \u70B9\u51FB\u5C01\u9762\u89E6\u53D1\u533A\u57DF: ${selector}`);
                await trigger.click();
                await page.waitForTimeout(1e3);
                clickedTrigger = true;
                break;
              }
            }
          }
          if (clickedTrigger) break;
        } catch (error) {
          console.log(`   \u9009\u62E9\u5668 ${selector} \u5931\u8D25:`, error);
          continue;
        }
      }
      if (!clickedTrigger) {
        console.log("   \u5C1D\u8BD5\u70B9\u51FB\u7B2C\u4E00\u4E2A\u53EF\u89C1\u7684\u5C01\u9762\u533A\u57DF...");
        for (const selector of coverTriggerSelectors) {
          try {
            const trigger = await page.$(selector);
            if (trigger) {
              const isVisible = await trigger.isVisible();
              if (isVisible) {
                console.log(`   \u70B9\u51FB\u5C01\u9762\u533A\u57DF: ${selector}`);
                await trigger.click();
                await page.waitForTimeout(1e3);
                clickedTrigger = true;
                break;
              }
            }
          } catch {
            continue;
          }
        }
      }
      const fileInputSelectors = [
        'input[type="file"][accept*="image"]:not([accept*="video"])',
        '#bjhNewsCover input[type="file"]',
        '[class*="cover"] input[type="file"]',
        '.cheetah-upload input[type="file"]'
      ];
      let uploaded = false;
      for (const selector of fileInputSelectors) {
        if (uploaded) break;
        try {
          const fileInputs = await page.$$(selector);
          console.log(`   \u67E5\u627E\u9009\u62E9\u5668 ${selector}, \u627E\u5230 ${fileInputs.length} \u4E2A\u5143\u7D20`);
          for (const fileInput of fileInputs) {
            const accept = await fileInput.getAttribute("accept");
            console.log(`   file input accept: ${accept}`);
            if (!accept?.includes("video")) {
              console.log(`   \u2705 \u627E\u5230\u56FE\u7247\u4E0A\u4F20\u8F93\u5165\u6846: ${selector}`);
              await fileInput.setInputFiles(imagePath);
              await page.waitForTimeout(3e3);
              console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0A\u4F20: ${imagePath}`);
              uploaded = true;
              break;
            }
          }
        } catch (error) {
          console.log(`   \u9009\u62E9\u5668 ${selector} \u5931\u8D25:`, error);
          continue;
        }
      }
      if (!uploaded) {
        try {
          console.log("   \u5C1D\u8BD5\u5907\u7528\u65B9\u6848\uFF1A\u67E5\u627E\u6240\u6709 file input...");
          const allFileInputs = await page.$$('input[type="file"]');
          console.log(`   \u627E\u5230 ${allFileInputs.length} \u4E2A file input`);
          for (const fileInput of allFileInputs) {
            const accept = await fileInput.getAttribute("accept");
            console.log(`   file input accept: ${accept}`);
            if (accept && !accept.includes("video")) {
              console.log("   \u2705 \u4F7F\u7528\u5907\u7528\u65B9\u6848\u627E\u5230\u56FE\u7247\u4E0A\u4F20\u8F93\u5165\u6846");
              await fileInput.setInputFiles(imagePath);
              await page.waitForTimeout(3e3);
              console.log(`   \u2705 \u5C01\u9762\u56FE\u7247\u5DF2\u4E0A\u4F20: ${imagePath}`);
              uploaded = true;
              break;
            }
          }
        } catch (error) {
          console.log("   \u5907\u7528\u65B9\u6848\u5931\u8D25:", error);
        }
      }
      console.log("   \u70B9\u51FB\u786E\u5B9A\u6309\u94AE\u786E\u8BA4\u5C01\u9762\u9009\u62E9...");
      await page.waitForTimeout(1e3);
      const modalSelectors = [
        ".cheetah-modal-content",
        ".cheetah-modal-wrap",
        '[class*="modal-content"]',
        '[role="dialog"]'
      ];
      let confirmed = false;
      for (const modalSelector of modalSelectors) {
        if (confirmed) break;
        try {
          const modals = await page.$$(modalSelector);
          console.log(`   \u67E5\u627E\u5F39\u51FA\u6846 ${modalSelector}, \u627E\u5230 ${modals.length} \u4E2A`);
          for (const modal of modals) {
            const isVisible = await modal.isVisible();
            if (!isVisible) continue;
            const confirmBtnSelectors = [
              ".e8c90bfac9d4eab4-confirmBtn",
              'button[class*="confirm"]',
              ".cheetah-btn-primary",
              'button:has-text("\u786E\u5B9A")',
              'button:has-text("\u786E\u8BA4")'
            ];
            for (const btnSelector of confirmBtnSelectors) {
              try {
                const confirmBtn = await modal.$(btnSelector);
                if (confirmBtn) {
                  const isVisible2 = await confirmBtn.isVisible();
                  if (isVisible2) {
                    const btnText = await confirmBtn.textContent();
                    console.log(`   \u2705 \u5728\u5F39\u51FA\u6846\u4E2D\u627E\u5230\u786E\u5B9A\u6309\u94AE: ${btnText}`);
                    await confirmBtn.click();
                    await page.waitForTimeout(1e3);
                    console.log("   \u2705 \u5DF2\u70B9\u51FB\u786E\u5B9A\u6309\u94AE");
                    confirmed = true;
                    break;
                  }
                }
              } catch {
                continue;
              }
            }
            if (confirmed) break;
          }
        } catch {
          continue;
        }
      }
      if (!confirmed) {
        console.log("   \u5C1D\u8BD5\u5168\u5C40\u641C\u7D22\u786E\u5B9A\u6309\u94AE...");
        const globalBtnSelectors = [
          'button:has-text("\u786E\u5B9A")',
          'button:has-text("\u786E\u8BA4")',
          ".cheetah-btn-primary"
        ];
        for (const selector of globalBtnSelectors) {
          try {
            const confirmBtn = await page.$(selector);
            if (confirmBtn) {
              const isVisible = await confirmBtn.isVisible();
              if (isVisible) {
                const btnText = await confirmBtn.textContent();
                console.log(`   \u2705 \u627E\u5230\u786E\u5B9A\u6309\u94AE: ${btnText}`);
                await confirmBtn.click();
                await page.waitForTimeout(1e3);
                console.log("   \u2705 \u5DF2\u70B9\u51FB\u786E\u5B9A\u6309\u94AE");
                confirmed = true;
                break;
              }
            }
          } catch {
            continue;
          }
        }
      }
      if (!confirmed) {
        console.warn("   \u26A0\uFE0F \u672A\u627E\u5230\u786E\u5B9A\u6309\u94AE");
      }
      return;
    } catch (error) {
      console.warn("   \u26A0\uFE0F \u5C01\u9762\u4E0A\u4F20\u5931\u8D25:", error instanceof Error ? error.message : String(error));
    }
  }
  /**
   * 填写文章摘要
   * 百家号摘要输入框：textarea.cheetah-ui-pro-countable-textbox-textarea，placeholder="请输入摘要"
   */
  async fillSummary(summary) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      console.log("   \u67E5\u627E\u6458\u8981\u8F93\u5165\u6846...");
      await page.waitForTimeout(500);
      const summarySelectors = [
        "textarea.cheetah-ui-pro-countable-textbox-textarea",
        'textarea[placeholder="\u8BF7\u8F93\u5165\u6458\u8981"]',
        'textarea[placeholder*="\u6458\u8981"]',
        ".cheetah-ui-pro-countable-textbox-textarea"
      ];
      for (const selector of summarySelectors) {
        try {
          console.log(`   \u5C1D\u8BD5\u9009\u62E9\u5668: ${selector}`);
          const summaryInput = await page.$(selector);
          if (summaryInput) {
            const isVisible = await summaryInput.isVisible();
            if (isVisible) {
              const placeholder = await summaryInput.getAttribute("placeholder");
              console.log(`   \u5143\u7D20 placeholder: ${placeholder}`);
              console.log(`   \u2705 \u627E\u5230\u6458\u8981\u8F93\u5165\u6846: ${selector}`);
              await summaryInput.click();
              await page.waitForTimeout(300);
              await summaryInput.fill("");
              await page.waitForTimeout(300);
              await summaryInput.fill(summary);
              await page.waitForTimeout(500);
              console.log(`   \u2705 \u6458\u8981\u586B\u5199\u5B8C\u6210: ${summary.substring(0, 50)}...`);
              return;
            }
          }
        } catch {
          continue;
        }
      }
      try {
        console.log("   \u5C1D\u8BD5\u5907\u7528\u65B9\u6848\uFF1A\u67E5\u627E\u6240\u6709 textarea...");
        const allTextareas = await page.$$("textarea");
        for (const textarea of allTextareas) {
          const isVisible = await textarea.isVisible();
          if (isVisible) {
            const placeholder = await textarea.getAttribute("placeholder");
            if (placeholder?.includes("\u6458\u8981")) {
              console.log(`   \u2705 \u901A\u8FC7\u5907\u7528\u65B9\u6848\u627E\u5230\u6458\u8981\u8F93\u5165\u6846`);
              await textarea.click();
              await page.waitForTimeout(300);
              await textarea.fill("");
              await page.waitForTimeout(300);
              await textarea.fill(summary);
              await page.waitForTimeout(500);
              console.log(`   \u2705 \u6458\u8981\u586B\u5199\u5B8C\u6210: ${summary.substring(0, 50)}...`);
              return;
            }
          }
        }
      } catch {
      }
      console.warn("   \u274C \u672A\u627E\u5230\u6458\u8981\u8F93\u5165\u6846");
    } catch (error) {
      console.warn("   \u26A0\uFE0F \u6458\u8981\u586B\u5199\u5931\u8D25:", error instanceof Error ? error.message : String(error));
    }
  }
  /**
   * 选择文章分类
   * 百家号分类选择器：cheetah-select cheetah-cascader 组件
   * 支持级联选择，category 可以用 "/" 或 ">" 分隔多级分类
   * 例如: "科技/互联网" 或 "科技>互联网"
   */
  async selectCategory(category) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      console.log("   \u67E5\u627E\u5206\u7C7B\u9009\u62E9\u5668...");
      await page.waitForTimeout(500);
      const categories = category.split(/[\/>]/).map((c) => c.trim()).filter((c) => c);
      console.log(`   \u5206\u7C7B\u5C42\u7EA7: ${categories.join(" > ")}`);
      try {
        const allSelects = await page.$$(".cheetah-select-selector");
        console.log(`   \u627E\u5230 ${allSelects.length} \u4E2A cheetah-select-selector \u5143\u7D20`);
        for (const select of allSelects) {
          const text = await select.textContent();
          console.log(`   \u9009\u62E9\u5668\u6587\u672C: ${text?.substring(0, 50)}`);
          if (text?.includes("\u5185\u5BB9\u5206\u7C7B") || text?.includes("\u5206\u7C7B")) {
            console.log("   \u627E\u5230\u5206\u7C7B\u9009\u62E9\u5668");
            await select.click();
            await page.waitForTimeout(800);
            for (let level = 0; level < categories.length; level++) {
              const cat = categories[level];
              console.log(`   \u9009\u62E9\u7B2C ${level + 1} \u7EA7\u5206\u7C7B: ${cat}`);
              await page.waitForTimeout(500);
              const menuSelectors = [
                ".cheetah-cascader-menu",
                '[class*="cascader-menu"]',
                ".cheetah-select-dropdown"
              ];
              let found = false;
              for (const menuSelector of menuSelectors) {
                const menus = await page.$$(menuSelector);
                console.log(`   \u627E\u5230 ${menus.length} \u4E2A\u83DC\u5355\u5217`);
                const targetMenu = menus[level] || menus[menus.length - 1];
                if (targetMenu) {
                  const options = await targetMenu.$$('[class*="menu-item"], [class*="option"], li');
                  console.log(`   \u7B2C ${level + 1} \u5217\u6709 ${options.length} \u4E2A\u9009\u9879`);
                  for (const opt of options) {
                    const optText = await opt.textContent();
                    if (optText?.includes(cat)) {
                      console.log(`   \u627E\u5230\u5339\u914D\u9009\u9879: ${optText}`);
                      await opt.click();
                      await page.waitForTimeout(500);
                      found = true;
                      break;
                    }
                  }
                }
                if (found) break;
              }
              if (!found) {
                console.log(`   \u5C1D\u8BD5\u5907\u7528\u65B9\u6848\u67E5\u627E: ${cat}`);
                const allOptions = await page.$$('[class*="cascader-menu-item"], [class*="select-option"], [class*="option"], li');
                for (const opt of allOptions) {
                  const optText = await opt.textContent();
                  if (optText?.trim() === cat || optText?.includes(cat)) {
                    console.log(`   \u627E\u5230\u5339\u914D\u9009\u9879: ${optText}`);
                    await opt.click();
                    await page.waitForTimeout(500);
                    found = true;
                    break;
                  }
                }
              }
              if (!found) {
                console.warn(`   \u26A0\uFE0F \u672A\u627E\u5230\u7B2C ${level + 1} \u7EA7\u5206\u7C7B: ${cat}`);
                break;
              }
            }
            console.log(`   \u2705 \u5206\u7C7B\u9009\u62E9\u5B8C\u6210: ${categories.join(" > ")}`);
            return;
          }
        }
      } catch (error) {
        console.log("   \u65B9\u6CD51\u5931\u8D25:", error);
      }
      try {
        const allFormItems = await page.$$(".cheetah-form-item");
        for (const formItem of allFormItems) {
          const labelEl = await formItem.$(".cheetah-form-item-label");
          const labelText = labelEl ? await labelEl.textContent() : "";
          if (labelText?.includes("\u5206\u7C7B")) {
            console.log("   \u627E\u5230\u5206\u7C7B\u8868\u5355\u9879");
            const selector = await formItem.$(".cheetah-select-selector");
            if (selector) {
              await selector.click();
              await page.waitForTimeout(800);
              for (let level = 0; level < categories.length; level++) {
                const cat = categories[level];
                console.log(`   \u9009\u62E9\u7B2C ${level + 1} \u7EA7\u5206\u7C7B: ${cat}`);
                await page.waitForTimeout(500);
                const allOptions = await page.$$('[class*="cascader-menu-item"], [class*="select-option"], li');
                for (const opt of allOptions) {
                  const optText = await opt.textContent();
                  if (optText?.includes(cat)) {
                    await opt.click();
                    await page.waitForTimeout(500);
                    break;
                  }
                }
              }
              console.log(`   \u2705 \u5206\u7C7B\u9009\u62E9\u5B8C\u6210: ${categories.join(" > ")}`);
              return;
            }
          }
        }
      } catch {
      }
      console.warn("   \u274C \u672A\u627E\u5230\u5206\u7C7B\u9009\u62E9\u5668");
    } catch (error) {
      console.warn("   \u26A0\uFE0F \u5206\u7C7B\u9009\u62E9\u5931\u8D25:", error instanceof Error ? error.message : String(error));
    }
  }
  async setTags(tags) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      console.log("   \u67E5\u627E\u6807\u7B7E\u8F93\u5165\u6846...");
      await page.waitForTimeout(500);
      const tagInputSelectors = [
        'input[placeholder*="\u6807\u7B7E"]',
        'input[placeholder*="\u5173\u952E\u8BCD"]',
        'input[placeholder*="tag"]',
        ".tag-input input",
        '[class*="tag"] input'
      ];
      for (const selector of tagInputSelectors) {
        try {
          console.log(`   \u5C1D\u8BD5\u9009\u62E9\u5668: ${selector}`);
          const tagInput = await page.$(selector);
          if (tagInput) {
            const isVisible = await tagInput.isVisible();
            if (isVisible) {
              console.log(`   \u2705 \u627E\u5230\u6807\u7B7E\u8F93\u5165\u6846: ${selector}`);
              for (const tag of tags.slice(0, 5)) {
                await tagInput.click();
                await page.waitForTimeout(300);
                await tagInput.fill(tag);
                await page.waitForTimeout(500);
                await page.keyboard.press("Enter");
                await page.waitForTimeout(500);
              }
              console.log(`   \u2705 \u6807\u7B7E\u8BBE\u7F6E\u5B8C\u6210: ${tags.slice(0, 5).join(", ")}`);
              return;
            }
          }
        } catch {
          continue;
        }
      }
      console.warn("   \u274C \u672A\u627E\u5230\u6807\u7B7E\u8F93\u5165\u6846");
    } catch (error) {
      console.warn("   \u26A0\uFE0F \u6807\u7B7E\u8BBE\u7F6E\u5931\u8D25:", error instanceof Error ? error.message : String(error));
    }
  }
  async clickPublish() {
    const page = this.browserManager.getPage();
    if (!page) return;
    const publishSelectors = [
      'button:has-text("\u53D1\u5E03")',
      ".publish-btn",
      '[class*="publish"]:not([class*="draft"])',
      'button[type="submit"]',
      ".submit-btn"
    ];
    for (const selector of publishSelectors) {
      try {
        console.log(`   \u5C1D\u8BD5\u9009\u62E9\u5668: ${selector}`);
        const publishBtn = await page.$(selector);
        if (publishBtn) {
          const isVisible = await publishBtn.isVisible();
          if (isVisible) {
            console.log(`   \u2705 \u627E\u5230\u53D1\u5E03\u6309\u94AE: ${selector}`);
            await publishBtn.click();
            await page.waitForTimeout(3e3);
            console.log("   \u2705 \u5DF2\u70B9\u51FB\u53D1\u5E03\u6309\u94AE");
            return;
          }
        }
      } catch {
        continue;
      }
    }
    console.warn("   \u26A0\uFE0F \u672A\u627E\u5230\u53D1\u5E03\u6309\u94AE");
  }
  async getArticleUrl() {
    const page = this.browserManager.getPage();
    if (!page) return null;
    try {
      await page.waitForTimeout(2e3);
      const url = page.url();
      if (url.includes("baijiahao.baidu.com/")) {
        return url;
      }
      return null;
    } catch {
      return null;
    }
  }
};

// src/adapters/toutiao.ts
var ToutiaoAdapter = class extends BaseAdapter {
  constructor() {
    super("toutiao");
  }
  /**
   * 发布文章到头条号
   * @param article 文章内容
   * @param testMode 测试模式，为true时不点击发布按钮
   */
  async publish(article, testMode = false) {
    try {
      console.log(`\u{1F680} \u5F00\u59CB\u53D1\u5E03\u6587\u7AE0\u5230\u5934\u6761\u53F7...`);
      if (testMode) {
        console.log("\u{1F4DD} \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u5C06\u586B\u5199\u6587\u7AE0\u4F46\u4E0D\u53D1\u5E03");
      }
      await this.browserManager.launch();
      const page = this.browserManager.getPage();
      if (!page) {
        throw new Error("Page not initialized");
      }
      console.log("\u{1F4F1} \u5BFC\u822A\u5230\u53D1\u5E03\u9875\u9762...");
      await this.browserManager.gotoPublishPage();
      await page.waitForTimeout(2e3);
      if (this.browserManager.isOnLoginPage()) {
        console.log("\u26A0\uFE0F \u68C0\u6D4B\u5230\u672A\u767B\u5F55\uFF0C\u5F00\u59CB\u767B\u5F55\u6D41\u7A0B...");
        console.log("\u8BF7\u5728\u6D4F\u89C8\u5668\u4E2D\u626B\u7801\u767B\u5F55\u5934\u6761\u53F7...");
        const loginSuccess = await this.browserManager.waitForLogin(12e4);
        if (!loginSuccess) {
          await this.browserManager.close();
          return {
            success: false,
            platform: this.platform,
            message: "\u767B\u5F55\u8D85\u65F6\uFF0C\u8BF7\u91CD\u8BD5"
          };
        }
        console.log("\u{1F4F1} \u767B\u5F55\u6210\u529F\uFF0C\u7EE7\u7EED\u53D1\u5E03\u6D41\u7A0B...");
        await this.browserManager.gotoPublishPage();
        await page.waitForTimeout(2e3);
      }
      console.log("\u{1F4DD} \u586B\u5145\u6587\u7AE0\u6807\u9898...");
      await this.fillTitle(article.title);
      console.log("\u{1F4DD} \u586B\u5145\u6587\u7AE0\u5185\u5BB9...");
      await this.fillContent(article.content);
      if (article.coverImage) {
        console.log("\u{1F5BC}\uFE0F \u4E0A\u4F20\u5C01\u9762\u56FE\u7247...");
        await this.uploadCover(article.coverImage);
      }
      if (article.tags && article.tags.length > 0) {
        console.log("\u{1F3F7}\uFE0F \u8BBE\u7F6E\u6807\u7B7E...");
        await this.setTags(article.tags);
      }
      if (testMode) {
        console.log("");
        console.log("===========================================");
        console.log("\u2705 \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u5DF2\u586B\u5199\u5B8C\u6210\uFF01");
        console.log("\u26A0\uFE0F  \u672A\u70B9\u51FB\u53D1\u5E03\u6309\u94AE\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("===========================================");
        console.log("");
        const screenshotPath = `./test-screenshot-toutiao-${Date.now()}.png`;
        await this.screenshot(screenshotPath);
        console.log(`\u{1F4F8} \u622A\u56FE\u5DF2\u4FDD\u5B58: ${screenshotPath}`);
        await this.browserManager.saveCookies();
        console.log("");
        console.log("\u{1F4A1} \u6D4F\u89C8\u5668\u5C06\u4FDD\u6301\u6253\u5F00\u72B6\u6001\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("   \u68C0\u67E5\u5B8C\u6210\u540E\uFF0C\u8BF7\u624B\u52A8\u5173\u95ED\u6D4F\u89C8\u5668\u7A97\u53E3");
        console.log("");
        return {
          success: true,
          platform: this.platform,
          message: "\u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u5DF2\u586B\u5199\u5B8C\u6210\uFF0C\u672A\u53D1\u5E03",
          testMode: true
        };
      }
      console.log("\u{1F4E4} \u70B9\u51FB\u53D1\u5E03\u6309\u94AE...");
      await this.clickPublish();
      const articleUrl = await this.getArticleUrl();
      await this.browserManager.saveCookies();
      await this.browserManager.close();
      return {
        success: true,
        platform: this.platform,
        message: "\u6587\u7AE0\u53D1\u5E03\u6210\u529F",
        url: articleUrl || void 0
      };
    } catch (error) {
      await this.browserManager.close();
      return {
        success: false,
        platform: this.platform,
        message: "\u53D1\u5E03\u5931\u8D25",
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
  async fillTitle(title) {
    const page = this.browserManager.getPage();
    if (!page) return;
    const titleSelectors = [
      'input[placeholder*="\u6807\u9898"]',
      ".article-title input",
      'input[class*="title"]',
      'input[name="title"]'
    ];
    let titleInput = null;
    for (const selector of titleSelectors) {
      try {
        titleInput = await page.$(selector);
        if (titleInput) {
          console.log(`   \u4F7F\u7528\u9009\u62E9\u5668: ${selector}`);
          break;
        }
      } catch {
        continue;
      }
    }
    if (titleInput) {
      await titleInput.click();
      await titleInput.fill(title);
      console.log(`   \u6807\u9898: ${title}`);
    } else {
      console.warn("   \u672A\u627E\u5230\u6807\u9898\u8F93\u5165\u6846");
    }
  }
  async fillContent(content) {
    const page = this.browserManager.getPage();
    if (!page) return;
    const contentSelectors = [
      ".ql-editor",
      '[contenteditable="true"]',
      ".editor-content",
      "#editor"
    ];
    let contentEditor = null;
    for (const selector of contentSelectors) {
      try {
        contentEditor = await page.$(selector);
        if (contentEditor) {
          console.log(`   \u4F7F\u7528\u9009\u62E9\u5668: ${selector}`);
          break;
        }
      } catch {
        continue;
      }
    }
    if (contentEditor) {
      await contentEditor.click();
      await page.waitForTimeout(500);
      await contentEditor.fill("");
      await page.keyboard.type(content, { delay: 10 });
      console.log(`   \u5185\u5BB9\u957F\u5EA6: ${content.length} \u5B57\u7B26`);
    } else {
      console.warn("   \u672A\u627E\u5230\u5185\u5BB9\u7F16\u8F91\u5668");
    }
  }
  async uploadCover(imagePath) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      const coverSelector = 'input[type="file"][accept*="image"], .cover-upload input';
      await page.setInputFiles(coverSelector, imagePath);
      await page.waitForTimeout(2e3);
      console.log(`   \u5C01\u9762\u56FE\u7247: ${imagePath}`);
    } catch (error) {
      console.warn("   \u5C01\u9762\u4E0A\u4F20\u5931\u8D25:", error);
    }
  }
  async setTags(tags) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      const tagInputSelector = 'input[placeholder*="\u6807\u7B7E"], input[placeholder*="\u8BDD\u9898"], .tag-input input';
      await page.waitForSelector(tagInputSelector, { timeout: 5e3 });
      for (const tag of tags.slice(0, 3)) {
        await page.fill(tagInputSelector, tag);
        await page.waitForTimeout(500);
        await page.keyboard.press("Enter");
        await page.waitForTimeout(500);
      }
      console.log(`   \u6807\u7B7E: ${tags.slice(0, 3).join(", ")}`);
    } catch (error) {
      console.warn("   \u6807\u7B7E\u8BBE\u7F6E\u5931\u8D25:", error);
    }
  }
  async clickPublish() {
    const page = this.browserManager.getPage();
    if (!page) return;
    const publishSelector = 'button:has-text("\u53D1\u5E03"), .publish-btn, [class*="publish"]';
    await page.waitForSelector(publishSelector, { timeout: 1e4 });
    await page.click(publishSelector);
    await page.waitForTimeout(3e3);
  }
  async getArticleUrl() {
    const page = this.browserManager.getPage();
    if (!page) return null;
    try {
      await page.waitForTimeout(2e3);
      const url = page.url();
      if (url.includes("toutiao.com/")) {
        return url;
      }
      return null;
    } catch {
      return null;
    }
  }
};

// src/adapters/xiaohongshu.ts
var XiaohongshuAdapter = class extends BaseAdapter {
  constructor() {
    super("xiaohongshu");
  }
  /**
   * 发布笔记到小红书
   * @param article 文章内容
   * @param testMode 测试模式，为true时不点击发布按钮
   */
  async publish(article, testMode = false) {
    try {
      console.log(`\u{1F680} \u5F00\u59CB\u53D1\u5E03\u7B14\u8BB0\u5230\u5C0F\u7EA2\u4E66...`);
      if (testMode) {
        console.log("\u{1F4DD} \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u5C06\u586B\u5199\u7B14\u8BB0\u4F46\u4E0D\u53D1\u5E03");
      }
      await this.browserManager.launch();
      const page = this.browserManager.getPage();
      if (!page) {
        throw new Error("Page not initialized");
      }
      console.log("\u{1F4F1} \u5BFC\u822A\u5230\u53D1\u5E03\u9875\u9762...");
      await this.browserManager.gotoPublishPage();
      await page.waitForTimeout(2e3);
      if (this.browserManager.isOnLoginPage()) {
        console.log("\u26A0\uFE0F \u68C0\u6D4B\u5230\u672A\u767B\u5F55\uFF0C\u5F00\u59CB\u767B\u5F55\u6D41\u7A0B...");
        console.log("\u8BF7\u5728\u6D4F\u89C8\u5668\u4E2D\u626B\u7801\u767B\u5F55\u5C0F\u7EA2\u4E66...");
        const loginSuccess = await this.browserManager.waitForLogin(12e4);
        if (!loginSuccess) {
          await this.browserManager.close();
          return {
            success: false,
            platform: this.platform,
            message: "\u767B\u5F55\u8D85\u65F6\uFF0C\u8BF7\u91CD\u8BD5"
          };
        }
        console.log("\u{1F4F1} \u767B\u5F55\u6210\u529F\uFF0C\u7EE7\u7EED\u53D1\u5E03\u6D41\u7A0B...");
        await this.browserManager.gotoPublishPage();
        await page.waitForTimeout(2e3);
      }
      console.log("\u{1F4DD} \u586B\u5145\u7B14\u8BB0\u6807\u9898...");
      await this.fillTitle(article.title);
      console.log("\u{1F4DD} \u586B\u5145\u7B14\u8BB0\u5185\u5BB9...");
      await this.fillContent(article.content);
      if (article.coverImage) {
        console.log("\u{1F5BC}\uFE0F \u4E0A\u4F20\u5C01\u9762\u56FE\u7247...");
        await this.uploadCover(article.coverImage);
      }
      if (article.tags && article.tags.length > 0) {
        console.log("\u{1F3F7}\uFE0F \u8BBE\u7F6E\u6807\u7B7E...");
        await this.setTags(article.tags);
      }
      if (testMode) {
        console.log("");
        console.log("===========================================");
        console.log("\u2705 \u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u7B14\u8BB0\u5DF2\u586B\u5199\u5B8C\u6210\uFF01");
        console.log("\u26A0\uFE0F  \u672A\u70B9\u51FB\u53D1\u5E03\u6309\u94AE\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("===========================================");
        console.log("");
        const screenshotPath = `./test-screenshot-xiaohongshu-${Date.now()}.png`;
        await this.screenshot(screenshotPath);
        console.log(`\u{1F4F8} \u622A\u56FE\u5DF2\u4FDD\u5B58: ${screenshotPath}`);
        await this.browserManager.saveCookies();
        console.log("");
        console.log("\u{1F4A1} \u6D4F\u89C8\u5668\u5C06\u4FDD\u6301\u6253\u5F00\u72B6\u6001\uFF0C\u8BF7\u624B\u52A8\u68C0\u67E5\u9875\u9762\u5185\u5BB9");
        console.log("   \u68C0\u67E5\u5B8C\u6210\u540E\uFF0C\u8BF7\u624B\u52A8\u5173\u95ED\u6D4F\u89C8\u5668\u7A97\u53E3");
        console.log("");
        return {
          success: true,
          platform: this.platform,
          message: "\u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u7B14\u8BB0\u5DF2\u586B\u5199\u5B8C\u6210\uFF0C\u672A\u53D1\u5E03",
          testMode: true
        };
      }
      console.log("\u{1F4E4} \u70B9\u51FB\u53D1\u5E03\u6309\u94AE...");
      await this.clickPublish();
      const articleUrl = await this.getArticleUrl();
      await this.browserManager.saveCookies();
      await this.browserManager.close();
      return {
        success: true,
        platform: this.platform,
        message: "\u7B14\u8BB0\u53D1\u5E03\u6210\u529F",
        url: articleUrl || void 0
      };
    } catch (error) {
      await this.browserManager.close();
      return {
        success: false,
        platform: this.platform,
        message: "\u53D1\u5E03\u5931\u8D25",
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
  async fillTitle(title) {
    const page = this.browserManager.getPage();
    if (!page) return;
    const titleSelectors = [
      'input[placeholder*="\u6807\u9898"]',
      ".title-input input",
      'input[class*="title"]',
      'input[name="title"]'
    ];
    let titleInput = null;
    for (const selector of titleSelectors) {
      try {
        titleInput = await page.$(selector);
        if (titleInput) {
          console.log(`   \u4F7F\u7528\u9009\u62E9\u5668: ${selector}`);
          break;
        }
      } catch {
        continue;
      }
    }
    if (titleInput) {
      await titleInput.click();
      await titleInput.fill(title);
      console.log(`   \u6807\u9898: ${title}`);
    } else {
      console.warn("   \u672A\u627E\u5230\u6807\u9898\u8F93\u5165\u6846");
    }
  }
  async fillContent(content) {
    const page = this.browserManager.getPage();
    if (!page) return;
    const contentSelectors = [
      "#post-textarea",
      '[contenteditable="true"]',
      ".editor-content",
      'textarea[placeholder*="\u6B63\u6587"]'
    ];
    let contentEditor = null;
    for (const selector of contentSelectors) {
      try {
        contentEditor = await page.$(selector);
        if (contentEditor) {
          console.log(`   \u4F7F\u7528\u9009\u62E9\u5668: ${selector}`);
          break;
        }
      } catch {
        continue;
      }
    }
    if (contentEditor) {
      await contentEditor.click();
      await page.waitForTimeout(500);
      await contentEditor.fill("");
      await page.keyboard.type(content, { delay: 10 });
      console.log(`   \u5185\u5BB9\u957F\u5EA6: ${content.length} \u5B57\u7B26`);
    } else {
      console.warn("   \u672A\u627E\u5230\u5185\u5BB9\u7F16\u8F91\u5668");
    }
  }
  async uploadCover(imagePath) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      const coverSelector = 'input[type="file"][accept*="image"], .upload-input input';
      await page.setInputFiles(coverSelector, imagePath);
      await page.waitForTimeout(3e3);
      console.log(`   \u5C01\u9762\u56FE\u7247: ${imagePath}`);
    } catch (error) {
      console.warn("   \u5C01\u9762\u4E0A\u4F20\u5931\u8D25:", error);
    }
  }
  async setTags(tags) {
    const page = this.browserManager.getPage();
    if (!page) return;
    try {
      const tagInputSelector = 'input[placeholder*="\u8BDD\u9898"], input[placeholder*="\u6807\u7B7E"], .tag-input input';
      await page.waitForSelector(tagInputSelector, { timeout: 5e3 });
      for (const tag of tags.slice(0, 3)) {
        await page.fill(tagInputSelector, "#" + tag);
        await page.waitForTimeout(500);
        await page.keyboard.press("Enter");
        await page.waitForTimeout(500);
      }
      console.log(`   \u6807\u7B7E: ${tags.slice(0, 3).join(", ")}`);
    } catch (error) {
      console.warn("   \u6807\u7B7E\u8BBE\u7F6E\u5931\u8D25:", error);
    }
  }
  async clickPublish() {
    const page = this.browserManager.getPage();
    if (!page) return;
    const publishSelector = 'button:has-text("\u53D1\u5E03"), .publish-btn, [class*="publish"]';
    await page.waitForSelector(publishSelector, { timeout: 1e4 });
    await page.click(publishSelector);
    await page.waitForTimeout(3e3);
  }
  async getArticleUrl() {
    const page = this.browserManager.getPage();
    if (!page) return null;
    try {
      await page.waitForTimeout(2e3);
      const url = page.url();
      if (url.includes("xiaohongshu.com/")) {
        return url;
      }
      return null;
    } catch {
      return null;
    }
  }
};

// src/adapters/index.ts
var adapterMap = {
  zhihu: () => new ZhihuAdapter(),
  bilibili: () => new BilibiliAdapter(),
  baijiahao: () => new BaijiahaoAdapter(),
  toutiao: () => new ToutiaoAdapter(),
  xiaohongshu: () => new XiaohongshuAdapter()
};
function getAdapter(platform) {
  const createAdapter = adapterMap[platform];
  if (!createAdapter) {
    throw new Error(`Unknown platform: ${platform}`);
  }
  return createAdapter();
}
function getAllAdapters() {
  return Object.values(adapterMap).map((create) => create());
}

// src/lib/auto-install.ts
import { existsSync as existsSync4, readdirSync } from "fs";
import { homedir } from "os";
import { join as join4, dirname } from "path";
import { fileURLToPath as fileURLToPath2 } from "url";
var __filename2 = fileURLToPath2(import.meta.url);
var __dirname2 = dirname(__filename2);
var checkResult = null;
function getPlaywrightCacheDir() {
  const platform = process.platform;
  const home = homedir();
  switch (platform) {
    case "win32":
      return join4(home, "AppData", "Local", "ms-playwright");
    case "darwin":
      return join4(home, "Library", "Caches", "ms-playwright");
    default:
      return join4(home, ".cache", "ms-playwright");
  }
}
function hasNodeModules() {
  const nodeModulesPath = join4(__dirname2, "..", "node_modules");
  const playwrightPath = join4(nodeModulesPath, "playwright");
  return existsSync4(nodeModulesPath) && existsSync4(playwrightPath);
}
function hasChromiumInstalled() {
  const cacheDir = getPlaywrightCacheDir();
  if (!existsSync4(cacheDir)) {
    return false;
  }
  try {
    const files = readdirSync(cacheDir);
    return files.some((file) => file.startsWith("chromium-"));
  } catch {
    return false;
  }
}
async function checkAndInstall() {
  if (checkResult) {
    const { hasDeps: hasDeps2, hasBrowser: hasBrowser2 } = checkResult;
    if (hasDeps2 && hasBrowser2) {
      return { ready: true, message: "All dependencies are ready." };
    }
  }
  const hasDeps = hasNodeModules();
  const hasBrowser = hasChromiumInstalled();
  checkResult = { hasDeps, hasBrowser };
  if (hasDeps && hasBrowser) {
    return { ready: true, message: "All dependencies are ready." };
  }
  const instructions = [];
  if (!hasDeps) {
    instructions.push("npm dependencies not found. Please run:");
    instructions.push("  cd " + join4(__dirname2, ".."));
    instructions.push("  npm install --registry=https://registry.npmmirror.com");
  }
  if (!hasBrowser) {
    instructions.push("Playwright browser not found. Please run:");
    instructions.push("  npm run install:browser:cn");
    instructions.push("or:");
    instructions.push("  npx playwright install chromium");
  }
  return {
    ready: false,
    message: "Missing dependencies:\n" + instructions.join("\n")
  };
}

// src/index.ts
async function check_environment() {
  try {
    const result = await checkAndInstall();
    if (result.ready) {
      return {
        result: `\u2705 ${result.message}

\u73AF\u5883\u5DF2\u5C31\u7EEA\uFF0C\u53EF\u4EE5\u4F7F\u7528\u4EE5\u4E0B\u529F\u80FD\uFF1A
- login_platform: \u767B\u5F55\u5E73\u53F0
- publish_article: \u53D1\u5E03\u6587\u7AE0
- list_platforms: \u67E5\u770B\u6240\u6709\u5E73\u53F0`,
        data: { ready: true }
      };
    } else {
      return {
        result: `\u26A0\uFE0F ${result.message}`,
        data: { ready: false }
      };
    }
  } catch (error) {
    return {
      result: `\u73AF\u5883\u68C0\u67E5\u5931\u8D25: ${error instanceof Error ? error.message : String(error)}

\u8BF7\u624B\u52A8\u8FD0\u884C\u4EE5\u4E0B\u547D\u4EE4\u5B89\u88C5\u4F9D\u8D56\uFF1A
1. npm install --registry=https://registry.npmmirror.com
2. npm run install:browser:cn`,
      data: { ready: false }
    };
  }
}
async function login_platform(params) {
  const { platform } = params;
  if (!PLATFORMS[platform]) {
    return {
      result: `\u4E0D\u652F\u6301\u7684\u5E73\u53F0: ${platform}\u3002\u652F\u6301\u7684\u5E73\u53F0\u6709: ${Object.keys(PLATFORMS).join(", ")}`
    };
  }
  try {
    const adapter = getAdapter(platform);
    const message = await adapter.openLoginPage();
    return {
      result: message,
      data: {
        platform,
        status: "waiting_for_login",
        loginUrl: PLATFORMS[platform].loginUrl
      }
    };
  } catch (error) {
    return {
      result: `\u767B\u5F55\u5931\u8D25: ${error instanceof Error ? error.message : String(error)}`
    };
  }
}
async function wait_for_login(params) {
  const { platform, timeout = 12e4 } = params;
  try {
    const adapter = getAdapter(platform);
    const success = await adapter.waitForLogin(timeout);
    if (success) {
      return {
        result: `${PLATFORMS[platform].displayName}\u767B\u5F55\u6210\u529F\uFF01\u767B\u5F55\u72B6\u6001\u5DF2\u4FDD\u5B58\uFF0C\u4E0B\u6B21\u4F7F\u7528\u65E0\u9700\u91CD\u65B0\u767B\u5F55\u3002`,
        data: { platform, status: "logged_in" }
      };
    } else {
      return {
        result: `${PLATFORMS[platform].displayName}\u767B\u5F55\u8D85\u65F6\uFF0C\u8BF7\u91CD\u8BD5\u3002`,
        data: { platform, status: "login_timeout" }
      };
    }
  } catch (error) {
    return {
      result: `\u7B49\u5F85\u767B\u5F55\u5931\u8D25: ${error instanceof Error ? error.message : String(error)}`
    };
  }
}
async function check_login_status(params) {
  const { platform } = params;
  if (platform) {
    if (!PLATFORMS[platform]) {
      return {
        result: `\u4E0D\u652F\u6301\u7684\u5E73\u53F0: ${platform}`
      };
    }
    try {
      const adapter = getAdapter(platform);
      const isLoggedIn = await adapter.checkLoginStatus();
      const cookieInfo = await new (await Promise.resolve().then(() => (init_cookie_manager(), cookie_manager_exports))).CookieManager(platform).getCookieInfo();
      const status = {
        platform,
        isLoggedIn,
        lastLoginTime: cookieInfo?.createdAt,
        expiresAt: cookieInfo?.expiresAt
      };
      return {
        result: isLoggedIn ? `${PLATFORMS[platform].displayName}\u5DF2\u767B\u5F55\u3002\u767B\u5F55\u65F6\u95F4: ${status.lastLoginTime?.toLocaleString()}\uFF0C\u8FC7\u671F\u65F6\u95F4: ${status.expiresAt?.toLocaleString()}` : `${PLATFORMS[platform].displayName}\u672A\u767B\u5F55\u6216\u767B\u5F55\u5DF2\u8FC7\u671F\uFF0C\u8BF7\u5148\u767B\u5F55\u3002`,
        data: status
      };
    } catch (error) {
      return {
        result: `\u68C0\u67E5\u767B\u5F55\u72B6\u6001\u5931\u8D25: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  } else {
    const statuses = [];
    const adapters = getAllAdapters();
    for (const adapter of adapters) {
      try {
        const isLoggedIn = await adapter.checkLoginStatus();
        const cookieInfo = await new (await Promise.resolve().then(() => (init_cookie_manager(), cookie_manager_exports))).CookieManager(adapter.getPlatformName()).getCookieInfo();
        statuses.push({
          platform: adapter.getPlatformName(),
          isLoggedIn,
          lastLoginTime: cookieInfo?.createdAt,
          expiresAt: cookieInfo?.expiresAt
        });
      } catch (error) {
        statuses.push({
          platform: adapter.getPlatformName(),
          isLoggedIn: false
        });
      }
    }
    const loggedIn = statuses.filter((s) => s.isLoggedIn);
    const notLoggedIn = statuses.filter((s) => !s.isLoggedIn);
    let message = "\u767B\u5F55\u72B6\u6001\u6C47\u603B:\n";
    if (loggedIn.length > 0) {
      message += `
\u5DF2\u767B\u5F55\u5E73\u53F0: ${loggedIn.map((s) => PLATFORMS[s.platform].displayName).join("\u3001")}`;
    }
    if (notLoggedIn.length > 0) {
      message += `
\u672A\u767B\u5F55\u5E73\u53F0: ${notLoggedIn.map((s) => PLATFORMS[s.platform].displayName).join("\u3001")}`;
    }
    return {
      result: message,
      data: statuses
    };
  }
}
async function logout_platform(params) {
  const { platform } = params;
  if (!PLATFORMS[platform]) {
    return {
      result: `\u4E0D\u652F\u6301\u7684\u5E73\u53F0: ${platform}`
    };
  }
  try {
    const adapter = getAdapter(platform);
    await adapter.logout();
    return {
      result: `${PLATFORMS[platform].displayName}\u5DF2\u9000\u51FA\u767B\u5F55\uFF0C\u767B\u5F55\u72B6\u6001\u5DF2\u6E05\u9664\u3002`,
      data: { platform, status: "logged_out" }
    };
  } catch (error) {
    return {
      result: `\u9000\u51FA\u767B\u5F55\u5931\u8D25: ${error instanceof Error ? error.message : String(error)}`
    };
  }
}
async function publish_article(params) {
  const { platform, title, content, coverImage, tags, summary, category, testMode } = params;
  if (!PLATFORMS[platform]) {
    return {
      result: `\u4E0D\u652F\u6301\u7684\u5E73\u53F0: ${platform}`
    };
  }
  if (!title || !content) {
    return {
      result: "\u6807\u9898\u548C\u5185\u5BB9\u4E0D\u80FD\u4E3A\u7A7A"
    };
  }
  try {
    const adapter = getAdapter(platform);
    const article = { title, content, coverImage, tags, summary, category };
    const result = await adapter.publish(article, testMode);
    if (result.success) {
      if (testMode) {
        return {
          result: `\u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u300A${title}\u300B\u5DF2\u586B\u5199\u5230${PLATFORMS[platform].displayName}\uFF0C\u672A\u53D1\u5E03\u3002`,
          data: result
        };
      }
      return {
        result: `\u6587\u7AE0\u300A${title}\u300B\u5DF2\u6210\u529F\u53D1\u5E03\u5230${PLATFORMS[platform].displayName}\uFF01${result.url ? `
\u6587\u7AE0\u94FE\u63A5: ${result.url}` : ""}`,
        data: result
      };
    } else {
      return {
        result: `\u53D1\u5E03\u5931\u8D25: ${result.message}${result.error ? `
\u9519\u8BEF: ${result.error}` : ""}`,
        data: result
      };
    }
  } catch (error) {
    return {
      result: `\u53D1\u5E03\u5931\u8D25: ${error instanceof Error ? error.message : String(error)}`
    };
  }
}
async function publish_to_all(params) {
  const { title, content, coverImage, tags, summary, category, testMode } = params;
  if (!title || !content) {
    return {
      result: "\u6807\u9898\u548C\u5185\u5BB9\u4E0D\u80FD\u4E3A\u7A7A"
    };
  }
  const article = { title, content, coverImage, tags, summary, category };
  const adapters = getAllAdapters();
  const results = [];
  for (const adapter of adapters) {
    try {
      const isLoggedIn = await adapter.checkLoginStatus();
      if (isLoggedIn) {
        const result = await adapter.publish(article, testMode);
        results.push(result);
      }
    } catch (error) {
      results.push({
        success: false,
        platform: adapter.getPlatformName(),
        message: "\u53D1\u5E03\u5931\u8D25",
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }
  const successCount = results.filter((r) => r.success).length;
  const failCount = results.filter((r) => !r.success).length;
  let message = testMode ? `\u6D4B\u8BD5\u6A21\u5F0F\uFF1A\u6587\u7AE0\u300A${title}\u300B\u5DF2\u586B\u5199\u5B8C\u6210\uFF01
` : `\u6587\u7AE0\u300A${title}\u300B\u53D1\u5E03\u5B8C\u6210\uFF01
`;
  message += `\u6210\u529F: ${successCount}\u4E2A\u5E73\u53F0
`;
  message += `\u5931\u8D25: ${failCount}\u4E2A\u5E73\u53F0
`;
  for (const result of results) {
    const platformName = PLATFORMS[result.platform].displayName;
    if (result.success) {
      if (testMode) {
        message += `
\u2705 ${platformName}: \u5DF2\u586B\u5199${result.url ? ` - ${result.url}` : ""}`;
      } else {
        message += `
\u2705 ${platformName}: \u53D1\u5E03\u6210\u529F${result.url ? ` - ${result.url}` : ""}`;
      }
    } else {
      message += `
\u274C ${platformName}: ${result.message}`;
    }
  }
  return {
    result: message,
    data: results
  };
}
async function list_platforms() {
  const adapters = getAllAdapters();
  const platformList = [];
  for (const adapter of adapters) {
    try {
      const isLoggedIn = await adapter.checkLoginStatus();
      platformList.push({
        name: adapter.getPlatformName(),
        displayName: adapter.getDisplayName(),
        isLoggedIn
      });
    } catch {
      platformList.push({
        name: adapter.getPlatformName(),
        displayName: adapter.getDisplayName(),
        isLoggedIn: false
      });
    }
  }
  let message = "\u652F\u6301\u7684\u5E73\u53F0\u5217\u8868:\n\n";
  for (const platform of platformList) {
    const status = platform.isLoggedIn ? "\u2705 \u5DF2\u767B\u5F55" : "\u274C \u672A\u767B\u5F55";
    message += `${platform.displayName} (${platform.name}): ${status}
`;
  }
  return {
    result: message,
    data: platformList
  };
}
async function get_category_options(params) {
  const { platform } = params;
  if (!PLATFORMS[platform]) {
    return {
      result: `\u4E0D\u652F\u6301\u7684\u5E73\u53F0: ${platform}`
    };
  }
  const categoryMap = {
    baijiahao: {
      categories: [
        "\u79D1\u6280/\u4E92\u8054\u7F51",
        "\u79D1\u6280/\u6570\u7801",
        "\u79D1\u6280/\u624B\u673A",
        "\u79D1\u6280/\u7535\u8111",
        "\u8D22\u7ECF/\u80A1\u7968",
        "\u8D22\u7ECF/\u57FA\u91D1",
        "\u8D22\u7ECF/\u7406\u8D22",
        "\u5A31\u4E50/\u660E\u661F",
        "\u5A31\u4E50/\u7535\u5F71",
        "\u5A31\u4E50/\u97F3\u4E50",
        "\u4F53\u80B2/\u8DB3\u7403",
        "\u4F53\u80B2/\u7BEE\u7403",
        "\u4F53\u80B2/\u5065\u8EAB",
        "\u6559\u80B2/\u8003\u8BD5",
        "\u6559\u80B2/\u7559\u5B66",
        "\u6559\u80B2/\u804C\u573A",
        "\u6C7D\u8F66/\u8BC4\u6D4B",
        "\u6C7D\u8F66/\u5BFC\u8D2D",
        "\u7F8E\u98DF/\u83DC\u8C31",
        "\u7F8E\u98DF/\u63A2\u5E97",
        "\u65C5\u6E38/\u56FD\u5185\u6E38",
        "\u65C5\u6E38/\u51FA\u5883\u6E38",
        "\u65F6\u5C1A/\u7A7F\u642D",
        "\u65F6\u5C1A/\u7F8E\u5986",
        "\u6E38\u620F/\u624B\u6E38",
        "\u6E38\u620F/\u7AEF\u6E38",
        "\u6E38\u620F/\u4E3B\u673A",
        "\u5065\u5EB7/\u517B\u751F",
        "\u5065\u5EB7/\u533B\u7597",
        "\u80B2\u513F/\u65E9\u6559",
        "\u80B2\u513F/\u4EB2\u5B50",
        "\u5386\u53F2/\u5386\u53F2\u6545\u4E8B",
        "\u5386\u53F2/\u4EBA\u7269",
        "\u6587\u5316/\u4F20\u7EDF\u6587\u5316",
        "\u6587\u5316/\u827A\u672F",
        "\u793E\u4F1A/\u6C11\u751F",
        "\u793E\u4F1A/\u70ED\u70B9",
        "\u56FD\u9645/\u56FD\u9645\u65B0\u95FB",
        "\u56FD\u9645/\u519B\u4E8B"
      ],
      format: "\u4E00\u7EA7\u5206\u7C7B/\u4E8C\u7EA7\u5206\u7C7B",
      example: "\u79D1\u6280/\u4E92\u8054\u7F51"
    },
    toutiao: {
      categories: [
        "\u79D1\u6280",
        "\u8D22\u7ECF",
        "\u5A31\u4E50",
        "\u4F53\u80B2",
        "\u6559\u80B2",
        "\u6C7D\u8F66",
        "\u7F8E\u98DF",
        "\u65C5\u6E38",
        "\u65F6\u5C1A",
        "\u6E38\u620F",
        "\u5065\u5EB7",
        "\u80B2\u513F",
        "\u5386\u53F2",
        "\u6587\u5316",
        "\u793E\u4F1A",
        "\u56FD\u9645"
      ],
      format: "\u5355\u7EA7\u5206\u7C7B",
      example: "\u79D1\u6280"
    },
    zhihu: {
      categories: [
        "\u79D1\u6280",
        "\u79D1\u5B66",
        "\u4E92\u8054\u7F51",
        "\u7F16\u7A0B",
        "\u4EBA\u5DE5\u667A\u80FD",
        "\u5FC3\u7406\u5B66",
        "\u7ECF\u6D4E\u5B66",
        "\u91D1\u878D",
        "\u6CD5\u5F8B",
        "\u6559\u80B2",
        "\u804C\u4E1A\u53D1\u5C55",
        "\u751F\u6D3B",
        "\u6587\u5316",
        "\u827A\u672F",
        "\u5386\u53F2",
        "\u4F53\u80B2",
        "\u6E38\u620F",
        "\u6C7D\u8F66",
        "\u7F8E\u98DF",
        "\u65C5\u884C",
        "\u6444\u5F71",
        "\u65F6\u5C1A",
        "\u5065\u5EB7",
        "\u60C5\u611F"
      ],
      format: "\u5355\u7EA7\u5206\u7C7B",
      example: "\u79D1\u6280"
    },
    bilibili: {
      categories: [
        "\u52A8\u753B",
        "\u6E38\u620F",
        "\u79D1\u6280",
        "\u6570\u7801",
        "\u6C7D\u8F66",
        "\u751F\u6D3B",
        "\u7F8E\u98DF",
        "\u65F6\u5C1A",
        "\u5A31\u4E50",
        "\u97F3\u4E50",
        "\u821E\u8E48",
        "\u5F71\u89C6",
        "\u77E5\u8BC6",
        "\u6559\u80B2",
        "\u8FD0\u52A8",
        "\u52A8\u7269",
        "\u9B3C\u755C",
        "\u56FD\u521B"
      ],
      format: "\u5355\u7EA7\u5206\u7C7B",
      example: "\u79D1\u6280"
    },
    xiaohongshu: {
      categories: [
        "\u7A7F\u642D",
        "\u7F8E\u5986",
        "\u62A4\u80A4",
        "\u7F8E\u98DF",
        "\u65C5\u884C",
        "\u5065\u8EAB",
        "\u5BB6\u5C45",
        "\u6BCD\u5A74",
        "\u6559\u80B2",
        "\u804C\u573A",
        "\u60C5\u611F",
        "\u5BA0\u7269",
        "\u6444\u5F71",
        "\u827A\u672F",
        "\u6570\u7801",
        "\u6C7D\u8F66"
      ],
      format: "\u5355\u7EA7\u5206\u7C7B",
      example: "\u7A7F\u642D"
    }
  };
  const categoryInfo = categoryMap[platform];
  if (!categoryInfo) {
    return {
      result: `\u6682\u672A\u914D\u7F6E ${PLATFORMS[platform].displayName} \u7684\u5206\u7C7B\u5217\u8868\uFF0C\u8BF7\u624B\u52A8\u4F20\u5165\u5206\u7C7B\u53C2\u6570`,
      data: { platform, categories: [], format: "unknown" }
    };
  }
  let message = `${PLATFORMS[platform].displayName} \u652F\u6301\u7684\u5206\u7C7B\u9009\u9879:

`;
  message += `\u5206\u7C7B\u683C\u5F0F: ${categoryInfo.format}
`;
  message += `\u793A\u4F8B: ${categoryInfo.example}

`;
  message += `\u652F\u6301\u7684\u5206\u7C7B:
`;
  const sortedCategories = [...categoryInfo.categories].sort();
  for (const cat of sortedCategories) {
    message += `  - ${cat}
`;
  }
  message += `
\u63D0\u793A: \u8BF7\u6839\u636E\u6587\u7AE0\u6807\u9898\u548C\u5185\u5BB9\uFF0C\u9009\u62E9\u6700\u5408\u9002\u7684\u5206\u7C7B\u3002`;
  message += `
\u5982\u679C\u6587\u7AE0\u5185\u5BB9\u6D89\u53CA\u591A\u4E2A\u9886\u57DF\uFF0C\u8BF7\u9009\u62E9\u6700\u4E3B\u8981\u7684\u4E00\u4E2A\u5206\u7C7B\u3002`;
  return {
    result: message,
    data: {
      platform,
      categories: categoryInfo.categories,
      format: categoryInfo.format,
      example: categoryInfo.example
    }
  };
}
var index_default = {
  tools: {
    check_environment: {
      description: "\u68C0\u67E5\u73AF\u5883\u4F9D\u8D56\u5E76\u81EA\u52A8\u5B89\u88C5\uFF08\u9996\u6B21\u4F7F\u7528\u65F6\u5FC5\u987B\u8C03\u7528\u6B64\u5DE5\u5177\uFF09\u3002\u4F1A\u81EA\u52A8\u68C0\u6D4B\u5E76\u5B89\u88C5 npm \u4F9D\u8D56\u548C Playwright \u6D4F\u89C8\u5668\u3002",
      parameters: {},
      execute: check_environment
    },
    login_platform: {
      description: "\u767B\u5F55\u6307\u5B9A\u5E73\u53F0\uFF0C\u6253\u5F00\u6D4F\u89C8\u5668\u8BA9\u7528\u6237\u626B\u7801\u767B\u5F55",
      parameters: {
        platform: {
          type: "string",
          description: "\u5E73\u53F0\u540D\u79F0\uFF0C\u53EF\u9009\u503C: zhihu, bilibili, baijiahao, toutiao, xiaohongshu",
          required: true
        }
      },
      execute: login_platform
    },
    wait_for_login: {
      description: "\u7B49\u5F85\u7528\u6237\u5B8C\u6210\u626B\u7801\u767B\u5F55",
      parameters: {
        platform: {
          type: "string",
          description: "\u5E73\u53F0\u540D\u79F0",
          required: true
        },
        timeout: {
          type: "number",
          description: "\u8D85\u65F6\u65F6\u95F4\uFF08\u6BEB\u79D2\uFF09\uFF0C\u9ED8\u8BA4120000",
          required: false
        }
      },
      execute: wait_for_login
    },
    check_login_status: {
      description: "\u68C0\u67E5\u6307\u5B9A\u5E73\u53F0\u6216\u6240\u6709\u5E73\u53F0\u7684\u767B\u5F55\u72B6\u6001",
      parameters: {
        platform: {
          type: "string",
          description: "\u5E73\u53F0\u540D\u79F0\uFF0C\u4E0D\u4F20\u5219\u68C0\u67E5\u6240\u6709\u5E73\u53F0",
          required: false
        }
      },
      execute: check_login_status
    },
    logout_platform: {
      description: "\u9000\u51FA\u6307\u5B9A\u5E73\u53F0\u7684\u767B\u5F55",
      parameters: {
        platform: {
          type: "string",
          description: "\u5E73\u53F0\u540D\u79F0",
          required: true
        }
      },
      execute: logout_platform
    },
    publish_article: {
      description: "\u53D1\u5E03\u6587\u7AE0\u5230\u6307\u5B9A\u5E73\u53F0",
      parameters: {
        platform: {
          type: "string",
          description: "\u5E73\u53F0\u540D\u79F0",
          required: true
        },
        title: {
          type: "string",
          description: "\u6587\u7AE0\u6807\u9898",
          required: true
        },
        content: {
          type: "string",
          description: "\u6587\u7AE0\u5185\u5BB9",
          required: true
        },
        coverImage: {
          type: "string",
          description: "\u5C01\u9762\u56FE\u7247\u8DEF\u5F84\u6216URL",
          required: false
        },
        tags: {
          type: "array",
          description: "\u6587\u7AE0\u6807\u7B7E",
          required: false
        },
        summary: {
          type: "string",
          description: "\u6587\u7AE0\u6458\u8981",
          required: false
        },
        category: {
          type: "string",
          description: "\u6587\u7AE0\u5206\u7C7B",
          required: false
        },
        testMode: {
          type: "boolean",
          description: "\u6D4B\u8BD5\u6A21\u5F0F\uFF0C\u4E3Atrue\u65F6\u53EA\u586B\u5199\u6587\u7AE0\u4E0D\u53D1\u5E03",
          required: false
        }
      },
      execute: publish_article
    },
    publish_to_all: {
      description: "\u53D1\u5E03\u6587\u7AE0\u5230\u6240\u6709\u5DF2\u767B\u5F55\u7684\u5E73\u53F0",
      parameters: {
        title: {
          type: "string",
          description: "\u6587\u7AE0\u6807\u9898",
          required: true
        },
        content: {
          type: "string",
          description: "\u6587\u7AE0\u5185\u5BB9",
          required: true
        },
        coverImage: {
          type: "string",
          description: "\u5C01\u9762\u56FE\u7247\u8DEF\u5F84\u6216URL",
          required: false
        },
        tags: {
          type: "array",
          description: "\u6587\u7AE0\u6807\u7B7E",
          required: false
        },
        summary: {
          type: "string",
          description: "\u6587\u7AE0\u6458\u8981",
          required: false
        },
        category: {
          type: "string",
          description: "\u6587\u7AE0\u5206\u7C7B",
          required: false
        },
        testMode: {
          type: "boolean",
          description: "\u6D4B\u8BD5\u6A21\u5F0F\uFF0C\u4E3Atrue\u65F6\u53EA\u586B\u5199\u6587\u7AE0\u4E0D\u53D1\u5E03",
          required: false
        }
      },
      execute: publish_to_all
    },
    list_platforms: {
      description: "\u5217\u51FA\u6240\u6709\u652F\u6301\u7684\u5E73\u53F0\u53CA\u5176\u767B\u5F55\u72B6\u6001",
      parameters: {},
      execute: list_platforms
    },
    get_category_options: {
      description: "\u83B7\u53D6\u6307\u5B9A\u5E73\u53F0\u652F\u6301\u7684\u5206\u7C7B\u9009\u9879\u5217\u8868\u3002OpenClaw\u5E94\u6839\u636E\u6587\u7AE0\u6807\u9898\u548C\u5185\u5BB9\uFF0C\u5206\u6790\u9009\u62E9\u6700\u5408\u9002\u7684\u5206\u7C7B\uFF0C\u7136\u540E\u8C03\u7528publish_article\u65F6\u4F20\u5165\u5206\u7C7B\u53C2\u6570",
      parameters: {
        platform: {
          type: "string",
          description: "\u5E73\u53F0\u540D\u79F0\uFF0C\u53EF\u9009\u503C: zhihu, bilibili, baijiahao, toutiao, xiaohongshu",
          required: true
        }
      },
      execute: get_category_options
    }
  }
};
export {
  check_environment,
  check_login_status,
  index_default as default,
  get_category_options,
  list_platforms,
  login_platform,
  logout_platform,
  publish_article,
  publish_to_all,
  wait_for_login
};
