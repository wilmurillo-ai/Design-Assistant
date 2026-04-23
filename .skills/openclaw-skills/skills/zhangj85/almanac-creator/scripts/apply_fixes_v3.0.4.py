#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用 V3.0.4 修复：
1. 第一页农历 + 干支 + 节气合并到一行
2. 生肖运势使用 PNG 图标（学习星座技能）
"""

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# ==================== 修复 1: 压缩第一页布局 ====================
old_header = """    y = 40
    y = draw_centered_text(draw, "每日黄历", y, fonts['title'], template['title'])
    y += SPACING['after_title']
    y = draw_centered_text(draw, data['date_gregorian'], y, fonts['subtitle'], template['text'])
    y += SPACING['after_subtitle']
    
    # 【V3.0.3 新增】生肖添加 emoji 图标（使用 emoji 字体）
    zodiac_emoji_map = {
        '鼠': '🐭', '牛': '🐮', '虎': '🐯', '兔': '🐰',
        '龙': '🐲', '蛇': '🐍', '马': '🐴', '羊': '🐑',
        '猴': '🐵', '鸡': '🐔', '狗': '🐶', '猪': '🐷'
    }
    
    # 获取 emoji 字体
    emoji_font = fonts.get('emoji', fonts['content'])"""

new_header = """    y = 40
    y = draw_centered_text(draw, "每日黄历", y, fonts['title'], template['title'])
    y += SPACING['after_title']
    y = draw_centered_text(draw, data['date_gregorian'], y, fonts['subtitle'], template['text'])
    y += SPACING['after_subtitle']
    
    # 【V3.0.4 优化】农历 + 干支 + 节气合并到一行，节省垂直空间
    lunar_ganzhi_jieqi = f"{data['date_lunar']}  {data['ganzhi_full']}"
    if data['special_day']:
        lunar_ganzhi_jieqi += f"  {data['special_day']}"
    y = draw_centered_text(draw, lunar_ganzhi_jieqi, y, fonts['content'], template['text'])
    y += SPACING['after_lunar']
    
    # 【V3.0.4 新增】生肖图标路径（学习星座技能）
    ZODIAC_ICONS = {
        '鼠': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/shu.png',
        '牛': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/niu.png',
        '虎': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/hu.png',
        '兔': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/tu.png',
        '龙': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/long.png',
        '蛇': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/she.png',
        '马': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/ma.png',
        '羊': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/yang.png',
        '猴': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/hou.png',
        '鸡': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/ji.png',
        '狗': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/gou.png',
        '猪': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/zhu.png',
    }
    
    # 缓存加载的生肖图标
    _zodiac_icon_cache = {}
    
    def get_zodiac_icon(name, size=(40, 40)):
        \"\"\"获取生肖图标（带缓存）\"\"\"
        if name in _zodiac_icon_cache:
            return _zodiac_icon_cache[name]
        
        path = ZODIAC_ICONS.get(name)
        if path and os.path.exists(path):
            try:
                icon = Image.open(path)
                icon = icon.resize(size, Image.Resampling.LANCZOS)
                _zodiac_icon_cache[name] = icon
                return icon
            except Exception as e:
                print(f"加载生肖图标失败 {name}: {e}")
        return None"""

content = content.replace(old_header, new_header)

# ==================== 修复 2: 生肖运势使用图标 ====================
# 找到生肖绘制部分并替换
old_zodiac_drawing = """    # 【V3.0.3 新增】生肖添加【】符号（方案 B - 兼容性最好）
    for zodiac in data['zodiac_red']:
        # 提取生肖名称（如"虎：传统说法六合，贵人相助" → "虎"）
        zodiac_name = zodiac.split(':')[0]
        # 使用【】包裹生肖，视觉效果类似图标
        zodiac_formatted = f"【{zodiac_name}】{zodiac.split(':')[1]}"
        y = draw_centered_text(draw, zodiac_formatted, y, fonts['content'], template['text'])
        y += SPACING['after_zodiac_item']
    
    y += 8
    y = draw_centered_text(draw, "今日需注意生肖", y, fonts['content'], template['section'])
    y += SPACING['after_zodiac_item']
    
    for zodiac in data['zodiac_black']:
        zodiac_name = zodiac.split(':')[0]
        # 使用【】包裹生肖
        zodiac_formatted = f"【{zodiac_name}】{zodiac.split(':')[1]}"
        y = draw_centered_text(draw, zodiac_formatted, y, fonts['content'], template['text'])
        y += SPACING['after_zodiac_item']"""

new_zodiac_drawing = """    # 【V3.0.4 新增】生肖运势使用图标（学习星座技能）
    for zodiac in data['zodiac_red']:
        zodiac_name = zodiac.split(':')[0]
        zodiac_desc = zodiac.split(':')[1] if ':' in zodiac else ''
        
        # 加载并粘贴生肖图标
        icon = get_zodiac_icon(zodiac_name, size=(40, 40))
        if icon:
            # 计算图标位置（居中偏左）
            header_text = f"{zodiac_name}: {zodiac_desc}"
            bbox = draw.textbbox((0, 0), header_text, font=fonts['content'])
            text_width = bbox[2] - bbox[0]
            total_width = text_width + 45  # 图标宽度 + 间距
            start_x = (WIDTH - total_width) // 2
            
            # 粘贴图标
            icon_y = y + 5
            img.paste(icon, (start_x, icon_y), icon if icon.mode == 'RGBA' else None)
            
            # 绘制文字（在图标右侧）
            draw.text((start_x + 45, y), f"{zodiac_name}: {zodiac_desc}", fill=template['text'], font=fonts['content'])
            y += max(40, bbox[3] - bbox[1]) + 10  # 增加 10px 间隔
        else:
            # 如果没有图标，只显示文字
            y = draw_centered_text(draw, f"{zodiac_name}: {zodiac_desc}", y, fonts['content'], template['text'])
            y += SPACING['after_zodiac_item']
    
    y += 8
    y = draw_centered_text(draw, "今日需注意生肖", y, fonts['content'], template['section'])
    y += SPACING['after_zodiac_item']
    
    for zodiac in data['zodiac_black']:
        zodiac_name = zodiac.split(':')[0]
        zodiac_desc = zodiac.split(':')[1] if ':' in zodiac else ''
        
        # 加载并粘贴生肖图标
        icon = get_zodiac_icon(zodiac_name, size=(40, 40))
        if icon:
            header_text = f"{zodiac_name}: {zodiac_desc}"
            bbox = draw.textbbox((0, 0), header_text, font=fonts['content'])
            text_width = bbox[2] - bbox[0]
            total_width = text_width + 45
            start_x = (WIDTH - total_width) // 2
            
            icon_y = y + 5
            img.paste(icon, (start_x, icon_y), icon if icon.mode == 'RGBA' else None)
            draw.text((start_x + 45, y), f"{zodiac_name}: {zodiac_desc}", fill=template['text'], font=fonts['content'])
            y += max(40, bbox[3] - bbox[1]) + 10
        else:
            y = draw_centered_text(draw, f"{zodiac_name}: {zodiac_desc}", y, fonts['content'], template['text'])
            y += SPACING['after_zodiac_item']"""

content = content.replace(old_zodiac_drawing, new_zodiac_drawing)

# 写回文件
with open(script_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("OK! Applied V3.0.4 fixes:")
print("  1. Page 1 layout compressed (lunar + ganzhi + jieqi in one line)")
print("  2. Zodiac signs now use PNG icons (like constellation skill)")
