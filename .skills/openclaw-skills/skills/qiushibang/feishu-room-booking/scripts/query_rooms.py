#!/usr/bin/env python3
"""
飞书会议室批量忙闲查询工具

用法:
  python3 query_rooms.py --building "丽金" --start "2026-04-20T14:00:00+08:00" --end "2026-04-20T15:00:00+08:00"
  python3 query_rooms.py --building "F4" --start "2026-04-20T09:00:00+08:00" --end "2026-04-20T18:00:00+08:00" --capacity-gte 8
  python3 query_rooms.py --list-buildings
  python3 query_rooms.py --list-rooms --building "丽金"

输出: JSON 格式，包含每个会议室的名称、room_id、容量、忙闲状态
"""

import argparse
import json
import subprocess
import sys
import os
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
MAPPING_FILE = SCRIPT_DIR.parent / "references" / "room-mapping.json"


def load_mapping():
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def match_building(data, keyword):
    """根据关键词匹配楼栋，支持模糊匹配 name 和 alias"""
    keyword = keyword.lower().strip()
    matched = []
    for building in data.get("buildings", []):
        # 检查名称
        if keyword in building["name"].lower():
            matched.append(building)
            continue
        # 检查别名
        for alias in building.get("alias", []):
            if keyword in alias.lower():
                matched.append(building)
                break
    return matched


def query_freebusy(room_id, time_min, time_max):
    """查询单个会议室的忙闲状态"""
    cmd = [
        "lark-cli", "calendar", "freebusys", "list", "--as", "bot",
        "--data", json.dumps({
            "room_id": room_id,
            "time_min": time_min,
            "time_max": time_max
        })
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return {"status": "error", "busy_periods": []}
        data = json.loads(result.stdout)
        fb_list = data.get("data", {}).get("freebusy_list", [])
        return {
            "status": "busy" if fb_list else "free",
            "busy_periods": fb_list
        }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return {"status": "error", "busy_periods": []}


def compute_free_slots(busy_periods, time_min, time_max):
    """从忙碌时段计算空闲时段"""
    if not busy_periods:
        return [{"start": time_min, "end": time_max, "duration_min": 60}]

    # 解析时间
    def parse_time(t):
        # ISO 8601 → minutes from midnight (简化处理，仅用于时长大概计算)
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})", t)
        if m:
            h, mi = int(m.group(4)), int(m.group(5))
            return h * 60 + mi
        return 0

    gaps = []
    sorted_busy = sorted(busy_periods, key=lambda x: x["start_time"])
    last_end = time_min

    for period in sorted_busy:
        if period["start_time"] > last_end:
            start_min = parse_time(last_end)
            end_min = parse_time(period["start_time"])
            duration = end_min - start_min
            gaps.append({
                "start": last_end,
                "end": period["start_time"],
                "duration_min": duration
            })
        last_end = max(last_end, period["end_time"])

    if last_end < time_max:
        start_min = parse_time(last_end)
        end_min = parse_time(time_max)
        duration = end_min - start_min
        gaps.append({
            "start": last_end,
            "end": time_max,
            "duration_min": duration
        })

    return sorted(gaps, key=lambda x: -x["duration_min"])


def main():
    parser = argparse.ArgumentParser(description="飞书会议室忙闲查询")
    parser.add_argument("--building", "-b", help="楼栋关键词（模糊匹配）")
    parser.add_argument("--start", "-s", help="查询开始时间 (ISO 8601)")
    parser.add_argument("--end", "-e", help="查询结束时间 (ISO 8601)")
    parser.add_argument("--capacity-gte", "-c", type=int, default=0, help="最小容量筛选")
    parser.add_argument("--capacity-lte", type=int, default=999, help="最大容量筛选")
    parser.add_argument("--list-buildings", action="store_true", help="列出所有楼栋")
    parser.add_argument("--list-rooms", action="store_true", help="列出指定楼栋的会议室")
    parser.add_argument("--output", "-o", choices=["json", "table"], default="json", help="输出格式")

    args = parser.parse_args()
    data = load_mapping()

    # 列出楼栋
    if args.list_buildings:
        for b in data.get("buildings", []):
            rooms_count = len(b.get("rooms", []))
            aliases = ", ".join(b.get("alias", []))
            print(f"📍 {b['name']}  ({rooms_count}个会议室)  别名: {aliases}")
        return

    # 列出会议室
    if args.list_rooms:
        if not args.building:
            print("错误: --list-rooms 需要同时指定 --building")
            sys.exit(1)
        matched = match_building(data, args.building)
        if not matched:
            print(f"未找到匹配的楼栋: {args.building}")
            sys.exit(1)
        for b in matched:
            print(f"\n🏢 {b['name']}:")
            for r in b.get("rooms", []):
                print(f"  {r['name']}  容量:{r['capacity']}  room_id:{r['room_id']}")
        return

    # 查询忙闲
    if not args.building:
        print("错误: 必须指定 --building")
        sys.exit(1)

    matched = match_building(data, args.building)
    if not matched:
        print(f"未找到匹配的楼栋: {args.building}")
        # 列出可用楼栋
        print("\n可用楼栋:")
        for b in data.get("buildings", []):
            print(f"  - {b['name']}")
        sys.exit(1)

    # 收集所有会议室
    all_rooms = []
    for b in matched:
        for r in b.get("rooms", []):
            cap = r.get("capacity", 0)
            if args.capacity_gte <= cap <= args.capacity_lte:
                all_rooms.append({
                    "name": r["name"],
                    "room_id": r["room_id"],
                    "capacity": cap,
                    "building": b["name"]
                })

    if not all_rooms:
        print(f"没有符合条件的会议室 (容量 >= {args.capacity_gte}, <= {args.capacity_lte})")
        sys.exit(0)

    # 逐个查询
    results = []
    for room in all_rooms:
        fb = query_freebusy(room["room_id"], args.start, args.end)
        result = {
            "name": room["name"],
            "room_id": room["room_id"],
            "capacity": room["capacity"],
            "building": room["building"],
            "status": fb["status"],
        }
        if fb["status"] == "free":
            result["free_slots"] = [{"start": args.start, "end": args.end, "duration_min": 60}]
        elif fb["status"] == "busy":
            result["free_slots"] = compute_free_slots(fb["busy_periods"], args.start, args.end)
        else:
            result["free_slots"] = []
        results.append(result)

    # 排序：空闲的在前，按容量降序
    free_rooms = [r for r in results if r["status"] == "free"]
    busy_rooms = [r for r in results if r["status"] != "free"]
    free_rooms.sort(key=lambda x: -x["capacity"])
    busy_rooms.sort(key=lambda x: x["name"])
    results = free_rooms + busy_rooms

    if args.output == "table":
        # 简洁表格输出
        print(f"\n{'会议室':<25} {'容量':>4}  {'状态':<6}  空闲时段")
        print("-" * 70)
        for r in results:
            status_icon = "🟢" if r["status"] == "free" else ("🔴" if r["status"] == "busy" else "⚠️")
            slots_str = ", ".join([f"{s['start'][11:16]}-{s['end'][11:16]}" for s in r["free_slots"]]) if r["free_slots"] else "-"
            print(f"{status_icon} {r['name']:<22} {r['capacity']:>4}人  {r['status']:<6}  {slots_str}")
        free_count = len(free_rooms)
        total = len(results)
        print(f"\n共 {total} 个会议室，{free_count} 个空闲")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
