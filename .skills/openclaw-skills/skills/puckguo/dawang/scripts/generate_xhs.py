from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

# 创建输出目录
output_dir = "/Users/godspeed/.openclaw/workspaces/dawang/test_output"
os.makedirs(output_dir, exist_ok=True)

# 小红书风格配色
COLORS = {
    'bg': '#FF2442',           # 小红书红
    'bg_gradient': '#FF6B7A',  # 浅红
    'text': '#FFFFFF',         # 白色
    'accent': '#FFD700',       # 金色点缀
    'dark': '#1A1A2E',         # 深色文字
}

# 创建画布 - 小红书 3:4 比例
width, height = 900, 1200
img = Image.new('RGB', (width, height), COLORS['bg'])
draw = ImageDraw.Draw(img)

# 绘制渐变背景
for y in range(height):
    ratio = y / height
    r = int(255 * (1 - ratio * 0.3))
    g = int(36 + ratio * 50)
    b = int(66 + ratio * 30)
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# 尝试加载字体
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 72)
    font_subtitle = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 48)
    font_body = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
    font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
except:
    font_title = ImageFont.load_default()
    font_subtitle = font_title
    font_body = font_title
    font_small = font_title

# 绘制装饰元素
# 顶部装饰线
draw.rectangle([50, 80, 850, 85], fill=COLORS['accent'])

# 标题
title = "💪 健身小白必看"
draw.text((width//2, 200), title, font=font_title, fill=COLORS['text'], anchor="mm")

# 副标题
subtitle = "新手入门完全指南"
draw.text((width//2, 300), subtitle, font=font_subtitle, fill=COLORS['accent'], anchor="mm")

# 内容区域背景 - 圆角矩形
corner_radius = 30
content_box = [80, 400, 820, 1000]
draw.rounded_rectangle(content_box, radius=corner_radius, fill='white')

# 内容要点
content_items = [
    "✅ 制定合理的训练计划",
    "✅ 掌握正确的动作姿势", 
    "✅ 循序渐进增加强度",
    "✅ 注意休息和恢复",
    "✅ 配合合理的饮食"
]

y_pos = 480
for item in content_items:
    draw.text((120, y_pos), item, font=font_body, fill=COLORS['dark'])
    y_pos += 100

# 底部标签
tags = "#健身 #新手入门 #健身教程 #运动"
draw.text((width//2, 1080), tags, font=font_small, fill=COLORS['text'], anchor="mm")

# 保存图片
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(output_dir, f"小红书笔记_健身_{timestamp}.png")
img.save(output_path, quality=95)

print(f"✅ 图片已生成: {output_path}")
