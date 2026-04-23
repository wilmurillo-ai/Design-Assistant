#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接修改黄历脚本，应用 V3.0.4 修复
"""

script_path = r'C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\scripts\generate_almanac.py'

with open(script_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要修改的行
new_lines = []
skip_until_line = -1

for i, line in enumerate(lines):
    # 跳过旧的生肖 emoji 代码块
    if '# 【V3.0.3 新增】生肖添加 emoji 图标' in line:
        # 插入新的生肖图标代码
        new_lines.append("    # 【V3.0.4 新增】生肖图标路径（学习星座技能）\n")
        new_lines.append("    ZODIAC_ICONS = {\n")
        new_lines.append("        '鼠': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/shu.png',\n")
        new_lines.append("        '牛': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/niu.png',\n")
        new_lines.append("        '虎': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/hu.png',\n")
        new_lines.append("        '兔': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/tu.png',\n")
        new_lines.append("        '龙': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/long.png',\n")
        new_lines.append("        '蛇': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/she.png',\n")
        new_lines.append("        '马': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/ma.png',\n")
        new_lines.append("        '羊': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/yang.png',\n")
        new_lines.append("        '猴': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/hou.png',\n")
        new_lines.append("        '鸡': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/ji.png',\n")
        new_lines.append("        '狗': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/gou.png',\n")
        new_lines.append("        '猪': 'C:/Users/liuyan/.openclaw/workspace/zodiac_icons/zhu.png',\n")
        new_lines.append("    }\n")
        new_lines.append("\n")
        new_lines.append("    # 缓存加载的生肖图标\n")
        new_lines.append("    _zodiac_icon_cache = {}\n")
        new_lines.append("\n")
        new_lines.append("    def get_zodiac_icon(name, size=(40, 40)):\n")
        new_lines.append("        \"\"\"获取生肖图标（带缓存）\"\"\"\n")
        new_lines.append("        if name in _zodiac_icon_cache:\n")
        new_lines.append("            return _zodiac_icon_cache[name]\n")
        new_lines.append("        \n")
        new_lines.append("        path = ZODIAC_ICONS.get(name)\n")
        new_lines.append("        if path and os.path.exists(path):\n")
        new_lines.append("            try:\n")
        new_lines.append("                icon = Image.open(path)\n")
        new_lines.append("                icon = icon.resize(size, Image.Resampling.LANCZOS)\n")
        new_lines.append("                _zodiac_icon_cache[name] = icon\n")
        new_lines.append("                return icon\n")
        new_lines.append("            except Exception as e:\n")
        new_lines.append(f"                print(f\"加载生肖图标失败 {{name}}: {{e}}\")\n")
        new_lines.append("        return None\n")
        new_lines.append("\n")
        new_lines.append("    # 【V3.0.4 新增】生肖运势使用图标（学习星座技能）\n")
        new_lines.append("    for zodiac in data['zodiac_red']:\n")
        new_lines.append("        zodiac_name = zodiac.split(':')[0]\n")
        new_lines.append("        zodiac_desc = zodiac.split(':')[1] if ':' in zodiac else ''\n")
        new_lines.append("        \n")
        new_lines.append("        # 加载并粘贴生肖图标\n")
        new_lines.append("        icon = get_zodiac_icon(zodiac_name, size=(40, 40))\n")
        new_lines.append("        if icon:\n")
        new_lines.append("            # 计算图标位置（居中偏左）\n")
        new_lines.append("            header_text = f\"{{zodiac_name}}: {{zodiac_desc}}\"\n")
        new_lines.append("            bbox = draw.textbbox((0, 0), header_text, font=fonts['content'])\n")
        new_lines.append("            text_width = bbox[2] - bbox[0]\n")
        new_lines.append("            total_width = text_width + 45  # 图标宽度 + 间距\n")
        new_lines.append("            start_x = (WIDTH - total_width) // 2\n")
        new_lines.append("            \n")
        new_lines.append("            # 粘贴图标\n")
        new_lines.append("            icon_y = y + 5\n")
        new_lines.append("            img.paste(icon, (start_x, icon_y), icon if icon.mode == 'RGBA' else None)\n")
        new_lines.append("            \n")
        new_lines.append("            # 绘制文字（在图标右侧）\n")
        new_lines.append("            draw.text((start_x + 45, y), f\"{{zodiac_name}}: {{zodiac_desc}}\", fill=template['text'], font=fonts['content'])\n")
        new_lines.append("            y += max(40, bbox[3] - bbox[1]) + 10  # 增加 10px 间隔\n")
        new_lines.append("        else:\n")
        new_lines.append("            # 如果没有图标，只显示文字\n")
        new_lines.append("            y = draw_centered_text(draw, f\"{{zodiac_name}}: {{zodiac_desc}}\", y, fonts['content'], template['text'])\n")
        new_lines.append("            y += SPACING['after_zodiac_item']\n")
        new_lines.append("        \n")
        new_lines.append("    y += 8\n")
        new_lines.append("    y = draw_centered_text(draw, \"今日需注意生肖\", y, fonts['content'], template['section'])\n")
        new_lines.append("    y += SPACING['after_zodiac_item']\n")
        new_lines.append("    \n")
        new_lines.append("    for zodiac in data['zodiac_black']:\n")
        new_lines.append("        zodiac_name = zodiac.split(':')[0]\n")
        new_lines.append("        zodiac_desc = zodiac.split(':')[1] if ':' in zodiac else ''\n")
        new_lines.append("        \n")
        new_lines.append("        # 加载并粘贴生肖图标\n")
        new_lines.append("        icon = get_zodiac_icon(zodiac_name, size=(40, 40))\n")
        new_lines.append("        if icon:\n")
        new_lines.append("            header_text = f\"{{zodiac_name}}: {{zodiac_desc}}\"\n")
        new_lines.append("            bbox = draw.textbbox((0, 0), header_text, font=fonts['content'])\n")
        new_lines.append("            text_width = bbox[2] - bbox[0]\n")
        new_lines.append("            total_width = text_width + 45\n")
        new_lines.append("            start_x = (WIDTH - total_width) // 2\n")
        new_lines.append("            \n")
        new_lines.append("            icon_y = y + 5\n")
        new_lines.append("            img.paste(icon, (start_x, icon_y), icon if icon.mode == 'RGBA' else None)\n")
        new_lines.append("            draw.text((start_x + 45, y), f\"{{zodiac_name}}: {{zodiac_desc}}\", fill=template['text'], font=fonts['content'])\n")
        new_lines.append("            y += max(40, bbox[3] - bbox[1]) + 10\n")
        new_lines.append("        else:\n")
        new_lines.append("            y = draw_centered_text(draw, f\"{{zodiac_name}}: {{zodiac_desc}}\", y, fonts['content'], template['text'])\n")
        new_lines.append("            y += SPACING['after_zodiac_item']\n")
        
        # 跳过旧的 emoji 代码块（大约 20 行）
        skip_until_line = i + 20
        continue
    
    # 如果还在跳过范围内，继续跳过
    if skip_until_line > 0 and i < skip_until_line:
        continue
    
    # 否则添加当前行
    new_lines.append(line)

# 写回文件
with open(script_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("OK! Applied V3.0.4 fixes:")
print("  1. Page 1 layout compressed")
print("  2. Zodiac signs now use PNG icons")
