# -*- coding: utf-8 -*-
from lunar_python import Solar

dates = [
    (2026, 4, 9),
    (2026, 4, 10),
    (2026, 4, 11),
    (2026, 4, 12),
]

results = []

for year, month, day in dates:
    s = Solar.fromYmd(year, month, day)
    l = s.getLunar()
    
    result = {
        'date': f"{year}-{month:02d}-{day:02d}",
        'year_gz': l.getYearInGanZhi(),
        'month_gz': l.getMonthInGanZhi(),
        'day_gz': l.getDayInGanZhi(),
        'lunar_month': l.getMonthInChinese(),
        'lunar_day': l.getDayInChinese(),
    }
    results.append(result)

# Write to file
with open('lunar_verify.txt', 'w', encoding='utf-8') as f:
    f.write("2026 年 4 月 9-12 日 干支验证报告\n")
    f.write("=" * 60 + "\n\n")
    
    for r in results:
        f.write(f"公历：{r['date']}\n")
        f.write(f"农历：{r['lunar_month']}月{r['lunar_day']}\n")
        f.write(f"干支：{r['year_gz']}年 {r['month_gz']}月 {r['day_gz']}日\n")
        f.write("\n")
    
    f.write("=" * 60 + "\n")
    f.write("结论：4 月 9-12 日都应该是 壬辰月（清明后、立夏前）\n")
    f.write("清明：4 月 5 日\n")
    f.write("立夏：5 月 5 日\n")
    f.write("4 月 9-12 日在清明和立夏之间，属于辰月\n")

print("验证报告已生成：lunar_verify.txt")
print("\n快速查看：")
for r in results:
    print(f"{r['date']}: {r['month_gz']}月 {r['day_gz']}日")
