---
name: agent-memory
description: 生产级 Agent 记忆系统 — 6维坐标编码 + 语义检索 + 智能压缩
user-invocable: true
---

# Agent Memory Skill

为 OpenClaw Agent 提供结构化记忆能力。替代 MEMORY.md 的扁平文件方案，提供语义搜索、自动分类、记忆衰减、因果链等高级功能。

## 快速使用

```bash
# 写入记忆
python3 ~/.openclaw/workspace/agent-memory/cli.py remember "我决定用 Chroma 做向量库"

# 检索记忆
python3 ~/.openclaw/workspace/agent-memory/cli.py recall "用户选了什么向量库"

# 组装上下文（直接拼入 system prompt）
python3 ~/.openclaw/workspace/agent-memory/cli.py context "当前对话主题"

# 查看统计
python3 ~/.openclaw/workspace/agent-memory/cli.py stats

# 执行维护（衰减分析 + 去重 + 自修复）
python3 ~/.openclaw/workspace/agent-memory/cli.py maintain

# 压缩老记忆
python3 ~/.openclaw/workspace/agent-memory/cli.py compress

# 生成图谱
python3 ~/.openclaw/workspace/agent-memory/cli.py graph --format ascii
```

## 集成方式

### 对话中自动使用

当用户谈论技术决策、踩坑、偏好时，自动写入记忆：

```bash
python3 ~/.openclaw/workspace/agent-memory/cli.py remember "内容" --importance high
```

### 对话前检索上下文

在回复用户之前，检索相关记忆：

```bash
python3 ~/.openclaw/workspace/agent-memory/cli.py context "用户的问题"
```

### Cron 定期维护

设置 cron job 每天执行维护：
- 衰减分析
- 批量去重
- 自我修复（矛盾/过时检测）

## 数据存储

- SQLite 数据库: `~/.openclaw/workspace/agent-memory/memory.db`
- 向量缓存: `~/.openclaw/workspace/agent-memory/chroma_db/`
- 质量统计: `~/.openclaw/workspace/agent-memory/quality_stats.json`
- 每日索引: `~/.openclaw/workspace/agent-memory/daily_index/`

## 依赖

Python 3.10+（已安装）。可选：chromadb + sentence-transformers（语义搜索）。
