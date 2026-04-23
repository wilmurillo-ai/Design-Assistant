# -*- coding: utf-8 -*-
from lunar_python import Solar

dates = [
    (2026, 4, 9),
    (2026, 4, 10),
    (2026, 4, 11),
    (2026, 4, 12),
]

print("2026 年 4 月 9-12 日 干支查询")
print("=" * 60)

for year, month, day in dates:
    s = Solar.fromYmd(year, month, day)
    l = s.getLunar()
    yg = l.getYearInGanZhi()
    mg = l.getMonthInGanZhi()
    dg = l.getDayInGanZhi()
    lunar_month = l.getMonthInChinese()
    lunar_day = l.getDayInChinese()
    jieqi = l.getJieQi()
    
    print(f"公历：{year}-{month:02d}-{day:02d}")
    print(f"农历：{yg}年 {lunar_month}月{lunar_day}")
    print(f"干支：{yg}年 {mg}月 {dg}日")
    print(f"节气：{jieqi if jieqi else '无'}")
    print("-" * 60)
