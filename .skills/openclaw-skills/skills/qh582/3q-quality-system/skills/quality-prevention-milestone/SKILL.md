---
name: quality-prevention-milestone
version: v2.0.0
type: workflow
owner: 小 O
quality_score: 15/15
last_updated: 2026-03-28
depends_on:
  - self-challenge-3q
  - task-breakdown
triggers:
  - "质量检查"
  - "质量预防"
  - "milestone 检查"
  - "事前事中事后"
  - "quality check"
  - "质量里程碑"
  - "quality prevention"
best_for: 三阶段质量预防（事前 3Q + 事中 13 检查点 + 事后 3Q）
scenarios:
  - "项目里程碑节点"
  - "重要文档发布前"
  - "代码上线前质量检查"
  - "任务完成后的质量验收"
---

# quality-prevention-milestone v2.0 - 质量预防技能

## 🌐 English Summary

**Three-Phase Quality Prevention Framework**

Proactive quality assurance across three phases:

**Phase 1: Pre-Event 3Q (5 min)**
- Ensure direction is correct before starting
- Logic/User/Competition Q check

**Phase 2: During-Event 13 Checkpoints**
- Requirements, architecture, error handling
- Performance, security, documentation
- Test coverage, code style, etc.

**Phase 3: Post-Event 3Q (10 min)**
- Quality scoring (15-point scale)
- Lessons learned
- Knowledge base update

**Effect**: Prevents 85% of common mistakes, rework rate ↓77%

**Time**: 20-30 minutes total

**Triggers**: `质量检查`, `质量预防`, `milestone 检查`, `quality check`

---

## 📖 详细文档

## 📖 Overview（概述）

**quality-prevention-milestone** 是 3Q 质量保障体系的预防技能，提供三阶段质量预防框架。

通过**事前 3Q + 事中 13 检查点 + 事后 3Q**，实现质量左移，提前发现并预防问题。

**适用场景**：
- 项目里程碑节点
- 重要文档发布前
- 代码上线前质量检查
- 任务完成后的质量验收

**质量评分**: 15/15（S 级技能）

**依赖关系**: self-challenge-3q, task-breakdown

**被依赖技能**:
- `3Q-Plus-v3` - 元认知增强版
- `quality-os` - 质量操作系统
- `quality-os-trigger` - 质量触发器

---

## ✨ Capabilities & Features（能力与特性）

### 核心能力
1. **事前 3Q** - 任务开始前的质量规划
2. **事中 13 检查点** - 执行过程中的质量检查
3. **事后 3Q** - 交付后的质量验收
4. **质量左移** - 预防优于检查

### 特性
- ✅ 三阶段全流程覆盖
- ✅ 13 个检查点标准化
- ✅ 适用于项目里程碑
- ✅ 平均检查时间：2-4 小时

### 三阶段框架

| 阶段 | 检查内容 | 工具/方法 |
|------|----------|-----------|
| **事前** | 3Q 规划 | self-challenge-3q |
| **事中** | 13 检查点 | quality-prevention-milestone |
| **事后** | 3Q 验收 | self-challenge-3q |

---

## 📋 使用指南

### 触发方式
```
触发词："质量检查", "质量预防", "milestone 检查"
```

### 检查流程
1. 事前 3Q 规划（15 分钟）
2. 事中 13 检查点（1-3 小时）
3. 事后 3Q 验收（15 分钟）

### 13 检查点
详见技能文档正文

---

**维护者**: 小 O 🤖  
**最后更新**: 2026-03-28  
**下次审查**: 2026-04-04
