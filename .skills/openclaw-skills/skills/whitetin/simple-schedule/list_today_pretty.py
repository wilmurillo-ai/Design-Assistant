#!/usr/bin/env python3
from scripts.schedule_manager import ScheduleManager
from scripts.map_router import get_config
from datetime import datetime

config = get_config()
manager = ScheduleManager(config['data_path'])
today = manager.list_today()  # 默认自动过滤过期

today.sort(key=lambda x: x['datetime'])

if not today:
    print("🎉 今天没有未完成的行程啦，好好休息！")
else:
    now = datetime.now().astimezone()
    print(f"📅 今天剩余日程（共{len(today)}条）")
    print("=" * 30)
    for s in today:
        dt = datetime.fromisoformat(s['datetime'])
        time_str = dt.strftime('%H:%M')
        s_type = s.get('type', 'schedule')
        
        if s_type == 'ddl':
            # DDL 输出格式
            what = s['what']
            print(f"🔴 DDL {time_str} | {what}")
            print("-" * 30)
        else:
            # 行程输出格式
            where = s['where']
            what = s['what']
            duration = s.get('duration_minutes')
            remind_departure = s.get('remind_departure_at')
            
            first_line = f"🕒 {time_str} | {where} | {what}"
            print(first_line)
            
            second_parts = []
            if remind_departure:
                remind_dt = datetime.fromisoformat(remind_departure)
                second_parts.append(f"提醒出发：{remind_dt.strftime('%H:%M')}")
            if duration:
                second_parts.append(f"路程耗时：{duration}分钟")
            
            if second_parts:
                print(f"      {' | '.join(second_parts)}")
            
            print("-" * 30)
