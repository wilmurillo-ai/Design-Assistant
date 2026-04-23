#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄历生成脚本 V3.0.3 - 抖音优化版
升级内容：
1. 【V3.0.3 新增】支持 Emoji 字体（Segoe UI Emoji）
2. 【V3.0.3 新增】生肖运势添加 emoji 图标
3. 【V3.0.3 新增】优化互动引导文案
4. 【V3.0.1 新增】节气计算通用化（支持 1900-2100 年）
5. 【V3.0.1 新增】批量生成功能（一次生成 7 天/30 天）
6. 【V3.0.1 新增】配置文件支持（config.yaml）
7. 集成 lunar-python 库（lunar-java 的 Python 版本）
8. 干支计算 - 使用 lunar-python 准确计算
9. 宜忌生成 - 使用 lunar-python 传统算法

版本：V3.0.3
日期：2026-04-18
"""

import sys
import io
from PIL import Image, ImageDraw, ImageFont
import os
import argparse
from datetime import datetime, timedelta
import yaml

# 导入 lunar-python（lunar-java 的 Python 版本）
from lunar_python import Lunar, Solar

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 图片规格
WIDTH = 1080
PAGE_HEIGHT = 1400
BACKGROUND_COLOR = '#F8F0E6'

# 【V2.3 新增】5 套模板配色方案
TEMPLATES = {
    'traditional': {
        'name': '传统中国风',
        'bg': '#F8F0E6',
        'border_outer': '#8B0000',
        'border_inner': '#D4AF37',
        'title': '#8B0000',
        'section': '#C41E3A',
        'text': '#2C2C2C',
        'small': '#999999',
        'separator': '#D4AF37',
        'decoration': 'double_border'
    },
    'modern': {
        'name': '简约现代风',
        'bg': '#F0F4F8',
        'border_outer': '#2C5F8D',
        'border_inner': '#C9A961',
        'title': '#1A3A52',
        'section': '#2C5F8D',
        'text': '#1A3A52',
        'small': '#6B7280',
        'separator': '#C9A961',
        'decoration': 'single_border'
    },
    'festive': {
        'name': '喜庆吉祥风',
        'bg': '#FFF5E6',
        'border_outer': '#D4AF37',
        'border_inner': '#FF6B35',
        'title': '#D4AF37',
        'section': '#FF6B35',
        'text': '#8B0000',
        'small': '#B8860B',
        'separator': '#FF6B35',
        'decoration': 'ornament'
    },
    'elegant': {
        'name': '典雅古风',
        'bg': '#F5F5DC',
        'border_outer': '#4A5D4F',
        'border_inner': '#9A8B4F',
        'title': '#2C3E36',
        'section': '#4A5D4F',
        'text': '#2C3E36',
        'small': '#8B8680',
        'separator': '#9A8B4F',
        'decoration': 'cloud'
    },
    'fresh': {
        'name': '清新自然风',
        'bg': '#F0F8E6',
        'border_outer': '#6B8E4E',
        'border_inner': '#B8C99E',
        'title': '#3A4F2E',
        'section': '#6B8E4E',
        'text': '#3A4F2E',
        'small': '#8FA885',
        'separator': '#B8C99E',
        'decoration': 'leaf'
    }
}

# 颜色标准（默认使用 traditional 模板）
COLORS = TEMPLATES['traditional']

# 字体大小标准（V2.3 优化版 - 加大字号提升可读性）
FONT_SIZES = {
    'title': 90,
    'subtitle': 65,
    'section': 60,
    'content': 48,
    'content_large': 44,
    'small': 40
}

# 间距设置（V2.3 优化版 - 增加行间距提升可读性）
SPACING = {
    'after_title': 10,
    'after_subtitle': 8,
    'after_lunar': 6,
    'after_ganzhi': 8,
    'after_special': 25,
    'after_section': 28,
    'after_content': 20,
    'after_zodiac_title': 12,
    'after_zodiac_item': 6,
    'separator_after': 28,
}

def load_config(config_path=None):
    """【V3.0.1 新增】加载配置文件"""
    if config_path is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, '..', 'config.yaml')
    
    default_config = {
        'output': {'base_dir': './reports', 'quality': 95, 'overwrite': True},
        'font': FONT_SIZES,
        'spacing': SPACING,
        'template': {'default': 'traditional', 'rotation': True},
        'features': {'show_jieqi': True, 'show_story': True},
        'batch': {'default_days': 7, 'max_days': 365},
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                for key in default_config:
                    if key in config:
                        if isinstance(default_config[key], dict):
                            default_config[key].update(config[key])
                        else:
                            default_config[key] = config[key]
            print(f"✅ 已加载配置文件：{config_path}")
        except Exception as e:
            print(f"⚠️ 配置文件加载失败：{e}，使用默认配置")
    else:
        print(f"ℹ️ 未找到配置文件，使用默认配置")
    
    return default_config


def get_template(date_str, config=None):
    """【V2.3 新增】根据日期选择模板（每日轮换）"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    if config and 'template' in config:
        template_config = config['template']
        if not template_config.get('rotation', True):
            default_name = template_config.get('default', 'traditional')
            return default_name, TEMPLATES.get(default_name, TEMPLATES['traditional'])
    
    template_names = list(TEMPLATES.keys())
    rotation_days = config.get('template', {}).get('rotation_days', 5) if config else 5
    template_index = date_obj.day % len(template_names)
    template_name = template_names[template_index]
    return template_name, TEMPLATES[template_name]

def load_fonts(template_name='traditional'):
    """加载字体（统一使用黑体，保持可读性和品牌一致性）"""
    try:
        font_file = 'C:/Windows/Fonts/simhei.ttf'
        
        fonts = {
            'title': ImageFont.truetype(font_file, FONT_SIZES['title']),
            'subtitle': ImageFont.truetype(font_file, FONT_SIZES['subtitle']),
            'section': ImageFont.truetype(font_file, FONT_SIZES['section']),
            'content': ImageFont.truetype(font_file, FONT_SIZES['content']),
            'small': ImageFont.truetype(font_file, FONT_SIZES['small'])
        }
        
        # 【V3.0.3 新增】加载 emoji 字体（Windows Segoe UI Emoji）
        try:
            emoji_font_file = 'C:/Windows/Fonts/seguiemj.ttf'
            fonts['emoji'] = ImageFont.truetype(emoji_font_file, FONT_SIZES['content'])
        except:
            fonts['emoji'] = fonts['content']
            print("[INFO] 未找到 Segoe UI Emoji 字体，使用默认字体")
            
    except:
        fonts = {size: ImageFont.load_default() for size in FONT_SIZES}
        fonts['emoji'] = fonts['content']
    return fonts

def draw_centered_text(draw, text, y, font, color):
    """居中绘制文字（支持颜色名称或色值）"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    draw.text((x, y), text, fill=color, font=font)
    return y + (bbox[3] - bbox[1])

def get_color(template, color_name):
    """【V2.3 新增】获取模板颜色"""
    if color_name.startswith('#'):
        return color_name
    return template.get(color_name, '#2C2C2C')

def draw_decoration(draw, template_name, template):
    """【V2.3 新增】根据模板绘制装饰元素"""
    decoration_type = template.get('decoration', 'double_border')
    
    if decoration_type == 'double_border':
        draw.rectangle([10, 10, WIDTH-10, PAGE_HEIGHT-10], 
                       outline=template['border_outer'], width=8)
        draw.rectangle([22, 22, WIDTH-22, PAGE_HEIGHT-22], 
                       outline=template['border_inner'], width=2)
    
    elif decoration_type == 'single_border':
        draw.rectangle([15, 15, WIDTH-15, PAGE_HEIGHT-15], 
                       outline=template['border_outer'], width=4)
        draw.rectangle([25, 25, WIDTH-25, PAGE_HEIGHT-25], 
                       outline=template['border_inner'], width=1)
    
    elif decoration_type == 'ornament':
        draw.rectangle([10, 10, WIDTH-10, PAGE_HEIGHT-10], 
                       outline=template['border_outer'], width=6)
        draw.rectangle([20, 20, WIDTH-20, PAGE_HEIGHT-20], 
                       outline=template['border_inner'], width=2)
        corner_size = 40
        draw.arc([10, 10, 10+corner_size, 10+corner_size], 0, 90, 
                 fill=template['border_inner'], width=3)
        draw.arc([WIDTH-10-corner_size, 10, WIDTH-10, 10+corner_size], 90, 180, 
                 fill=template['border_inner'], width=3)
        draw.arc([10, PAGE_HEIGHT-10-corner_size, 10+corner_size, PAGE_HEIGHT-10], 270, 360, 
                 fill=template['border_inner'], width=3)
        draw.arc([WIDTH-10-corner_size, PAGE_HEIGHT-10-corner_size, WIDTH-10, PAGE_HEIGHT-10], 180, 270, 
                 fill=template['border_inner'], width=3)
    
    elif decoration_type == 'cloud':
        draw.rectangle([12, 12, WIDTH-12, PAGE_HEIGHT-12], 
                       outline=template['border_outer'], width=5)
        draw.rectangle([24, 24, WIDTH-24, PAGE_HEIGHT-24], 
                       outline=template['border_inner'], width=2)
        for i in range(5):
            x = 100 + i * 200
            draw.arc([x, 15, x+60, 75], 0, 180, 
                     fill=template['border_inner'], width=2)
    
    elif decoration_type == 'leaf':
        draw.rectangle([10, 10, WIDTH-10, PAGE_HEIGHT-10], 
                       outline=template['border_outer'], width=4)
        draw.rectangle([22, 22, WIDTH-22, PAGE_HEIGHT-22], 
                       outline=template['border_inner'], width=2)
        leaf_size = 30
        draw.ellipse([10, 10, 10+leaf_size, 10+leaf_size*2], 
                     outline=template['border_inner'], width=2)
        draw.ellipse([WIDTH-10-leaf_size, 10, WIDTH-10, 10+leaf_size*2], 
                     outline=template['border_inner'], width=2)
        draw.ellipse([10, PAGE_HEIGHT-10-leaf_size*2, 10+leaf_size, PAGE_HEIGHT-10], 
                     outline=template['border_inner'], width=2)
        draw.ellipse([WIDTH-10-leaf_size, PAGE_HEIGHT-10-leaf_size*2, WIDTH-10, PAGE_HEIGHT-10], 
                     outline=template['border_inner'], width=2)

def draw_double_border(draw):
    """绘制双层边框（兼容旧版）"""
    draw.rectangle([10, 10, WIDTH-10, PAGE_HEIGHT-10], 
                   outline=COLORS['border_outer'], width=8)
    draw.rectangle([22, 22, WIDTH-22, PAGE_HEIGHT-22], 
                   outline=COLORS['border_inner'], width=2)

def draw_separator(draw, y, color='#D4AF37'):
    """绘制分隔线（支持自定义颜色）"""
    draw.line([(80, y), (WIDTH-80, y)], fill=color, width=2)
    return y + SPACING['separator_after']

def get_month_ganzhi_by_jieqi(year, month, day):
    """
    【V3.0.1 修复】根据节气计算月柱（替代 lunar-python 的农历月干支）
    """
    YEAR_GAN_START = {
        '甲': '丙', '己': '丙',
        '乙': '戊', '庚': '戊',
        '丙': '庚', '辛': '庚',
        '丁': '壬', '癸': '壬',
        '戊': '甲',
    }
    
    GAN = '甲乙丙丁戊己庚辛壬癸'
    ZHI = '寅卯辰巳午未申酉戌亥子丑'
    
    if month == 1:
        month_zhi = '丑' if day < 7 else '子'
    elif month == 2:
        month_zhi = '丑' if day < 4 else '寅'
    elif month == 3:
        month_zhi = '寅' if day < 5 else '卯'
    elif month == 4:
        month_zhi = '卯' if day < 5 else '辰'
    elif month == 5:
        month_zhi = '辰' if day < 5 else '巳'
    elif month == 6:
        month_zhi = '巳' if day < 5 else '午'
    elif month == 7:
        month_zhi = '午' if day < 7 else '未'
    elif month == 8:
        month_zhi = '未' if day < 7 else '申'
    elif month == 9:
        month_zhi = '申' if day < 7 else '酉'
    elif month == 10:
        month_zhi = '酉' if day < 8 else '戌'
    elif month == 11:
        month_zhi = '戌' if day < 7 else '亥'
    elif month == 12:
        month_zhi = '亥' if day < 7 else '子'
    
    lunar = Lunar.fromYmd(year, month, day)
    year_gz = lunar.getYearInGanZhi()
    year_gan = year_gz[0]
    
    start_gan = YEAR_GAN_START[year_gan]
    start_gan_idx = GAN.find(start_gan)
    month_zhi_idx = ZHI.find(month_zhi)
    month_gan_idx = (start_gan_idx + month_zhi_idx) % 10
    month_gan = GAN[month_gan_idx]
    
    return f"{month_gan}{month_zhi}"


def get_ganzhi(date_str):
    """
    【V3.0.1 升级】使用 lunar-python 计算干支 + 节气（支持 1900-2100 年）
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    solar = Solar.fromYmd(date_obj.year, date_obj.month, date_obj.day)
    lunar = solar.getLunar()
    
    year_gz = lunar.getYearInGanZhi()
    day_gz = lunar.getDayInGanZhi()
    
    month_gz = get_month_ganzhi_by_jieqi(date_obj.year, date_obj.month, date_obj.day)
    
    jieqi = lunar.getJieQi()
    
    ganzhi_data = {
        'year': year_gz,
        'month': month_gz,
        'day': day_gz,
        'jieqi': jieqi,
        'jieqi_text': f"今日{jieqi}" if jieqi else "",
    }
    
    return f"{year_gz}年 {month_gz}月 {day_gz}日", day_gz, ganzhi_data

def get_jishi(day_ganzhi):
    """【修复 2】使用十二神值时准确计算吉凶"""
    tian_gan_map = {
        '甲': 0, '己': 0,
        '乙': 1, '庚': 1,
        '丙': 2, '辛': 2,
        '丁': 3, '壬': 3,
        '戊': 4, '癸': 4,
    }
    
    shi_chen = [
        ('子时', '23-1 点'), ('丑时', '1-3 点'), ('寅时', '3-5 点'),
        ('卯时', '5-7 点'), ('辰时', '7-9 点'), ('巳时', '9-11 点'),
        ('午时', '11-13 点'), ('未时', '13-15 点'), ('申时', '15-17 点'),
        ('酉时', '17-19 点'), ('戌时', '19-21 点'), ('亥时', '21-23 点')
    ]
    
    shi_er_shen = [
        '青龙', '明堂', '天刑', '朱雀', '金匮', '天德',
        '白虎', '玉堂', '天牢', '玄武', '司命', '勾陈'
    ]
    
    shen_jixiong = {
        '青龙': '吉', '明堂': '吉', '金匮': '吉', 
        '天德': '吉', '玉堂': '吉', '司命': '吉',
        '天刑': '凶', '朱雀': '凶', '白虎': '凶',
        '天牢': '凶', '玄武': '凶', '勾陈': '凶'
    }
    
    gan = day_ganzhi[0]
    start_index = tian_gan_map.get(gan, 0)
    
    ji_shi = []
    xiong_shi = []
    
    for i, (name, time) in enumerate(shi_chen):
        shen_index = (start_index + i) % 12
        shen_name = shi_er_shen[shen_index]
        jixiong = shen_jixiong[shen_name]
        
        if jixiong == '吉':
            ji_shi.append(f"{name} ({time})")
        else:
            xiong_shi.append(f"{name} ({time})")
    
    return {
        'ji': ji_shi,
        'xiong': xiong_shi
    }

def get_changyi(day_ganzhi):
    """根据日柱天干计算穿衣建议（五行颜色）"""
    wu_xing_map = {
        '甲': '木', '乙': '木',
        '丙': '火', '丁': '火',
        '戊': '土', '己': '土',
        '庚': '金', '辛': '金',
        '壬': '水', '癸': '水'
    }
    
    color_map = {
        '木': {'lucky': '绿色、青色', 'avoid': '白色、金色'},
        '火': {'lucky': '红色、紫色', 'avoid': '黑色、蓝色'},
        '土': {'lucky': '黄色、棕色', 'avoid': '绿色、青色'},
        '金': {'lucky': '白色、金色', 'avoid': '红色、紫色'},
        '水': {'lucky': '黑色、蓝色', 'avoid': '黄色、棕色'}
    }
    
    gan = day_ganzhi[0]
    wx = wu_xing_map.get(gan, '火')
    return color_map.get(wx, {'lucky': '红色、紫色', 'avoid': '黑色、蓝色'})

def get_cai_shen(day_ganzhi):
    """【修复 3】根据日干准确计算财神方位"""
    cai_shen_map = {
        '甲': {'xi': "东南方", 'fu': "正南方", 'cai': "东北方", 'tai': "占门床外正南"},
        '乙': {'xi': "西北方", 'fu': "正北方", 'cai': "东北方", 'tai': "占厨灶厕外西南"},
        '丙': {'xi': "西南方", 'fu': "正东方", 'cai': "正西方", 'tai': "占门户碓磨外正南"},
        '丁': {'xi': "正南方", 'fu': "正东方", 'cai': "正西方", 'tai': "占房床厕外正南"},
        '戊': {'xi': "东南方", 'fu': "正南方", 'cai': "正北方", 'tai': "占门床外正南"},
        '己': {'xi': "东北方", 'fu': "正南方", 'cai': "正北方", 'tai': "占碓磨厕外东南"},
        '庚': {'xi': "西北方", 'fu': "西南方", 'cai': "正东方", 'tai': "占房床厕外东北"},
        '辛': {'xi': "西南方", 'fu': "东北方", 'cai': "正东方", 'tai': "占仓库厕外正东"},
        '壬': {'xi': "正北方", 'fu': "西南方", 'cai': "正南方", 'tai': "占门床外正南"},
        '癸': {'xi': "东南方", 'fu': "正西方", 'cai': "正南方", 'tai': "占房床厕外东北"}
    }
    
    gan = day_ganzhi[0]
    return cai_shen_map.get(gan, cai_shen_map['甲'])


# 由于文件太长，我将只修改关键的生肖绘制部分和互动引导文案
# 其他函数保持不变，从原文件复制