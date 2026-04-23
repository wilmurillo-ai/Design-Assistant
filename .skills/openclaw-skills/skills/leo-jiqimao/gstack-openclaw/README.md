# gstack-openclaw 🦞

> 把 Garry Tan 的虚拟工程团队带到 OpenClaw 生态

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/Built%20for-OpenClaw-blue)](https://github.com/openclaw/openclaw)

---

## 🎯 什么是 gstack-openclaw？

**gstack** 是 Y Combinator CEO Garry Tan 开源的 Claude Code 工作流系统，让他能在 60 天内产出 **60 万行代码**。

**gstack-openclaw** 是它的 OpenClaw 移植版本，让每个人都能拥有 YC 级别的虚拟工程团队。

### 核心理念

> 不是把 AI 当工具用，而是**当团队管** —— 每个阶段切换不同专家角色。

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
| `gstack:docs` | 技术文档工程师 | 自动生成 README、API 文档 |
| `gstack:test` | 测试工程师 | 生成测试用例和测试代码 |
| `gstack:deploy` | DevOps 工程师 | 生成部署脚本和 CI/CD 配置 |
| `gstack:init` | 项目初始化 | 自动创建 GSTACK.md 和项目骨架 |
| `gstack:status` | 项目状态追踪 | 查看进度和下一步行动 |
| `gstack:github` | GitHub 集成 | PR 检查、CI 监控、发布说明 |
| `gstack:notify` | 消息通知 | 飞书/Discord 多渠道通知 |

---

## 🚀 快速开始

### 从 ClawHub 安装（推荐）

```bash
clawhub install openclaw/gstack
```

### 手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/openclaw/gstack-openclaw ~/.openclaw/skills/gstack

# 2. 运行安装脚本
cd ~/.openclaw/skills/gstack
chmod +x install.sh
./install.sh
```

### 验证安装

```bash
clawhub list
# 应该看到 gstack 及其子技能
```

---

## 💡 使用方法

### 基础用法

在项目根目录随时调用：

```
@gstack:ceo 帮我分析一下这个功能的产品价值

@gstack:review 审查一下这个模块的代码

@gstack:qa 设计一下测试用例

@gstack:ship 准备发布 v1.0.0
```

### 完整工作流示例

**新功能开发**：

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

### 项目配置

在项目根目录创建 `GSTACK.md` 记录项目上下文：

```markdown
# Project Context

## 项目概述
- 名称: MyApp
- 技术栈: React + Node.js + PostgreSQL
- 团队规模: 5人

## 关键链接
- 设计稿: [Figma URL]
- API 文档: [Swagger URL]
- 监控面板: [Grafana URL]

## 注意事项
- 用户表敏感字段需加密
- 支付模块需要额外审查
```

---

## 📚 技能详解

### gstack:ceo —— CEO / 产品经理
像 Brian Chesky 一样思考产品，找到真正的用户痛点。

```
@gstack:ceo 我想做一个XXX功能
```

**输出**：痛点分析、目标用户、价值主张、MVP 范围、成功指标

---

### gstack:eng —— 工程经理
设计稳健的技术架构，做好技术选型。

```
@gstack:eng 帮我设计这个功能的架构
```

**输出**：架构图、数据模型、接口设计、技术选型、风险分析

---

### gstack:review —— 代码审查员
像资深工程师一样审查代码，发现隐藏问题。

```
@gstack:review 审查当前文件
```

**输出**：代码质量评分、阻塞问题、警告问题、优化建议

---

### gstack:qa —— QA 负责人
设计全面的测试策略，定义验收标准。

```
@gstack:qa 设计测试用例
```

**输出**：测试计划、测试用例、边界情况、风险评估

---

### gstack:ship —— 发布工程师
确保每次发布都稳定可靠。

```
@gstack:ship 准备发布 v1.2.0
```

**输出**：发布检查清单、Changelog、回滚方案、发布后验证

---

### gstack:browse —— 浏览器测试
进行真实的浏览器测试，验证功能。

```
@gstack:browse 打开 https://example.com
```

**输出**：页面截图、功能检查、UI/UX 评估、问题发现

---

### gstack:retro —— 复盘师
从经验中学习，持续改进。

```
@gstack:retro 复盘最近这个项目
```

**输出**：4L 分析 (Loved/Learned/Lacked/Longed for)、行动项

---

### gstack:office —— 办公室时间
像 YC 合伙人一样帮助澄清思路。

```
@gstack:office 帮我看看这个产品方向
```

**输出**：问题诊断、决策分析、方向校准

---

## 🎓 设计理念

### 为什么角色驱动？

传统 AI 助手是"你问什么我答什么"，缺乏上下文和专业深度。

gstack 通过**角色切换**，让 AI 在每个阶段都以专家身份思考：
- 产品阶段 → 用 CEO 思维
- 技术阶段 → 用架构师思维
- 测试阶段 → 用 QA 思维

### 从 Garry Tan 学到的

Garry 用这套系统 60 天产出 60 万行代码，关键不是"更快"，而是：
1. **结构化**: 每个阶段有明确的目标和输出
2. **专业化**: 不同角色专注不同领域
3. **可复用**: 把个人最佳实践封装成流程

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. **Fork 仓库**
2. **创建分支**: `git checkout -b feature/amazing-feature`
3. **提交更改**: `git commit -m 'Add amazing feature'`
4. **推送分支**: `git push origin feature/amazing-feature`
5. **创建 Pull Request**

### 贡献内容

- 🐛 Bug 修复
- ✨ 新技能或技能改进
- 📚 文档改进
- 🌐 翻译支持
- 💡 新想法和建议

---

## 🙏 致谢

- [Garry Tan](https://github.com/garrytan) —— 原创 gstack 作者，开源精神的典范
- [Y Combinator](https://www.ycombinator.com/) —— 持续推动创业生态
- [OpenClaw](https://github.com/openclaw/openclaw) —— 让 AI Agent 触手可及
- 所有贡献者 —— 让这个生态变得更好

---

## 📄 License

MIT License —— 完全免费，随意使用、修改、分发

```
Copyright (c) 2026 OpenClaw Community

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

**我们的目标**：让每个开发者都能拥有 YC 级别的工程团队

---

## 💬 社区

- GitHub Issues: [提问和反馈](https://github.com/openclaw/gstack-openclaw/issues)
- Discord: [加入讨论](https://discord.gg/openclaw)
- Twitter: [@openclaw](https://twitter.com/openclaw)

---

*Made with 🦞 by OpenClaw Community*

> "Build something people want" —— Y Combinator
