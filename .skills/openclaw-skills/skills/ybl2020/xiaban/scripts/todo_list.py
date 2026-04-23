#!/usr/bin/env python3
"""
查询待办事项脚本
显示所有待办，分为未完成和已完成两类
"""

import os
import json


def load_todos():
    """加载 todos.json"""
    todo_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'todos.json')
    try:
        with open(todo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def format_todo(todo):
    """格式化单个待办"""
    status_icon = "✅" if todo['status'] == 'done' else "⏳"
    mode_icon = "🖼️" if todo['mode'] == 'image' else "📝"

    lines = [
        f"{status_icon} [{todo['id']}] {mode_icon} {todo['content']}",
        f"    📅 创建: {todo['created_at']}"
    ]

    if todo.get('image_description'):
        lines.append(f"    🖼️  原图: {todo['image_description']}")

    if todo['status'] == 'done':
        # 如果有完成时间，显示完成时间
        if 'completed_at' in todo:
            lines.append(f"    ✅ 完成: {todo['completed_at']}")

    return "\n".join(lines)


def list_todos():
    """列出所有待办"""
    todos = load_todos()

    pending = [t for t in todos if t['status'] == 'pending']
    done = [t for t in todos if t['status'] == 'done']

    print("=" * 60)
    print("📋 待办事项列表")
    print("=" * 60)

    print(f"\n🔴 未完成 ({len(pending)} 项):")
    print("-" * 60)
    if pending:
        for todo in sorted(pending, key=lambda x: x['created_at'], reverse=True):
            print(format_todo(todo))
            print()
    else:
        print("（暂无未完成事项）")

    print(f"\n🟢 已完成 ({len(done)} 项):")
    print("-" * 60)
    if done:
        for todo in sorted(done, key=lambda x: x.get('completed_at', x['created_at']), reverse=True):
            print(format_todo(todo))
            print()
    else:
        print("（暂无已完成事项）")

    print("\n" + "=" * 60)
    print(f"总计: {len(todos)} 个待办 | 未完成: {len(pending)} | 已完成: {len(done)}")
    print("=" * 60)


def main():
    list_todos()


if __name__ == "__main__":
    main()
