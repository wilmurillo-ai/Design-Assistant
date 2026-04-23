#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看所有Agent状态
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import json
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

def list_agents():
    """列出所有Agent"""
    qclaw_base = detect_qclaw_base()
    agents_dir = os.path.join(qclaw_base, ".qclaw", "agents")
    
    config_path = os.path.join(qclaw_base, ".qclaw", "openclaw.json")
    
    # 读取配置获取Agent列表
    registered_agents = []
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            agents_list = config.get('agents', {}).get('list', [])
            for a in agents_list:
                registered_agents.append({
                    'id': a.get('id'),
                    'name': a.get('name', a.get('id')),
                    'default': a.get('default', False)
                })
    
    print("=" * 50)
    print("QClaw Agent 列表")
    print("=" * 50)
    print(f"Agents目录: {agents_dir}")
    print()
    
    if not registered_agents:
        print("未找到已注册的Agent")
        return
    
    for agent in registered_agents:
        agent_id = agent['id']
        agent_path = os.path.join(agents_dir, agent_id, "workspace")
        
        # 检查工作区是否存在
        exists = "✓" if os.path.exists(agent_path) else "✗"
        
        # 检查记忆文件
        memory_file = os.path.join(agent_path, "MEMORY.md") if os.path.exists(agent_path) else None
        has_memory = "✓" if memory_file else "✗"
        
        # 检查今日日志
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        daily_log = os.path.join(agent_path, "memory", f"{today}.md") if os.path.exists(agent_path) else None
        has_daily = "✓" if daily_log else "✗"
        
        default_tag = " [默认]" if agent.get('default') else ""
        
        print(f"{exists} {agent_id}{default_tag}")
        print(f"   名称: {agent['name']}")
        print(f"   工作区: {agent_path}")
        print(f"   记忆: {has_memory} | 今日日志: {has_daily}")
        print()

if __name__ == "__main__":
    list_agents()
