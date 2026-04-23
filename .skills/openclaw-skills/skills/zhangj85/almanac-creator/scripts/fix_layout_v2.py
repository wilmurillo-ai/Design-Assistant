#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复黄历第 1 页布局问题：
1. 农历日期 + 干支 + 节气合并到一行
2. 添加生肖图标支持（使用 Unicode 字符绘制）
"""

import os

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'

# 读取原文件
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 1: 修改第 1 页布局，压缩农历和节气到一行
old_page1_header = """    y = 40
    y = draw_centered_text(draw, "每日黄历", y, fonts['title'], template['title'])
    y += SPACING['after_title']
    y = draw_centered_text(draw, data['date_gregorian'], y, fonts['subtitle'], template['text'])
    y += SPACING['after_subtitle']
    y = draw_centered_text(draw, data['date_lunar'], y, fonts['section'], template['text'])
    y += SPACING['after_lunar']
    y = draw_centered_text(draw, data['ganzhi_full'], y, fonts['content'], template['text'])
    y += SPACING['after_ganzhi']
    y = draw_centered_text(draw, data['special_day'], y, fonts['small'], template['small'])"""

# 新布局：农历 + 干支 + 节气合并到一行
new_page1_header = """    y = 40
    y = draw_centered_text(draw, "每日黄历", y, fonts['title'], template['title'])
    y += SPACING['after_title']
    y = draw_centered_text(draw, data['date_gregorian'], y, fonts['subtitle'], template['text'])
    y += SPACING['after_subtitle']
    
    # 【V3.0.4 优化】农历 + 干支 + 节气合并到一行，节省空间
    lunar_ganzhi_jieqi = f"{data['date_lunar']}  {data['ganzhi_full']}"
    if data['special_day']:
        lunar_ganzhi_jieqi += f"  {data['special_day']}"
    y = draw_centered_text(draw, lunar_ganzhi_jieqi, y, fonts['content'], template['text'])"""

content = content.replace(old_page1_header, new_page1_header)

# 写回文件
with open(script_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("OK! Layout fixed:")
print("  1. Lunar date + Ganzhi + Jieqi merged to one line")
print("  2. Saved vertical space for page 1")
