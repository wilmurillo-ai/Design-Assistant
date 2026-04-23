#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StarryForest Agent SKILL 使用示例
"""

import sys

sys.path.append("/home/wudi")

from skills import (
    StarryForestAgent,
    send_reminder,
    send_memo,
    send_alarm,
    send_calendar_event,
    send_focus_mode,
    send_music,
    send_journal,
)


def example_1_single_reminder():
    """示例 1：发送单个提醒事项"""
    print("\n=== 示例 1：单个提醒事项 ===")
    send_reminder(
        title="测试提醒：喝水",
        to_email="starryforest_ymxk@hotmail.com",
        due="2026-02-07 15:00",
        notes="来自 Python SKILL 示例",
        priority="中",
        email_title="自动化推送 - 单个提醒",
    )


def example_2_batch_operations():
    """示例 2：批量发送多个操作"""
    print("\n=== 示例 2：批量操作 ===")

    agent = StarryForestAgent(account="126")

    # 闹钟
    agent.create_alarm(
        time="07:30",
        label="晨练",
        enabled=True,
        repeat=["Monday", "Wednesday", "Friday"],
    )

    # 提醒事项
    agent.create_reminder(
        title="测试提醒：喝水",
        due="2026-02-07 15:00",
        notes="来自 Python SKILL",
        priority="中",
    )

    # 备忘录
    agent.create_memo(
        title="OpenClaw 测试备忘录", content="这是通过 SKILL 批量创建的备忘录"
    )

    # 日历日程
    agent.create_calendar_event(
        title="OpenClaw 测试日程",
        start="2026-02-07 10:00",
        end="2026-02-07 10:30",
        location="Home",
        notes="测试：创建日历事件",
        all_day=False,
    )

    # 专注模式
    agent.focus_mode(name="工作", on=True, until="2026-02-07 12:00")

    # 音乐控制
    agent.play_music(play=True, playlist="每日推荐")

    # 日记
    agent.write_journal(
        title="日记", date="2026-02-07", content="今天完成了 SKILL 批量操作测试"
    )

    # 一次性发送所有操作
    agent.send_all(to_email="starryforest_ymxk@hotmail.com", title="批量自动化推送")


def example_3_calendar_event():
    """示例 3：创建日历日程"""
    print("\n=== 示例 3：日历日程 ===")

    agent = StarryForestAgent()
    agent.create_calendar_event(
        title="工作会议",
        start="2026-02-07 09:00",
        end="2026-02-07 10:00",
        location="会议室",
        notes="讨论项目进度",
        all_day=False,
    )
    agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送 - 日历日程")


def example_4_memo():
    """示例 4：创建备忘录"""
    print("\n=== 示例 4：备忘录 ===")

    agent = StarryForestAgent()
    agent.create_memo(
        title="Python SKILL 使用笔记",
        content="1. 创建 Agent 对象\n2. 添加操作\n3. 发送邮件",
    )
    agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送 - 备忘录")


def example_5_focus_mode():
    """示例 5：专注模式"""
    print("\n=== 示例 5：专注模式 ===")

    agent = StarryForestAgent()
    agent.focus_mode(name="工作", on=True, until="2026-02-07 18:00")
    agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送 - 专注模式")


def example_6_music_control():
    """示例 6：音乐控制"""
    print("\n=== 示例 6：音乐控制 ===")

    agent = StarryForestAgent()
    agent.play_music(play=True, playlist="每日推荐")
    agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送 - 音乐控制")


def example_7_journal():
    """示例 7：写日记"""
    print("\n=== 示例 7：写日记 ===")

    agent = StarryForestAgent()
    agent.write_journal(
        title="学习日记",
        date="2026-02-07",
        content="今天学习了 StarryForest Agent SKILL 的使用方法",
    )
    agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送 - 写日记")


def example_8_qq_account():
    """示例 8：使用 QQ 邮箱发送"""
    print("\n=== 示例 8：QQ 邮箱 ===")

    agent = StarryForestAgent(account="qq")
    agent.create_reminder(
        title="QQ 邮箱测试提醒",
        due="2026-02-07 20:00",
        notes="来自 QQ 邮箱发送",
        priority="中",
    )
    agent.send_all(to_email="starryforest_ymxk@hotmail.com", title="来自 QQ 邮箱的推送")


def example_9_convenience_functions():
    """示例 9：使用便捷函数"""
    print("\n=== 示例 9：便捷函数 ===")

    # 使用便捷函数单个发送
    send_alarm(time="07:00", to_email="starryforest_ymxk@hotmail.com", label="起床闹钟")


def example_10_clear_and_reuse():
    """示例 10：清空操作列表并复用"""
    print("\n=== 示例 10：复用 Agent ===")

    agent = StarryForestAgent()

    # 第一批操作
    agent.create_reminder(title="提醒 1", due="2026-02-07 15:00")
    agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送 - 第一批")

    # 第二批操作（不需要重新创建 Agent）
    agent.create_reminder(title="提醒 2", due="2026-02-07 16:00")
    agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送 - 第二批")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="StarryForest Agent SKILL 示例")
    parser.add_argument(
        "--example",
        type=int,
        choices=range(1, 11),
        help="运行示例 1-10，不指定则运行示例 2（批量操作）",
    )

    args = parser.parse_args()

    # 运行示例
    examples = {
        1: example_1_single_reminder,
        2: example_2_batch_operations,
        3: example_3_calendar_event,
        4: example_4_memo,
        5: example_5_focus_mode,
        6: example_6_music_control,
        7: example_7_journal,
        8: example_8_qq_account,
        9: example_9_convenience_functions,
        10: example_10_clear_and_reuse,
    }

    example_num = args.example if args.example else 2
    examples[example_num]()

    print("\n✅ 示例执行完成")
