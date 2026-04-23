---
name: ai-twitter-briefing
description: ZeeLin AI Twitter博主信息简报生成与自动发推。从指定AI博主账号抓取近10天推文 → 整理成中文高信号简报 → 提炼英文推文 → 发布到用户X账号。触发关键词：AI博主简报、爬取推文、信息简报发推、x-creator-briefing、AI简报、博主推文汇总、抓近10天推文、整理简报发推。
---

# AI Twitter博主信息简报

## 工作流（4步）

1. **抓推文** — 用 agent-browser 打开每位博主主页，抓近10天内容（最多20条/人）
2. **整理简报** — 提炼高信号内容，按主题聚合，写中文简报，保存到 `reports/x-creator-briefing-YYYY-MM-DD.md`
3. **提炼英文推文** — 从简报中提炼1条精炼英文推文（≤240字），高价值内容摘要
4. **发推** — 用 ZeeLin Twitter/X AutoPost skill 发布英文推文

## 默认博主列表

见 `references/bloggers.md`，包含18位AI/AIGC/工具博主。可按用户指令临时增减。

## 简报格式

```markdown
# AI 博主动态简报 YYYY-MM-DD

## 🔥 高信号主线
- 主题1：[摘要]（来源 @handle）
- 主题2：[摘要]

## 📌 各账号亮点
### @handle
- 要点1
- 要点2

## ⚠️ 未检索到近期内容
- @handle（原因）
```

## 英文推文格式

```
🧵 AI Signal Briefing [date]

Key themes from top AI creators:
• [insight 1] (@handle)
• [insight 2] (@handle)
• [insight 3]

#AI #AITools #BuildInPublic
```

## 注意事项

- 打开 X 需要用户已在浏览器登录
- 若某账号内容抓取失败，在简报末尾标注，不中断整体流程
- 发推前展示英文推文内容给用户确认（除非用户明确说自动发）
- 如需读取 agent-browser skill，路径：`~/.openclaw/workspace/skills/agent-browser-clawdbot/SKILL.md`
- 如需读取 Twitter autopost skill，路径：`~/.openclaw/workspace/skills/zeelin-twitter-web-autopost/SKILL.md`
