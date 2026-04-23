from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

# 创建输出目录
output_dir = "/Users/godspeed/.openclaw/workspaces/dawang/test_output"
os.makedirs(output_dir, exist_ok=True)

# 创建一张简单的测试图片
width, height = 800, 600
img = Image.new('RGB', (width, height), '#FF6B6B')  # 红色背景
draw = ImageDraw.Draw(img)

# 尝试加载字体
try:
    font_large = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 80)
    font_medium = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 50)
except:
    font_large = ImageFont.load_default()
    font_medium = font_large

# 绘制文字
draw.text((width//2, height//2 - 100), "🔴", font=font_large, fill='white', anchor="mm")
draw.text((width//2, height//2), "测试图片", font=font_large, fill='white', anchor="mm")
draw.text((width//2, height//2 + 100), datetime.now().strftime("%H:%M:%S"), font=font_medium, fill='white', anchor="mm")

# 保存
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = os.path.join(output_dir, f"测试图片_{timestamp}.png")
img.save(output_path, quality=95)

print(f"✅ 测试图片已生成: {output_path}")
