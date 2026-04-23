# -*- coding: utf-8 -*-
"""
验证 lunar-python 的月柱计算逻辑
确认是农历月还是节气月
"""

from lunar_python import Solar, Lunar

# 测试边界日期：清明前后
test_dates = [
    (2026, 4, 4),   # 清明前一天（应为卯月）
    (2026, 4, 5),   # 清明当天（应为辰月）
    (2026, 4, 12),  # 清明后 7 天（应为辰月）
    (2026, 5, 4),   # 立夏前一天（应为辰月）
    (2026, 5, 5),   # 立夏当天（应为巳月）
]

print("=" * 70)
print("月柱计算验证 - 农历月 vs 节气月")
print("=" * 70)

for year, month, day in test_dates:
    solar = Solar.fromYmd(year, month, day)
    lunar = solar.getLunar()
    
    month_gz = lunar.getMonthInGanZhi()
    lunar_month = lunar.getMonthInChinese()
    jieqi = lunar.getJieQi()
    
    print(f"{year}-{month:02d}-{day:02d}:")
    print(f"  农历：{lunar_month}月")
    print(f"  月柱：{month_gz}")
    print(f"  节气：{jieqi if jieqi else '无'}")
    print()

print("=" * 70)
print("结论:")
print("1. 如果清明当天（4/5）显示'壬辰月'，说明 lunar-python 使用节气月 ✅")
print("2. 如果清明当天显示'癸卯月'，说明 lunar-python 使用农历月 ❌")
print("=" * 70)
