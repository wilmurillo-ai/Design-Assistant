# Skill 需求分析 & 架构设计参考指南

## 目录

1. [需求分析模板](#1-需求分析模板)
2. [架构设计模板](#2-架构设计模板)
3. [Frontmatter 编写规范](#3-frontmatter-编写规范)
4. [SKILL.md 编写模板](#4-skillmd-编写模板)
5. [示例：PDF Processor Skill](#5-示例pdf-processor-skill)

---

## 1. 需求分析模板

### 1.1 基础信息

| 字段 | 内容 |
|------|------|
| Skill 名称 | `<name>` |
| 版本 | `X.Y.Z` |
| 核心功能 | `<一句话描述>` |
| 触发关键词 | `<用户会说什么>` |
| 触发时机 | `<什么场景下激活>` |

### 1.2 功能范围

```
主要功能：
1. [功能1]
2. [功能2]
3. [功能3]

边界情况：
• [处理不了的场景]
• [限制条件]
```

### 1.3 工具权限需求

| 权限类型 | 工具 | 用途 | 安全评估 |
|---------|------|------|---------|
| 文件读取 | `read` | 读取输入文件 | ✅ 限定 workspace |
| 文件写入 | `write` | 输出结果 | ✅ 限定 workspace |
| 命令执行 | `exec` | [如需要] | ⚠️ 列出命令 |
| 网络访问 | `web_search` | [如需要] | ⚠️ 列出域名 |

### 1.4 敏感数据评估

```
涉及敏感数据： [是/否]
PII 处理：      [是/否 — 如是说明脱敏方案]
凭证使用：      [是/否 — 如是说明获取方式]
```

### 1.5 依赖分析

```
运行时依赖：
• Node.js 包: [列表]
• Python 包:  [列表]
• CLI 工具:   [列表]

系统要求：
• 操作系统:   [列表]
• 最低版本:   [如 Node ≥ 18]
```

---

## 2. 架构设计模板

### 2.1 目录结构

```
<skill-name>/
├── SKILL.md           # 主文件（必需）
├── scripts/
│   └── <script-name>.py  # 如需要
├── references/
│   └── <topic>.md        # 详细文档
└── assets/
    └── <resource>        # 静态资源
```

### 2.2 模块划分

```
模块 A（核心）：
• 功能：<描述>
• 触发条件：<何时调用>
• 输入：<参数/文件>
• 输出：<返回值/文件>

模块 B（辅助）：
• ...
```

### 2.3 流程图（文字版）

```
用户触发 → [验证输入] → [执行核心逻辑] → [格式化输出] → 完成

错误处理：
[验证输入失败] → 返回错误提示
[执行失败] → 记录日志，返回友好错误
```

---

## 3. Frontmatter 编写规范

### 3.1 标准格式

```yaml
---
name: <skill-name>        # 必须：英文小写+连字符，唯一
version: X.Y.Z           # 必须：语义化版本
description: |          # 必须：>50字，描述触发时机+功能
  当用户<做什么>时触发，执行<什么功能>。
  触发关键词：<关键词1>、<关键词2>、<关键词3>。
  用于：<主要用途>。
metadata:
  {"openclaw":{"emoji":"🔧","os":["linux","darwin","win32"]}}
---
```

### 3.2 描述字段编写公式

```
当用户[触发场景]时触发，执行[核心动作]。

触发关键词：[词1] / [词2] / [词3]
用于：[功能范围]
```

### 3.3 常见错误

| 错误 | 问题 | 修正 |
|------|------|------|
| `name: My Skill` | 含空格 | `name: my-skill` |
| `version: 1.0` | 非 semver | `version: 1.0.0` |
| `description: PDF处理` | 不足50字 | 扩展至完整描述 |
| 缺 `metadata` | 平台兼容性不明 | 添加 OS 列表 |
| 缺 emoji | 不可识别 | 添加代表性 emoji |

---

## 4. SKILL.md 编写模板

```markdown
---
name: <skill-name>
version: X.Y.Z
description: |
  <详细描述，>50字>
metadata:
  {"openclaw":{"emoji":"<emoji>","os":["linux","darwin","win32"]}}
---

# <Skill 名称>

> 简介（1-2句）

## 快速开始

[最常用的 2-3 个操作]

## 核心功能

### 功能模块 A

[说明]

### 功能模块 B

[说明]

## 安全考虑（如有）

[如无则删除此节]

## 常见错误

1. [错误1] → [修正]
2. [错误2] → [修正]
```

---

## 5. 示例：PDF Processor Skill

### 5.1 需求分析输出

```markdown
Skill 名称: pdf-processor
核心功能: 读取、拆分、合并、旋转 PDF 文件
触发关键词: PDF / 拆分PDF / 合并PDF / 旋转PDF
工具权限: read(输入PDF), write(输出PDF), exec(pdf处理CLI)
安全评估: ✅ 纯本地处理，无网络访问，无敏感数据
```

### 5.2 SKILL.md 示例

```markdown
---
name: pdf-processor
version: 1.0.0
description: |
  PDF 文件处理技能。触发关键词：PDF、拆分PDF、合并PDF、旋转PDF。
  当用户需要读取、拆分、合并、旋转 PDF 文件时触发。
  执行 PDF 操作，输出处理后的文件到 workspace。
metadata:
  {"openclaw":{"emoji":"📄","os":["linux","darwin","win32"]}}
---

# PDF Processor

## 快速开始

- "读取 PDF 内容" → 使用 pdfplumber 提取文本
- "拆分 PDF" → 按页数或书签拆分
- "合并 PDF" → 按顺序合并多个 PDF
- "旋转 PDF" → 旋转指定页面

## 核心功能

### 读取 PDF

使用 `pdfplumber` 提取文本：

```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    for page in pdf.pages:
        print(page.extract_text())
```

### 拆分 PDF

[详细实现说明]

[详见 references/pdf-advanced.md]
```

---

## 6. 设计决策记录

每次设计决策应记录：

| 决策 | 选项 | 选中 | 原因 |
|------|------|------|------|
| 依赖管理 | npm/pip/手动 | X | 因为... |
| 文件格式 | JSON/YAML/CSV | X | 因为... |
| 执行方式 | 脚本/直接执行 | X | 因为... |
