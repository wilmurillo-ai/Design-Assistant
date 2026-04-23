# qclaw-subagent-factory - QClaw独立子Agent创建工厂

> 一键创建独立子Agent，自动配置权限和记忆系统

## 功能总览

| 功能 | 说明 | 命令 |
|-----|------|------|
| **create** | 交互式创建新Agent | 提供名称、ID、角色即可 |
| **list** | 查看所有Agent及状态 | 列出当前系统中的Agent |
| **setup-memory** | 初始化Agent记忆系统 | 为指定Agent创建记忆文件 |
| **summarize** | 汇总各Agent重要记忆 | 提取并展示各Agent的记忆摘要 |

## 使用方法

### 创建新Agent

```
请执行：创建Agent

提供以下信息：
- Agent名称（如：数据分析助手）
- Agent ID（如：data-analyst，英文唯一标识）
- 角色描述（如：负责数据处理和分析）
- 核心能力（如：股票分析、投资分析等）
```

示例对话：
```
用户：创建一个股票分析Agent
助手：请提供以下信息：
      1. Agent名称：股票分析助手
      2. Agent ID：stock-analyst
      3. 角色描述：负责股票数据分析和技术分析
      4. 核心能力：K线分析、资金流向、板块轮动

      确认创建？ (y/n)
用户：y

✅ Agent创建成功！
```

### 查看Agent列表

```
请执行：查看所有Agent
```

输出示例：
```
=== QClaw Agent 列表 ===

✓ main [默认]
   名称: 协调员
   记忆: ✓ | 今日日志: ✓

✓ ai-director
   名称: AI技术总监
   记忆: ✓ | 今日日志: ✓

✓ investment-director
   名称: 投资总监
   记忆: ✓ | 今日日志: ✓
```

### 初始化记忆系统

```
请执行：为 investment-director 初始化记忆系统
```

### 汇总记忆

```
请执行：汇总所有Agent的记忆
```

## 自动检测

| 检测项 | 方式 |
|-------|------|
| QClaw路径 | 智能检测 ~/.qclaw 或 AppData |
| Agent目录 | ~/.qclaw/agents/ |
| 工作区 | ~/.qclaw/workspace/ |

## 创建的目录结构

```
~/.qclaw/agents/{agent_id}/
├── agent/
│   └── models.json       # 模型配置
└── workspace/
    ├── SOUL.md           # 角色定义
    ├── AGENTS.md         # 协作协议
    ├── USER.md           # 用户信息
    ├── MEMORY.md         # 长期记忆
    ├── TOOLS.md          # 工具配置
    ├── HEARTBEAT.md      # 心跳配置
    ├── IDENTITY.md       # 身份定义
    ├── memory/           # 每日日志
    │   └── YYYY-MM-DD.md
    ├── reports/          # 报告文件
    └── projects/         # 项目文件
```

## 自动配置

创建时自动完成以下配置：

1. **目录结构**：创建完整的Agent工作区
2. **配置文件**：生成SOUL.md、AGENTS.md等
3. **记忆系统**：创建MEMORY.md和每日日志
4. **openclaw.json注册**：
   - 添加到 `agents.list`
   - 配置 `main.subagents.allowAgents`
   - 配置 `tools.agentToAgent`

## 注意事项

1. **重启生效**：创建后需要重启QClaw
2. **ID唯一性**：Agent ID必须唯一，不能重复
3. **路径自动**：自动检测QClaw安装路径，无需手动指定
4. **权限隔离**：每个Agent有独立的工作区和记忆

## 文件位置

```
C:\Users\Tang\.qclaw\skills\qclaw-subagent-factory\
├── SKILL.md              # 本文件
├── scripts/
│   ├── create_agent.py    # 创建Agent脚本
│   ├── list_agents.py     # 列出Agent脚本
│   ├── setup_memory.py    # 初始化记忆脚本
│   └── summarize_memory.py # 汇总记忆脚本
└── templates/            # 模板文件目录
```
