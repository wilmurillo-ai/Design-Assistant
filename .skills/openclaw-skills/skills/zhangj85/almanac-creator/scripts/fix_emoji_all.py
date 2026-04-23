#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底修复互动引导 emoji 显示问题
"""

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'

with open(script_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # 查找所有包含 emoji 的互动引导文本
    if '点赞接好运' in line:
        # 替换为纯文字版本
        new_line = line.replace('👍 点赞接好运 💬 评论区留下你的生肖 ➕ 关注每日更新', 
                                '点赞接好运  评论留生肖  关注每日更新')
        new_line = new_line.replace('👍点赞接好运 💬评论区留下你的生肖 ➕ 关注每日更新',
                                    '点赞接好运  评论留生肖  关注每日更新')
        new_lines.append(new_line)
        if new_line != line:
            print(f"Fixed line {i+1}")
    else:
        new_lines.append(line)

with open(script_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("OK! All interaction text fixed")
