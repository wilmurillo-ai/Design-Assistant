# SlonAide 录音笔记

OpenClaw 技能 — 查询和管理 SlonAide 录音笔记，获取转写文本和 AI 总结。

## 安装

```bash
openclaw skills install slonaide
```

或通过 ClawHub CLI：

```bash
npx clawhub@latest install slonaide
```

## 配置

1. 获取 API Key：访问 [SlonAide](https://h5.aidenote.cn/) → 登录 → 我的 → API Key → 生成访问密钥

2. 在 `~/.openclaw/openclaw.json` 中添加配置：

```json
{
  "skills": {
    "entries": {
      "slonaide": {
        "enabled": true,
        "env": {
          "SLONAIDE_API_KEY": "sk-你的API密钥"
        }
      }
    }
  }
}
```

## 功能

- 查询录音笔记列表（支持分页和关键词搜索）
- 获取录音转写文本（分段、带说话人标注）
- 查看 AI 自动总结
- 查看转写和总结状态

## 使用示例

在 OpenClaw 对话中直接说：

- "查看我的录音笔记"
- "搜索包含'会议'的录音"
- "获取最新一条录音的转写文本"
- "帮我看看录音笔记的 AI 总结"

## 许可证

MIT-0
