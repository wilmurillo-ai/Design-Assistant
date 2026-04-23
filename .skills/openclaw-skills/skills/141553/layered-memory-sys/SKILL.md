---
name: layered-memory-sys
description: >
  分层记忆系统（Layered Memory System）— 为AI助手提供类人的6层记忆架构。
  自动管理记忆的生命周期：闪存(3天)、活跃(7天)、关注(30天)、沉淀(90天)、核心(永久)。
  包含梦境模式（Dream Cycle）自动执行记忆巩固、归档、遗忘和合并。
  支持语义相似度检测和Session日志优先检索。
  
  当用户需要：(1) 优化AI记忆管理，(2) 建立分层TTL记忆系统，(3) 实现自动记忆整理，
  (4) 搭建梦境模式处理流程，(5) 改善AI跨会话记忆连续性 时使用。
  
  关键词：记忆、记忆系统、分层记忆、TTL、梦境模式、记忆归档、语义相似度、session日志
---

# 分层记忆系统 (Layered Memory)

为AI助手提供类人的6层记忆架构，模拟人类大脑的"白天经历→夜晚整理→巩固/遗忘"循环。

## 6层记忆架构

```
核心层（永久）━━━━━━━━━━━━━━━━━━━ MEMORY.md
沉淀层（90天）━━━━━━━━━ 重要决策/项目经验
关注层（30天）━━━━━ 反复讨论的话题
活跃层（7天）━━━ 正在进行的任务
闪存层（3天）━ 临时查询/一次性问答
Session（实时）━━━━━━ 当前对话上下文
```

## 快速开始

### 1. 初始化记忆系统

复制以下文件到AI助手的 `memory/` 目录：

```
memory/
├── index.json              ← 分层记忆索引
├── archive.md              ← 归档记忆
├── dream-log.md            ← 梦境日志
└── scripts/
    ├── dream-cycle.mjs         ← 梦境执行器
    ├── session-search.mjs      ← Session日志检索
    └── semantic-similarity.mjs ← 语义相似度检测
```

### 2. 配置心跳触发梦境

在心跳配置（如 HEARTBEAT.md）中添加：

```
当时间在凌晨2-5点或白天空闲时：
  1. 执行 `node memory/scripts/dream-cycle.mjs`
  2. 自动处理：巩固/归档/遗忘/合并
  3. 结果写入 dream-log.md
```

### 3. 初始化 index.json

首次使用时创建索引文件，格式见 [references/index-schema.md](references/index-schema.md)。

## 自动写入规则

每次对话中根据条件自动写入记忆：

- **对话轮次 > 10** → 写入 active 层（7天）
- **用户说"记住这个"** → 直接写 settled 层（90天）
- **一次性问答（< 5轮）** → flash 层（3天，自动过期删除）
- **任务完成** → 标记 `status: "completed"`，7天后归档

## 升级规则

| 条件 | 动作 |
|------|------|
| recallCount ≥ 3 且 flash | 升级到 active（7天） |
| recallCount ≥ 5 且 active | 升级到 attention（30天） |
| recallCount ≥ 10 且 attention | 升级到 settled（90天） |
| settled 被频繁引用 | 写入 MEMORY.md（永久） |

## 任务类型

| 类型 | 起始层 | 策略 |
|------|--------|------|
| short（短期任务） | active | 完成后7天归档 |
| recurring（周期任务） | attention | 每次执行刷新TTL |
| exploration（探索话题） | flash | 反复讨论才升级 |

## 梦境模式

见 [references/dream-cycle.md](references/dream-cycle.md) 获取完整的梦境模式流程说明。

## 检索优先级

```
1. memory/index.json（结构化索引）
2. memory/*.md（每日记忆）
3. Session日志（session-search.mjs）
   → 路径: ~/.openclaw/agents/main/sessions/*.jsonl
```

## 脚本使用

### dream-cycle.mjs — 梦境执行器

```bash
node dream-cycle.mjs
```

自动执行：巩固检查 → 归档检查 → 遗忘检查 → 合并检查 → session日志检索

### session-search.mjs — 日志检索

```bash
node session-search.mjs <关键词1> <关键词2> ...
```

搜索最近的session日志，找回compaction丢失的对话细节。

### semantic-similarity.mjs — 语义相似度

```bash
node semantic-similarity.mjs
```

测试语义相似度检测（TF-IDF + 余弦相似度，中文n-gram + 英文词）。

## 归档格式

过期记忆概括保存到 archive.md：

```markdown
## 技术
- [2026-04-17] AI定价策略/Token成本
  状态：completed | 概括：讨论了传输vs推理成本、厂商定价逻辑

## 运维
- [2026-04-10] 龙虾服务修复
  难点：systemd限制 → 改独立脚本
```
