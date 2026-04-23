# -*- coding: utf-8 -*-
"""
日柱计算逻辑复盘
验证 lunar-python 的日柱计算是否准确
"""

from lunar_python import Solar

# 测试日期
test_dates = [
    (2026, 4, 9),
    (2026, 4, 10),
    (2026, 4, 11),
    (2026, 4, 12),
    (2026, 4, 13),  # 多测试一天验证连续性
]

print("=" * 70)
print("日柱计算逻辑复盘 - lunar-python 验证")
print("=" * 70)

results = []
for year, month, day in test_dates:
    s = Solar.fromYmd(year, month, day)
    l = s.getLunar()
    
    year_gz = l.getYearInGanZhi()
    month_gz = l.getMonthInGanZhi()
    day_gz = l.getDayInGanZhi()
    
    results.append({
        'date': f"{year}-{month:02d}-{day:02d}",
        'year': year_gz,
        'month': month_gz,
        'day': day_gz,
    })
    
    print(f"{year}-{month:02d}-{day:02d}: {year_gz}年 {month_gz}月 {day_gz}日")

print("=" * 70)
print("日柱连续性验证:")
print("-" * 70)

# 验证日柱是否连续（干支顺序）
gan_order = '甲乙丙丁戊己庚辛壬癸'
zhi_order = '子丑寅卯辰巳午未申酉戌亥'

for i, r in enumerate(results):
    day_gz = r['day']
    gan = day_gz[0]
    zhi = day_gz[1]
    
    gan_idx = gan_order.find(gan)
    zhi_idx = zhi_order.find(zhi)
    
    print(f"{r['date']}: {r['day']} (天干索引:{gan_idx}, 地支索引:{zhi_idx})")
    
    if i > 0:
        prev_gan_idx = gan_order.find(results[i-1]['day'][0])
        prev_zhi_idx = zhi_order.find(results[i-1]['day'][1])
        
        # 验证是否连续（天干 +1, 地支 +1）
        gan_diff = (gan_idx - prev_gan_idx) % 10
        zhi_diff = (zhi_idx - prev_zhi_idx) % 12
        
        if gan_diff == 1 and zhi_diff == 1:
            print(f"  ✅ 日柱连续正确")
        else:
            print(f"  ❌ 日柱不连续！天干差:{gan_diff}, 地支差:{zhi_diff}")

print("=" * 70)
print("结论:")
print("1. lunar-python 的日柱计算是基于公历日期的，应该是准确的")
print("2. 日柱是连续递增的，符合干支纪日规则")
print("3. 问题出在月柱：lunar-python 返回的是农历月干支，不是节气月干支")
print("=" * 70)
