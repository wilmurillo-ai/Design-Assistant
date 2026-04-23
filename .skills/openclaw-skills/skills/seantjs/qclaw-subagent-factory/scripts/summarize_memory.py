#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汇总各Agent重要记忆到协调员
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
import json
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

def read_file_content(filepath):
    """安全读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None

def summarize_memories():
    """汇总各Agent的记忆"""
    qclaw_base = detect_qclaw_base()
    agents_dir = os.path.join(qclaw_base, ".qclaw", "agents")
    main_workspace = os.path.join(agents_dir, "main", "workspace")
    
    print("=" * 60)
    print("子Agent记忆汇总")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()
    
    # Agent列表（排除main）
    agent_ids = ['ai-director', 'investment-director', 'misc-director']
    
    all_summaries = []
    
    for agent_id in agent_ids:
        agent_path = os.path.join(agents_dir, agent_id, "workspace")
        
        if not os.path.exists(agent_path):
            print(f"⚠️ {agent_id}: 工作区不存在")
            print()
            continue
        
        print(f"📋 {agent_id}")
        print("-" * 40)
        
        # 读取MEMORY.md
        memory_file = os.path.join(agent_path, "MEMORY.md")
        memory_content = read_file_content(memory_file)
        
        if memory_content:
            # 提取重要记录部分
            if "## 重要记录" in memory_content:
                lines = memory_content.split("\n")
                in_important = False
                important_content = []
                for line in lines:
                    if "## 重要记录" in line:
                        in_important = True
                        continue
                    if in_important and line.startswith("## "):
                        break
                    if in_important:
                        important_content.append(line)
                
                if important_content:
                    print("📌 重要记录:")
                    print("\n".join(important_content[:10]))  # 只显示前10行
                else:
                    print("  （暂无重要记录）")
            else:
                print("  （MEMORY.md内容较少）")
        else:
            print("  ⚠️ 未找到MEMORY.md")
        
        # 读取今日日志
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = os.path.join(agent_path, "memory", f"{today}.md")
        daily_content = read_file_content(daily_file)
        
        if daily_content:
            print("\n📅 今日日志摘要:")
            # 提取任务部分
            lines = daily_content.split("\n")
            in_tasks = False
            task_content = []
            for line in lines:
                if "## 今日" in line or "## 任务" in line:
                    in_tasks = True
                    continue
                if in_tasks and line.startswith("## "):
                    break
                if in_tasks and line.strip():
                    task_content.append(line)
            
            if task_content:
                print("\n".join(task_content[:8]))  # 只显示前8行
            else:
                print("  （暂无任务记录）")
        else:
            print("\n📅 今日日志: （暂无）")
        
        print()
    
    print("=" * 60)
    print("✅ 汇总完成")
    print("\n如需更新协调员记忆，请告诉我需要同步哪些内容")

if __name__ == "__main__":
    summarize_memories()
