---
name: skill-lifecycle
description: |
  Skill 全生命周期管理工具 - 标准化开发、测试、发布流程
  核心流程：版本管理 + 测试 + 质量扫描 + Git 提交
  扩展流程：ClawHub 发布（可选）+ 知识提炼（可选）
  效率提升：本地开发 35 分钟→3 分钟，完整发布 50 分钟→5 分钟
version: 0.2.0
tags: ["lifecycle", "devops", "cli", "skill-management", "automation"]
metadata:
  openclaw:
    emoji: "🔄"
---

# Skill Lifecycle - 全生命周期管理工具

## 触发词

当用户提到以下内容时使用此 Skill：
- "创建 skill-lifecycle"
- "开发生命周期工具"
- "自动化发布流程"
- "sl-dev" / "sl-full"
- "Skill 版本管理"

## 快速开始

```bash
# 安装依赖
cd ~/.openclaw/workspace/skills/skill-lifecycle
pip install -r requirements.txt

# 本地开发流程（不含发布）
sl-dev --bump patch

# 完整发布流程（含 ClawHub）
sl-full --bump patch

# 单独命令
sl-version bump patch
sl-test
sl-scan
sl-commit -m "更新"
sl-publish  # 可选
```

## 命令说明

| 命令 | 功能 | 必需/可选 |
|------|------|----------|
| `sl-dev` | 开发流程（版本 + 测试 + 扫描 + Git） | 核心 |
| `sl-full` | 完整流程（开发 + 发布） | 可选 |
| `sl-version` | 版本管理 | 核心 |
| `sl-test` | 测试执行 | 核心 |
| `sl-scan` | 质量扫描 | 核心 |
| `sl-commit` | Git 提交 | 核心 |
| `sl-publish` | ClawHub 发布 | 可选 |

## 使用场景

**场景 1: 本地开发**
```bash
cd skills/my-tool
python3 ../skill-lifecycle/lifecycle.py dev --bump patch
```

**场景 2: 正式发布**
```bash
cd skills/doc-processor
python3 ../skill-lifecycle/lifecycle.py full --bump minor
```

**场景 3: 仅质量检查**
```bash
python3 ../skill-lifecycle/lifecycle.py test && python3 ../skill-lifecycle/lifecycle.py scan
```

## 文档

**详细文档**已归档到 `~/backups/skills-archive/skill-lifecycle-docs/`：
- `DESIGN.md` - 详细设计文档
- `README.md` - 快速概览
- `USAGE.md` - 使用指南
