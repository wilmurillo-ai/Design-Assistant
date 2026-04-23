#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复互动引导 emoji 显示问题
"""

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复第 2 页互动引导
content = content.replace(
    'interaction_text = "👍 点赞接好运 💬 评论区留下你的生肖 ➕ 关注每日更新"',
    'interaction_text = "点赞接好运  评论留生肖  关注每日更新"  # 【V3.0.4 修复】移除 emoji，避免显示问题'
)

# 修复第 3 页互动引导（如果有）
content = content.replace(
    'interaction_text = "👍点赞接好运 💬评论区留下你的生肖 ➕ 关注每日更新"',
    'interaction_text = "点赞接好运  评论留生肖  关注每日更新"  # 【V3.0.4 修复】移除 emoji'
)

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("OK! Fixed interaction text (removed emoji)")
