---
name: chrome-use
description: "Use chrome-use when standard web access (fetch/web search) fails due to Cloudflare challenges, CAPTCHAs, JavaScript-rendered content, or bot detection — or when you need to interact with a site (click, fill, scroll, login). Controls a real Chrome browser via the Chrome debugger API to bypass anti-bot."
version: 0.2.0
license: MIT
compatibility: Requires Node.js >=18, Chrome browser installed, and Chrome extension installed
metadata:
  author: cnlangzi
  repository: https://github.com/cnlangzi/chrome-use
  node_version: ">=18"
  openclaw:
    requires:
      bins: ["node"]
      env: []
      config: []
---

# Chrome Use OpenClaw Skill

Control your local Chrome browser via `chrome.debugger` API using a Chrome extension. Provides Playwright-like functionality with full browser control using your existing Chrome profile, with improved stealth against bot detection.

## How to Use (Read First)

### ⚠️ Non-Headless Mode Required
**Do NOT use headless Chrome.** Cloudflare and anti-bot systems detect and block headless browsers. Always launch Chrome with the built-in `launchChrome()` method. If running in a headless environment (no display), Chrome must still be launched in non-headless mode — the extension and debugger API require it.

### ⚠️ Initialization Sequence
**The extension requires 15 seconds to initialize after Chrome starts.** Calling `connect()` too early will fail.

```javascript
// Import from ./index.js (relative path, NOT 'chrome-use')
import { connect, navigate, evaluate, click, fill, screenshot, disconnect } from './index.js';
import { launchChrome } from './index.js';

// Step 1: Launch Chrome with extension
await launchChrome();

// Step 2: Wait 15 seconds for extension service worker to initialize
await new Promise(r => setTimeout(r, 15000));

// Step 3: Connect to Chrome
await connect();

// Step 4: Use
await navigate('https://example.com');

// ... do things ...

// Disconnect when done
disconnect();
```

**When implementing**: always use the built-in `launchChrome()` function — never spawn Chrome yourself or use other launch methods.

### Rules
- Always import from `./index.js` (relative path), NOT from `'chrome-use'`
- Do NOT run `google-chrome` or `chromium` commands directly
- Do NOT use CDP protocol or `chrome.debugger` directly
- Always wait 15 seconds after `launchChrome()` before calling `connect()`
- Chrome can be running already — `launchChrome()` will open a new window if Chrome is already running
- If port 9224 is in use: run `fuser -k 9224/tcp` first

## Features

- **Stealth First**: Uses `chrome.debugger` API via extension to evade anti-bot detection (Cloudflare, reCAPTCHA, fingerprinting)
- **Auto WebSocket Server**: Automatically starts and manages WebSocket server for extension communication
- **Real Browser Rendering**: Access JavaScript-rendered content and SPAs that standard search cannot
- **Direct Search Engine Access**: Query Google, Bing, etc. as a real user - returns unfiltered, real-time results
- **Full Browser Control** - Navigate, click, fill, hover, scroll, screenshot, execute JavaScript
- **Tab Management** - List, create, close, and switch tabs
- **Cross-Platform** - Supports macOS, Windows, and Linux

## Installation (One-time)

**Chrome extension must be installed manually (one-time):**
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `extension/` folder in the skill directory

After this, the extension loads automatically every time Chrome starts — no need to reload it each session.

**Install npm dependencies:**
```bash
cd ~/workspace/skills/chrome-use && npm install
```

## Functions

### Connection Management

#### connect()
Connect to Chrome via extension WebSocket server. Starts the WebSocket server and waits for the extension to connect. Does NOT launch Chrome - you must call `launchChrome()` first.

```javascript
await launchChrome();
await new Promise(r => setTimeout(r, 15000));
await connect();
// Returns: { status: "connected", mode: "debugger", port: 9224, extension_installed: true, tab_id: 12345 }
```

#### disconnect()
Disconnect from Chrome browser. Does NOT close Chrome - leaves it running.

#### isConnected()
Check if currently connected to Chrome extension. Returns: boolean

#### launchChrome()
Launch Chrome with the extension loaded. After calling this, **you MUST wait 15 seconds** before calling `connect()`.

```javascript
{ status: "launched", pid: 12345 }
```

### Page Operations

#### navigate(url)
Navigate to a URL.

#### evaluate(script)
Execute JavaScript synchronously.

```javascript
const title = await evaluate("document.title");
```

#### getHtml()
Get the page HTML. Returns: string

#### screenshot(fullPage?)
Take a screenshot. `fullPage` (boolean, optional): Capture full page or just viewport (default: false). Returns: string (Base64 PNG)

### Element Interaction

#### click(selector)
Click an element using CSS selector.

#### fill(selector, value)
Input text into an element.

### Tab Management

#### listTabs()
List all open tabs.

```javascript
[
  { id: 708554825, title: "Google", url: "https://google.com", active: true },
  { id: 708554826, title: "Example", url: "https://example.com", active: false }
]
```

#### switchTab(tabId)
Switch to a different tab.

#### closeTab(tabId)
Close a tab.

#### newTab(url?)
Create a new tab.

## Common Mistakes

| Don't Do This | Why |
|---------------|-----|
| `import ... from 'chrome-use'` | Not a npm package. Use `from './index.js'` |
| `google-chrome --load-extension=...` | Use `launchChrome()` instead |
| `npm install chrome-use` | Not published to npm |
| Calling `connect()` immediately after `launchChrome()` | Always wait 15 seconds first |
| Port 9224 in use | Run `fuser -k 9224/tcp` first |

## Troubleshooting

### connect() fails
1. Did you wait 15 seconds after `launchChrome()`?
2. Is port 9224 free? (`fuser -k 9224/tcp`)
3. Is the extension installed in Chrome?

### Port 9224 already in use
```bash
fuser -k 9224/tcp
```

## Notes

- Node.js starts a WebSocket server (port 9224) via `connect()`; the Chrome extension connects to Node.js as a WebSocket client, then uses `chrome.debugger` API to control Chrome
- `disconnect()` does NOT close Chrome by default
- All selectors use CSS selector syntax
