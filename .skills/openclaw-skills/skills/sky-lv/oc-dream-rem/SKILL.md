---
name: dream-rem
slug: oc-dream-rem
version: 3.1.0
description: "Deep memory consolidation. Distills daily logs into topic files, removes outdated content. Triggers: dream-rem, deep memory consolidation, /dream-rem"
license: MIT
triggers:
  - 深度整合记忆
  - 梦境整理
  - 整合记忆
  - dream-rem
  - "/dream-rem"
---

# dream-rem v3.1.0 — 睡梦式记忆深度整合

定时深度整合：将分散的 daily 日记提炼合并到 topic 文件，删除过时内容，保持 `MEMORY.md` 简洁可用。

## 触发条件

- sessionCount >= 5 **且** 距上次整合 > 24小时
- 或距上次整合 > 72小时（强制整合）
- 手动：`/dream-rem`

## 工作流

```
Step 1 — 准备：读 heartbeat-state.json，检查触发条件
Step 2 — Orient：读 MEMORY.md，扫描 topics/ 目录
Step 3 — Gather：扫描最近14天 daily 文件，识别新信息/过时/矛盾
Step 4 — Consolidate：执行整合（新增/更新/删除 topic 文件）
Step 5 — Prune & Index：重写 MEMORY.md（≤200行），更新 heartbeat-state.json
Step 6 — 输出执行报告
```

## 核心原则

1. MEMORY.md = 纯索引，每行一个指针
2. topic 文件 = 真实记忆，存在 topics/ 下
3. 删除被推翻的，不保留矛盾版本
4. 相对日期转绝对日期

## 文件结构

```
memory/
├── MEMORY.md              ← 纯索引（≤200行）
├── heartbeat-state.json   ← {lastExtraction, lastDreamAt, sessionCount}
├── topics/                ← 真实记忆
└── YYYY-MM-DD.md          ← 日记原料
```

## 执行报告格式

```
## 🌙 Dream 完成 · YYYY-MM-DD HH:MM
扫描窗口：14天 | 已扫描文件：N个

| 类型 | 数量 |
|------|------|
| 新增/更新 topic | N个 |
| 清理过时记忆 | N条 |
| MEMORY.md | N行 |
```
