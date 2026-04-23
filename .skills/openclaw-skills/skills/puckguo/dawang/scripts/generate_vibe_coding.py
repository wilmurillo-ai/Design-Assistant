from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

# 创建输出目录
output_dir = "/Users/godspeed/.openclaw/workspaces/dawang/test_output"
os.makedirs(output_dir, exist_ok=True)

# 深色科技风格
COLORS = {
    'bg': '#0D1117',           # GitHub 深色背景
    'card': '#161B22',         # 卡片背景
    'border': '#30363D',       # 边框
    'text': '#C9D1D9',         # 主文字
    'text_secondary': '#8B949E',  # 次要文字
    'accent': '#58A6FF',       # 蓝色强调
    'accent_green': '#238636', # 绿色
    'accent_purple': '#8957E5', # 紫色
}

# 创建画布
width, height = 900, 1200
img = Image.new('RGB', (width, height), COLORS['bg'])
draw = ImageDraw.Draw(img)

# 绘制装饰网格
for i in range(0, width, 50):
    draw.line([(i, 0), (i, height)], fill='#21262D', width=1)
for i in range(0, height, 50):
    draw.line([(0, i), (width, i)], fill='#21262D', width=1)

# 尝试加载字体
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 64)
    font_subtitle = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
    font_body = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
    font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
    font_code = ImageFont.truetype("/System/Library/Fonts/SFMono-Regular.otf", 28)
except:
    font_title = ImageFont.load_default()
    font_subtitle = font_title
    font_body = font_title
    font_small = font_title
    font_code = font_title

# 顶部装饰条
draw.rectangle([0, 0, width, 6], fill=COLORS['accent'])

# 标题区域
draw.text((60, 80), "🚀", font=font_title, fill=COLORS['accent'])
draw.text((140, 80), "Vibe Coding", font=font_title, fill=COLORS['text'])
draw.text((60, 160), "AI 驱动开发实战指南", font=font_subtitle, fill=COLORS['text_secondary'])

# 主内容卡片
card_margin = 60
card_top = 260
card_height = 700
draw.rounded_rectangle(
    [card_margin, card_top, width - card_margin, card_top + card_height],
    radius=16,
    fill=COLORS['card'],
    outline=COLORS['border'],
    width=2
)

# 代码块样式内容
content_items = [
    ("💡", "核心原则", COLORS['accent']),
    ("", "• 用自然语言描述需求", COLORS['text']),
    ("", "• AI 生成代码实现", COLORS['text']),
    ("", "• 快速迭代验证", COLORS['text']),
    ("", "", COLORS['text']),  # 空行
    ("⚡", "效率提升", COLORS['accent_green']),
    ("", "• 开发速度提升 10x", COLORS['text']),
    ("", "• 降低技术门槛", COLORS['text']),
    ("", "• 专注创意而非语法", COLORS['text']),
    ("", "", COLORS['text']),  # 空行
    ("🎯", "适用场景", COLORS['accent_purple']),
    ("", "• MVP 快速验证", COLORS['text']),
    ("", "• 自动化脚本", COLORS['text']),
    ("", "• 原型设计", COLORS['text']),
]

y_pos = card_top + 40
for emoji, text, color in content_items:
    if emoji:
        draw.text((card_margin + 30, y_pos), emoji, font=font_body, fill=color)
        draw.text((card_margin + 80, y_pos), text, font=font_body, fill=color)
    elif text:
        draw.text((card_margin + 30, y_pos), text, font=font_body, fill=color)
    y_pos += 50

# 底部状态栏
draw.rectangle([0, height - 80, width, height], fill=COLORS['card'])
draw.text((60, height - 55), "● 在线", font=font_small, fill=COLORS['accent_green'])
draw.text((200, height - 55), "Python", font=font_small, fill=COLORS['text_secondary'])
draw.text((350, height - 55), "TypeScript", font=font_small, fill=COLORS['text_secondary'])
draw.text((550, height - 55), datetime.now().strftime("%Y-%m-%d"), font=font_small, fill=COLORS['text_secondary'])

# 保存图片
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(output_dir, f"VibeCoding指南_{timestamp}.png")
img.save(output_path, quality=95)

print(f"✅ 图片已生成: {output_path}")
