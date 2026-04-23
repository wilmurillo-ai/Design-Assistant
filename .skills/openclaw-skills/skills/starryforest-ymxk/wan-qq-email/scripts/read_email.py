#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Email Client - 读取邮件内容命令行工具
"""

import sys
import os

# 添加skill目录到路径
skill_dir = os.path.join(
    os.path.expanduser("~/.openclaw/workspace/skills/qq-email/scripts")
)
sys.path.insert(0, skill_dir)

from __init__ import QQEmailClient, read_email


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h"]:
        print("使用方法：")
        print("  python3 read_email.py <邮件ID> [选项]")
        print()
        print("选项：")
        print("  --json                输出JSON格式")
        print("  --body-only          仅显示正文")
        print("  --attachments         显示附件信息")
        print("  --help, -h           显示帮助")
        print()
        print("示例：")
        print("  python3 read_email.py 12345              # 读取邮件")
        print("  python3 read_email.py 12345 --json      # JSON格式输出")
        print()
        print("提示：邮件ID从 list_emails.py 获取")
        return

    email_id = sys.argv[1]
    output_json = False
    body_only = False
    show_attachments = False

    # 解析参数
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--json":
            output_json = True
        elif sys.argv[i] == "--body-only":
            body_only = True
        elif sys.argv[i] == "--attachments":
            show_attachments = True
        i += 1

    try:
        email = read_email(email_id)

        if output_json:
            import json

            print(json.dumps(email, indent=2, ensure_ascii=False))
        else:
            print("=" * 80)
            print(f"📧 邮件详情")
            print("=" * 80)
            print(f"ID: {email['id']}")
            print(f"发件人: {email['from']}")
            print(f"收件人: {email['to']}")
            print(f"主题: {email['subject']}")
            print(f"日期: {email['date']}")

            if not body_only:
                print("\n--- 正文 ---")
                print(email["body"])

            if show_attachments and email["attachments"]:
                print("\n--- 附件 ({len(email['attachments'])} 个) ---")
                for idx, attachment in enumerate(email["attachments"], 1):
                    print(
                        f"  {idx}. {attachment['filename']} ({attachment['size']} bytes)"
                    )

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
