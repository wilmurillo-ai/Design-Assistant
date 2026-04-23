#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Email Client - 发送邮件命令行工具
"""

import sys
import os

# 添加skill目录到路径
skill_dir = os.path.join(
    os.path.expanduser("~/.openclaw/workspace/skills/qq-email/scripts")
)
sys.path.insert(0, skill_dir)

from __init__ import QQEmailClient, send_email


def main():
    if len(sys.argv) < 4 or sys.argv[1] in ["--help", "-h"]:
        print("使用方法：")
        print("  python3 send_email.py <收件人> <主题> <正文> [选项]")
        print()
        print("选项：")
        print("  --html, -h          使用HTML格式")
        print("  --help, -h           显示帮助")
        print()
        print("示例：")
        print('  python3 send_email.py "user@example.com" "测试" "这是测试邮件"')
        print(
            '  python3 send_email.py "user@example.com" "测试" "<h1>HTML</h1>" --html'
        )
        return

    to = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    use_html = False

    # 解析参数
    i = 4
    while i < len(sys.argv):
        if sys.argv[i] in ["--html", "-h"]:
            use_html = True
        i += 1

    try:
        send_email(to, subject, body, html="<body></body>" if use_html else None)
        print("✅ 邮件发送成功")

    except Exception as e:
        print(f"❌ 发送失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
