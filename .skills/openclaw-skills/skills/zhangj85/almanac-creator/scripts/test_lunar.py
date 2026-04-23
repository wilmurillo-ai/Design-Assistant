# -*- coding: utf-8 -*-
from lunar_python import Solar

print("2026 年 4 月 9-12 日 干支查询")
print("=" * 50)

for day in range(9, 13):
    s = Solar.fromYmd(2026, 4, day)
    l = s.getLunar()
    print(f"{day}日：{l.getYearInGanZhi()}年 {l.getMonthInGanZhi()}月 {l.getDayInGanZhi()}日")
    
print("=" * 50)
print("结论：4 月 9-12 日都应该是 壬辰月（清明后、立夏前）")
