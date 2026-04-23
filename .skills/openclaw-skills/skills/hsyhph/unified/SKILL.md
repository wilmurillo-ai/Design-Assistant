# GitHub Knowledge Base Skill

## 概述
这个技能用于管理本地GitHub仓库知识库，提供GitHub仓库的本地管理和分析功能。

## 配置
- **本地GitHub目录**: `@/home/node/clawd/skills/unified/github-kb/CLAUDE.md`
- **GitHub CLI**: 使用 `gh` 命令进行GitHub操作
- **Git命令**: 用于克隆和管理本地仓库

## 功能

### 1. 仓库管理
- 自动检测本地GitHub目录
- 记录每个仓库的一句话摘要
- 支持克隆新仓库到本地目录

### 2. 智能搜索
- 当用户提到 "github"、"repo"、"仓库" 时自动触发
- 优先在本地目录搜索用户提到的仓库
- 使用GitHub CLI搜索远程仓库信息

### 3. 内容分析
- 分析本地仓库结构和内容
- 提供仓库相关的技术信息
- 查看issues、PRs等信息

### 4. 自动更新
- 仓库克隆后自动更新CLAUDE.md
- 记录仓库摘要和关键信息

## 使用方法

### 基本操作
- `下载 [仓库名]` - 克隆指定仓库到本地目录
- `[仓库名] 的信息` - 查询仓库详细信息
- `搜索 [关键词]` - 在GitHub上搜索相关仓库

### 示例
- "下载 openai/gpt-3"
- "react 仓库的issues"
- "搜索 python machine learning"

## 注意事项
- Token使用限制：300万tokens，超过会提醒用户
- 需要GitHub CLI已安装并配置
- 本地目录需要存在且可写

## 文件结构
```
/home/node/clawd/skills/unified/github-kb/
├── CLAUDE.md          # 仓库摘要记录
├── [仓库名1]/        # 克隆的仓库1
├── [仓库名2]/        # 克隆的仓库2
└── ...
```