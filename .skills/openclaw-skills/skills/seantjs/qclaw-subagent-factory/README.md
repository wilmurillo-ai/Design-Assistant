# qclaw-subagent-factory

> QClaw 独立子Agent创建工厂 - 一键创建、管理多Agent系统

[English](README_EN.md) | 中文

---

## 功能特性

| 功能 | 说明 |
|-----|------|
| **create** | 交互式创建新子Agent |
| **list** | 查看所有Agent及状态 |
| **setup-memory** | 初始化Agent记忆系统 |
| **summarize** | 汇总各Agent重要记忆 |

---

## 安装方式

### 方式1：复制到Skills目录

```bash
# 复制到QClaw Skills目录
cp -r qclaw-subagent-factory ~/.qclaw/skills/

# 或 Windows
xcopy /E /I qclaw-subagent-factory %USERPROFILE%\.qclaw\skills\
```

### 方式2：使用 SkillHub

```bash
skillhub install qclaw-subagent-factory
```

---

## 快速开始

### 创建新Agent

```python
# 方式1：命令行参数
python scripts/create_agent.py "数据分析助手" "data-analyst" "负责数据处理和分析" "股票分析,数据可视化"

# 方式2：交互式
python scripts/create_agent.py
# 按提示输入信息
```

### 查看Agent列表

```bash
python scripts/list_agents.py
```

输出：
```
==================================================
QClaw Agent 列表
==================================================

✓ main [默认]
   名称: 协调员
   记忆: ✓ | 今日日志: ✓

✓ ai-director
   名称: AI技术总监
   记忆: ✓ | 今日日志: ✓
```

### 汇总记忆

```bash
python scripts/summarize_memory.py
```

---

## 自动检测

| 检测项 | 说明 |
|-------|------|
| QClaw路径 | 自动检测 `~/.qclaw` 或 `AppData/QClaw` |
| Agent目录 | `~/.qclaw/agents/` |
| 工作区 | `~/.qclaw/workspace/` |

支持 Windows、macOS、Linux 跨平台。

---

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
    ├── memory/
    │   └── YYYY-MM-DD.md # 每日日志
    ├── reports/          # 报告文件
    └── projects/         # 项目文件
```

---

## 系统架构

```
用户消息 → 协调员(main)
              ↓
         sessions_spawn 召唤
    ┌────────┼────────┐
    ↓        ↓        ↓
 ai-dir  invest-dir  misc-dir
 (AI技术)  (投资)   (杂务)
```

---

## 注意事项

1. **重启生效**：创建后需要重启QClaw
2. **ID唯一性**：Agent ID必须唯一，不能重复
3. **记忆限制**：memory_search工具在子Agent环境不可用，需用本地搜索替代

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 相关项目

- [QClaw](https://github.com/openclaw/qclaw) - 核心框架
- [ClawHub](https://clawhub.com) - Skill市场
- [SkillHub](https://skillhub.com) - 中文Skill市场
