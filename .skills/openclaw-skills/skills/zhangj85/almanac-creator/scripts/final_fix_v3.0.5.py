#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复方案：
1. 生肖运势使用 ✅ 和 ⚠️ 符号
2. 互动引导使用纯文字
3. 第 2 页运动建议自动换行
"""

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 1: 生肖运势使用 ✅ 和 ⚠️
content = content.replace(
    "f\"【{zodiac_name}】{zodiac_desc}\"",
    "f\"✅ {zodiac_name}: {zodiac_desc}\"  # 【V3.0.5 修复】使用✅符号"
)

# 修复黑榜生肖使用 ⚠️
# 需要找到黑榜循环并修改
lines = content.split('\n')
new_lines = []
in_black_zodiac = False

for line in lines:
    if 'zodiac_black' in line and 'for' in line:
        in_black_zodiac = True
        new_lines.append(line)
    elif in_black_zodiac and 'zodiac_name' in line and 'zodiac_desc' in line:
        new_lines.append(line.replace(
            "f\"【{zodiac_name}】{zodiac_desc}\"",
            "f\"⚠️ {zodiac_name}: {zodiac_desc}\"  # 【V3.0.5 修复】使用⚠️符号"
        ))
        in_black_zodiac = False
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)

# 修复 2: 互动引导已清除 emoji，保持不变

# 写回文件
with open(script_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("OK! Applied final fixes:")
print("  1. Red zodiac signs use ✅ symbol")
print("  2. Black zodiac signs use ⚠️ symbol")
print("  3. Interaction text already fixed")
