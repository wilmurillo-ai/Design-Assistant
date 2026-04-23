/**
 * Chrome Use - Control your local Chrome browser via chrome.debugger API
 *
 * Usage:
 *   import { connect, navigate, evaluate, click, fill, screenshot } from 'chrome-use';
 *
 *   await connect();
 *   await navigate('https://example.com');
 *   const html = await getHtml();
 *   await disconnect();
 */

import { ChromeBridge } from './src/chrome-bridge.js';

// Global bridge instance
let bridge = null;

/**
 * Connect to Chrome browser
 * Automatically starts WebSocket server and waits for extension to connect.
 * If extension is not connected, it will launch Chrome automatically.
 */
export async function connect() {
  bridge = new ChromeBridge();
  return await bridge.connect(true);
}

/**
 * Launch Chrome with extension loaded manually.
 * Use this ONLY when you need to start Chrome before calling connect().
 * Normally connect() handles this automatically.
 *
 * @returns {Object} { status: 'launched', pid: Chrome process ID }
 */
export function launchChrome() {
  if (!bridge) {
    bridge = new ChromeBridge();
  }
  return bridge.launchChrome();
}

/**
 * Disconnect from Chrome browser.
 * Does NOT close Chrome - leaves it running.
 */
export function disconnect() {
  if (!bridge) {
    return { status: 'disconnected' };
  }
  return bridge.disconnect();
}

/**
 * Check if connected to Chrome
 */
export function isConnected() {
  return bridge && bridge.isConnected();
}

/**
 * Navigate to a URL
 * @param {string} url - Target URL
 */
export async function navigate(url) {
  if (!bridge) throw new Error('Not connected. Call connect() first.');
  return await bridge.navigate(url);
}

/**
 * Evaluate JavaScript in the current tab
 * @param {string} script - JavaScript code to execute
 * @returns {*} Result of the evaluation
 */
export async function evaluate(script) {
  if (!bridge) throw new Error('Not connected. Call connect() first.');
  return await bridge.evaluate(script);
}

/**
 * Get page HTML content
 * @returns {string} Full page HTML
 */
export async function getHtml() {
  if (!bridge) throw new Error('Not connected. Call connect() first.');
  return await bridge.getHtml();
}

/**
 * Take a screenshot
 * @param {boolean} fullPage - Capture full page or just viewport
 * @returns {string} Base64 encoded PNG image
 */
export async function screenshot(fullPage = false) {
  if (!bridge) throw new Error('Not connected. Call connect() first.');
  return await bridge.screenshot(fullPage);
}

/**
 * Click an element
 * @param {string} selector - CSS selector
 */
export async function click(selector) {
  if (!bridge) throw new Error('Not connected. Call connect() first.');
  return await bridge.click(selector);
}

/**
 * Fill an input field
 * @param {string} selector - CSS selector
 * @param {string} value - Value to fill
 */
export async function fill(selector, value) {
  if (!bridge) throw new Error('Not connected. Call connect() first.');
  return await bridge.fill(selector, value);
}

/**
 * List all open tabs
 * @returns {Array} List of tab objects
 */
export async function listTabs() {
  if (!bridge) throw new Error('Not connected. Call connect() first.');
  return await bridge.listTabs();
}

/**
 * Switch to a different tab
 * @param {number} tabId - Tab ID to switch to
 */
export async function switchTab(tabId) {
  if (!bridge) throw new Error('Not connected. Call connect() first.');
  return await bridge.switchTab(tabId);
}

/**
 * Create a new tab
 * @param {string} url - URL to open in new tab (default: about:blank)
 */
export async function newTab(url = 'about:blank') {
  if (!bridge) throw new Error('Not connected. Call connect() first.');
  return await bridge.newTab(url);
}

/**
 * Get Chrome installation command
 */
export function getInstallationCommand() {
  const b = new ChromeBridge();
  return b.getInstallationCommand();
}

/**
 * Get installation guide
 */
export function getInstallationGuide() {
  const b = new ChromeBridge();
  return b.getInstallationGuide();
}
