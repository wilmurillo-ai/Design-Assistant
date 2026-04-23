#!/usr/bin/env python3
"""
小红书笔记发布脚本
支持本地签名发布（无需额外服务）

用法:
    python3 publish.py --title "标题" --desc "正文" --images a.jpg b.jpg c.jpg [--private]

环境变量:
    XHS_COOKIE=your_cookie_string
    (或从 ~/.config/xiaohongshu/cookie.txt 自动读取)
"""
import argparse, os, sys, json, re
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
for path in [Path.home() / '.config/xiaohongshu/cookie.txt',
             Path.home() / '.config/xhs/cookie.txt',
             Path(__file__).parent.parent / '.env',
             Path.cwd() / '.env']:
    if path.exists():
        try:
            content = path.read_text().strip()
            if 'web_session=' in content or 'a1=' in content:
                os.environ.setdefault('XHS_COOKIE', content)
        except: pass

dotenv_path = Path(__file__).parent.parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)

XHS_COOKIE = os.environ.get('XHS_COOKIE', '')
if not XHS_COOKIE:
    # 尝试从 cookie 文件读取
    for p in [Path.home() / '.config/xiaohongshu/cookie.txt']:
        if p.exists():
            XHS_COOKIE = p.read_text().strip()
            break

if not XHS_COOKIE:
    print("错误: 未找到 XHS_COOKIE，请设置环境变量或在 ~/.config/xiaohongshu/cookie.txt 中放置cookie")
    sys.exit(1)

import requests

BASE_URL = "https://www.xiaohongshu.com"

HEADERS = {
    "Cookie": XHS_COOKIE,
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.xiaohongshu.com/",
    "Origin": "https://www.xiaohongshu.com",
}

def upload_image(image_path: str) -> dict:
    """上传单张图片，返回 file_id"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片不存在: {image_path}")

    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
        data = {'platform': 'web', 'topic': 'web_note'}
        resp = requests.post(
            f"{BASE_URL}/api/sns/web/v1/image_upload",
            files=files, data=data, headers=HEADERS, timeout=30
        )

    result = resp.json()
    if result.get('success') or result.get('code') == 0:
        return result.get('data', result.get('result', {}))
    raise Exception(f"图片上传失败: {result}")


def upload_images(image_paths: list) -> list:
    """上传多张图片，返回 file_id 列表"""
    uploaded = []
    for i, path in enumerate(image_paths, 1):
        print(f"  上传第{i}张图片: {os.path.basename(path)}")
        data = upload_image(path)
        # 尝试从嵌套结构中提取 file_id
        file_id = (data.get('file_id') or data.get('fileId')
                   or data.get('results', {}).get('file_id')
                   if isinstance(data, dict) else None)
        uploaded.append(file_id or data)
        print(f"    file_id: {uploaded[-1]}")
    return uploaded


def publish_note(title: str, desc: str, image_paths: list, as_private: bool = False) -> dict:
    """发布小红书笔记"""
    print(f"🚀 准备发布笔记（本地模式）...")
    print(f"  📌 标题: {title}")
    print(f"  📝 描述: {desc[:50]}...")
    print(f"  🖼️ 图片数量: {len(image_paths)}")

    # 上传图片
    print("📤 开始上传图片...")
    file_ids = upload_images(image_paths)

    # 构建笔记数据
    note_data = {
        "title": title,
        "desc": desc,
        "at": [],
        "postTime": "",
        "symbol": [],
        "imageIds": file_ids,
        "source": "pc_web_aladdin",
        "topic": {"id": ""},
        "visibleInfo": {"visible": 7 if as_private else 0},
    }

    # 发布
    resp = requests.post(
        f"{BASE_URL}/api/sns/web/v1/feed/create",
        json=note_data,
        headers={**HEADERS, "Content-Type": "application/json"},
        timeout=30
    )

    result = resp.json()
    print(f"\n📬 响应: code={result.get('code')}, success={result.get('success')}")

    if result.get('success') or result.get('code') == 0:
        note_id = result.get('data', {}).get('id', '')
        share_link = f"https://www.xiaohongshu.com/explore/{note_id}"
        print(f"\n✨ 笔记发布成功！")
        print(f"  📎 笔记ID: {note_id}")
        print(f"  🔗 链接: {share_link}")
        print(f"  📌 状态: {'私密' if as_private else '公开'}")
        return {'id': note_id, 'link': share_link, 'success': True}
    else:
        print(f"\n❌ 发布失败: {result}")
        return {'success': False, 'error': result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='小红书笔记发布工具')
    parser.add_argument('--title', required=True, help='笔记标题')
    parser.add_argument('--desc', required=True, help='笔记正文')
    parser.add_argument('--images', nargs='+', required=True, help='图片路径')
    parser.add_argument('--private', action='store_true', help='私密发布')
    args = parser.parse_args()

    result = publish_note(args.title, args.desc, args.images, args.private)
    if not result.get('success'):
        sys.exit(1)
