// Chrome Use - Background Script
// Uses chrome.debugger API to control Chrome browser
// Communication: Chrome Extension ↔ WebSocket ↔ Node.js

let ws = null;
let reconnectTimer = null;
let messageId = 0;
let debuggerSessions = new Map(); // tabId -> debugger session info

// Default connection settings
let serverHost = 'localhost';
let serverPort = 9224;

const DEBUGGER_VERSION = '1.3';
const DEFAULT_PORT = 9224;

// Attach debugger to a tab
async function attachToTab(tabId) {
  return new Promise((resolve, reject) => {
    if (debuggerSessions.has(tabId)) {
      resolve(true);
      return;
    }

    chrome.debugger.attach({tabId}, DEBUGGER_VERSION, () => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      debuggerSessions.set(tabId, { attached: true });
      resolve(true);
    });
  });
}

// Detach debugger from a tab
async function detachFromTab(tabId) {
  return new Promise((resolve) => {
    if (!debuggerSessions.has(tabId)) {
      resolve(true);
      return;
    }

    chrome.debugger.detach({tabId}, () => {
      debuggerSessions.delete(tabId);
      resolve(true);
    });
  });
}

// Send command to debugger
async function debuggerCommand(tabId, method, params = {}) {
  await attachToTab(tabId);

  return new Promise((resolve, reject) => {
    chrome.debugger.sendCommand({tabId}, method, params, (result, error) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      if (error) {
        reject(new Error(error.message || JSON.stringify(error)));
        return;
      }
      resolve(result);
    });
  });
}

// Connect to Python WebSocket server
function connect(host, port) {
  serverHost = host || 'localhost';
  serverPort = port || DEFAULT_PORT;

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close();
  }

  const url = `ws://${serverHost}:${serverPort}`;

  console.log(`[Chrome Use] Connecting to ${url}`);
  statusUpdate(`Connecting to ${url}...`);

  try {
    ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('[Chrome Use] Connected');
      statusUpdate('Connected', 'green');
      // Get current window ID and send with registration
      chrome.windows.getCurrent((win) => {
        send({ type: 'register', role: 'extension', api: 'debugger', windowId: win.id });
      });

      // Send tabs list after short delay
      setTimeout(() => {
        sendTabsList().catch(e => console.error('Failed to send tabs:', e));
      }, 1000);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleMessage(msg);
      } catch (e) {
        console.error('[Chrome Use] Failed to parse message:', e);
      }
    };

    ws.onclose = () => {
      console.log('[Chrome Use] Disconnected');
      statusUpdate('Disconnected', 'red');
      scheduleReconnect();
    };

    ws.onerror = (error) => {
      console.error('[Chrome Use] WebSocket error:', error);
      statusUpdate('Error', 'red');
    };
  } catch (e) {
    console.error('[Chrome Use] Failed to connect:', e);
    statusUpdate('Failed to connect', 'red');
    scheduleReconnect();
  }
}

function scheduleReconnect() {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
  }
  // Don't reconnect if already connected
  if (ws && ws.readyState === WebSocket.OPEN) {
    return;
  }
  reconnectTimer = setTimeout(() => {
    // Double-check before reconnecting
    if (ws && ws.readyState === WebSocket.OPEN) {
      return;
    }
    console.log('[Chrome Use] Attempting to reconnect...');
    statusUpdate('Reconnecting...', 'orange');
    connect(serverHost, serverPort);
  }, 3000);
}

// Send message to Python
function send(message) {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.warn('[Chrome Use] Not connected');
    return Promise.reject(new Error('Not connected'));
  }

  // Only assign id if not already present (preserve id from incoming requests)
  if (!('id' in message)) {
    message.id = ++messageId;
  }

  ws.send(JSON.stringify(message));
  return Promise.resolve();
}

// Handle incoming messages from Python
function handleMessage(msg) {
  console.log('[Chrome Use] Received:', msg.type, msg);

  // Handle commands from Python
  switch (msg.type) {
    case 'ping':
      send({ type: 'pong' });
      break;

    case 'get_tabs':
      handleGetTabs(msg);
      break;

    case 'navigate':
      handleNavigate(msg);
      break;

    case 'evaluate':
      handleEvaluate(msg);
      break;

    case 'get_content':
      handleGetContent(msg);
      break;

    case 'click':
      handleClick(msg);
      break;

    case 'fill':
      handleFill(msg);
      break;

    case 'screenshot':
      handleScreenshot(msg);
      break;

    case 'switch_tab':
      handleSwitchTab(msg);
      break;

    case 'close_tab':
      handleCloseTab(msg);
      break;

    case 'new_tab':
      handleNewTab(msg);
      break;

    default:
      console.warn('[Chrome Use] Unknown message type:', msg.type);
  }
}

// Get list of tabs
async function handleGetTabs(msg) {
  try {
    const tabs = await chrome.tabs.query({});

    const tabInfo = tabs.map(tab => ({
      id: tab.id,
      title: tab.title,
      url: tab.url,
      active: tab.active
    }));

    send({
      type: 'tabs_list',
      id: msg.id,
      success: true,
      tabs: tabInfo
    });
  } catch (error) {
    send({
      type: 'tabs_list',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Navigate to URL using Page.navigate
async function handleNavigate(msg) {
  const { tabId, url } = msg;

  try {
    await debuggerCommand(tabId, 'Page.navigate', { url });
    send({
      type: 'navigate_result',
      id: msg.id,
      success: true
    });
  } catch (error) {
    send({
      type: 'navigate_result',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Evaluate JavaScript using Runtime.evaluate
async function handleEvaluate(msg) {
  const { tabId, expression } = msg;

  try {
    const result = await debuggerCommand(tabId, 'Runtime.evaluate', {
      expression: expression,
      returnByValue: true
    });

    send({
      type: 'evaluate_result',
      id: msg.id,
      success: true,
      result: result.result ? result.result.value : undefined
    });
  } catch (error) {
    send({
      type: 'evaluate_result',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Get page content
async function handleGetContent(msg) {
  const { tabId } = msg;

  try {
    const result = await debuggerCommand(tabId, 'Runtime.evaluate', {
      expression: 'document.documentElement.outerHTML',
      returnByValue: true
    });

    send({
      type: 'content_result',
      id: msg.id,
      success: true,
      content: result.result ? result.result.value : ''
    });
  } catch (error) {
    send({
      type: 'content_result',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Click element
async function handleClick(msg) {
  const { tabId, selector } = msg;

  try {
    // First find the element
    const result = await debuggerCommand(tabId, 'Runtime.evaluate', {
      expression: `
        (function() {
          const el = document.querySelector('${selector.replace(/'/g, "\\'")}');
          if (!el) return { success: false, error: 'Element not found' };
          el.click();
          return { success: true };
        })()
      `,
      returnByValue: true
    });

    send({
      type: 'click_result',
      id: msg.id,
      ...(result.result ? result.result.value : { success: false, error: 'No result' })
    });
  } catch (error) {
    send({
      type: 'click_result',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Fill input
async function handleFill(msg) {
  const { tabId, selector, value } = msg;

  try {
    const result = await debuggerCommand(tabId, 'Runtime.evaluate', {
      expression: `
        (function() {
          const el = document.querySelector('${selector.replace(/'/g, "\\'")}');
          if (!el) return { success: false, error: 'Element not found' };
          el.value = ${JSON.stringify(value)};
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return { success: true };
        })()
      `,
      returnByValue: true
    });

    send({
      type: 'fill_result',
      id: msg.id,
      ...(result.result ? result.result.value : { success: false, error: 'No result' })
    });
  } catch (error) {
    send({
      type: 'fill_result',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Take screenshot
async function handleScreenshot(msg) {
  const { tabId, fullPage } = msg;

  try {
    // Enable Page domain first
    await debuggerCommand(tabId, 'Page.enable');

    const result = await debuggerCommand(tabId, 'Page.captureScreenshot', {
      format: 'png',
      quality: 100,
      fromSurface: !fullPage
    });

    send({
      type: 'screenshot_result',
      id: msg.id,
      success: true,
      data: result.data,
      fullPage: fullPage || false
    });
  } catch (error) {
    send({
      type: 'screenshot_result',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Switch to a different tab
async function handleSwitchTab(msg) {
  const { tabId } = msg;

  try {
    await chrome.tabs.update(tabId, { active: true });
    send({
      type: 'switch_tab_result',
      id: msg.id,
      success: true
    });
  } catch (error) {
    send({
      type: 'switch_tab_result',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Close a tab
async function handleCloseTab(msg) {
  const { tabId } = msg;

  try {
    await chrome.tabs.remove(tabId);
    send({
      type: 'close_tab_result',
      id: msg.id,
      success: true
    });
  } catch (error) {
    send({
      type: 'close_tab_result',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Create new tab
async function handleNewTab(msg) {
  const { url, active } = msg;

  try {
    const tab = await chrome.tabs.create({ url: url || 'about:blank', active: active !== false });
    send({
      type: 'new_tab_result',
      id: msg.id,
      success: true,
      tab: {
        id: tab.id,
        url: tab.url,
        title: tab.title,
        active: tab.active
      }
    });
  } catch (error) {
    send({
      type: 'new_tab_result',
      id: msg.id,
      success: false,
      error: error.message
    });
  }
}

// Update extension toolbar badge based on connection state
function statusUpdate(text, color) {
  // Map color names to badge background colors
  const colorMap = {
    'green': '#4CAF50',
    'red': '#F44336',
    'orange': '#FF9800',
    'yellow': '#FFEB3B',
    'blue': '#2196F3',
    'gray': '#9E9E9E'
  };

  const bgColor = colorMap[color] || colorMap['gray'];

  // Set badge text (first char of status or a symbol)
  const badgeText = text === 'Connected' ? '●' : text === 'Disconnected' ? '○' : '...';

  setTimeout(() => {
    try {
      chrome.action.setBadgeText({ text: badgeText });
      chrome.action.setBadgeBackgroundColor({ color: bgColor });
    } catch (e) {
      console.error('[Chrome Use] setBadge failed:', e.message || e);
    }
  }, 100);

  // Notify popup if open
  chrome.runtime.sendMessage({ type: 'status', text, color }).catch(() => {});
}

// Send tabs list to server
async function sendTabsList() {
  try {
    const tabs = await chrome.tabs.query({});
    const tabInfo = tabs.map(tab => ({
      id: tab.id,
      title: tab.title,
      url: tab.url,
      active: tab.active
    }));
    send({
      type: 'tabs_list',
      tabs: tabInfo
    });
    console.log('[Chrome Use] Sent tabs list:', tabInfo.length, 'tabs');
  } catch (error) {
    console.error('[Chrome Use] Failed to get tabs:', error);
  }
}

// Initialize connection when extension loads
chrome.runtime.onInstalled.addListener(() => {
  console.log('[Chrome Use] Extension installed');
  connect('localhost', DEFAULT_PORT);
});

// Also connect when extension starts
chrome.runtime.onStartup.addListener(() => {
  console.log('[Chrome Use] Chrome startup, connecting...');
  connect('localhost', DEFAULT_PORT);
});

// Auto-connect when script is loaded
console.log('[Chrome Use] Extension loading, connecting...');
connect('localhost', DEFAULT_PORT);

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'connect') {
    connect(message.host, message.port);
    sendResponse({ status: 'connecting' });
  } else if (message.type === 'disconnect') {
    if (ws) {
      ws.close();
    }
    sendResponse({ status: 'disconnected' });
  } else if (message.type === 'get_status') {
    sendResponse({
      connected: ws && ws.readyState === WebSocket.OPEN,
      host: serverHost,
      port: serverPort
    });
  }
  return true;
});

// Handle debugger detachment on tab close
chrome.tabs.onRemoved.addListener((tabId) => {
  if (debuggerSessions.has(tabId)) {
    debuggerSessions.delete(tabId);
  }
});
