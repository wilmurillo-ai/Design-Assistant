# session-memory-sync 🔄

跨 Session 记忆查找与同步机制（v0.2 - 潜意识触发器）

## 功能

当你需要查找其他 session 中的记忆、决策或待办事项时，这个技能帮你高效检索和同步。

**✨ 新功能：潜意识触发器**
- 无需用户说"检查其他 session"
- 自动检测暗示、假设、模糊指代
- 静默检索，自然融入回答

## 使用场景

### 显式触发
- "检查一下微信 session 里有没有我说的提醒事项"
- "昨天的飞书对话里提到了什么重要决定？"
- "同步一下所有 session 的记忆，看看有没有遗漏"

### 潜意识触发（自动）
- "我昨天说的那个报告..." → 自动检索
- "你知道蒙老师的报告时间吧？" → 自动检索
- "那个会议改到什么时候了？" → 自动检索
- "微信里蒙老师发的消息" → 自动检索

## 安装

```bash
# 如果已经通过 npm 安装 OpenClaw，技能会自动可用
# 或者从 clawhub 安装
openclaw skill install session-memory-sync
```

## 工作原理

1. **快速扫描** - 列出活跃 session，查看最近消息
2. **记忆文件优先** - 先查 `memory/YYYY-MM-DD.md` 和 `MEMORY.md`
3. **深度检索** - 必要时读取特定 session 的完整历史
4. **智能同步** - 将发现的重要信息写入共享 memory 文件

## 示例

**用户：** "检查一下有没有漏掉蒙老师的报告提醒"

**技能执行：**
```
1. 搜索 memory 文件：grep -r "蒙老师" memory/
2. 列出活跃 session：sessions_list(activeMinutes=1440)
3. 读取相关 session 历史
4. 发现：✅ 已设置 cron 提醒 (08:30)
5. 同步：写入 memory/2026-03-27.md
```

## 技术细节

- 使用 `sessions_list` 获取 session 元数据
- 使用 `sessions_history` 读取完整对话
- 使用 `grep/find` 搜索 memory 文件
- 使用 `write/edit` 同步发现的信息

## 许可证

MIT - 自由使用、修改、分发

---

Created by 郭泉 (Dr. Guo) 🎯
Available on [ClawHub](https://clawhub.ai)
