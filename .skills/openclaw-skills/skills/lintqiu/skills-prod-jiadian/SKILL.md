---
name: skills-prod-jiadian
description: 收费技能示例 - 授权验证 + 手机号绑定 skills-prod-jiadian
license: MIT-0
---

# skills-prod-jiadian

收费技能示例，演示如何在 ClawHub 发布带授权验证和手机号绑定的付费技能。

## Installation

**Via ClawHub (recommended):**

```bash
clawhub install skills-prod-jiadian
```

**Manual:**

通用环境（技能目录 `~/.openclaw/skills/`）：

```bash
git clone https://github.com/lintqiu/skills-prod-jiadian.git ~/.openclaw/skills/skills-prod-jiadian
```

火山 ArClaw（技能目录 `/root/.openclaw/workspace/skills/`）：

```bash
git clone https://github.com/lintqiu/skills-prod-jiadian.git /root/.openclaw/workspace/skills/skills-prod-jiadian
```

## 授权说明

- **演示模式**：不配置 `SKILL_LICENSE_VERIFY_URL` 时，仅接受本地校验，演示授权码为 `demo-license-123`。
- **生产模式**：设置 `SKILL_LICENSE_VERIFY_URL` 为你的校验接口后，授权码将通过该 URL 进行服务端验证（POST `{"key":"授权码"}`，返回 `{"valid":true/false,"message":"..."}`）。

## 隐私说明

**本技能是付费技能演示，需要绑定手机号才能使用。**

本技能会：
1. **收集手机号** - 需要用户输入手机号进行绑定
2. **发送到后端** - 手机号会通过 HTTPS POST 发送到第三方服务器 `https://yunji.focus-jd.cn/api/skill/lin/test` 进行注册验证
3. **本地存储** - 绑定成功后，手机号会**使用授权码作为密钥加密存储**在技能目录下的 `.phone.json` 文件中，方便下次直接使用

**⚠️ 重要提示：使用本技能即表示你同意将手机号发送到上述第三方域名。请确保你信任该域名和技能作者后再使用。**

## 配置

### 必需环境变量

```bash
export SKILL_LICENSE_KEY=你的授权码
```

演示可用：`SKILL_LICENSE_KEY=demo-license-123`。购买授权码请访问：https://your-website.com/buy

### 可选环境变量

| 变量 | 说明 |
|------|------|
| `SKILL_LICENSE_VERIFY_URL` | 生产环境授权校验接口 URL，设置后使用服务端验证 |
| `SKILL_BUY_URL` | 购买授权码页面链接，授权失败时提示用 |

## When to use

- 用户触发付费技能
- 需要授权验证 + 手机号绑定
- 授权通过后保存手机号，下次直接使用

## Instructions

1. 用户触发技能
2. 打印欢迎信息
3. 检查 `SKILL_LICENSE_KEY` 授权 → 授权失败提示购买并退出
4. 授权通过后，检查本地是否已有手机号 → 有直接使用，没有提示输入
5. 发送手机号到后端 → 成功保存，失败提示

## Parameters

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 否 | 测试消息 |