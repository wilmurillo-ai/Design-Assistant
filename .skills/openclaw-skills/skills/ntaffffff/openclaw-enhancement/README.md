# 🤖 OpenClaw 增强模块集 (Skill)

> 一行命令安装，20个增强模块立刻能用！

## 安装

### 方法1：ClawHub（推荐）
```bash
openclaw skill install openclaw-enhancement
```

### 方法2：手动安装
```bash
# 克隆到 skills 目录
git clone https://github.com/ntaffffff/openclaw-enhancement.git ~/.openclaw/skills/openclaw-enhancement
```

## 使用方法

直接告诉 AI 你想用什么功能：

| 你说 | 功能 |
|------|------|
| "用彩色输出" | CLI 彩色终端 |
| "用记忆系统" | 分层记忆 |
| "用多Agent" | 多Agent协作 |
| "用沙箱" | 安全沙箱 |
| "用错误恢复" | 自动重试 |
| "用智能压缩" | 压缩上下文 |

## 命令行用法

```bash
# enhancer.py 在技能目录下
python3 ~/.openclaw/skills/openclaw-enhancement/enhancer.py <模块> [参数]

# 示例
python3 ~/.openclaw/skills/openclaw-enhancement/enhancer.py cli
python3 ~/.openclaw/skills/openclaw-enhancement/enhancer.py memory
python3 ~/.openclaw/skills/openclaw-enhancement/enhancer.py multi_agent "写一个计算器"
```

## 可用模块

| # | 模块 | 功能 |
|---|------|------|
| 1 | cli | 彩色输出、表格、进度条 |
| 2 | memory | 分层记忆系统 |
| 3 | multi_agent | 多Agent协作 |
| 4 | sandbox | 沙箱隔离执行 |
| 5 | error_recovery | 错误自动恢复 |
| 6 | compression | 智能压缩 |
| 7 | tools | 工具系统 |
| 8 | repl | REPL交互增强 |

## 示例

### 彩色输出
```
ℹ 系统消息
✓ 成功
⚠ 警告
✗ 错误

+------+----+
| 功能 | 状态 |
+------+----+
| REPL | ✓   |
| MCP  | ✓   |
+------+----+
```

### 多Agent协作
```
✓ 添加 Agent: planner (planner)
✓ 添加 Agent: executor (executor)
完成 3 个任务:
  ✓ 1. 理解需求
  ✓ 2. 编写代码
  ✓ 3. 测试验证
```

### 记忆系统
```
记忆搜索: 找到 2 条
统计: 短期2条, 长期0条
```

## 在代码中使用

```python
import sys
sys.path.insert(0, '~/.openclaw/skills/openclaw-enhancement/')

from cli.color_output import info, success
from memory.layered_memory import LayeredMemory
from multi_agent.system import AgentTeam
# ...
```

---

*让 OpenClaw 更强更好用 🦀*
*一键安装: openclaw skill install openclaw-enhancement*