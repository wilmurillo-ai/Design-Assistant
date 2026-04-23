#!/usr/bin/env python3
"""
定时提醒脚本
扫描未完成的待办事项，推送到 Telegram
"""

import os
import json
from datetime import datetime

# 导入 OpenClaw 的 message 工具（需要运行在 OpenClaw 环境中）
try:
    from openclaw import message
except ImportError:
    # 如果不是在 OpenClaw 环境中运行，则使用模拟的 message 函数
    print("警告: 未找到 openclaw 模块，将使用模拟输出")
    message = None

# Telegram chat_id
TELEGRAM_CHAT_ID = "5171675321"


def load_todos():
    """加载 todos.json"""
    todo_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'todos.json')
    try:
        with open(todo_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_pending_todos():
    """获取所有未完成的待办"""
    todos = load_todos()
    pending = [t for t in todos if t['status'] == 'pending']
    return pending


def format_remind_message(pending_todos):
    """格式化提醒消息"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not pending_todos:
        return None

    lines = [
        "🔔 待办事项提醒",
        f"📅 时间: {now}",
        "",
        f"你有 {len(pending_todos)} 个未完成的待办:",
        "-" * 40
    ]

    for i, todo in enumerate(pending_todos, 1):
        mode_icon = "🖼️" if todo['mode'] == 'image' else "📝"
        lines.append(f"{i}. {mode_icon} {todo['content']}")
        lines.append(f"   🆔 {todo['id']} | 📅 {todo['created_at']}")
        lines.append("")

    lines.append("-" * 40)
    lines.append("💡 使用 `todo_list.py` 查看完整列表")
    lines.append("💡 使用 `todo_done.py --complete <ID>` 标记完成")

    return "\n".join(lines)


def send_telegram_message(text):
    """发送消息到 Telegram"""
    try:
        # 尝试使用 OpenClaw 的 message tool
        if message:
            message(
                action="send",
                target=f"telegram:{TELEGRAM_CHAT_ID}",
                message=text
            )
            print(f"✅ 已发送提醒到 Telegram (chat_id: {TELEGRAM_CHAT_ID})")
            return True
        else:
            print("模拟发送到 Telegram:")
            print("=" * 60)
            print(text)
            print("=" * 60)
            return True
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")
        return False


def remind():
    """主函数：扫描并发送提醒"""
    pending = get_pending_todos()
    msg = format_remind_message(pending)

    if not msg:
        print(f"ℹ️  没有未完成的待办事项 (时间: {datetime.now().strftime('%H:%M:%S')})")
        return

    send_telegram_message(msg)


def main():
    remind()


if __name__ == "__main__":
    main()
