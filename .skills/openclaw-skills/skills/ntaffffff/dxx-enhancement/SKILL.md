---
name: dxx-enhancement
description: 20个OpenClaw增强模块 - CLI彩色输出、分层记忆、多Agent协作、沙箱隔离、智能压缩、工作流编排等。让AI更强更好用。
---

# 🤖 DXX 增强模块集

让 OpenClaw 更强更好用的20个可选增强模块。

## 安装

```bash
openclaw skill install dxx-enhancement
```

## 模块列表

| # | 模块 | 功能 |
|---|------|------|
| 1 | cli | 彩色终端、表格、进度条 |
| 2 | memory | 分层记忆（短期+长期） |
| 3 | multi_agent | 多Agent协作（规划+执行+审查） |
| 4 | sandbox | 沙箱隔离执行 |
| 5 | repl | Tab补全、命令历史 |
| 6 | error_recovery | 自动重试、熔断保护 |
| 7 | compression | 智能压缩上下文 |
| 8 | tools | 工具系统标准化 |
| 9 | streaming | 流式输出打字机效果 |
| 10 | sessions | 多会话管理 |
| 11 | project_memory | 项目级CLAUDE.md |
| 12 | marketplace | 插件市场 |
| 13 | steering | Steering引导 |
| 14 | permissions | 权限验证增强 |
| 15 | async_queue | 异步消息队列 |
| 16 | monitor | 状态监控 |
| 17 | workflows | 工作流编排 |
| 18 | ide | IDE集成 |
| 19 | mcp | MCP协议 |
| 20 | tools/discovery | 工具自动发现 |

## 使用方法

### 命令行
```bash
python3 ~/.openclaw/skills/dxx-enhancement/enhancer.py cli
python3 ~/.openclaw/skills/dxx-enhancement/enhancer.py memory
python3 ~/.openclaw/skills/dxx-enhancement/enhancer.py multi_agent "写一个计算器"
```

### 在代码中引用
```python
import sys
sys.path.insert(0, '~/.openclaw/skills/dxx-enhancement/')

from cli.color_output import info, success
from memory.layered_memory import LayeredMemory
from multi_agent.system import AgentTeam
```

## 示例对话

- "用彩色输出显示当前状态"
- "用记忆系统记住我喜欢瓦罗兰特"
- "用多Agent帮我写个Python脚本"

---

*让OpenClaw更强🦀*
