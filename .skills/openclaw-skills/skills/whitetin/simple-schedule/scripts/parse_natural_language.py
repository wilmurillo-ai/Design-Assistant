#!/usr/bin/env python3
"""
从自然语言文本解析日程信息：时间、地点、事项、出发地
依赖 dateparser 库解析中文时间
"""

import re
import dateparser
from datetime import datetime, timedelta
import uuid
import json
import os
from typing import Optional, Dict, Tuple

class NaturalLanguageParser:
    def __init__(self):
        # 常见的时间关键词
        self.time_patterns = [
            r'(今天|明天|后天|大后天|周一|周二|周三|周四|周五|周六|周日|下周一|下周二|下周三|下周四|下周五|下周六|下周日|上午|下午|早上|晚上|凌晨|中午)\s*(\d+)点?(半)?',
            r'(?P<month>\d+)月(?P<day>\d+)日\s*(?P<hour>\d+)点',
        ]
        # 地点关键词：终止字符包括常见动词，避免把后面事项也吃了
        self.where_patterns = [
            r'去\s*(?P<where>[^去做，。看开参加]+)\s*(做|开|参加|看)',
            r'到\s*(?P<where>[^去做，。看开参加]+)\s*(做|开|参加|看)',
            r'在\s*(?P<where>[^去做，。看开参加]+)\s*(做|开|参加|看)',
        ]
        # 事项关键词
        self.what_patterns = [
            r'(做|开|参加|见)\s*(?P<what>[^，。]+)$',
            r'(开会|飞机|火车|约会|面试)$',
        ]

    def parse(self, text: str, timezone: str = "Asia/Shanghai") -> Dict:
        """
        解析自然语言文本，返回解析后的日程信息
        """
        # 第一步：判断是不是DDL截止日期
        is_ddl = any(keyword in text for keyword in ['截止', 'ddl', 'DDL', '之前要完成', ' deadline', '截止日期'])
        
        # 第二步：解析时间
        parsed_time = self._parse_time(text, timezone)
        if not parsed_time:
            return {
                "success": False,
                "error": "无法识别时间，请说清楚什么时候"
            }
        
        # 第三步：DDL不需要地点，纯会议没有地点也允许
        where = self._parse_where(text)
        # 如果没找到地点，但也不是DDL，允许，地点设为None不影响，用户只是开会没说地点也能存
        # 只有完全啥也解析不出来才报错
        
        # 第四步：解析事项
        what = self._parse_what(text)
        if not what:
            what = "待办"
        
        # 第五步：解析出发地（如果提到了）
        from_address = self._parse_from(text)
        
        now = datetime.now().astimezone().isoformat()
        
        from datetime import timedelta
        result = {
            "success": True,
            "data": {
                "id": str(uuid.uuid4()),
                "type": "ddl" if is_ddl else "schedule",
                "datetime": parsed_time.isoformat(),
                "where": where.strip() if where else None,
                "what": what.strip(),
                "from_address": from_address.strip() if from_address else None,
                "duration_minutes": None,
                "created_at": now,
                "updated_at": now,
                "remind_departure_at": None,
                "remind_arrive_at": parsed_time.isoformat(),
                "remind_ddl_1day_before": None,
                "remind_ddl_1hour_before": None
            }
        }
        
        # DDL添加提前提醒
        if is_ddl:
            result["data"]["remind_ddl_1day_before"] = (parsed_time - timedelta(days=1)).isoformat()
            result["data"]["remind_ddl_1hour_before"] = (parsed_time - timedelta(hours=1)).isoformat()
        
        # 行程才需要出发提醒，后面计算
        return result
    
    def _parse_time(self, text: str, timezone: str) -> Optional[datetime]:
        """使用 dateparser 解析中文时间，预处理一些dateparser不支持的格式"""
        settings = {
            'TIMEZONE': timezone,
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DATES_FROM': 'future'
        }
        
        # 预处理：替换 "X点半" 为 "X点30分"，帮助dateparser识别
        processed_text = text
        processed_text = re.sub(r'(\d+)点半', r'\1点30分', processed_text)
        processed_text = re.sub(r'(\d+):30', r'\1点30分', processed_text)
        
        # 预处理：如果只给了时间没说今天，默认补今天，帮助dateparser识别
        has_explicit_date = any(word in processed_text for word in [
            '今天', '明天', '后天', '周一', '周二', '周三', '周四', '周五', '周六', '周日',
            '月', '日', '号'
        ])
        if not has_explicit_date and re.search(r'\d+点', processed_text):
            processed_text = '今天 ' + processed_text
        
        # 尝试解析
        dt = dateparser.parse(processed_text, settings=settings)
        
        # 如果还是失败，尝试手工解析最简单的情况
        if dt is None:
            # 手工匹配 "今天 X点半" "今天下午 X点30" "X点半" 这种
            # 把period放前面，允许它在任何位置匹配到上午/下午
            hour_match = re.search(r'(上午|下午|早上|晚上|凌晨|中午)', processed_text)
            period = hour_match.group(1) if hour_match else None
            num_match = re.search(r'(\d+)(点|点30分|半)', processed_text)
            if num_match:
                hour = int(num_match.group(1))
                # 检查整个文本中有没有半或者30
                minute = 30 if ('半' in processed_text or '30' in processed_text) else 0
                
                # 下午/晚上 加12小时
                if period in ['下午', '晚上'] and hour < 12:
                    hour += 12
                
                now = datetime.now().astimezone()
                dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # 如果解析出来的时间已经过去了，而且用户没有明确说是今天，就加一天到明天
                has_explicit_today = '今天' in processed_text
                if dt < now and not has_explicit_today:
                    dt = dt + timedelta(days=1)
                
                return dt
        
        return dt
    
    def _parse_where(self, text: str) -> Optional[str]:
        """尝试提取地点"""
        for pattern in self.where_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group('where').strip()
        # 简单 fallback 1：找"去"后面第一个短语
        if '去' in text:
            parts = text.split('去')
            if len(parts) > 1:
                after_go = parts[1].strip()
                # 找到第一个分隔符
                for sep in ['做', '开', '参加', '了', '，', '。', ' ']:
                    if sep in after_go:
                        after_go = after_go.split(sep)[0]
                return after_go.strip()
        # 简单 fallback 2："回家"/"上班"直接提取，匹配"XX回家"
        if text.endswith('回家'):
            return '家'
        if text.endswith('上班'):
            return '公司'
        return None
    
    def _parse_what(self, text: str) -> Optional[str]:
        """尝试提取事项"""
        for pattern in self.what_patterns:
            match = re.search(pattern, text)
            if match:
                if 'what' in match.groupdict():
                    return match.group('what')
                else:
                    return match.group(0)
        # fallback：最后一个短语
        parts = re.split(r'[，。]', text)
        for part in reversed(parts):
            if part.strip():
                return part.strip()
        return None
    
    def _parse_from(self, text: str) -> Optional[str]:
        """提取出发地"""
        if '从' in text and '到' in text:
            parts = text.split('从')[1].split('到')[0]
            return parts.strip()
        return None

if __name__ == "__main__":
    import sys
    # 修复Windows中文输出乱码：强制stdout用utf-8
    if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
        sys.stdout.reconfigure(encoding='utf-8')
    parser = NaturalLanguageParser()
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = parser.parse(text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
