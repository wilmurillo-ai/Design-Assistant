#!/usr/bin/env python3
"""
Pexels免费图片获取工具
自动下载高质量配图，无需API Key

用法:
    python3 fetch_image.py --query "coffee latte" --count 5
    python3 fetch_image.py --url "https://images.pexels.com/..." --output /tmp/img.jpg
"""
import argparse, os, urllib.request, random

PROXY = "socks5://127.0.0.1:1080"
OUTPUT_DIR = "/tmp/xhs_imgs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def proxy_url(url):
    """通过新加坡隧道访问URL"""
    proxies = {"http": PROXY, "https": PROXY}
    proxy_handler = urllib.request.ProxyHandler(proxies)
    opener = urllib.request.build_opener(proxy_handler)
    return opener

# 预置高质量图片URL（直接可下载，无水印）
CURATED_URLS = {
    # 咖啡/生活方式
    "coffee": [
        ("https://images.pexels.com/photos/312418/pexels-photo-312418.jpeg?auto=compress&cs=tinysrgb&w=1920", "latte_art.jpg"),
        ("https://images.pexels.com/photos/302899/pexels-photo-302899.jpeg?auto=compress&cs=tinysrgb&w=1920", "coffee_cup.jpg"),
        ("https://images.pexels.com/photos/2074130/pexels-photo-2074130.jpeg?auto=compress&cs=tinysrgb&w=1920", "white_cup.jpg"),
        ("https://images.pexels.com/photos/2788792/pexels-photo-2788792.jpeg?auto=compress&cs=tinysrgb&w=1920", "cafe_shop.jpg"),
    ],
    # 自然/山川
    "mountain": [
        ("https://images.pexels.com/photos/2901209/pexels-photo-2901209.jpeg?auto=compress&cs=tinysrgb&w=1920", "mountain1.jpg"),
        ("https://images.pexels.com/photos/1366919/pexels-photo-1366919.jpeg?auto=compress&cs=tinysrgb&w=1920", "mist_mountain.jpg"),
        ("https://images.pexels.com/photos/1261728/pexels-photo-1261728.jpeg?auto=compress&cs=tinysrgb&w=1920", "lake_mountain.jpg"),
    ],
    # 夜空/抽象
    "night": [
        ("https://images.pexels.com/photos/110854/pexels-photo-110854.jpeg?auto=compress&cs=tinysrgb&w=1920", "starry_night.jpg"),
    ],
    # 植物/茉莉
    "jasmine": [
        ("https://images.pexels.com/photos/761854/pexels-photo-761854.jpeg?auto=compress&cs=tinysrgb&w=1920", "jasmine_tea.jpg"),
        ("https://images.pexels.com/photos/1358278/pexels-photo-1358278.jpeg?auto=compress&cs=tinysrgb&w=1920", "white_flowers.jpg"),
    ],
    # 天空/云
    "sky": [
        ("https://images.pexels.com/photos/167699/pexels-photo-167699.jpeg?auto=compress&cs=tinysrgb&w=1920", "cloudy_sky.jpg"),
    ],
    # 海洋
    "ocean": [
        ("https://images.pexels.com/photos/1049298/pexels-photo-1049298.jpeg?auto=compress&cs=tinysrgb&w=1920", "ocean_waves.jpg"),
    ],
    # 森林
    "forest": [
        ("https://images.pexels.com/photos/1149831/pexels-photo-1149831.jpeg?auto=compress&cs=tinysrgb&w=1920", "forest_path.jpg"),
    ],
    # 书籍/学习
    "book": [
        ("https://images.pexels.com/photos/159711/books-bookstore-book-reading-159711.jpeg?auto=compress&cs=tinysrgb&w=1920", "books.jpg"),
    ],
    # 工作/科技
    "tech": [
        ("https://images.pexels.com/photos/4050291/pexels-photo-4050291.jpeg?auto=compress&cs=tinysrgb&w=1920", "workspace.jpg"),
        ("https://images.pexels.com/photos/1957477/pexels-photo-1957477.jpeg?auto=compress&cs=tinysrgb&w=1920", "minimal_desk.jpg"),
    ],
    # 抽象纹理
    "abstract": [
        ("https://images.pexels.com/photos/1626462/pexels-photo-1626462.jpeg?auto=compress&cs=tinysrgb&w=1920", "abstract1.jpg"),
        ("https://images.pexels.com/photos/1626481/pexels-photo-1626481.jpeg?auto=compress&cs=tinysrgb&w=1920", "abstract2.jpg"),
    ],
}

def download(url, output_path, max_size_mb=2):
    """下载文件（通过代理）"""
    proxy_handler = urllib.request.ProxyHandler({
        "http": PROXY, "https": PROXY
    })
    opener = urllib.request.build_opener(proxy_handler)

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    with opener.open(req, timeout=30) as resp:
        data = resp.read()

    # 大小检查
    size_mb = len(data) / 1024 / 1024
    if size_mb > max_size_mb:
        print(f"  文件过大 ({size_mb:.1f}MB)，跳过")
        return None

    with open(output_path, 'wb') as f:
        f.write(data)
    return len(data)


def fetch_by_keyword(keyword, count=3):
    """根据关键词随机获取图片"""
    keyword = keyword.lower()
    matched = []

    # 精确匹配分类
    for kw, urls in CURATED_URLS.items():
        if kw in keyword:
            matched.extend(urls)

    # 泛匹配
    if not matched:
        all_urls = []
        for urls in CURATED_URLS.values():
            all_urls.extend(urls)
        matched = all_urls

    random.shuffle(matched)
    selected = matched[:count]

    results = []
    for url, fname in selected:
        out = os.path.join(OUTPUT_DIR, fname)
        size = download(url, out)
        if size:
            mb = size / 1024 / 1024
            results.append(out)
            print(f"OK: {fname} ({mb:.0f}KB) → {out}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pexels图片获取')
    parser.add_argument('--query', help='搜索关键词')
    parser.add_argument('--count', type=int, default=3, help='下载数量')
    parser.add_argument('--url', help='直接下载URL')
    parser.add_argument('--output', help='输出路径')
    args = parser.parse_args()

    if args.url:
        out = args.output or os.path.join(OUTPUT_DIR, "downloaded.jpg")
        size = download(args.url, out)
        print(f"OK: {out} ({size//1024}KB)")
    elif args.query:
        paths = fetch_by_keyword(args.query, args.count)
        print(f"\n下载完成 {len(paths)} 张图片:")
        for p in paths:
            print(f"  {p}")
    else:
        print("可用分类:", ", ".join(CURATED_URLS.keys()))
        print("示例: python3 fetch_image.py --query coffee --count 3")
