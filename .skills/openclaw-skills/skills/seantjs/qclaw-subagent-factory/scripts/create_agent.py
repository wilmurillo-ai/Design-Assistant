#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QClaw 独立子Agent创建脚本
自动检测QClaw路径，创建完整的Agent配置
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

# ==================== 路径检测 ====================

def detect_qclaw_base():
    """检测QClaw基础路径"""
    # 尝试多个可能的位置
    possible_paths = [
        Path.home() / ".qclaw",
        Path.home() / "AppData" / "Roaming" / "QClaw",
        Path("C:/Users") / os.getenv("USERNAME", "Tang") / ".qclaw",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path.parent)
    
    # 默认使用用户目录
    return str(Path.home())

def detect_agents_dir():
    """检测agents目录路径"""
    qclaw_base = detect_qclaw_base()
    return os.path.join(qclaw_base, ".qclaw", "agents")

def detect_workspace():
    """检测workspace目录路径"""
    qclaw_base = detect_qclaw_base()
    return os.path.join(qclaw_base, ".qclaw", "workspace")

def get_openclaw_config():
    """读取openclaw.json配置"""
    qclaw_base = detect_qclaw_base()
    config_path = os.path.join(qclaw_base, ".qclaw", "openclaw.json")
    
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# ==================== Agent创建 ====================

def create_agent(name, agent_id, role, capabilities):
    """创建新的子Agent"""
    
    print(f"[qclaw-subagent-factory] 开始创建Agent...")
    print(f"  名称: {name}")
    print(f"  ID: {agent_id}")
    print(f"  角色: {role}")
    
    # 检测路径
    agents_dir = detect_agents_dir()
    workspace = detect_workspace()
    
    print(f"[检测] Agents目录: {agents_dir}")
    print(f"[检测] Workspace: {workspace}")
    
    # 创建目录结构
    agent_base = os.path.join(agents_dir, agent_id)
    agent_workspace = os.path.join(agent_base, "workspace")
    agent_dir = os.path.join(agent_base, "agent")
    
    dirs_to_create = [
        agent_base,
        agent_workspace,
        agent_dir,
        os.path.join(agent_workspace, "memory"),
        os.path.join(agent_workspace, "reports"),
        os.path.join(agent_workspace, "projects"),
    ]
    
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)
        print(f"[创建] {d}")
    
    # 生成SOUL.md
    soul_content = generate_soul_md(name, role, capabilities)
    with open(os.path.join(agent_workspace, "SOUL.md"), 'w', encoding='utf-8') as f:
        f.write(soul_content)
    print(f"[创建] SOUL.md")
    
    # 生成AGENTS.md
    agents_content = generate_agents_md(name, agent_id)
    with open(os.path.join(agent_workspace, "AGENTS.md"), 'w', encoding='utf-8') as f:
        f.write(agents_content)
    print(f"[创建] AGENTS.md")
    
    # 生成USER.md
    user_content = generate_user_md()
    with open(os.path.join(agent_workspace, "USER.md"), 'w', encoding='utf-8') as f:
        f.write(user_content)
    print(f"[创建] USER.md")
    
    # 生成MEMORY.md
    memory_content = generate_memory_md(name)
    with open(os.path.join(agent_workspace, "MEMORY.md"), 'w', encoding='utf-8') as f:
        f.write(memory_content)
    print(f"[创建] MEMORY.md")
    
    # 生成TOOLS.md
    tools_content = generate_tools_md(capabilities)
    with open(os.path.join(agent_workspace, "TOOLS.md"), 'w', encoding='utf-8') as f:
        f.write(tools_content)
    print(f"[创建] TOOLS.md")
    
    # 复制models.json
    main_models = os.path.join(agents_dir, "main", "agent", "models.json")
    target_models = os.path.join(agent_dir, "models.json")
    if os.path.exists(main_models):
        shutil.copy(main_models, target_models)
        print(f"[创建] models.json")
    
    # 创建今日日志
    today = datetime.now().strftime("%Y-%m-%d")
    daily_log = f"# {today} 工作日志\n\n## 今日任务\n\n（暂无）\n\n## 明日待办\n\n"
    with open(os.path.join(agent_workspace, "memory", f"{today}.md"), 'w', encoding='utf-8') as f:
        f.write(daily_log)
    print(f"[创建] memory/{today}.md")
    
    # 更新openclaw.json
    update_openclaw_config(agent_id, name, agent_workspace, agent_dir)
    print(f"[更新] openclaw.json")
    
    print(f"\n✅ Agent创建成功！")
    print(f"  路径: {agent_workspace}")
    print(f"  ID: {agent_id}")
    print(f"  名称: {name}")
    print(f"\n⚠️ 请重启QClaw使配置生效")

# ==================== 模板生成 ====================

def generate_soul_md(name, role, capabilities):
    """生成SOUL.md"""
    caps_text = "\n".join([f"- **{c}**" for c in capabilities])
    
    return f"""# SOUL.md - {name}

你是一位{role}。

## 核心职责

{caps_text}

## 工作风格

- 专业、高效、注重细节
- 善于分析和解决问题
- 表达清晰简洁

## 协作方式

- 接收协调员的指令，执行任务
- 完成后将结果返回给协调员

## 记忆管理规范

**每次启动任务时：**
1. 读取 `MEMORY.md`（长期记忆）
2. 读取 `memory/YYYY-MM-DD.md`（今日日志）
3. 使用 `exec + Select-String` 搜索历史

**任务完成后：**
- 将结论写入 `memory/YYYY-MM-DD.md`
- 重大发现更新 `MEMORY.md`

## 文件管理规范

**所有工作文件必须保存到自己的工作区**

### 存储位置
```
{agent_workspace.replace(chr(92), '/')}/
├── reports/          # 报告文件
├── projects/         # 项目文件
├── memory/           # 记忆文件
└── [其他生成的文件]
```

### 共享规则
- 需要展示的内容直接在对话中输出
- 需要协调员保存的文件在结果中说明路径
- 重要文档保存到自己的workspace + 通知协调员

## ⚠️ 重要限制

- `memory_search` 工具在子Agent环境不可用
- 使用 `exec + Select-String` 本地搜索替代
"""

def generate_agents_md(name, agent_id):
    """生成AGENTS.md"""
    return f"""# AGENTS.md

## Agent ID
`{agent_id}`

## 角色
{name}

## 协作协议
- 接收来自协调员（main agent）的任务指派
- 执行完任务后将结果以结构化格式返回
- 如遇问题，及时反馈给协调员
"""

def generate_user_md():
    """生成USER.md"""
    return """# USER.md - 关于用户

- **用户名**: Tang
- **桌面路径**: `E:\\Tang\\Desktop`
- **工作区**: `C:\\Users\\Tang\\.qclaw\\workspace`
- **常用磁盘**: E盘（桌面、数据）、C盘（系统）
"""

def generate_memory_md(name):
    """生成MEMORY.md"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"""# MEMORY.md - {name}长期记忆

> 更新于 {today}

## 专业领域

## 常用资源

## 重要记录

"""

def generate_tools_md(capabilities):
    """生成TOOLS.md"""
    return f"""# TOOLS.md - 工具配置

## 可用工具
- 网络搜索
- 文件读写
- 代码执行
- 数据分析

## 能力清单
{chr(10).join([f"- {c}" for c in capabilities])}

## 数据源
- ClawHub Skill市场
- 各专业数据API
"""

# ==================== 配置更新 ====================

def update_openclaw_config(agent_id, name, workspace, agent_dir):
    """更新openclaw.json"""
    qclaw_base = detect_qclaw_base()
    config_path = os.path.join(qclaw_base, ".qclaw", "openclaw.json")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 确保agents.list存在
    if 'agents' not in config:
        config['agents'] = {}
    if 'list' not in config['agents']:
        config['agents']['list'] = []
    
    # 检查是否已存在
    exists = any(a.get('id') == agent_id for a in config['agents']['list'])
    if not exists:
        # 添加新Agent
        config['agents']['list'].append({
            "id": agent_id,
            "name": name,
            "workspace": workspace,
            "agentDir": agent_dir
        })
    
    # 确保main有subagents.allowAgents
    for agent in config['agents']['list']:
        if agent.get('id') == 'main':
            if 'subagents' not in agent:
                agent['subagents'] = {}
            if 'allowAgents' not in agent['subagents']:
                agent['subagents']['allowAgents'] = []
            for aid in ['ai-director', 'investment-director', 'misc-director', agent_id]:
                if aid not in agent['subagents']['allowAgents']:
                    agent['subagents']['allowAgents'].append(aid)
            break
    
    # 确保tools.agentToAgent存在
    if 'tools' not in config:
        config['tools'] = {}
    if 'agentToAgent' not in config['tools']:
        config['tools']['agentToAgent'] = {"enabled": True, "allow": []}
    if config['tools']['agentToAgent'].get('enabled') is None:
        config['tools']['agentToAgent']['enabled'] = True
    if 'allow' not in config['tools']['agentToAgent']:
        config['tools']['agentToAgent']['allow'] = []
    
    for aid in ['ai-director', 'investment-director', 'misc-director', agent_id]:
        if aid not in config['tools']['agentToAgent']['allow']:
            config['tools']['agentToAgent']['allow'].append(aid)
    
    # 写回配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# ==================== 主入口 ====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("用法: create_agent.py <名称> <ID> <角色> [能力1,能力2,...]")
        print("示例: create_agent.py 数据分析助手 data-analyst 负责数据处理和分析 股票分析,数据可视化")
        sys.exit(1)
    
    name = sys.argv[1]
    agent_id = sys.argv[2]
    role = sys.argv[3]
    capabilities = sys.argv[4].split(",") if len(sys.argv) > 4 else ["通用能力"]
    
    create_agent(name, agent_id, role, capabilities)
