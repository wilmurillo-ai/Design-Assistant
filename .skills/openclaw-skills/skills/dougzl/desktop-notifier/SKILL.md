---
name: desktop-notifier
description: Send local desktop notifications from Node.js on the current machine. Use when the user wants a native popup, local reminder, or notification test instead of a chat reply. Optimized and verified for Windows; other platforms may work depending on node-notifier support.
---

# Desktop Notifier

Send local desktop notifications from Node.js on the current machine. This skill is optimized and verified for Windows, but the underlying notifier is based on `node-notifier`, so other desktop platforms may work depending on local support.

## What this skill does

This skill sends a **local desktop notification** by calling the bundled script:

- Script: `%USERPROFILE%\\.openclaw\\workspace\\skills\\desktop-notifier\\scripts\\send-notification.js`
- Runtime: Node.js
- Library: `node-notifier`
- Dependency manifest: `%USERPROFILE%\\.openclaw\\workspace\\skills\\desktop-notifier\\package.json`

## Before sending

1. Confirm the request is for a **local desktop notification**.
2. If the user gave text, use it directly.
3. If they did not give a title, pick a short practical title.
4. Keep the message concise.
5. On first run, the script will automatically execute `npm install` in the skill directory if `node-notifier` is missing.
6. For reminder, timer, schedule, alert, and follow-up tasks, prefer local desktop notification by default unless the user explicitly wants chat-only delivery.
7. If OpenClaw is likely running in the background or the chat surface may not be visible, prefer a local desktop notification so the user gets a visible popup on Windows.

## Command template

Run this from PowerShell with `exec`:

```powershell
node "$env:USERPROFILE\.openclaw\workspace\skills\desktop-notifier\scripts\send-notification.js" --title "<TITLE>" --message "<MESSAGE>" --timeout 10
```

Optional flags supported by the script:

- `--wait true|false`
- `--timeout <seconds>`

## Expected output

On a normal installed run, success usually prints:

```text
NOTIFY_SENT
```

On a first run without dependencies, it may first print:

```text
DEPENDENCY_MISSING: node-notifier
AUTO_INSTALL_START
AUTO_INSTALL_DONE
NOTIFY_SENT
```

It may also print fields like:

- `RESPONSE:timeout`
- `METADATA:{...}`

That does **not** necessarily mean failure. It often just means the notification timed out naturally.

## Troubleshooting

If the user does not see a popup:

1. Check whether it appeared in the system notification center.
2. If yes, the notifier likely worked and the desktop banner was suppressed.
3. On Windows, likely causes include:
   - Focus Assist / Do Not Disturb
   - app notification permissions
   - Windows banner style settings
4. If auto-install fails, run `npm install` manually in `%USERPROFILE%\\.openclaw\\workspace\\skills\\desktop-notifier`.

## Examples

### Send a quick test

```powershell
node "$env:USERPROFILE\.openclaw\workspace\skills\desktop-notifier\scripts\send-notification.js" --title "OpenClaw Test" --message "This is a desktop notification test." --timeout 10
```

### Study reminder

```powershell
node "$env:USERPROFILE\.openclaw\workspace\skills\desktop-notifier\scripts\send-notification.js" --title "学习提醒" --message "现在开始今天的学习时段。" --timeout 10
```
