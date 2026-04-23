#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ Email Client - 使用示例
"""

import sys
import os
import json

# 添加skill目录到路径
skill_dir = os.path.join(
    os.path.expanduser("~/.openclaw/workspace/skills/qq-email/scripts")
)
sys.path.insert(0, skill_dir)

from __init__ import QQEmailClient


def example_1_list_emails():
    """示例1：列出最近10封邮件"""
    print("示例1：列出最近10封邮件\n")

    with QQEmailClient() as client:
        emails = client.list_emails(limit=10)

        for idx, email in enumerate(emails, 1):
            print(f"{idx}. {email['subject']}")

    print(f"✅ 共{len(emails)}封邮件\n")


def example_2_read_email():
    """示例2：读取指定邮件"""
    print("\n示例2：读取邮件内容\n")
    print("提示：请先运行 list_emails.py 获取邮件ID\n")

    # 这里需要实际的邮件ID
    email_id = input("请输入邮件ID（从list_emails.py获取）: ")

    if email_id:
        with QQEmailClient() as client:
            email = client.read_email(email_id)

            print(f"主题: {email['subject']}")
            print(f"发件人: {email['from']}")
            print(f"正文:\n{email['body']}")


def example_3_search_emails():
    """示例3：搜索邮件"""
    print("\n示例3：搜索包含'Unity'的邮件\n")

    with QQEmailClient() as client:
        emails = client.search_emails("Unity", limit=5)

        for idx, email in enumerate(emails, 1):
            print(f"{idx}. {email['subject']}")

    print(f"✅ 找到{len(emails)}封相关邮件\n")


def example_4_send_email():
    """示例4：发送新邮件"""
    print("\n示例4：发送测试邮件\n")
    print("⚠️  注意：请修改收件人地址")

    with QQEmailClient() as client:
        client.send_email(
            to="recipient@example.com",
            subject="测试邮件 - QQ Email Client",
            body="这是通过QQ Email Client发送的测试邮件。\n\n时间: "
            + str(__import__("datetime").datetime.now()),
        )

    print("✅ 邮件已发送\n")


def example_5_json_output():
    """示例5：JSON格式输出"""
    print("\n示例5：JSON格式输出\n")

    with QQEmailClient() as client:
        emails = client.list_emails(limit=3)

        print(json.dumps(emails, indent=2, ensure_ascii=False))


def example_6_list_folders():
    """示例6：列出所有文件夹"""
    print("\n示例6：列出所有文件夹\n")

    with QQEmailClient() as client:
        folders = client.list_folders()

        for idx, folder in enumerate(folders, 1):
            print(f"{idx}. {folder}")

    print(f"✅ 共{len(folders)}个文件夹\n")


def main():
    print("=" * 80)
    print("QQ Email Client 使用示例")
    print("=" * 80)
    print()

    examples = [
        ("列出最近邮件", example_1_list_emails),
        ("读取邮件内容", example_2_read_email),
        ("搜索邮件", example_3_search_emails),
        ("发送新邮件", example_4_send_email),
        ("JSON格式输出", example_5_json_output),
        ("列出文件夹", example_6_list_folders),
    ]

    print("可用示例：")
    for idx, (name, func) in enumerate(examples, 1):
        print(f"  {idx}. {name}")

    print()
    print("请选择示例编号 (1-6，0退出): ", end="")

    try:
        choice = int(input())

        if choice == 0:
            print("退出")
            return
        elif 1 <= choice <= len(examples):
            _, func = examples[choice - 1]
            func()
        else:
            print("❌ 无效的选择")

    except ValueError:
        print("❌ 请输入有效的数字")
    except KeyboardInterrupt:
        print("\n退出")


if __name__ == "__main__":
    main()
