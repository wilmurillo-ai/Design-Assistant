/**
 * Chrome Bridge - manages Chrome browser and WebSocket server
 */

import { spawn, execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { ChromeWebSocketServer } from './websocket-server.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const EXTENSION_PATH = path.resolve(__dirname, '../extension');

export class ChromeBridge {
  constructor() {
    this.server = new ChromeWebSocketServer(9224);
    this.chromeProc = null;
    this.currentTabId = null;
    this.connected = false;
    this.aliveInterval = null;
  }

  _keepAlive() {
    // Prevent process from exiting by keeping event loop busy
    this.aliveInterval = setInterval(() => {
      // Periodically check connection is still alive
      if (!this.server.isConnected()) {
        console.log('[Chrome Use] Extension disconnected');
      }
    }, 30000);
  }

  /**
   * Get Chrome executable path based on platform
   */
  getChromePath() {
    const platform = process.platform;
    if (platform === 'darwin') {
      return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
    } else if (platform === 'win32') {
      return 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
    } else {
      return 'google-chrome';
    }
  }

  /**
   * Get Chrome profile directory
   */
  getProfileDir() {
    const platform = process.platform;
    if (platform === 'darwin') {
      return process.env.HOME + '/Library/Application Support/Google/Chrome';
    } else if (platform === 'win32') {
      return process.env.LOCALAPPDATA + '\\Google\\Chrome\\User Data';
    } else {
      return process.env.HOME + '/.config/google-chrome';
    }
  }

  /**
   * Launch Chrome with extension loaded
   */
  launchChrome() {
    const chromePath = this.getChromePath();
    const profileDir = this.getProfileDir();

    const args = [
      '--no-first-run',
      '--no-default-browser-check',
      '--new-window',
      `--user-data-dir=${profileDir}`,
      `--load-extension=${EXTENSION_PATH}`,
    ];

    // Set DISPLAY for Linux
    const env = { ...process.env };
    if (process.platform === 'linux') {
      const display = process.env.DISPLAY || ':0';
      env.DISPLAY = display;
    }

    console.log(`Launching Chrome: ${chromePath} ${args.join(' ')}`);

    this.chromeProc = spawn(chromePath, args, {
      env,
      stdio: 'ignore',
      detached: false,
    });

    this.chromeProc.on('error', (err) => {
      console.error('Failed to launch Chrome:', err);
      throw new Error(`google-chrome not found. Please install Google Chrome.`);
    });

    console.log(`Chrome launched with PID: ${this.chromeProc.pid}`);
    return { pid: this.chromeProc.pid };
  }

  /**
   * Connect to Chrome via extension
   */
  async connect(autoLaunch = true) {
    // Start WebSocket server
    await this.server.start();

    // Wait for extension to connect
    let connected = await this._waitForExtension(10000);
    if (connected) {
      return await this._finishConnect();
    }

    if (!autoLaunch) {
      return { status: 'failed', error: 'Extension not connected and autoLaunch disabled.' };
    }

    // Launch Chrome and retry connection up to 3 times
    for (let retry = 1; retry <= 3; retry++) {
      console.log(`Launch attempt ${retry}/3...`);
      this.launchChrome();

      // Wait for Chrome process to appear (up to 30s)
      const processFound = await this._waitForChromeProcess(30000);
      if (!processFound) {
        console.log('Chrome process not found after 30s');
        if (retry === 3) {
          return { status: 'failed', error: 'Chrome process did not start after 3 attempts.' };
        }
        continue;
      }

      // Wait for extension to connect (up to 10s)
      connected = await this._waitForExtension(10000);
      if (connected) {
        return await this._finishConnect();
      }

      console.log('Extension not connected after 10s');
      if (retry === 3) {
        return { status: 'failed', error: 'Could not connect to Chrome extension after 3 attempts.' };
      }
    }
  }

  /**
   * Wait for Chrome process to appear
   */
  async _waitForChromeProcess(timeout) {
    const chromePath = this.getChromePath();
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      if (this._isChromeRunning(chromePath)) {
        return true;
      }
      await this.sleep(500);
    }
    return false;
  }

  /**
   * Check if Chrome process is running
   */
  _isChromeRunning(chromePath) {
    try {
      const cmd = process.platform === 'win32'
        ? `tasklist /FI "IMAGENAME eq chrome.exe" /NH`
        : `pgrep -f "${chromePath}" | head -1`;
      const output = execSync(cmd, { encoding: 'utf8' });
      return output.trim().length > 0;
    } catch {
      return false;
    }
  }

  /**
   * Wait for extension to connect
   */
  async _waitForExtension(timeout) {
    for (let i = 0; i < timeout / 1000; i++) {
      await this.sleep(1000);
      if (this.server.isConnected()) {
        return true;
      }
      console.log(`Waiting for extension to connect... (${i + 1}/${timeout / 1000})`);
    }
    return false;
  }

  /**
   * Finish connection after extension is connected
   */
  async _finishConnect() {
    // Get tabs - prefer the active tab
    const tabsResult = await this.server.getTabs();
    const tabs = tabsResult.tabs || [];
    const activeTab = tabs.find(t => t.active);
    this.currentTabId = activeTab ? activeTab.id : (tabs.length > 0 ? tabs[0].id : null);

    this.connected = true;
    this._keepAlive();

    return {
      status: 'connected',
      mode: 'debugger',
      port: 9224,
      extension_installed: true,
      tab_id: this.currentTabId,
    };
  }

  /**
   * Disconnect from Chrome
   */
  disconnect() {
    if (this.aliveInterval) {
      clearInterval(this.aliveInterval);
      this.aliveInterval = null;
    }
    if (this.chromeProc) {
      // Don't kill Chrome, just stop the server
      this.chromeProc = null;
    }
    this.server.stop();
    this.connected = false;
    return { status: 'disconnected' };
  }

  /**
   * Check if connected
   */
  isConnected() {
    return this.connected && this.server.isConnected();
  }

  /**
   * Navigate to URL using window.location.href
   * (Works on chrome:// tabs unlike Page.navigate)
   */
  async navigate(url) {
    if (!this.currentTabId) {
      throw new Error('No active tab');
    }
    await this.server.evaluate(this.currentTabId, `window.location.href = '${url}'`);
    return { status: 'navigated', url };
  }

  /**
   * Evaluate JavaScript
   */
  async evaluate(script) {
    if (!this.currentTabId) {
      throw new Error('No active tab');
    }
    const result = await this.server.evaluate(this.currentTabId, script);
    return result.result;
  }

  /**
   * Get HTML content
   */
  async getHtml() {
    if (!this.currentTabId) {
      throw new Error('No active tab');
    }
    const result = await this.server.getContent(this.currentTabId);
    return result.content;
  }

  /**
   * Take screenshot
   */
  async screenshot(fullPage = false) {
    if (!this.currentTabId) {
      throw new Error('No active tab');
    }
    const result = await this.server.screenshot(this.currentTabId, fullPage);
    return result.data;
  }

  /**
   * Click element
   */
  async click(selector) {
    if (!this.currentTabId) {
      throw new Error('No active tab');
    }
    const result = await this.server.click(this.currentTabId, selector);
    if (!result.success) {
      throw new Error(result.error || 'Click failed');
    }
    return { status: 'clicked', selector };
  }

  /**
   * Fill input
   */
  async fill(selector, value) {
    if (!this.currentTabId) {
      throw new Error('No active tab');
    }
    const result = await this.server.fill(this.currentTabId, selector, value);
    if (!result.success) {
      throw new Error(result.error || 'Fill failed');
    }
    return { status: 'filled', selector, value };
  }

  /**
   * List tabs
   */
  async listTabs() {
    const result = await this.server.getTabs();
    return result.tabs || [];
  }

  /**
   * Switch tab
   */
  async switchTab(tabId) {
    await this.server.switchTab(tabId);
    this.currentTabId = tabId;
    return { status: 'switched', tabId };
  }

  /**
   * Create a new tab
   */
  async newTab(url = 'about:blank') {
    const result = await this.server.newTab(url);
    if (result.tab && result.tab.id) {
      this.currentTabId = result.tab.id;
    }
    return result;
  }

  /**
   * Get installation command
   */
  getInstallationCommand() {
    const profileDir = this.getProfileDir();
    return `google-chrome --user-data-dir=${profileDir} --load-extension=${EXTENSION_PATH} --no-first-run --no-default-browser-check about:blank`;
  }

  /**
   * Get installation guide
   */
  getInstallationGuide() {
    return `
=== Chrome Use Extension Installation ===

Extension path: ${EXTENSION_PATH}

Installation steps:
1. Open Chrome and go to: chrome://extensions/
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select this folder: ${EXTENSION_PATH}

Once installed, the extension will automatically connect when you use chrome-use.

The extension uses chrome.debugger API which is harder for websites to detect.
`;
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
