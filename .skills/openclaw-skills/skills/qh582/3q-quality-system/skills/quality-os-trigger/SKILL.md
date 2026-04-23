---
name: quality-os-trigger
version: v4.0.0
type: workflow
owner: 小 O
quality_score: 15/15
last_updated: 2026-03-28
depends_on:
  - quality-prevention-milestone
  - self-challenge-3q
  - 3Q-Plus-v3
triggers:
  - "质量检查"
  - "QualityOS"
  - "质量触发"
  - "自动质量检查"
  - "质量左移"
  - "技能联动"
  - "quality trigger"
  - "3Q 检查"
  - "auto quality check"
best_for: QualityOS 统一触发入口 + 技能联动机制（自动触发 + 技能联动 + 质量左移）
scenarios:
  - "文档保存时"
  - "代码提交时"
  - "决策开始时"
  - "子代理创建/交付时"
  - "内容发布前"
---

# quality-os-trigger v4.0 - 质量触发器

## 🌐 English Summary

**QualityOS Unified Trigger & Auto-Dispatch System**

Automatic quality check dispatcher that triggers appropriate 3Q skills based on task type:

- **Document Save** → quality-prevention (post-3Q check)
- **Code Commit** → quality-prevention(CODE) (13 checkpoints)
- **Decision Start** → decision-checklist (12 decision points)
- **Subagent Creation** → subagent-brief-template (3Q requirements)
- **Subagent Delivery** → 3Q-Plus-v3 (acceptance check)
- **Content Publish** → 3Q-Plus-v3 (mandatory pre-publish check)

**Effect**: Auto-trigger rate ≥90%, avg score ≥14/15, rework rate ≤10%

**Response Time**: <1 second

**Triggers**: `质量检查`, `QualityOS`, `质量触发`, `quality trigger`

---

## 📖 详细文档

## 📖 Overview（概述）

**quality-os-trigger** 是 QualityOS 的统一触发入口，提供自动触发和技能联动机制。

通过**自动触发 + 技能联动 + 质量左移**，实现质量检查的自动化和标准化。

**适用场景**：
- 文档保存时
- 代码提交时
- 决策开始时
- 子代理创建/交付时
- 内容发布前

**质量评分**: 15/15（S 级技能）

**依赖关系**: quality-prevention-milestone, self-challenge-3q, 3Q-Plus-v3

**被依赖技能**: 无（顶层触发器）

---

## ✨ Capabilities & Features（能力与特性）

### 核心能力
1. **自动触发** - 文档保存/代码提交时自动检查
2. **技能联动** - 根据任务类型自动匹配质量技能
3. **质量左移** - 事前预防优于事后检查

### 特性
- ✅ 自动触发机制
- ✅ 技能智能联动
- ✅ 质量左移理念
- ✅ 平均响应时间：<1 秒

### 触发规则

| 事件 | 触发技能 | 检查内容 |
|------|----------|----------|
| 文档保存 | quality-prevention-milestone | 3Q 检查 |
| 代码提交 | quality-prevention-milestone(CODE) | 13 检查点 |
| 决策开始 | decision-checklist | 12 决策点 |
| 子代理创建 | subagent-brief-template | 3Q 要求 |
| 子代理交付 | 3Q-Plus-v3 | 验收 Q |
| 内容发布 | 3Q-Plus-v3 | 发布前检查 |

---

## 📋 使用指南

### 触发方式
```
触发词："质量检查", "QualityOS", "质量触发"
```

### 自动触发流程
1. 检测事件（保存/提交/决策等）
2. 匹配触发规则
3. 调用对应技能
4. 返回检查结果

---

**维护者**: 小 O 🤖  
**最后更新**: 2026-03-28  
**下次审查**: 2026-04-04
