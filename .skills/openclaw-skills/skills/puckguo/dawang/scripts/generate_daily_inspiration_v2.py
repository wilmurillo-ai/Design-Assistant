from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

# 创建输出目录
output_dir = "/Users/godspeed/.openclaw/workspaces/dawang/test_output"
os.makedirs(output_dir, exist_ok=True)

# 温暖渐变风格 - 新版本
COLORS = {
    'bg_top': '#FF9A9E',
    'bg_bottom': '#FECFEF',
    'card': '#FFFFFF',
    'text': '#333333',
    'text_light': '#666666',
    'accent': '#FF6B6B',
}

# 创建画布
width, height = 900, 1200
img = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(img)

# 绘制渐变背景
for y in range(height):
    ratio = y / height
    r = int(255 * (1 - ratio) + 254 * ratio)
    g = int(154 * (1 - ratio) + 207 * ratio)
    b = int(158 * (1 - ratio) + 239 * ratio)
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# 尝试加载字体
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 72)
    font_subtitle = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
    font_body = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 36)
    font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
except:
    font_title = ImageFont.load_default()
    font_subtitle = font_title
    font_body = font_title
    font_small = font_title

# 标题
draw.text((width//2, 120), "✨ 每日灵感", font=font_title, fill=COLORS['text'], anchor="mm")
draw.text((width//2, 200), "Stay Positive", font=font_subtitle, fill=COLORS['text_light'], anchor="mm")

# 内容卡片
card_margin = 80
card_top = 300
card_height = 600
# 卡片阴影
draw.rounded_rectangle(
    [card_margin+4, card_top+4, width - card_margin+4, card_top + card_height+4],
    radius=24,
    fill='#E0E0E0'
)
# 卡片主体
draw.rounded_rectangle(
    [card_margin, card_top, width - card_margin, card_top + card_height],
    radius=24,
    fill=COLORS['card']
)

# 引用内容
quotes = [
    "\"代码是写给人看的，",
    "  只是顺便让机器执行。\"",
    "",
    "—— Harold Abelson"
]

y_pos = card_top + 100
for line in quotes:
    if line:
        draw.text((width//2, y_pos), line, font=font_body, fill=COLORS['text'], anchor="mm")
    y_pos += 60

# 装饰线
draw.line([(card_margin + 100, card_top + 350), (width - card_margin - 100, card_top + 350)], 
          fill=COLORS['accent'], width=3)

# 底部提示
tips = [
    "💡 今日提示：保持好奇心",
    "🎯 专注于当下",
    "☕ 记得休息"
]

y_pos = card_top + 400
for tip in tips:
    draw.text((width//2, y_pos), tip, font=font_small, fill=COLORS['text_light'], anchor="mm")
    y_pos += 50

# 底部时间
draw.text((width//2, height - 100), datetime.now().strftime("%Y年%m月%d日"), 
          font=font_small, fill=COLORS['text_light'], anchor="mm")

# 保存图片 - 使用全新文件名
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(output_dir, f"daily_inspiration_{timestamp}.png")
img.save(output_path, quality=95)

print(f"✅ 图片已生成: {output_path}")
