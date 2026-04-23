#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改生肖显示为【】包裹格式（方案 B - 兼容性最好）
"""

# 读取原文件
with open(r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到生肖绘制部分，替换为【】格式
old_zodiac_code = """    # 【V3.0.3 新增】生肖添加 emoji 图标（使用 emoji 字体）
    zodiac_emoji_map = {
        '鼠': '🐭', '牛': '🐮', '虎': '🐯', '兔': '🐰',
        '龙': '🐲', '蛇': '🐍', '马': '🐴', '羊': '🐑',
        '猴': '🐵', '鸡': '🐔', '狗': '🐶', '猪': '🐷'
    }
    
    # 获取 emoji 字体
    emoji_font = fonts.get('emoji', fonts['content'])
    
    for zodiac in data['zodiac_red']:
        # 提取生肖名称（如"鼠：传统说法六合，贵人相助" → "鼠"）
        zodiac_name = zodiac.split(':')[0]
        emoji = zodiac_emoji_map.get(zodiac_name, '')
        
        # 分离绘制：先画 emoji，再画中文
        if emoji:
            # 计算 emoji 宽度
            emoji_text = emoji + '  '
            emoji_bbox = draw.textbbox((0, 0), emoji_text, font=emoji_font)
            emoji_width = emoji_bbox[2] - emoji_bbox[0]
            
            # 计算中文宽度
            chinese_bbox = draw.textbbox((0, 0), zodiac, font=fonts['content'])
            chinese_width = chinese_bbox[2] - chinese_bbox[0]
            
            # 计算总宽度和起始位置
            total_width = emoji_width + chinese_width
            start_x = (WIDTH - total_width) // 2
            
            # 绘制 emoji（使用 emoji 字体）
            draw.text((start_x, y), emoji_text, fill=template['text'], font=emoji_font)
            # 绘制中文（使用黑体）
            draw.text((start_x + emoji_width, y), zodiac, fill=template['text'], font=fonts['content'])
        else:
            y = draw_centered_text(draw, zodiac, y, fonts['content'], template['text'])
        
        y += SPACING['after_zodiac_item']
    
    y += 8
    y = draw_centered_text(draw, "今日需注意生肖", y, fonts['content'], template['section'])
    y += SPACING['after_zodiac_item']
    
    for zodiac in data['zodiac_black']:
        # 提取生肖名称
        zodiac_name = zodiac.split(':')[0]
        emoji = zodiac_emoji_map.get(zodiac_name, '')
        
        # 分离绘制：先画 emoji，再画中文
        if emoji:
            emoji_text = emoji + '  '
            emoji_bbox = draw.textbbox((0, 0), emoji_text, font=emoji_font)
            emoji_width = emoji_bbox[2] - emoji_bbox[0]
            
            chinese_bbox = draw.textbbox((0, 0), zodiac, font=fonts['content'])
            chinese_width = chinese_bbox[2] - chinese_bbox[0]
            
            total_width = emoji_width + chinese_width
            start_x = (WIDTH - total_width) // 2
            
            draw.text((start_x, y), emoji_text, fill=template['text'], font=emoji_font)
            draw.text((start_x + emoji_width, y), zodiac, fill=template['text'], font=fonts['content'])
        else:
            y = draw_centered_text(draw, zodiac, y, fonts['content'], template['text'])
        
        y += SPACING['after_zodiac_item']"""

# 方案 B：使用【】符号包裹生肖名称
new_zodiac_code = """    # 【V3.0.3 新增】生肖添加【】符号（方案 B - 兼容性最好）
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

content = content.replace(old_zodiac_code, new_zodiac_code)

# 写回文件
with open(r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK! Modified to use [] format for zodiac signs.")
