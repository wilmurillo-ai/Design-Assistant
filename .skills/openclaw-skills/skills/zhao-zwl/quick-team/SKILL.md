# Agent 创建技能（通用版）

**用途：** 快速创建新的团队成员（子代理）。

**触发：** 用户说"创建新成员"、"添加agent"、"新建角色"、"组建团队"等。

---

## 核心原则

**主控不做执行。** 创建新agent是执行工作，应派给子代理完成。主控只负责确认名称和职责，然后派任务。

---

## 创建流程（5步）

### 第1步：确认名称和职责

确认两件事：
- **英文名称**（小写字母+数字，不能用"main"）
- **一句话职责**

### 第2步：创建workspace和SOUL.md

派子代理执行两件事：

**创建目录结构：**
```bash
mkdir -p ~/.qclaw/workspace-{mainID}/{名称}
mkdir -p ~/.qclaw/agents/{名称}/agent
```

**创建SOUL.md：**
```markdown
---
name: {名称}
description: "{一句话职责}"
---

# SOUL.md

## 我是谁

{角色定位}

## 我的职责

1. {职责1}
2. {职责2}

## 禁止事项

- {禁止1}
- {禁止2}
```

### 第3步：更新openclaw配置

派子代理在 `openclaw.json` 的 `agents.list` 中追加：

```json
{
  "id": "{名称}",
  "name": "{显示名}",
  "workspace": "~/.qclaw/workspace-{mainID}/{名称}",
  "agentDir": "~/.qclaw/agents/{名称}/agent"
}
```

同时确保 `agents.defaults.subagents.allowAgents` 包含 `["*"]`。

### 第4步：重启Gateway

```bash
openclaw gateway restart
```

**必须重启，配置才生效。**

### 第5步：验证激活

派第一个任务测试正常工作：

```
sessions_spawn({
  agentId: "{名称}",
  mode: "run",
  task: "读SOUL.md，回复你的名称和职责。"
})
```

---

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| 创建后无响应 | workspace目录不存在 | 确认第2步目录已创建 |
| sessions_spawn失败 | allowAgents未配置 | 检查openclaw.json |
| cron不执行 | gateway未重启 | 执行 `openclaw gateway restart` |

---

## 验证清单

- [ ] workspace目录已创建
- [ ] SOUL.md已写入
- [ ] openclaw.json已更新
- [ ] Gateway已重启
- [ ] sessions_spawn测试成功
