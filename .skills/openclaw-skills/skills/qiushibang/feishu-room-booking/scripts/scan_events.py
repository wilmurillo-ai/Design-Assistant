#!/usr/bin/env python3
"""
扫描用户日程，找出缺少会议室的日程并自动补订

用法:
  # 扫描未来24小时缺会议室的日程（dry-run 模式，不实际预订）
  python3 scan_events.py --user "ou_xxx" --hours 24 --dry-run

  # 扫描并自动补订（使用用户偏好）
  python3 scan_events.py --user "ou_xxx" --hours 24 --auto-book

  # 扫描指定日期范围
  python3 scan_events.py --user "ou_xxx" --start "2026-04-20T00:00:00+08:00" --end "2026-04-20T23:59:59+08:00" --auto-book

输出: JSON 格式，列出缺会议室的日程和建议方案
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PREFS_FILE = SCRIPT_DIR.parent / "references" / "user-preferences.json"
WAITLIST_FILE = SCRIPT_DIR.parent / "references" / "room-waitlist.json"


def load_json(filepath, default=None):
    if not filepath.exists():
        return default or {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user_preferences(user_id):
    """读取用户偏好"""
    prefs = load_json(PREFS_FILE, {"preferences": {}})
    return prefs.get("preferences", {}).get(user_id, {})


def parse_events_from_list_output(output):
    """从 feishu_calendar_event list 的输出中解析日程"""
    try:
        data = json.loads(output) if isinstance(output, str) else output
        return data.get("events", [])
    except:
        return []


def is_in_person_event(event):
    """判断是否是需要线下会议室的日程"""
    # 有 location 字段且不是线上
    location = event.get("location", {})
    if isinstance(location, dict):
        loc_str = location.get("name", "").lower()
        # 线上关键词
        online_keywords = ["飞书视频", "线上", "online", "zoom", "腾讯会议", "feishu"]
        if any(kw in loc_str for kw in online_keywords):
            return False
        if loc_str:
            return True

    # 有 vchat 的纯线上会议不需要会议室
    vchat = event.get("vchat", {})
    if vchat and vchat.get("vc_type") == "vc" and not location:
        # 纯线上视频会议，不需要会议室
        return False

    # 通过参会人判断：如果有 resource 类型参会人，说明已有会议室
    attendees = event.get("attendees", [])
    has_resource = any(a.get("type") == "resource" for a in attendees)

    # 通过标题判断
    summary = event.get("summary", "").lower()
    online_title_keywords = ["1:1", "1on1", "线上", "phone", "call"]
    if any(kw in summary for kw in online_title_keywords):
        return False

    if has_resource:
        return False  # 已有会议室

    # 默认认为需要会议室（线下会议通常是默认场景）
    return True


def needs_room(event):
    """判断日程是否需要补订会议室"""
    # 跳过全天事件
    start = event.get("start_time", "")
    if "T00:00:00" in start:
        return False, ""

    # 检查是否已有会议室
    attendees = event.get("attendees", [])
    has_resource = any(a.get("type") == "resource" for a in attendees)
    if has_resource:
        return False, "已有会议室"

    # 检查是否是线下会议
    if not is_in_person_event(event):
        return False, "纯线上会议"

    return True, "需要补订会议室"


def main():
    parser = argparse.ArgumentParser(description="扫描缺会议室的日程")
    parser.add_argument("--user", "-u", help="用户 open_id")
    parser.add_argument("--hours", type=int, default=24, help="扫描未来 N 小时")
    parser.add_argument("--start", "-s", help="开始时间")
    parser.add_argument("--end", "-e", help="结束时间")
    parser.add_argument("--dry-run", action="store_true", help="只扫描不预订")
    parser.add_argument("--auto-book", action="store_true", help="自动补订会议室")
    parser.add_argument("--output", "-o", choices=["json", "table"], default="table")

    args = parser.parse_args()

    # 计算时间范围
    now = datetime.now()
    if args.start:
        time_min = args.start
    else:
        time_min = (now + timedelta(hours=0)).strftime("%Y-%m-%dT%H:%M:%S+08:00")

    if args.end:
        time_max = args.end
    else:
        time_max = (now + timedelta(hours=args.hours)).strftime("%Y-%m-%dT%H:%M:%S+08:00")

    if not args.user:
        print("错误: 必须指定 --user")
        sys.exit(1)

    # 获取用户偏好
    prefs = get_user_preferences(args.user)
    default_building = prefs.get("default_building", "")
    capacity_gte = prefs.get("capacity_gte", 0)

    print(f"🔍 扫描日程: {time_min} ~ {time_max}")
    if default_building:
        print(f"🏠 默认楼栋: {default_building} (容量≥{capacity_gte})")
    print()

    # 注意：实际日程获取需要通过飞书 API 或工具
    # 这里输出扫描参数，由 agent 调用飞书工具获取日程后传入
    scan_config = {
        "user_id": args.user,
        "time_min": time_min,
        "time_max": time_max,
        "default_building": default_building,
        "capacity_gte": capacity_gte,
        "dry_run": args.dry_run,
        "auto_book": args.auto_book,
    }

    print("📋 扫描配置:")
    print(json.dumps(scan_config, ensure_ascii=False, indent=2))
    print()
    print("⚠️ 此脚本需要配合 agent 使用。agent 应:")
    print("  1. 调用 feishu_calendar_event list 获取日程")
    print("  2. 传入 --events-file 参数进行分析")
    print()
    print("完整用法: 先导出日程到 JSON，再传入分析")
    print(f"  feishu_calendar_event list → 保存到 /tmp/events.json")
    print(f"  python3 scan_events.py --user {args.user} --events-file /tmp/events.json --dry-run")

    # 支持 events-file 模式
    parser2 = argparse.ArgumentParser()
    parser2.add_argument("--events-file", help="日程 JSON 文件路径")
    args2 = parser2.parse_known_args()[0]

    if hasattr(args2, 'events_file') and args2.events_file:
        with open(args2.events_file, "r") as f:
            events = json.load(f)

        needs = []
        for event in events:
            need, reason = needs_room(event)
            if need:
                needs.append({
                    "event_id": event.get("event_id", ""),
                    "summary": event.get("summary", ""),
                    "start_time": event.get("start_time", ""),
                    "end_time": event.get("end_time", ""),
                    "organizer": event.get("event_organizer", {}).get("display_name", ""),
                    "reason": reason
                })

        if not needs:
            print("✅ 所有日程都已安排会议室（或为纯线上会议）")
            return

        print(f"找到 {len(needs)} 个需要补订会议室的日程:")
        for n in needs:
            print(f"  📌 {n['summary']}")
            print(f"     时间: {n['start_time']} ~ {n['end_time']}")
            print(f"     组织者: {n['organizer']}")

        if args.output == "json":
            print(json.dumps(needs, ensure_ascii=False, indent=2))

    # 输出 JSON 配置供 agent 使用
    if args.output == "json":
        print(json.dumps(scan_config, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
