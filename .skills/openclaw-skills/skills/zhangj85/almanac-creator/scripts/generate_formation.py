#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026 世界杯球队阵型图生成器
功能：生成足球队首发阵容图（PNG 格式）
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ==================== 配置 ====================
# 图片尺寸
WIDTH = 800
HEIGHT = 1000

# 颜色配置（按参考图片模板）
COLORS = {
    'field': '#4A7C2C',        # 球场绿色（浅）
    'field_dark': '#3D6B24',   # 球场绿色（深，条纹）
    'line': '#FFFFFF',         # 球场线白色
    'player_circle': '#FF8C00', # 球员圆圈（橙色）
    'player_number': '#FFFFFF', # 号码白色
    'player_name': '#FFFFFF',   # 名字白色
    'team_name': '#FFFFFF',    # 队名白色
    'goal': '#FFFFFF',         # 球门白色
}

# 球员位置（根据阵型）
FORMATIONS = {
    '4-3-3': {
        'GK': [(0.5, 0.08)],
        'RB': [(0.8, 0.22)],
        'CB': [(0.6, 0.15), (0.4, 0.15)],
        'LB': [(0.2, 0.22)],
        'CM': [(0.5, 0.45)],
        'RM': [(0.75, 0.55)],
        'LM': [(0.25, 0.55)],
        'RW': [(0.8, 0.75)],
        'ST': [(0.5, 0.88)],
        'LW': [(0.2, 0.75)],
    },
    '4-2-3-1': {
        'GK': [(0.5, 0.08)],
        'RB': [(0.8, 0.22)],
        'CB': [(0.6, 0.15), (0.4, 0.15)],
        'LB': [(0.2, 0.22)],
        'CDM': [(0.6, 0.4), (0.4, 0.4)],
        'RAM': [(0.75, 0.65)],
        'CAM': [(0.5, 0.7)],
        'LAM': [(0.25, 0.65)],
        'ST': [(0.5, 0.88)],
    },
    '3-5-2': {
        'GK': [(0.5, 0.08)],
        'CB': [(0.7, 0.18), (0.5, 0.12), (0.3, 0.18)],
        'RWB': [(0.9, 0.42)],
        'LWB': [(0.1, 0.42)],
        'CM': [(0.6, 0.52), (0.5, 0.58), (0.4, 0.52)],
        'ST': [(0.6, 0.82), (0.4, 0.82)],
    },
    '5-4-1': {
        'GK': [(0.5, 0.08)],
        'RWB': [(0.9, 0.28)],
        'CB': [(0.7, 0.18), (0.5, 0.12), (0.3, 0.18)],
        'LWB': [(0.1, 0.28)],
        'RM': [(0.85, 0.58)],
        'CM': [(0.6, 0.52), (0.4, 0.52)],
        'LM': [(0.15, 0.58)],
        'ST': [(0.5, 0.85)],
    },
}

# A 组 4 支球队阵容数据
TEAMS = {
    '墨西哥': {
        'formation': '4-3-3',
        'squad': {
            'GK': [('奥乔亚', 1)],
            'RB': [('桑切斯', 2)],
            'CB': [('蒙特斯', 15), ('巴斯克斯', 23)],
            'LB': [('加拉多', 20)],
            'CM': [('阿尔瓦雷斯', 4)],
            'RM': [('查韦斯', 6)],
            'LM': [('埃雷拉', 8)],
            'RW': [('洛萨诺', 22)],
            'ST': [('希门尼斯', 9)],
            'LW': [('富恩特斯', 11)],
        },
        'jersey_color': '#006847',  # 墨西哥绿
    },
    '韩国': {
        'formation': '4-2-3-1',
        'squad': {
            'GK': [('赵贤祐', 1)],
            'RB': [('李记帝', 3)],
            'CB': [('金玟哉', 4), ('金承奎', 19)],
            'LB': [('黄义足', 2)],
            'CDM': [('黄仁范', 6), ('李在城', 17)],
            'RAM': [('李刚仁', 18)],
            'CAM': [('孙兴慜', 7)],
            'LAM': [('郑优营', 10)],
            'ST': [('曹圭成', 9)],
        },
        'jersey_color': '#C60C30',  # 韩国红
    },
    '捷克': {
        'formation': '3-5-2',
        'squad': {
            'GK': [('瓦茨利克', 1)],
            'CB': [('切鲁斯特', 18), ('卡德莱克', 3), ('博日尔', 5)],
            'RWB': [('曹法尔', 5)],
            'LWB': [('赫洛热克', 12)],
            'CM': [('绍切克', 15), ('达里达', 8), ('扬克托', 14)],
            'ST': [('希克', 13)],
        },
        'jersey_color': '#D7141A',  # 捷克红
    },
    '南非': {
        'formation': '5-4-1',
        'squad': {
            'GK': [('威廉姆斯', 1)],
            'RWB': [('弗莱明', 4)],
            'CB': [('姆法', 5), ('恩东克', 15), ('姆切鲁', 3)],
            'LWB': [('皮纳尔', 8)],
            'RM': [('莫比帕', 6)],
            'CM': [('马班戈', 10), ('布罗迪', 11), ('迈耶', 7)],
            'LM': [('帕尔西', 9)],
            'ST': [('威廉斯', 9)],
        },
        'jersey_color': '#007A4D',  # 南非绿
    },
}


def draw_field(draw):
    """绘制足球场背景（带条纹）"""
    # 绿色条纹球场（横向条纹）
    stripe_height = 100
    for i in range(0, HEIGHT, stripe_height):
        color = COLORS['field'] if (i // stripe_height) % 2 == 0 else COLORS['field_dark']
        draw.rectangle([0, i, WIDTH, i + stripe_height], fill=color)
    
    # 球场线（白色）
    line_width = 2
    
    # 边界线
    draw.rectangle([30, 30, WIDTH-30, HEIGHT-30], outline=COLORS['line'], width=line_width)
    
    # 中线
    draw.line([(30, HEIGHT/2), (WIDTH-30, HEIGHT/2)], fill=COLORS['line'], width=line_width)
    
    # 中圈
    draw.ellipse([WIDTH/2-70, HEIGHT/2-70, WIDTH/2+70, HEIGHT/2+70], 
                 outline=COLORS['line'], width=line_width)
    
    # 中点
    draw.ellipse([WIDTH/2-4, HEIGHT/2-4, WIDTH/2+4, HEIGHT/2+4], 
                 fill=COLORS['line'])
    
    # 上禁区（对方禁区）
    draw.rectangle([WIDTH/2-120, 30, WIDTH/2+120, 150], 
                 outline=COLORS['line'], width=line_width)
    
    # 上球门区（小禁区）
    draw.rectangle([WIDTH/2-60, 30, WIDTH/2+60, 80], 
                 outline=COLORS['line'], width=line_width)
    
    # 下禁区（本方禁区）
    draw.rectangle([WIDTH/2-120, HEIGHT-150, WIDTH/2+120, HEIGHT-30], 
                 outline=COLORS['line'], width=line_width)
    
    # 下球门区（小禁区）
    draw.rectangle([WIDTH/2-60, HEIGHT-80, WIDTH/2+60, HEIGHT-30], 
                 outline=COLORS['line'], width=line_width)
    
    # 下角球弧
    draw.arc([WIDTH/2-100, HEIGHT-130, WIDTH/2+100, HEIGHT-30], 
             start=0, end=180, fill=COLORS['line'], width=line_width)
    
    # 上角球弧
    draw.arc([WIDTH/2-100, 30, WIDTH/2+100, 130], 
             start=180, end=360, fill=COLORS['line'], width=line_width)
    
    # 球门（上）
    draw.rectangle([WIDTH/2-25, 25, WIDTH/2+25, 30], 
                 fill=COLORS['goal'], outline=COLORS['line'], width=2)
    
    # 球门（下）
    draw.rectangle([WIDTH/2-25, HEIGHT-30, WIDTH/2+25, HEIGHT-25], 
                 fill=COLORS['goal'], outline=COLORS['line'], width=2)


def draw_player(draw, x, y, number, name, jersey_color, font_number, font_name):
    """绘制单个球员（橙色圆圈模板）"""
    # 球员圆圈（橙色，按参考图片）
    circle_radius = 24
    draw.ellipse([x-circle_radius, y-circle_radius, 
                  x+circle_radius, y+circle_radius], 
                 fill=COLORS['player_circle'], outline=COLORS['line'], width=2)
    
    # 号码（圆圈内，白色粗体）
    number_text = str(number)
    number_bbox = draw.textbbox((0, 0), number_text, font=font_number)
    number_width = number_bbox[2] - number_bbox[0]
    draw.text((x - number_width/2, y - 12), number_text, 
              fill=COLORS['player_number'], font=font_number)
    
    # 名字（圆圈下方，白色，加大）
    name_bbox = draw.textbbox((0, 0), name, font=font_name)
    name_width = name_bbox[2] - name_bbox[0]
    draw.text((x - name_width/2, y + circle_radius + 10), name, 
              fill=COLORS['player_name'], font=font_name)


def generate_formation_image(team_name, team_data, output_path):
    """生成单支球队的阵型图"""
    # 创建图片
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['field'])
    draw = ImageDraw.Draw(img)
    
    # 绘制球场
    draw_field(draw)
    
    # 加载字体（加大）
    try:
        font_number = ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', 16)
        font_name = ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', 14)
        font_title = ImageFont.truetype('C:/Windows/Fonts/simhei.ttf', 28)
    except:
        font_number = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_title = ImageFont.load_default()
    
    # 绘制队名（顶部）
    title = f"{team_name} - {team_data['formation']}"
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text((WIDTH/2 - title_width/2, 10), title, 
              fill=COLORS['team_name'], font=font_title)
    
    # 获取阵型数据
    formation = team_data['formation']
    squad = team_data['squad']
    jersey_color = team_data['jersey_color']
    
    # 获取阵型位置
    if formation in FORMATIONS:
        positions = FORMATIONS[formation]
        
        # 绘制每个位置的球员
        for position, players in squad.items():
            if position in positions:
                pos_coords = positions[position]
                for i, (name, number) in enumerate(players):
                    if i < len(pos_coords):
                        x = pos_coords[i][0] * WIDTH
                        y = pos_coords[i][1] * HEIGHT
                        draw_player(draw, x, y, number, name, jersey_color, 
                                   font_number, font_name)
    
    # 保存图片
    img.save(output_path, 'PNG', quality=95)
    print(f"[OK] 已生成：{output_path}")


def main():
    """主函数：生成 A 组 4 支球队阵型图"""
    # 创建输出目录
    output_dir = 'C:/Users/liuyan/.openclaw/workspace/formation_images'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成每支球队的阵型图
    for team_name, team_data in TEAMS.items():
        output_path = os.path.join(output_dir, f'{team_name}_阵型图.png')
        generate_formation_image(team_name, team_data, output_path)
    
    print(f"\n[OK] A 组 4 支球队阵型图生成完成！")
    print(f"输出目录：{output_dir}")


if __name__ == '__main__':
    main()
