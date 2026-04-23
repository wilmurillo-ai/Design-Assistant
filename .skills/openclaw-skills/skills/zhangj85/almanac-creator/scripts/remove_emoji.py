#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底清除所有 emoji
"""

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'

with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 替换所有互动引导中的 emoji
replacements = {
    '👍 点赞接好运 💬 评论区留下你的生肖 ➕ 关注每日更新': '点赞接好运  评论留生肖  关注每日更新',
    '👍点赞接好运 💬评论区留下你的生肖 ➕ 关注每日更新': '点赞接好运  评论留生肖  关注每日更新',
    '👍': '',
    '💬': '',
    '➕': '',
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("OK! All emoji removed")
