#!/usr/bin/env python3
"""Crisis Detector - 危机检测模块"""

HIGH_RISK = [
    "自杀", "自残", "不想活了", "死了", "活着没意思", "活着好累",
    "割腕", "跳楼", "活够了", "抑郁", "绝望", "轻生", "自尽",
    "了结", "活不下去", "没意思", "不想活", "不如死了", "死了算了",
    "一了百了", "hurt myself", "kill myself"
]

MEDIUM_RISK = [
    "焦虑", "恐惧", "害怕", "担心", "失眠", "崩溃", "无力", "无助",
    "很绝望", "好绝望", "难受", "崩溃", "很压抑", "压抑", "喘不过气",
    "好累", "太累了", "撑不住了", "熬不住了", "走不出来", "好无助"
]

def is_crisis(text):
    """检测文本是否包含危机信号"""
    text_lower = text.lower()
    for k in HIGH_RISK:
        if k in text_lower:
            return True, "high"
    for k in MEDIUM_RISK:
        if k in text_lower:
            return True, "medium"
    return False, "safe"
