# GitHub Knowledge Base 使用说明

## 技能概述
这个技能可以管理本地GitHub仓库知识库，支持下载、搜索、分析GitHub仓库。

## 自动触发
当用户提到以下关键词时会自动触发：
- github
- repo / repository  
- 仓库
- git

## 主要功能

### 1. 下载仓库
**命令格式**: `下载 [仓库名称]`

**示例**:
- `下载 openai/gpt-3` - 下载OpenAI的GPT-3仓库
- `下载 facebook/react` - 下载React仓库

### 2. 搜索仓库
**命令格式**: `搜索 [关键词]`

**示例**:
- `搜索 python machine learning` - 搜索相关仓库
- `搜索 web framework` - 搜索Web框架

### 3. 查询仓库信息
**命令格式**: `[仓库名称] 的信息`

**示例**:
- `react 仓库的信息` - 查看React仓库详情
- `openai/gpt-3 的信息` - 查看GPT-3仓库详情

### 4. 查看仓库列表
**命令格式**: `有哪些仓库` / `列表`

**示例**:
- `有哪些本地仓库`
- `列出所有仓库`

## 工作原理

### 本地仓库管理
- 仓库保存在: `/home/node/clawd/github-kb/`
- 每个仓库都会自动生成一句话摘要
- 摘要记录在: `CLAUDE.md` 文件中

### GitHub集成
- 使用 `gh` 命令搜索GitHub
- 自动分析仓库README生成摘要
- 支持查看issues、PRs等信息

## 使用示例

### 场景1: 下载新仓库
```
用户: 下载 facebook/react
技能: 正在克隆仓库: https://github.com/facebook/react
      分析仓库并更新摘要
      成功下载仓库: facebook/react
```

### 场景2: 搜索相关仓库
```
用户: 搜索 python web框架
技能: 本地找到相关仓库:
      - django: Django is a high-level Python web framework...
      
      GitHub相关仓库:
      - django/django: The Web framework for perfectionists...
      - flask/flask: A micro web framework for Python...
```

### 场景3: 查询仓库详情
```
用户: react 仓库的信息
技能: 仓库信息: react
      路径: /home/node/clawd/github-kb/react
      大小: 125.5 MB
      分支数: 15
      摘要: A declarative, efficient, and flexible JavaScript library...
```

## 注意事项

1. **Token限制**: 使用不超过300万tokens，超过会提醒用户
2. **依赖**: 需要安装Git和GitHub CLI (`gh`)
3. **网络**: 需要网络连接才能下载GitHub仓库
4. **权限**: 需要写入 `/home/node/clawd/github-kb/` 目录

## 故障排除

### 常见问题
1. **仓库下载失败**: 检查网络连接和仓库名称
2. **搜索无结果**: 尝试使用更具体的关键词
3. **权限错误**: 确保有目录写入权限

### 解决方案
1. 检查 `gh` 命令是否已安装和配置
2. 验证仓库名称格式是否正确
3. 查看技能日志获取详细错误信息