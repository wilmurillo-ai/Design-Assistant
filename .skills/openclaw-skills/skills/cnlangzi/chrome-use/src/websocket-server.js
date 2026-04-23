/**
 * WebSocket Server - receives connections from Chrome extension
 */

import { WebSocketServer, WebSocket } from 'ws';

export class ChromeWebSocketServer {
  constructor(port = 9224) {
    this.port = port;
    this.wss = null;
    this.clients = new Map(); // Map<ws, {windowId, connectionTime}>
    this.handlers = new Map();
    this.requestId = 0;
    this.pendingRequests = new Map();
  }

  /**
   * Get the most recent client (last to connect)
   */
  getExtension() {
    if (this.clients.size === 0) return null;
    let mostRecent = null;
    let latestTime = 0;
    for (const [ws, info] of this.clients) {
      if (info.connectionTime > latestTime) {
        latestTime = info.connectionTime;
        mostRecent = ws;
      }
    }
    return mostRecent;
  }

  /**
   * Start the WebSocket server
   */
  start() {
    return new Promise((resolve, reject) => {
      this.wss = new WebSocketServer({ port: this.port });

      this.wss.on('listening', () => {
        console.log(`WebSocket server started on port ${this.port}`);
        resolve();
      });

      this.wss.on('connection', (ws) => {
        console.log('Client connected');
        this.clients.set(ws, { windowId: null, connectionTime: Date.now() });

        ws.on('message', (data) => {
          try {
            const msg = JSON.parse(data.toString());
            this.handleMessage(ws, msg);
          } catch (e) {
            console.error('Failed to parse message:', e);
          }
        });

        ws.on('close', () => {
          console.log('Client disconnected');
          this.clients.delete(ws);
        });

        ws.on('error', (error) => {
          console.error('WebSocket error:', error);
        });
      });

      this.wss.on('error', (error) => {
        console.error('WebSocket server error:', error);
        reject(error);
      });
    });
  }

  /**
   * Stop the WebSocket server
   */
  stop() {
    return new Promise((resolve) => {
      if (this.wss) {
        this.wss.close(() => {
          console.log('WebSocket server stopped');
          resolve();
        });
      } else {
        resolve();
      }
    });
  }

  /**
   * Check if extension is connected
   */
  isConnected() {
    const ext = this.getExtension();
    return ext !== null && ext.readyState === WebSocket.OPEN;
  }

  /**
   * Handle incoming message from extension
   */
  handleMessage(ws, msg) {
    console.log('Received:', msg.type, msg);

    // Handle registration
    if (msg.type === 'register' && msg.role === 'extension') {
      console.log('Extension registered');
      const info = this.clients.get(ws);
      if (info) {
        info.windowId = msg.windowId || null;
        info.connectionTime = Date.now(); // Update connection time on re-registration
      }
      return;
    }

    // Handle tabs_list (extension sends this after registration)
    if (msg.type === 'tabs_list' && msg.success) {
      if (this.onTabsList) {
        this.onTabsList(msg.tabs);
      }
      // Resolve any pending get_tabs request
      this.resolveRequest(msg.id, msg);
      return;
    }

    // Handle results from extension
    if (msg.id && this.pendingRequests.has(msg.id)) {
      this.resolveRequest(msg.id, msg);
      return;
    }

    // Call custom handler if registered
    const handler = this.handlers.get(msg.type);
    if (handler) {
      handler(msg);
    }
  }

  /**
   * Register a handler for a message type
   */
  on(type, handler) {
    this.handlers.set(type, handler);
  }

  /**
   * Send request to extension and wait for response
   */
  sendRequest(message, timeout = 30000) {
    return new Promise((resolve, reject) => {
      const ext = this.getExtension();
      if (!ext || ext.readyState !== WebSocket.OPEN) {
        reject(new Error('Extension not connected'));
        return;
      }

      const id = ++this.requestId;
      message.id = id;

      const timeoutId = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error('Request timeout'));
      }, timeout);

      this.pendingRequests.set(id, (msg) => {
        clearTimeout(timeoutId);
        this.pendingRequests.delete(id);
        if (msg.success === false) {
          reject(new Error(msg.error || 'Request failed'));
        } else {
          resolve(msg);
        }
      });

      ext.send(JSON.stringify(message));
    });
  }

  /**
   * Resolve a pending request
   */
  resolveRequest(id, msg) {
    const resolver = this.pendingRequests.get(id);
    if (resolver) {
      resolver(msg);
    }
  }

  /**
   * Get tabs
   */
  async getTabs() {
    return this.sendRequest({ type: 'get_tabs' });
  }

  /**
   * Navigate to URL
   */
  async navigate(tabId, url) {
    return this.sendRequest({ type: 'navigate', tabId, url });
  }

  /**
   * Evaluate JavaScript
   */
  async evaluate(tabId, expression) {
    return this.sendRequest({ type: 'evaluate', tabId, expression });
  }

  /**
   * Click element
   */
  async click(tabId, selector) {
    return this.sendRequest({ type: 'click', tabId, selector });
  }

  /**
   * Fill input
   */
  async fill(tabId, selector, value) {
    return this.sendRequest({ type: 'fill', tabId, selector, value });
  }

  /**
   * Get content
   */
  async getContent(tabId) {
    return this.sendRequest({ type: 'get_content', tabId });
  }

  /**
   * Take screenshot
   */
  async screenshot(tabId, fullPage = false) {
    return this.sendRequest({ type: 'screenshot', tabId, fullPage });
  }

  /**
   * Switch tab
   */
  async switchTab(tabId) {
    return this.sendRequest({ type: 'switch_tab', tabId });
  }

  /**
   * Close tab
   */
  async closeTab(tabId) {
    return this.sendRequest({ type: 'close_tab', tabId });
  }

  /**
   * New tab
   */
  async newTab(url = 'about:blank') {
    return this.sendRequest({ type: 'new_tab', url });
  }
}
