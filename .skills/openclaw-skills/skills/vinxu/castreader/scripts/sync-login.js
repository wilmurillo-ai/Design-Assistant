#!/usr/bin/env node

/**
 * sync-login.js — Step-by-step login via screenshots for Telegram-based interaction
 *
 * Usage:
 *   node scripts/sync-login.js kindle start       → Launch Chrome, navigate to login, screenshot
 *   node scripts/sync-login.js kindle input "text" → Type text into active input, submit, screenshot
 *   node scripts/sync-login.js kindle status       → Check if logged in, screenshot current state
 *   node scripts/sync-login.js kindle stop         → Close Chrome
 *
 * Chrome stays running between calls via --remote-debugging-port.
 * Output: JSON with { event, screenshot?, message?, loggedIn? }
 */

const path = require('path');
const fs = require('fs');
const { execSync, spawn } = require('child_process');
const os = require('os');

const BUNDLED_EXT_PATH = path.resolve(__dirname, '../chrome-extension');
const DEV_EXT_PATH = path.resolve(os.homedir(), 'Documents/MyProject/readout-desktop/.output/chrome-mv3');
const CHROME_PROFILE = process.env.CHROME_PROFILE || path.resolve(__dirname, '../.chrome-profile');
const CDP_PORT = 9224;
const CDP_URL = `http://127.0.0.1:${CDP_PORT}`;
const SCREENSHOT_DIR = '/tmp/castreader-login';

const TARGETS = {
  kindle: {
    loginUrl: 'https://read.amazon.com/kindle-library',
    readyPattern: /read\.amazon\.com\/kindle-library/,
    name: 'Amazon Kindle',
  },
  weread: {
    loginUrl: 'https://weread.qq.com/web/shelf',
    readyPattern: /weread\.qq\.com\/web\/shelf/,
    name: 'WeRead',
  },
};

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function output(data) {
  console.log(JSON.stringify(data));
}

function getExtPath() {
  if (process.env.CASTREADER_EXT_PATH) return process.env.CASTREADER_EXT_PATH;
  if (fs.existsSync(path.join(DEV_EXT_PATH, 'manifest.json'))) return DEV_EXT_PATH;
  if (fs.existsSync(path.join(BUNDLED_EXT_PATH, 'manifest.json'))) return BUNDLED_EXT_PATH;
  return null;
}

// Lazy-loaded puppeteer
let puppeteer;
function loadPuppeteer() {
  if (!puppeteer) {
    const skillDir = path.resolve(__dirname, '..');
    const pp = path.join(skillDir, 'node_modules', 'puppeteer');
    if (!fs.existsSync(pp)) {
      execSync('npm install --silent 2>/dev/null', { cwd: skillDir, stdio: 'inherit' });
    }
    puppeteer = require('puppeteer');
  }
}

async function takeScreenshot(page, label) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  const filename = `${label}-${Date.now()}.png`;
  const filepath = path.join(SCREENSHOT_DIR, filename);

  // For WeRead QR code, try to screenshot just the QR element for easier scanning
  if (label === 'wechat_qr') {
    try {
      const qrEl = await page.$('.login-modal, .wr_login_modal, [class*="login"] img, canvas');
      if (qrEl) {
        await qrEl.screenshot({ path: filepath });
        return filepath;
      }
    } catch {}
  }

  await page.screenshot({ path: filepath, fullPage: false });
  return filepath;
}

async function isLoggedIn(url, source, page) {
  if (!TARGETS[source].readyPattern.test(url)) return false;
  // WeRead loads /web/shelf even when not logged in (empty shelf + "登录" button)
  // Must check page content to confirm actual login
  if (source === 'weread' && page) {
    const notLoggedIn = await page.evaluate(() => {
      const body = document.body?.innerText || '';
      // "登录" button visible in nav = not logged in
      // Also check if shelf is empty and has login prompt
      const nav = document.querySelector('.navBar_link_Login, .wr_avatar, .readerTopBar_avatar');
      if (nav && nav.textContent?.includes('登录')) return true;
      // Fallback: check body text
      if (body.includes('登录') && !body.includes('书架') && body.length < 500) return true;
      return false;
    });
    if (notLoggedIn) return false;
  }
  return true;
}

function detectPageState(url, bodyText) {
  // Detect what kind of page we're on and what input is needed
  if (url.includes('/ap/signin') || url.includes('/ap/register') || url.includes('amazon.com/gp/sign-in')) {
    if (bodyText.includes('Enter your email') || bodyText.includes('Email or mobile phone number') ||
        bodyText.includes('电子邮件') || bodyText.includes('手机号码')) {
      return { step: 'email', prompt: 'Please enter your Amazon email or phone number.' };
    }
    if (bodyText.includes('Enter your password') || bodyText.includes('Password') ||
        bodyText.includes('密码')) {
      return { step: 'password', prompt: 'Please enter your Amazon password.' };
    }
    if (bodyText.includes('verification code') || bodyText.includes('OTP') ||
        bodyText.includes('Two-Step Verification') || bodyText.includes('验证码') ||
        bodyText.includes('Approve the notification') || bodyText.includes('Enter the characters')) {
      return { step: '2fa', prompt: 'Please enter the verification code you received, or approve the notification on your phone.' };
    }
    if (bodyText.includes('CAPTCHA') || bodyText.includes('characters you see')) {
      return { step: 'captcha', prompt: 'Please enter the characters shown in the image.' };
    }
    return { step: 'unknown_login', prompt: 'Please enter the information shown on the login page.' };
  }
  if (url.includes('weread.qq.com') && (url.includes('login') || bodyText.includes('微信登录') || bodyText.includes('微信扫码'))) {
    return { step: 'wechat_qr', prompt: '请用微信扫描二维码登录微信读书。' };
  }
  // WeRead shelf page but not logged in (has "登录" button in nav)
  if (url.includes('weread.qq.com') && bodyText.includes('登录')) {
    return { step: 'weread_need_login', prompt: '需要登录微信读书。请稍候，正在跳转到登录页...' };
  }
  if (url.includes('/landing') || url.includes('/gp/browse.html')) {
    return { step: 'landing', prompt: 'Redirected to landing page. Retrying sign-in...' };
  }
  return { step: 'ready', prompt: null };
}

// ---- Commands ----

async function cmdStart(source) {
  loadPuppeteer();
  const target = TARGETS[source];
  const extPath = getExtPath();

  const args = [
    `--remote-debugging-port=${CDP_PORT}`,
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-popup-blocking',
    '--disable-blink-features=AutomationControlled',
  ];
  if (extPath) {
    args.push(`--disable-extensions-except=${extPath}`);
    args.push(`--load-extension=${extPath}`);
  }

  // Launch Chrome (stays running after script exits via detached)
  const browser = await puppeteer.launch({
    headless: false,
    protocolTimeout: 120_000,
    ignoreDefaultArgs: ['--disable-extensions'],
    args,
    userDataDir: CHROME_PROFILE,
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.goto(target.loginUrl, { waitUntil: 'networkidle2', timeout: 60000 });
  await sleep(2000);

  // Handle Kindle landing page redirect — auto-click "Sign in with your account"
  if (page.url().includes('/landing')) {
    const clicked = await page.evaluate(() => {
      const links = document.querySelectorAll('a, button, span');
      for (const el of links) {
        if (el.textContent?.includes('Sign in') || el.textContent?.includes('登录')) {
          el.click();
          return true;
        }
      }
      return false;
    });
    if (clicked) {
      await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 }).catch(() => {});
      await sleep(2000);
    }
  }

  const url = page.url();
  if (await isLoggedIn(url, source, page)) {
    const screenshot = await takeScreenshot(page, 'logged-in');
    output({
      event: 'already_logged_in',
      loggedIn: true,
      screenshot,
      message: `Already logged in to ${target.name}! You can start syncing.`,
    });
    await browser.disconnect();
    return;
  }

  const bodyText = await page.evaluate(() => document.body?.innerText?.substring(0, 2000) || '');
  let state = detectPageState(url, bodyText);

  // WeRead: auto-click "登录" to navigate to QR code page
  if (state.step === 'weread_need_login') {
    const clicked = await page.evaluate(() => {
      // Try clicking the login link/button in the nav bar
      const els = document.querySelectorAll('a, button, span, div');
      for (const el of els) {
        const text = el.textContent?.trim();
        if (text === '登录' || text === '登陆') {
          el.click();
          return true;
        }
      }
      return false;
    });
    if (clicked) {
      await sleep(3000);
      // Check if we're now on a QR code page
      const newBody = await page.evaluate(() => document.body?.innerText?.substring(0, 2000) || '');
      state = detectPageState(page.url(), newBody);
    }
  }

  const screenshot = await takeScreenshot(page, state.step);

  output({
    event: 'login_step',
    step: state.step,
    loggedIn: false,
    screenshot,
    message: state.prompt || `Please log in to ${target.name}.`,
  });

  await browser.disconnect();
}

async function cmdInput(source, inputText) {
  loadPuppeteer();
  const target = TARGETS[source];

  // Connect to running Chrome
  let browser;
  try {
    browser = await puppeteer.connect({ browserURL: CDP_URL });
  } catch {
    output({ event: 'error', message: 'Chrome is not running. Run "start" first.' });
    return;
  }

  const pages = await browser.pages();
  // Find the Amazon/WeRead page
  let page = pages.find((p) => {
    const url = p.url();
    return url.includes('amazon.com') || url.includes('weread.qq.com');
  });
  if (!page && pages.length > 0) page = pages[pages.length - 1];
  if (!page) {
    output({ event: 'error', message: 'No login page found.' });
    await browser.disconnect();
    return;
  }

  await page.bringToFront();

  // Find the visible input field and type into it using Puppeteer's native type()
  if (inputText) {
    const inputSelector = await page.evaluate(() => {
      const selectors = [
        'input[name="email"]', 'input[name="password"]', 'input[name="otpCode"]',
        'input[name="guess"]', 'input[name="claimspicker"]',
        'input[type="email"]', 'input[type="text"]', 'input[type="password"]', 'input[type="tel"]',
      ];
      for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.width > 0 && rect.height > 0 && !el.disabled) return sel;
        }
      }
      // Fallback: any visible text-like input
      const allInputs = document.querySelectorAll('input');
      for (const input of allInputs) {
        const type = input.type?.toLowerCase();
        if (['text', 'email', 'password', 'tel', 'number'].includes(type)) {
          const rect = input.getBoundingClientRect();
          if (rect.width > 0 && rect.height > 0 && !input.disabled) {
            // Return a unique selector
            if (input.id) return '#' + input.id;
            if (input.name) return 'input[name="' + input.name + '"]';
            return 'input[type="' + type + '"]';
          }
        }
      }
      return null;
    });

    if (inputSelector) {
      // Clear existing value and type new text (triggers proper keyboard events)
      await page.click(inputSelector, { clickCount: 3 }); // select all
      await page.type(inputSelector, inputText, { delay: 50 });
    }
  }

  await sleep(500);

  // Click the submit/continue button using Puppeteer's native click()
  const btnSelector = await page.evaluate(() => {
    const selectors = ['#continue', '#signInSubmit', 'input[type="submit"]', 'button[type="submit"]', '.a-button-input'];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) {
        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) return sel;
      }
    }
    return null;
  });

  if (btnSelector) {
    await page.click(btnSelector);
  }

  // Wait for page transition
  await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
  await sleep(2000);

  const url = page.url();
  if (await isLoggedIn(url, source, page)) {
    const screenshot = await takeScreenshot(page, 'logged-in');
    output({
      event: 'login_complete',
      loggedIn: true,
      screenshot,
      message: `Successfully logged in to ${target.name}! You can now sync your books.`,
    });
    await browser.disconnect();
    return;
  }

  // Still on login flow — detect next step
  const bodyText = await page.evaluate(() => document.body?.innerText?.substring(0, 2000) || '');
  const state = detectPageState(url, bodyText);
  const screenshot = await takeScreenshot(page, state.step);

  output({
    event: 'login_step',
    step: state.step,
    loggedIn: false,
    screenshot,
    message: state.prompt || 'Please enter the information shown on the screen.',
  });

  await browser.disconnect();
}

async function cmdStatus(source) {
  loadPuppeteer();
  const target = TARGETS[source];

  let browser;
  try {
    browser = await puppeteer.connect({ browserURL: CDP_URL });
  } catch {
    output({ event: 'not_running', loggedIn: false, message: 'Chrome is not running.' });
    return;
  }

  const pages = await browser.pages();
  const page = pages.find((p) => {
    const url = p.url();
    return url.includes('amazon.com') || url.includes('weread.qq.com');
  });

  if (!page) {
    output({ event: 'no_page', loggedIn: false, message: 'No login page found.' });
    await browser.disconnect();
    return;
  }

  const url = page.url();
  const loggedIn = await isLoggedIn(url, source, page);
  const screenshot = await takeScreenshot(page, loggedIn ? 'logged-in' : 'status');

  output({
    event: loggedIn ? 'already_logged_in' : 'not_logged_in',
    loggedIn,
    screenshot,
    message: loggedIn
      ? `Logged in to ${target.name}.`
      : `Not yet logged in to ${target.name}.`,
  });

  await browser.disconnect();
}

async function cmdStop() {
  loadPuppeteer();
  try {
    const browser = await puppeteer.connect({ browserURL: CDP_URL });
    await browser.close();
    output({ event: 'stopped', message: 'Chrome closed.' });
  } catch {
    output({ event: 'not_running', message: 'Chrome was not running.' });
  }
}

// ---- Main ----

async function main() {
  const [source, command, ...rest] = process.argv.slice(2);

  if (!source || !TARGETS[source]) {
    console.error('Usage: node scripts/sync-login.js <kindle|weread> <start|input|status|stop> [text]');
    process.exit(1);
  }

  switch (command) {
    case 'start':
      await cmdStart(source);
      break;
    case 'input':
      if (rest.length === 0) {
        console.error('Usage: node scripts/sync-login.js <source> input "text to type"');
        process.exit(1);
      }
      await cmdInput(source, rest.join(' '));
      break;
    case 'status':
      await cmdStatus(source);
      break;
    case 'stop':
      await cmdStop();
      break;
    default:
      console.error('Unknown command. Use: start, input, status, stop');
      process.exit(1);
  }
}

main().catch((err) => {
  output({ event: 'error', message: err.message });
  process.exit(1);
});
