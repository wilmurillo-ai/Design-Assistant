#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改黄历生成脚本，添加 emoji 字体支持和优化互动引导文案
"""

import re

# 读取原文件
with open(r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改 1: 在 load_fonts 函数中添加 emoji 字体加载
old_load_fonts = """def load_fonts(template_name='traditional'):
    \"\"\"加载字体（统一使用黑体，保持可读性和品牌一致性）\"\"\"
    try:
        # 统一使用黑体（所有模板）
        font_file = 'C:/Windows/Fonts/simhei.ttf'
        
        fonts = {
            'title': ImageFont.truetype(font_file, FONT_SIZES['title']),
            'subtitle': ImageFont.truetype(font_file, FONT_SIZES['subtitle']),
            'section': ImageFont.truetype(font_file, FONT_SIZES['section']),
            'content': ImageFont.truetype(font_file, FONT_SIZES['content']),
            'small': ImageFont.truetype(font_file, FONT_SIZES['small'])
        }
    except:
        fonts = {size: ImageFont.load_default() for size in FONT_SIZES}
    return fonts"""

new_load_fonts = """def load_fonts(template_name='traditional'):
    \"\"\"加载字体（统一使用黑体，保持可读性和品牌一致性）\"\"\"
    try:
        # 统一使用黑体（所有模板）
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
            # 如果找不到 emoji 字体，回退到黑体
            fonts['emoji'] = fonts['content']
            print("[INFO] 未找到 Segoe UI Emoji 字体，使用默认字体")
            
    except:
        fonts = {size: ImageFont.load_default() for size in FONT_SIZES}
        fonts['emoji'] = fonts['content']
    return fonts"""

content = content.replace(old_load_fonts, new_load_fonts)

# 修改 2: 优化互动引导文案（第 2 页）
old_interaction_p2 = """    # 【V3.0.3 新增】抖音互动引导
    interaction_text = "👍 点赞接好运 💬 评论区留下你的生肖 ➕ 关注每日更新"
    y = draw_centered_text(draw, interaction_text, y, fonts['content'], template['section'])"""

new_interaction_p2 = """    # 【V3.0.3 新增】抖音互动引导（优化版）
    interaction_text = "👍 点赞接好运  💬 评论留生肖  ➕ 关注每日更新"
    y = draw_centered_text(draw, interaction_text, y, fonts.get('emoji', fonts['content']), template['section'])"""

content = content.replace(old_interaction_p2, new_interaction_p2)

# 修改 3: 优化互动引导文案（第 3 页）
old_interaction_p3 = """    # 【V3.0.3 新增】抖音互动引导
    interaction_text = "👍 点赞接好运 💬 评论区留下你的生肖 ➕ 关注每日更新"
    y = draw_centered_text(draw, interaction_text, y, fonts['content'], template['section'])"""

new_interaction_p3 = """    # 【V3.0.3 新增】抖音互动引导（优化版）
    interaction_text = "👍 点赞接好运  💬 评论留生肖  ➕ 关注每日更新"
    y = draw_centered_text(draw, interaction_text, y, fonts.get('emoji', fonts['content']), template['section'])"""

content = content.replace(old_interaction_p3, new_interaction_p3)

# 写回文件
with open(r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 修改完成！")
print("  1. 已添加 emoji 字体支持（Segoe UI Emoji）")
print("  2. 已优化互动引导文案（缩短版，避免截断）")
print("  3. 互动引导使用 emoji 字体渲染")
