# -*- coding: utf-8 -*-
"""
日柱计算逻辑复盘 - 简化版
"""

from lunar_python import Solar

dates = [
    (2026, 4, 9),
    (2026, 4, 10),
    (2026, 4, 11),
    (2026, 4, 12),
]

print("=" * 60)
print("日柱计算逻辑复盘")
print("=" * 60)

for year, month, day in dates:
    s = Solar.fromYmd(year, month, day)
    l = s.getLunar()
    
    print(f"{year}-{month:02d}-{day:02d}: {l.getYearInGanZhi()}年 {l.getMonthInGanZhi()}月 {l.getDayInGanZhi()}日")

print("=" * 60)
print("结论:")
print("1. 日柱计算：lunar-python 基于公历日期计算，结果准确")
print("2. 月柱问题：lunar-python 返回农历月干支，不是节气月干支")
print("3. 4 月 9-12 日应为壬辰月（清明后），但 lunar 返回农历二月干支")
print("=" * 60)
