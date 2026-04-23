# Desktop Notifier Skill

Sends local desktop notifications through the bundled JavaScript wrapper inside this skill. It is optimized and verified for Windows, but the underlying implementation uses `node-notifier`, so other desktop platforms may also work depending on local support.

## Setup

No manual setup is required in the normal case. On first use, the script will automatically run `npm install` in the skill directory if `node-notifier` is missing.

If auto-install fails, run this manually:

```powershell
cd "$env:USERPROFILE\.openclaw\workspace\skills\desktop-notifier"
npm install
```

## Backing script

- `%USERPROFILE%\\.openclaw\\workspace\\skills\\desktop-notifier\\scripts\\send-notification.js`

## Example

```powershell
node "$env:USERPROFILE\.openclaw\workspace\skills\desktop-notifier\scripts\send-notification.js" --title "OpenClaw Test" --message "This is a desktop notification test." --timeout 10
```
