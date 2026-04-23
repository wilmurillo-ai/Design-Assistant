#!/usr/bin/env python3
"""
标记待办为完成或删除
用法：
  python todo_done.py --complete <id>    标记为完成
  python todo_done.py --delete <id>      删除待办
  python todo_done.py --toggle <id>      切换状态（pending <-> done）
"""

import os
import sys
import json
from datetime import datetime


def load_todos():
    """加载 todos.json"""
    todo_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'todos.json')
    try:
        with open(todo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_todos(todos):
    """保存 todos.json"""
    todo_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'todos.json')
    with open(todo_file, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def find_todo_by_id(todos, todo_id):
    """根据 ID 查找待办"""
    for todo in todos:
        if todo['id'] == todo_id:
            return todo
    return None


def complete_todo(todo_id):
    """标记待办为完成"""
    todos = load_todos()
    todo = find_todo_by_id(todos, todo_id)

    if not todo:
        print(f"❌ 未找到 ID 为 {todo_id} 的待办")
        return False

    if todo['status'] == 'done':
        print(f"⚠️  待办 {todo_id} 已经是完成状态")
        return False

    todo['status'] = 'done'
    todo['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_todos(todos)

    print(f"✅ 已完成待办 {todo_id}")
    print(f"   内容: {todo['content']}")
    return True


def delete_todo(todo_id):
    """删除待办"""
    todos = load_todos()
    todo = find_todo_by_id(todos, todo_id)

    if not todo:
        print(f"❌ 未找到 ID 为 {todo_id} 的待办")
        return False

    todos = [t for t in todos if t['id'] != todo_id]
    save_todos(todos)

    print(f"🗑️  已删除待办 {todo_id}")
    print(f"   内容: {todo['content']}")
    return True


def toggle_todo(todo_id):
    """切换待办状态"""
    todos = load_todos()
    todo = find_todo_by_id(todos, todo_id)

    if not todo:
        print(f"❌ 未找到 ID 为 {todo_id} 的待办")
        return False

    if todo['status'] == 'pending':
        todo['status'] = 'done'
        todo['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action = "已完成"
    else:
        todo['status'] = 'pending'
        if 'completed_at' in todo:
            del todo['completed_at']
        action = "已重置为待处理"

    save_todos(todos)
    print(f"✅ 待办 {todo_id} {action}")
    print(f"   内容: {todo['content']}")
    return True


def main():
    if len(sys.argv) < 3:
        print("用法:")
        print("  python todo_done.py --complete <id>    标记为完成")
        print("  python todo_done.py --delete <id>      删除待办")
        print("  python todo_done.py --toggle <id>      切换状态")
        print("\n示例:")
        print("  python todo_done.py --complete abc12345")
        sys.exit(1)

    action = sys.argv[1]
    todo_id = sys.argv[2]

    if action == "--complete":
        complete_todo(todo_id)
    elif action == "--delete":
        delete_todo(todo_id)
    elif action == "--toggle":
        toggle_todo(todo_id)
    else:
        print(f"错误: 未知操作 '{action}'")
        print("可用操作: --complete, --delete, --toggle")
        sys.exit(1)


if __name__ == "__main__":
    main()
