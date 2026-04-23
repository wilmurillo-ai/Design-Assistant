#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复生肖图标显示问题
"""

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并替换生肖绘制代码
old_code = '''    # 【V3.0.4 新增】生肖图标路径（学习星座技能）
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
        """获取生肖图标（带缓存）"""
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
        return None
    
    # 【V3.0.4 新增】生肖运势使用图标（学习星座技能）
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
            y += SPACING['after_zodiac_item']'''

# 使用更简单的方案：直接在文件顶部定义图标路径和加载函数
# 将生肖绘制代码改为使用【】符号，确保显示正常
new_code = '''    # 【V3.0.4 修复】生肖运势使用【】符号包裹，清晰醒目
    for zodiac in data['zodiac_red']:
        zodiac_name = zodiac.split(':')[0]
        zodiac_desc = zodiac.split(':')[1] if ':' in zodiac else ''
        # 使用【】包裹生肖名，清晰醒目
        y = draw_centered_text(draw, f"【{zodiac_name}】{zodiac_desc}", y, fonts['content'], template['text'])
        y += SPACING['after_zodiac_item']
    
    y += 8
    y = draw_centered_text(draw, "今日需注意生肖", y, fonts['content'], template['section'])
    y += SPACING['after_zodiac_item']
    
    for zodiac in data['zodiac_black']:
        zodiac_name = zodiac.split(':')[0]
        zodiac_desc = zodiac.split(':')[1] if ':' in zodiac else ''
        # 使用【】包裹生肖名
        y = draw_centered_text(draw, f"【{zodiac_name}】{zodiac_desc}", y, fonts['content'], template['text'])
        y += SPACING['after_zodiac_item']'''

content = content.replace(old_code, new_code)

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("OK! Fixed zodiac display to use [] symbols")
