#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化Agent记忆系统
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
from datetime import datetime
from pathlib import Path

def detect_qclaw_base():
    """检测QClaw基础路径"""
    possible_paths = [
        Path.home() / ".qclaw",
        Path("C:/Users") / os.getenv("USERNAME", "Tang") / ".qclaw",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path.parent)
    
    return str(Path.home())

def setup_memory(agent_id=None):
    """初始化记忆系统"""
    qclaw_base = detect_qclaw_base()
    agents_dir = os.path.join(qclaw_base, ".qclaw", "agents")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if agent_id:
        # 为指定Agent初始化
        agents = [agent_id]
    else:
        # 为所有Agent初始化
        agents = ['ai-director', 'investment-director', 'misc-director']
    
    print("=" * 50)
    print("初始化Agent记忆系统")
    print("=" * 50)
    print()
    
    for aid in agents:
        workspace = os.path.join(agents_dir, aid, "workspace")
        
        if not os.path.exists(workspace):
            print(f"⚠️ {aid}: 工作区不存在，跳过")
            continue
        
        print(f"📁 {aid}")
        print("-" * 40)
        
        # 创建memory目录
        memory_dir = os.path.join(workspace, "memory")
        os.makedirs(memory_dir, exist_ok=True)
        print(f"  ✓ 创建 memory/ 目录")
        
        # 创建今日日志
        daily_file = os.path.join(memory_dir, f"{today}.md")
        if not os.path.exists(daily_file):
            content = f"""# {today} 工作日志

## 今日任务

（暂无）

## 明日待办

"""
            with open(daily_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ 创建 {today}.md")
        else:
            print(f"  → {today}.md 已存在")
        
        # 检查/创建MEMORY.md
        memory_file = os.path.join(workspace, "MEMORY.md")
        if not os.path.exists(memory_file):
            content = f"""# MEMORY.md - {aid}长期记忆

> 更新于 {today}

## 专业领域

## 常用资源

## 重要记录

"""
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ 创建 MEMORY.md")
        else:
            print(f"  → MEMORY.md 已存在")
        
        print()
    
    print("=" * 50)
    print("✅ 记忆系统初始化完成")

if __name__ == "__main__":
    import sys
    agent_id = sys.argv[1] if len(sys.argv) > 1 else None
    setup_memory(agent_id)
