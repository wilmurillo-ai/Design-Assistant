#!/usr/bin/env python3
"""
todo.py — Unified TODO Management
==================================

Replaces file-based TODOs. All tasks in database with:
  - Priority levels (free/medium/high)
  - Dependencies (task blocking others)
  - Status tracking
  - Agent ownership

Commands:
  todo.py add --priority high --name "Research SEO" --agent research_agent
  todo.py list --priority high
  todo.py claim 5
  todo.py complete 5 "Found 10 competitors"
  todo.py report

Usage:
  from todo import TODO
  t = TODO()
  t.add_task("Analyze market", priority="high", depends_on=[1, 2])
  print(t.get_report())
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from workflow import WorkflowManager


class TODO:
    """Unified TODO management backed by database."""

    def __init__(self, backend: str = 'local'):
        self.wf = WorkflowManager(backend)

    def add_task(
        self,
        name: str,
        priority: str = 'medium',
        agent: str = None,
        task_type: str = None,
        depends_on: list = None,
    ) -> int:
        """Add a new TODO item."""
        task_id = self.wf.create_task(
            name=name,
            priority=priority,
            agent=agent,
            task_type=task_type,
            depends_on=depends_on or []
        )
        print(f"✅ Task #{task_id}: {name} ({priority})")
        return task_id

    def list_by_priority(self) -> None:
        """Print all TODOs organized by priority."""
        todos = self.wf.get_todos()
        
        print("\n" + "=" * 80)
        print("UNIFIED TODO LIST")
        print("=" * 80)
        
        for priority in ['high', 'medium', 'free']:
            items = todos.get(priority, [])
            if not items:
                continue
            
            emoji = {"high": "🔴", "medium": "🟡", "free": "🟢"}[priority]
            print(f"\n{emoji} {priority.upper()} ({len(items)} items)")
            print("-" * 80)
            
            for i, item in enumerate(items, 1):
                status_emoji = {
                    'pending': '⏳',
                    'ready': '✅',
                    'processing': '⚙️',
                    'complete': '✔️',
                    'failed': '❌',
                    'blocked': '🚫'
                }.get(item.get('status', 'pending'), '?')
                
                deps = item.get('dependencies', 0)
                deps_str = f" [{deps} blocking]" if deps else ""
                
                print(f"  {status_emoji} #{item.get('id', '?')} {item.get('name', '?')}{deps_str}")
                if item.get('agent'):
                    print(f"      → Agent: {item['agent']}")

    def get_report(self, priority: str = None) -> str:
        """Generate text report of TODOs."""
        todos = self.wf.get_todos(priority=priority)
        
        lines = [
            "=" * 80,
            "TODO REPORT",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 80,
        ]
        
        for p in ['high', 'medium', 'free']:
            items = todos.get(p, [])
            if not items:
                continue
            
            lines.append(f"\n{p.upper()} PRIORITY ({len(items)} items)")
            lines.append("-" * 80)
            
            for item in items:
                lines.append(f"  #{item.get('id', '?')} {item.get('name', '?')}")
                lines.append(f"      Status: {item.get('status', '?')}")
                if item.get('agent'):
                    lines.append(f"      Agent: {item['agent']}")
        
        return "\n".join(lines)

    def claim_task(self, task_id: int):
        """Claim a task to work on."""
        self.wf.claim_task(task_id)
        print(f"✅ Task #{task_id} claimed")

    def complete_task(self, task_id: int, result: str = ""):
        """Mark task complete."""
        self.wf.complete_task(task_id, result)
        print(f"✅ Task #{task_id} complete")
        if result:
            print(f"   Result: {result}")

    def fail_task(self, task_id: int, error: str = ""):
        """Mark task failed."""
        self.wf.fail_task(task_id, error)
        print(f"❌ Task #{task_id} failed")
        if error:
            print(f"   Error: {error}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified TODO management")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('--name', '-n', required=True, help='Task name')
    add_parser.add_argument('--priority', '-p', choices=['free', 'medium', 'high'], default='medium')
    add_parser.add_argument('--agent', '-a', help='Assigned agent')
    add_parser.add_argument('--type', '-t', help='Task type')
    add_parser.add_argument('--depends', '-d', type=int, nargs='+', help='Depends on task IDs')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List all tasks')
    list_parser.add_argument('--priority', '-p', choices=['free', 'medium', 'high'])
    
    # claim command
    claim_parser = subparsers.add_parser('claim', help='Claim a task')
    claim_parser.add_argument('task_id', type=int)
    
    # complete command
    complete_parser = subparsers.add_parser('complete', help='Mark task complete')
    complete_parser.add_argument('task_id', type=int)
    complete_parser.add_argument('--result', '-r', help='Result summary')
    
    # fail command
    fail_parser = subparsers.add_parser('fail', help='Mark task failed')
    fail_parser.add_argument('task_id', type=int)
    fail_parser.add_argument('--error', '-e', help='Error message')
    
    # report command
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument('--priority', '-p', choices=['free', 'medium', 'high'])
    
    args = parser.parse_args()
    
    todo = TODO()
    
    if args.command == 'add':
        todo.add_task(
            name=args.name,
            priority=args.priority,
            agent=args.agent,
            task_type=args.type,
            depends_on=args.depends
        )
    elif args.command == 'list':
        todo.list_by_priority()
    elif args.command == 'claim':
        todo.claim_task(args.task_id)
    elif args.command == 'complete':
        todo.complete_task(args.task_id, args.result or "")
    elif args.command == 'fail':
        todo.fail_task(args.task_id, args.error or "")
    elif args.command == 'report':
        print(todo.get_report(priority=args.priority))
    else:
        parser.print_help()
