# Chrome Debugger API vs CDP Commands

This document explains how the chrome.debugger API commands relate to Chrome DevTools Protocol (CDP) commands.

## Overview

The `chrome.debugger` API used by this extension provides access to CDP commands through a different interface. When you call `chrome.debugger.sendCommand()`, it wraps CDP commands.

## Command Mapping

The extension's `debuggerCommand()` function maps commands as follows:

### Page Commands

| Extension Call | CDP Equivalent |
|----------------|----------------|
| `Page.enable` | `{\"method\": \"Page.enable\"}` |
| `Page.navigate` | `{\"method\": \"Page.navigate\", \"params\": {\"url\": \"...\"}}` |
| `Page.captureScreenshot` | `{\"method\": \"Page.captureScreenshot\", \"params\": {\"format\": \"png\", ...}}` |

### Runtime Commands

| Extension Call | CDP Equivalent |
|----------------|----------------|
| `Runtime.evaluate` | `{\"method\": \"Runtime.evaluate\", \"params\": {\"expression\": \"...\", \"returnByValue\": true}}` |

### Input Commands

| Extension Call | CDP Equivalent |
|----------------|----------------|
| Via evaluate() | `{\"method\": \"Input.dispatchMouseEvent\", \"params\": {...}}` |

## How the Extension Works

The extension uses `chrome.debugger.attach()` to attach to a tab, then uses `chrome.debugger.sendCommand()` to send CDP commands. This is different from direct CDP connection because:

1. It requires explicit `chrome.debugger.attach({tabId})` before sending commands
2. It uses the extension's origin, making it harder to detect
3. Commands are sent via the extension's background script

## Sending Commands via Extension

```javascript
// Attach to tab first
chrome.debugger.attach({tabId: tabId}, "1.3", () => {
    // Send CDP command
    chrome.debugger.sendCommand({tabId}, "Runtime.evaluate", {
        expression: "document.title",
        returnByValue: true
    }, (result) => {
        console.log(result);
    });
});
```

## Common Operations

### Take Screenshot
```javascript
chrome.debugger.sendCommand({tabId}, "Page.captureScreenshot", {
    format: "png",
    quality: 100,
    fromSurface: true
});
```

### Evaluate JavaScript
```javascript
chrome.debugger.sendCommand({tabId}, "Runtime.evaluate", {
    expression: "document.documentElement.outerHTML",
    returnByValue: true
});
```

### Navigate
```javascript
chrome.debugger.sendCommand({tabId}, "Page.navigate", {
    url: "https://example.com"
});
```

## Debugger Session Management

The extension maintains debugger sessions per tab:

```javascript
let debuggerSessions = new Map(); // tabId -> debugger session info

async function attachToTab(tabId) {
    return new Promise((resolve, reject) => {
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
```

## Note

This extension uses `chrome.debugger` API, not direct CDP WebSocket connection. This provides better stealth against bot detection as it mimics the behavior of Chrome DevTools debugging rather than appearing as a direct CDP client.
