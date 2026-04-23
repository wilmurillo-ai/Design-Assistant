---
name: gstack
description: 世界顶级思维合集 —— Google Staff Engineer代码审查 + Martin Fowler/Kent Beck/Jeff Dean工程思维 + Paul Graham/Sam Altman创业思维 + Elon Musk创新思维。v1.0.0 Review角色深度融合Google工程实践：CR黄金法则、知识传递文化、安全/性能/可维护性审查清单、Staff Engineer CR原则。
metadata:
  {
    "openclaw":
      {
        "emoji": "🦞",
        "category": "productivity"
      }
  }
---

# gstack

**gstack for OpenClaw** —— 把 Garry Tan 的虚拟工程团队带到 OpenClaw 生态

> 将 AI Agent 从一个通用助手转变为结构化工程团队的 8 个核心角色

---

## 🎯 设计理念

Garry Tan (YC CEO) 用 Claude Code + gstack 在 60 天内产出 60 万行代码。我们把它移植到 OpenClaw，让每个人都能拥有虚拟工程团队。

**核心思想**：不是把 AI 当工具用，而是**当团队管** —— 每个阶段切换不同专家角色。

---

## 📦 包含技能

| 技能 | 角色 | 用途 |
|-----|------|-----|
| `gstack:ceo` | CEO / 产品经理 | 产品规划、需求分析、痛点挖掘 |
| `gstack:eng` | 工程经理 | 架构设计、技术选型、数据流规划 |
| `gstack:review` | 代码审查员 | 代码审查、Bug 发现、性能优化建议 |
| `gstack:qa` | QA 负责人 | 测试策略、验收标准、质量把关 |
| `gstack:ship` | 发布工程师 | 发版 checklist、部署流程、上线检查 |
| `gstack:browse` | 浏览器测试 | 网页抓取、功能验证、UI 检查 |
| `gstack:retro` | 复盘师 | 项目复盘、经验总结、改进建议 |
| `gstack:office` | 办公室时间 | 需求澄清、方向校准、头脑风暴 |

---

## 🚀 快速开始

### 1. 安装

```bash
clawhub install openclaw/gstack
```

或手动安装：

```bash
git clone https://github.com/openclaw/gstack-openclaw ~/.openclaw/skills/gstack
cd ~/.openclaw/skills/gstack && ./install.sh
```

### 2. 使用

在项目根目录创建 `GSTACK.md` 文件，记录项目上下文。

然后随时调用：

```
@gstack:ceo 帮我分析一下这个功能的产品价值

@gstack:review 审查一下这个模块的代码

@gstack:ship 准备发布 v1.0.0
```

---

## 🎭 工作流示例

### 新功能开发流程

```
1. @gstack:office      # 澄清需求，确定方向
2. @gstack:ceo         # 产品规划，写 PRD
3. @gstack:eng         # 技术架构设计
4. 【开发中...】
5. @gstack:review      # 代码审查
6. @gstack:qa          # 测试验收
7. @gstack:ship        # 发布上线
8. @gstack:retro       # 一周后复盘
```

---

## 📁 项目结构

```
gstack/
├── SKILL.md                 # 本文件
├── README.md                # 详细文档
├── GSTACK.md.template       # 项目上下文模板
├── skills/
│   ├── plan-ceo/           # CEO 技能
│   ├── plan-eng/           # 工程经理技能
│   ├── review/             # 代码审查技能
│   ├── qa/                 # QA 技能
│   ├── ship/               # 发布技能
│   ├── browse/             # 浏览器测试技能
│   ├── retro/              # 复盘技能
│   └── office/             # 办公室时间技能
└── docs/
    ├── workflow.md         # 完整工作流指南
    └── philosophy.md       # 设计理念
```

---

## 🙏 致谢

- [Garry Tan](https://github.com/garrytan) —— 原创 gstack 作者
- [Y Combinator](https://www.ycombinator.com/) —— 持续推动创业生态
- OpenClaw 社区 —— 让 AI Agent 触手可及

---

## 📄 License

MIT License —— 完全免费，随意使用、修改、分发

**我们的目标**：让每个开发者都能拥有 YC 级别的工程团队

---

*Made with 🦞 by OpenClaw Community*
