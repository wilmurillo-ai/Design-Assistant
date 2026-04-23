#!/usr/bin/env python3
"""
从七牛云下载文件到本地

用途：通过七牛 URL 下载文件

使用方式：
  python3 xgjk-base-skills/scripts/file_storage/qiniu_download.py <url> [--output <dir>] [--filename <name>]

说明：
  七牛公开 URL 无需 token，直接 HTTP GET 下载。

被其他脚本引用：
  from file_storage.qiniu_download import download_file
"""

import sys
import os
import argparse
import urllib.request
import urllib.error
import ssl


def _ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def download_file(url: str, output_dir: str = ".", filename: str = "") -> str:
    """
    下载文件到本地。

    Args:
        url:        七牛文件 URL
        output_dir: 输出目录（默认当前目录）
        filename:   保存文件名（默认从 URL 提取）

    Returns:
        保存的文件完整路径
    """
    if not filename:
        # 从 URL 提取文件名
        path_part = url.split("?")[0]  # 去掉 query string
        filename = os.path.basename(path_part)
        if not filename:
            filename = "downloaded_file"

    os.makedirs(output_dir, exist_ok=True)
    dest = os.path.join(output_dir, filename)

    ctx = _ssl_context()
    req = urllib.request.Request(url, method="GET")

    with urllib.request.urlopen(req, context=ctx, timeout=300) as resp:
        total = resp.headers.get("Content-Length")
        total_kb = int(total) / 1024 if total else 0

        downloaded = 0
        chunk_size = 8192

        with open(dest, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                if total_kb > 0:
                    pct = (downloaded / int(total)) * 100
                    print(f"\r下载中: {downloaded/1024:.1f} / {total_kb:.1f} KB ({pct:.0f}%)", end="", file=sys.stderr)

    if total_kb > 0:
        print("", file=sys.stderr)  # 换行

    return os.path.abspath(dest)


def main():
    parser = argparse.ArgumentParser(description="从七牛云下载文件")
    parser.add_argument("url", help="七牛文件 URL")
    parser.add_argument("--output", "-o", default=".", help="输出目录（默认当前目录）")
    parser.add_argument("--filename", "-f", default="", help="保存文件名（默认从 URL 提取）")
    args = parser.parse_args()

    try:
        saved = download_file(args.url, args.output, args.filename)
        print(f"下载完成: {saved}", file=sys.stderr)
        print(saved)
    except Exception as e:
        print(f"❌ 下载失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
