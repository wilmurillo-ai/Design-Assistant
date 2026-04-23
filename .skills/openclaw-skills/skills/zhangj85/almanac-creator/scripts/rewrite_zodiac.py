#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底重写生肖绘制代码
"""

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到生肖绘制部分并完全替换
old_code_start = content.find("    for zodiac in data['zodiac_red']:")
old_code_end = content.find("    y = draw_separator(draw, y + 18, template['separator'])")

if old_code_start > 0 and old_code_end > old_code_start:
    # 提取旧代码之前的部分
    before = content[:old_code_start]
    
    # 提取旧代码之后的部分
    after = content[old_code_end:]
    
    # 新的生肖绘制代码
    new_code = '''    # 【V3.0.5 修复】生肖运势使用 Unicode 符号
    for zodiac in data['zodiac_red']:
        # 直接使用完整文字，不做分割
        y = draw_centered_text(draw, "✅ " + zodiac, y, fonts['content'], template['text'])
        y += SPACING['after_zodiac_item']
    
    y += 8
    y = draw_centered_text(draw, "今日需注意生肖", y, fonts['content'], template['section'])
    y += SPACING['after_zodiac_item']
    
    for zodiac in data['zodiac_black']:
        # 直接使用完整文字，不做分割
        y = draw_centered_text(draw, "⚠️ " + zodiac, y, fonts['content'], template['text'])
        y += SPACING['after_zodiac_item']
    
'''
    
    # 组合新内容
    new_content = before + new_code + after
    
    # 写回文件
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("OK! Zodiac drawing code completely rewritten")
else:
    print(f"ERROR: Could not find code block (start={old_code_start}, end={old_code_end})")
