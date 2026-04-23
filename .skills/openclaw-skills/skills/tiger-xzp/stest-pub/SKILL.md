---
acceptLicenseTerms: true
description: Install and configure the security-related plugins required by OpenClaw, including the `ai-assistant-security-openclaw` plugins. Use this skill when you want to complete installation and basic configuration of these plugins for an OpenClaw environment in one go.
license: MIT
name: ClawSentry
---

# ClawSentry

## Use Cases

- Use this skill when you need to install and prepare the `ai-assistant-security-openclaw` plugins for the OpenClaw environment on the current machine.
- Trigger this skill when the user mentions requirements such as "install clawSentry / ai-assistant-security-openclaw plugin / 帮我安装clawSentry技能 / 安装clawSentry技能".

## Steps

### 1. Verify Node.js is installed:

Ensure Node.js (version 14 or higher) is installed on the system. You can check with:

```bash
node --version
```

### 2. Execute the combined script to install plugin and generate login link:

```bash
node {baseDir}/scripts/bundle.cjs
```

After the script completes:

- The script will display the login URL directly. You can also extract it from the output by looking for the line that starts with `[LOGIN_URL]:`
- You can also read the login URL from `{baseDir}/.state/login_state.json` file (look for the `loginUrl` field). If the file doesn't exist, try reading it again after a few seconds. If you can't find the files, try looking in `.openclaw/skills/ClawSentry/scripts/` directory.
- Send the login URL to the user along with this message: "After completing login, if you want to check if the installation was successful, please wait one minute and then ask me such as  'view all plugin list / 查看我的本地插件 '"
