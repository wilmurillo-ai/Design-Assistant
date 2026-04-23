#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StarryForest Agent Mail API v1 SKILL

封装七种自动化操作，通过邮件发送到 iOS 快捷指令自动化。

支持的操作：
1. 创建闹钟 (create_alarm)
2. 创建提醒事项 (create_reminder)
3. 创建备忘录 (create_memo)
4. 创建日历日程 (create_calendar_event)
5. 专注模式 (focus_mode)
6. 播放音乐 (play_music)
7. 写日记 (write_journal)

使用示例:
    from skills.starryforest_agent import StarryForestAgent

    agent = StarryForestAgent()

    # 创建提醒事项
    agent.create_reminder(
        title="测试提醒",
        due="2026-02-07 15:00",
        notes="来自 Python SKILL",
        priority="中"
    )

    # 批量发送多个操作
    agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送")
"""

import smtplib
import json
import uuid
import warnings
from datetime import datetime
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from email.header import Header


# 邮箱配置
SMTP_CONFIG = {
    "126": {
        "host": "smtp.126.com",
        "port": 465,
        "user": "starryforest_ymxk@126.com",
        "password": "VCddC36LS9CRjd36",
        "from_addr": "starryforest_ymxk@126.com",
    },
    "qq": {
        "host": "smtp.qq.com",
        "port": 465,
        "user": "1911308683@qq.com",
        "password": "nllzqegzklliebbh",
        "from_addr": "1911308683@qq.com",
    },
}


class StarryForestAgent:
    """StarryForest Agent Mail API v1 封装类"""

    def __init__(self, account: str = "126"):
        """
        初始化 Agent

        Args:
            account: 邮箱账户，可选 "126" 或 "qq"，默认 "126"
        """
        if account not in SMTP_CONFIG:
            raise ValueError(
                f"不支持的邮箱账户: {account}，支持: {list(SMTP_CONFIG.keys())}"
            )

        self.account = account
        self.smtp_config = SMTP_CONFIG[account]
        self.actions: List[Dict[str, Any]] = []
        self.payload_id = self._generate_id()

    def _generate_id(self) -> str:
        """生成唯一的 payload ID"""
        return (
            f"agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
        )

    def _add_action(self, action_type: str, payload: Dict[str, Any]) -> None:
        """
        添加动作到列表

        Args:
            action_type: 动作类型（中文）
            payload: 动作参数
        """
        self.actions.append({"type": action_type, "payload": payload})

    # ========== 七种操作封装 ==========

    def create_alarm(
        self,
        time: str,
        label: Optional[str] = None,
        enabled: bool = True,
        repeat: Optional[List[str]] = None,
    ) -> None:
        """
        创建闹钟

        Args:
            time: 闹钟时间，格式 "HH:mm"，例如 "07:30"
            label: 闹钟标签（可选）
            enabled: 是否启用（默认 true）
            repeat: 重复星期（英文全称列表），例如 ["Monday", "Wednesday", "Friday"]
                   可选值: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

        示例:
            agent.create_alarm(
                time="07:30",
                label="晨练",
                enabled=True,
                repeat=["Monday", "Wednesday", "Friday"]
            )
        """
        payload = {"time": time}

        if label is not None:
            payload["label"] = label
        if enabled is not None:
            payload["enabled"] = enabled
        if repeat is not None:
            payload["repeat"] = repeat

        self._add_action("创建闹钟", payload)

    def create_reminder(
        self,
        title: str,
        due: Optional[str] = None,
        notes: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> None:
        """
        创建提醒事项

        Args:
            title: 提醒事项标题（必填）
            due: 到期时间点，格式 "YYYY-MM-DD HH:mm"，例如 "2026-02-07 15:00"（可选）
            notes: 备注（可选）
            priority: 优先级，可选 "高" / "中" / "低"（可选）

        示例:
            agent.create_reminder(
                title="测试提醒：喝水",
                due="2026-02-07 15:00",
                notes="来自 Python SKILL",
                priority="中"
            )
        """
        payload = {"title": title}

        if due is not None:
            payload["due"] = due
        if notes is not None:
            payload["notes"] = notes
        if priority is not None:
            payload["priority"] = priority

        self._add_action("创建提醒事项", payload)

    def create_memo(self, title: str, content: str) -> None:
        """
        创建备忘录

        Args:
            title: 备忘录标题（必填）
            content: 备忘录内容（必填）

        示例:
            agent.create_memo(
                title="OpenClaw 测试备忘录",
                content="这是一条通过 Python SKILL 创建的备忘录。"
            )
        """
        self._add_action("创建备忘录", {"title": title, "content": content})

    def create_calendar_event(
        self,
        title: str,
        start: str,
        end: Optional[str] = None,
        location: Optional[str] = None,
        notes: Optional[str] = None,
        all_day: bool = False,
    ) -> None:
        """
        创建日历日程

        Args:
            title: 日程标题（必填）
            start: 开始时间点，格式 "YYYY-MM-DD HH:mm"，例如 "2026-02-07 10:00"（必填）
            end: 结束时间点，格式 "YYYY-MM-DD HH:mm"（可选，默认 start + 30分钟）
            location: 地点（可选）
            notes: 备注（可选）
            all_day: 是否全天（默认 false）

        示例:
            agent.create_calendar_event(
                title="OpenClaw 测试日程",
                start="2026-02-07 10:00",
                end="2026-02-07 10:30",
                location="Home",
                notes="测试：创建日历事件",
                all_day=False
            )
        """
        payload = {"title": title, "start": start}

        if end is not None:
            payload["end"] = end
        if location is not None:
            payload["location"] = location
        if notes is not None:
            payload["notes"] = notes
        if all_day is not None:
            payload["allDay"] = all_day

        self._add_action("创建日历日程", payload)

    def focus_mode(self, name: str, on: bool, until: Optional[str] = None) -> None:
        """
        设置专注模式

        Args:
            name: 专注模式名称（必填），可选 "工作" / "个人" / "睡眠"
            on: true 开启 / false 关闭（必填）
            until: 结束时间点，格式 "YYYY-MM-DD HH:mm"（可选，仅 on=true 时有意义）

        示例:
            agent.focus_mode(
                name="工作",
                on=True,
                until="2026-02-07 12:00"
            )
        """
        payload = {"name": name, "on": on}

        if until is not None:
            payload["until"] = until

        self._add_action("专注模式", payload)

    def play_music(self, play: bool, playlist: str) -> None:
        """
        播放音乐

        Args:
            play: true 播放 / false 暂停（必填）
            playlist: 播放列表（必填），可选 "每日推荐" / "私人漫游"

        示例:
            agent.play_music(
                play=True,
                playlist="每日推荐"
            )
        """
        self._add_action("播放音乐", {"play": play, "playlist": playlist})

    def write_journal(self, title: str, date: str, content: str) -> None:
        """
        写日记

        Args:
            title: 日记标题，例如 "日记" / "日报"（必填）
            date: 日期，格式 "YYYY-MM-DD"，例如 "2026-02-07"（必填）
            content: 日记正文（必填）

        示例:
            agent.write_journal(
                title="日记",
                date="2026-02-07",
                content="今天学习了 Python SKILL 封装。"
            )
        """
        self._add_action("写日记", {"title": title, "date": date, "content": content})

    # ========== 邮件发送 ==========

    def clear_actions(self) -> None:
        """清空所有已添加的动作"""
        self.actions = []
        self.payload_id = self._generate_id()

    def send_all(
        self, to_email: str, title: str = "自动化推送", clear: bool = True
    ) -> bool:
        """
        发送所有已添加的动作

        Args:
            to_email: 收件人邮箱
            title: 邮件标题（默认 "自动化推送"，必须包含此短语才能触发自动化）
            clear: 发送后是否清空动作列表（默认 true）

        Returns:
            成功返回 True，失败返回 False
        """
        if not self.actions:
            print("❌ 没有待发送的动作")
            return False

        # 验证邮件标题
        if "自动化推送" not in title:
            warnings.warn(
                f"⚠️  邮件标题 '{title}' 不包含 '自动化推送'，可能无法触发 iOS 自动化流程！",
                UserWarning,
            )

        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config["from_addr"]
            msg["To"] = to_email
            msg["Subject"] = Header(title, "utf-8")
            msg["Date"] = formatdate(localtime=True)

            # 构建 Agent Payload
            payload = {
                "version": 1,
                "token": "starryforest_agent",
                "id": self.payload_id,
                "actions": self.actions,
            }

            # 邮件正文（使用锚定块）
            body = f"""{title}

AGENT_PAYLOAD_BEGIN
{json.dumps(payload, ensure_ascii=False, indent=2)}
AGENT_PAYLOAD_END
"""

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # 连接 SMTP 服务器并发送
            with smtplib.SMTP_SSL(
                self.smtp_config["host"], self.smtp_config["port"]
            ) as server:
                server.login(self.smtp_config["user"], self.smtp_config["password"])
                server.send_message(msg)

            print(f"✅ 邮件发送成功: {to_email}")
            print(f"   Payload ID: {self.payload_id}")
            print(f"   动作数量: {len(self.actions)}")

            # 清空动作列表
            if clear:
                self.clear_actions()

            return True

        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False

    def get_actions_count(self) -> int:
        """获取当前待发送的动作数量"""
        return len(self.actions)


# ========== 便捷函数 ==========


def send_alarm(
    time: str,
    to_email: str,
    label: Optional[str] = None,
    enabled: bool = True,
    repeat: Optional[List[str]] = None,
    account: str = "126",
    title: str = "自动化推送",
) -> bool:
    """
    快捷发送闹钟

    Args:
        time: 闹钟时间，格式 "HH:mm"
        to_email: 收件人邮箱
        label: 闹钟标签（可选）
        enabled: 是否启用（默认 true）
        repeat: 重复星期（可选）
        account: 邮箱账户（默认 "126"）
        title: 邮件标题（默认 "自动化推送"）

    Returns:
        成功返回 True，失败返回 False
    """
    agent = StarryForestAgent(account)
    agent.create_alarm(time, label, enabled, repeat)
    return agent.send_all(to_email, title)


def send_reminder(
    title: str,
    to_email: str,
    due: Optional[str] = None,
    notes: Optional[str] = None,
    priority: Optional[str] = None,
    account: str = "126",
    email_title: str = "自动化推送",
) -> bool:
    """
    快捷发送提醒事项

    Args:
        title: 提醒事项标题
        to_email: 收件人邮箱
        due: 到期时间点（可选）
        notes: 备注（可选）
        priority: 优先级（可选）
        account: 邮箱账户（默认 "126"）
        email_title: 邮件标题（默认 "自动化推送"）

    Returns:
        成功返回 True，失败返回 False
    """
    agent = StarryForestAgent(account)
    agent.create_reminder(title, due, notes, priority)
    return agent.send_all(to_email, email_title)


def send_memo(
    title: str,
    content: str,
    to_email: str,
    account: str = "126",
    email_title: str = "自动化推送",
) -> bool:
    """
    快捷发送备忘录

    Args:
        title: 备忘录标题
        content: 备忘录内容
        to_email: 收件人邮箱
        account: 邮箱账户（默认 "126"）
        email_title: 邮件标题（默认 "自动化推送"）

    Returns:
        成功返回 True，失败返回 False
    """
    agent = StarryForestAgent(account)
    agent.create_memo(title, content)
    return agent.send_all(to_email, email_title)


def send_calendar_event(
    title: str,
    start: str,
    to_email: str,
    end: Optional[str] = None,
    location: Optional[str] = None,
    notes: Optional[str] = None,
    all_day: bool = False,
    account: str = "126",
    email_title: str = "自动化推送",
) -> bool:
    """
    快捷发送日历日程

    Args:
        title: 日程标题
        start: 开始时间点，格式 "YYYY-MM-DD HH:mm"
        to_email: 收件人邮箱
        end: 结束时间点（可选）
        location: 地点（可选）
        notes: 备注（可选）
        all_day: 是否全天（默认 false）
        account: 邮箱账户（默认 "126"）
        email_title: 邮件标题（默认 "自动化推送"）

    Returns:
        成功返回 True，失败返回 False
    """
    agent = StarryForestAgent(account)
    agent.create_calendar_event(title, start, end, location, notes, all_day)
    return agent.send_all(to_email, email_title)


def send_focus_mode(
    name: str,
    on: bool,
    to_email: str,
    until: Optional[str] = None,
    account: str = "126",
    email_title: str = "自动化推送",
) -> bool:
    """
    快捷设置专注模式

    Args:
        name: 专注模式名称（"工作" / "个人" / "睡眠"）
        on: true 开启 / false 关闭
        to_email: 收件人邮箱
        until: 结束时间点（可选）
        account: 邮箱账户（默认 "126"）
        email_title: 邮件标题（默认 "自动化推送"）

    Returns:
        成功返回 True，失败返回 False
    """
    agent = StarryForestAgent(account)
    agent.focus_mode(name, on, until)
    return agent.send_all(to_email, email_title)


def send_music(
    play: bool,
    playlist: str,
    to_email: str,
    account: str = "126",
    email_title: str = "自动化推送",
) -> bool:
    """
    快捷发送音乐控制

    Args:
        play: true 播放 / false 暂停
        playlist: 播放列表（"每日推荐" / "私人漫游"）
        to_email: 收件人邮箱
        account: 邮箱账户（默认 "126"）
        email_title: 邮件标题（默认 "自动化推送"）

    Returns:
        成功返回 True，失败返回 False
    """
    agent = StarryForestAgent(account)
    agent.play_music(play, playlist)
    return agent.send_all(to_email, email_title)


def send_journal(
    title: str,
    date: str,
    content: str,
    to_email: str,
    account: str = "126",
    email_title: str = "自动化推送",
) -> bool:
    """
    快捷发送日记

    Args:
        title: 日记标题
        date: 日期，格式 "YYYY-MM-DD"
        content: 日记正文
        to_email: 收件人邮箱
        account: 邮箱账户（默认 "126"）
        email_title: 邮件标题（默认 "自动化推送"）

    Returns:
        成功返回 True，失败返回 False
    """
    agent = StarryForestAgent(account)
    agent.write_journal(title, date, content)
    return agent.send_all(to_email, email_title)


if __name__ == "__main__":
    # 示例：发送测试邮件
    agent = StarryForestAgent("126")

    # 添加多个动作
    agent.create_reminder(
        title="SKILL 测试提醒",
        due="2026-02-07 23:00",
        notes="通过 SKILL 模块发送",
        priority="中",
    )

    agent.create_memo(
        title="SKILL 测试备忘录",
        content="这是通过 StarryForestAgent SKILL 创建的备忘录。",
    )

    # 发送到 Hotmail
    agent.send_all(to_email="starryforest_ymxk@hotmail.com", title="SKILL 自动化测试")
