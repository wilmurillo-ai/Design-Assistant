#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Email Client - 搜索邮件命令行工具
"""

import sys
import os

# 添加skill目录到路径
skill_dir = os.path.join(
    os.path.expanduser("~/.openclaw/workspace/skills/qq-email/scripts")
)
sys.path.insert(0, skill_dir)

from __init__ import QQEmailClient, search_emails


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h"]:
        print("使用方法：")
        print("  python3 search_emails.py <搜索关键词> [选项]")
        print()
        print("选项：")
        print("  --limit, -l <数字>    返回结果数量（默认：20）")
        print("  --json                输出JSON格式")
        print("  --help, -h           显示帮助")
        print()
        print("示例：")
        print(
            "  python3 search_emails.py Unity                      # 搜索Unity相关邮件"
        )
        print("  python3 search_emails.py Unity --limit 5             # 返回5条结果")
        print('  python3 search_emails.py "会议" --json              # JSON格式')
        return

    criteria = sys.argv[1]
    limit = 20
    output_json = False

    # 解析参数
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] in ["--limit", "-l"]:
            if i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
                i += 1
        elif sys.argv[i] == "--json":
            output_json = True
        i += 1

    try:
        with QQEmailClient() as client:
            emails = search_emails(criteria, limit=limit)

            if output_json:
                import json

                print(json.dumps(emails, indent=2, ensure_ascii=False))
            else:
                print(f'📧 搜索 "{criteria}" - 找到 {len(emails)} 封邮件')
                print("=" * 80)

                for idx, email in enumerate(emails, 1):
                    print(f"\n#{idx}")
                    print(f"发件人: {email['from']}")
                    print(f"主题: {email['subject']}")
                    print(f"日期: {email['date']}")
                    print("-" * 80)

    except Exception as e:
        print(f"❌ 搜索失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
