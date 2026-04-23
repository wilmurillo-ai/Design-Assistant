#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Email Client - 列出邮件命令行工具
"""

import sys
import os
import json

# 添加skill目录到路径
skill_dir = os.path.join(
    os.path.expanduser("~/.openclaw/workspace/skills/qq-email/scripts")
)
sys.path.insert(0, skill_dir)

from __init__ import QQEmailClient, list_emails


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("使用方法：")
        print("  python3 list_emails.py [选项]")
        print()
        print("选项：")
        print("  --limit, -l <数字>    列出邮件数量（默认：10）")
        print("  --folder, -f <名称>   文件夹名称（默认：INBOX）")
        print("  --json                输出JSON格式")
        print("  --help, -h           显示帮助")
        print()
        print("示例：")
        print("  python3 list_emails.py                      # 列出最近10封邮件")
        print("  python3 list_emails.py --limit 5         # 列出最近5封邮件")
        print("  python3 list_emails.py --folder Sent       # 列出发件箱邮件")
        print("  python3 list_emails.py --json              # JSON格式输出")
        return

    # 解析参数
    limit = 10
    folder = "INBOX"
    output_json = False

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] in ["--limit", "-l"]:
            if i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
                i += 1
        elif sys.argv[i] in ["--folder", "-f"]:
            if i + 1 < len(sys.argv):
                folder = sys.argv[i + 1]
                i += 1
        elif sys.argv[i] == "--json":
            output_json = True
        i += 1

    # 列出邮件
    try:
        with QQEmailClient() as client:
            emails = client.list_emails(limit=limit, folder=folder)

            if output_json:
                print(json.dumps(emails, indent=2, ensure_ascii=False))
            else:
                print(f"📧 {folder} 最近 {len(emails)} 封邮件")
                print("=" * 80)

                for idx, email in enumerate(emails, 1):
                    print(f"\n#{idx}")
                    print(f"发件人: {email['from']}")
                    print(f"日期: {email['date']}")
                    print(f"主题: {email['subject']}")
                    print("-" * 80)

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
