#!/usr/bin/env python3
"""
小红书笔记图片卡片渲染工具
支持多模板、文泉驿字体、Pexels配图

用法:
    python3 render_cards.py \
        --title "标题" \
        --subtitle "副标题" \
        --texts "文字1|文字2|文字3" \
        --output_prefix "card" \
        --theme "dark"
"""
import argparse, os, sys, random, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# 默认字体
FONT_WQY = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
FONT_DROID = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
FONT_DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H = 1080, 1440

def get_font(size, prefer='wqy'):
    path = FONT_WQY if prefer == 'wqy' else FONT_DROID
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.truetype(FONT_DROID, size)


def smart_crop(path, tw=W, th=H):
    """智能裁剪图片到指定尺寸"""
    img = Image.open(path).convert('RGB')
    iw, ih = img.size
    scale = max(tw/iw, th/ih)
    nw, nh = int(iw*scale), int(ih*scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    l = max(0, (nw-tw)//2)
    t = max(0, (nh-th)//2)
    return img.crop((l, t, l+tw, t+th))


def render_cover(photo_path, title, subtitle, tags, brand="", theme='dark'):
    """渲染封面卡片（照片+底部文字块）"""
    photo = smart_crop(photo_path)
    canvas = Image.new('RGB', (W, H), (20, 20, 25))
    canvas.paste(photo, (0, 0))

    box_y = int(H * 0.55)
    dark = Image.new('RGB', (W, H - box_y), (15, 15, 20))
    canvas.paste(dark, (0, box_y))

    d = ImageDraw.Draw(canvas)
    fnt = lambda s: get_font(s)

    # 标题
    lw = fnt(56).getlength(title)
    d.text(((W-lw)//2, box_y+40), title, fill=(255, 235, 150), font=fnt(56))

    # 副标题
    if subtitle:
        sw = fnt(24).getlength(subtitle)
        d.text(((W-sw)//2, box_y+130), subtitle, fill=(195, 215, 200), font=fnt(24))

    # 标签
    if tags:
        tw = fnt(20).getlength(tags)
        d.text(((W-tw)//2, box_y+190), tags, fill=(160, 190, 160), font=fnt(20))

    # 品牌
    if brand:
        bw = fnt(16).getlength(brand)
        d.text(((W-bw)//2, H-50), brand, fill=(100, 100, 115), font=fnt(16))

    return canvas


def render_opinion(texts, theme='light'):
    """渲染观点卡片（干净背景+大字排版）"""
    bg = (250, 248, 245) if theme == 'light' else (25, 22, 30)
    text_col = (40, 35, 30) if theme == 'light' else (255, 235, 150)
    sub_col = (100, 95, 85) if theme == 'light' else (180, 175, 200)
    accent = (200, 80, 50) if theme == 'light' else (255, 200, 100)

    canvas = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(canvas)
    fnt = lambda s: get_font(s)

    y = 80
    for line in texts:
        if isinstance(line, dict):
            size = line.get('size', 32)
            color = line.get('color', text_col)
            text = line.get('text', '')
        else:
            size = 32
            color = text_col
            text = str(line)

        lw = fnt(size).getlength(text)
        d.text(((W-lw)//2 if text.startswith('「') or len(text) < 15 else 80, y), text, fill=color, font=fnt(size))
        y += size + 20

    return canvas


def render_finish(photo_path, main_text, sub_text, highlight, theme='dark'):
    """渲染结尾卡片（照片+品牌文字）"""
    photo = smart_crop(photo_path)
    canvas = Image.new('RGB', (W, H), (15, 12, 25))
    canvas.paste(photo, (0, 0))

    box_y = int(H * 0.50)
    dark = Image.new('RGB', (W, H-box_y), (10, 8, 18))
    canvas.paste(dark, (0, box_y))

    d = ImageDraw.Draw(canvas)
    fnt = lambda s: get_font(s)

    y = box_y + 50
    d.text((80, y), main_text, fill=(255, 230, 170), font=fnt(46))
    y += 90

    for line in sub_text:
        lw = fnt(26).getlength(line)
        d.text((80, y), line, fill=(140, 135, 155), font=fnt(26))
        y += 45

    if highlight:
        y += 30
        d.line([(80, y), (W-80, y)], fill=(90, 70, 50), width=2)
        y += 25
        d.text((80, y), highlight, fill=(195, 165, 90), font=fnt(22))

    return canvas


def render_all(title, subtitle, main_text, sub_texts, highlight,
               photo1_path, photo2_path, output_prefix="xhs"):
    """生成三张卡片"""
    os.makedirs('/tmp/xhs_rendered', exist_ok=True)

    cards = [
        render_cover(photo1_path, title, subtitle, "", theme='dark'),
        render_opinion(main_text, theme='light'),
        render_finish(photo2_path, main_text[0] if isinstance(main_text, list) else main_text,
                      sub_texts, highlight, theme='dark'),
    ]

    paths = []
    for i, card in enumerate(cards, 1):
        path = f"/tmp/xhs_rendered/{output_prefix}_card{i}.jpg"
        card.save(path, quality=92)
        paths.append(path)
        print(f"Card {i}: {os.path.getsize(path)//1024}KB → {path}")

    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--title', required=True)
    parser.add_argument('--subtitle', default="")
    parser.add_argument('--texts', help='Pipe-separated texts for card 2')
    parser.add_argument('--photo1', help='Background photo for card 1')
    parser.add_argument('--photo2', help='Background photo for card 3')
    parser.add_argument('--output', default='xhs')
    args = parser.parse_args()

    texts = args.texts.split('|') if args.texts else []

    if args.photo1 and args.photo2:
        paths = render_all(
            args.title, args.subtitle,
            texts, texts, "",
            args.photo1, args.photo2,
            args.output
        )
        print(f"\n✅ 生成完成: {paths}")
    else:
        print("用法示例:")
        print(f"  python3 {__file__} --title '标题' --subtitle '副标题' --texts '观点1|观点2' --photo1 a.jpg --photo2 b.jpg")
