# -*- coding: utf-8 -*-
"""
月柱计算修复验证
根据节气计算月柱（非农历月）
"""

from lunar_python import Lunar, Solar
from datetime import datetime

def get_month_ganzhi_by_jieqi(year, month, day):
    """
    根据节气计算月柱（正确方法）
    
    节气月规则：
    - 寅月：立春 (2/4) - 惊蛰前
    - 卯月：惊蛰 (3/5) - 清明前
    - 辰月：清明 (4/5) - 立夏前
    - 巳月：立夏 (5/5) - 芒种前
    - ...
    """
    
    # 2026 年节气日期（公历）
    JIEQI_2026 = {
        '立春': (2, 4),
        '雨水': (2, 19),
        '惊蛰': (3, 5),
        '清明': (4, 5),
        '立夏': (5, 5),
        '芒种': (6, 5),
        '小暑': (7, 7),
        '立秋': (8, 7),
        '白露': (9, 7),
        '寒露': (10, 8),
        '立冬': (11, 7),
        '大雪': (12, 7),
    }
    
    # 月支（按节气）
    MONTH_ZHI = {
        2: '寅',  # 立春 - 惊蛰
        3: '卯',  # 惊蛰 - 清明
        4: '辰',  # 清明 - 立夏
        5: '巳',  # 立夏 - 芒种
        6: '午',  # 芒种 - 小暑
        7: '未',  # 小暑 - 立秋
        8: '申',  # 立秋 - 白露
        9: '酉',  # 白露 - 寒露
        10: '戌', # 寒露 - 立冬
        11: '亥', # 立冬 - 大雪
        12: '子', # 大雪 - 小寒
        1: '丑',  # 小寒 - 立春
    }
    
    # 年干（用于计算月干）
    # 甲己年起丙寅，乙庚年起戊寅，丙辛年起庚寅，丁壬年起壬寅，戊癸年起甲寅
    YEAR_GAN_START = {
        '甲': '丙', '己': '丙',
        '乙': '戊', '庚': '戊',
        '丙': '庚', '辛': '庚',
        '丁': '壬', '癸': '壬',
        '戊': '甲',
    }
    
    # 天干地支顺序
    GAN = '甲乙丙丁戊己庚辛壬癸'
    ZHI = '寅卯辰巳午未申酉戌亥子丑'
    
    date = datetime(year, month, day)
    
    # 判断属于哪个节气月
    if month == 1:
        # 1 月需要判断是否在小寒后
        if day >= 7:
            month_zhi = '丑'
        else:
            month_zhi = '子'  # 大雪 - 小寒
    elif month == 2:
        if day >= 4:  # 立春
            month_zhi = '寅'
        else:
            month_zhi = '丑'
    elif month == 3:
        if day >= 5:  # 惊蛰
            month_zhi = '卯'
        else:
            month_zhi = '寅'
    elif month == 4:
        if day >= 5:  # 清明
            month_zhi = '辰'
        else:
            month_zhi = '卯'
    elif month == 5:
        if day >= 5:  # 立夏
            month_zhi = '巳'
        else:
            month_zhi = '辰'
    elif month == 6:
        if day >= 5:  # 芒种
            month_zhi = '午'
        else:
            month_zhi = '巳'
    elif month == 7:
        if day >= 7:  # 小暑
            month_zhi = '未'
        else:
            month_zhi = '午'
    elif month == 8:
        if day >= 7:  # 立秋
            month_zhi = '申'
        else:
            month_zhi = '未'
    elif month == 9:
        if day >= 7:  # 白露
            month_zhi = '酉'
        else:
            month_zhi = '申'
    elif month == 10:
        if day >= 8:  # 寒露
            month_zhi = '戌'
        else:
            month_zhi = '酉'
    elif month == 11:
        if day >= 7:  # 立冬
            month_zhi = '亥'
        else:
            month_zhi = '戌'
    elif month == 12:
        if day >= 7:  # 大雪
            month_zhi = '子'
        else:
            month_zhi = '亥'
    
    # 获取年干
    lunar = Lunar.fromYmd(year, month, day)
    year_gz = lunar.getYearInGanZhi()
    year_gan = year_gz[0]
    
    # 根据年干计算月干
    start_gan = YEAR_GAN_START[year_gan]
    start_gan_idx = GAN.find(start_gan)
    month_zhi_idx = ZHI.find(month_zhi)
    
    # 月干 = 起始天干 + 月支索引
    month_gan_idx = (start_gan_idx + month_zhi_idx) % 10
    month_gan = GAN[month_gan_idx]
    
    return f"{month_gan}{month_zhi}"


# 测试
print("=" * 60)
print("月柱计算验证（按节气）")
print("=" * 60)

test_dates = [
    (2026, 4, 4),   # 清明前 → 卯月
    (2026, 4, 5),   # 清明 → 辰月
    (2026, 4, 12),  # 清明后 → 辰月
    (2026, 4, 13),  # 清明后 → 辰月
    (2026, 5, 4),   # 立夏前 → 辰月
    (2026, 5, 5),   # 立夏 → 巳月
]

for year, month, day in test_dates:
    lunar = Lunar.fromYmd(year, month, day)
    
    # lunar-python 的农历月干支
    lunar_month_gz = lunar.getMonthInGanZhi()
    
    # 按节气计算的月柱
    jieqi_month_gz = get_month_ganzhi_by_jieqi(year, month, day)
    
    print(f"{year}-{month:02d}-{day:02d}:")
    print(f"  lunar-python: {lunar_month_gz}月")
    print(f"  节气月柱：{jieqi_month_gz}月")
    print()

print("=" * 60)
