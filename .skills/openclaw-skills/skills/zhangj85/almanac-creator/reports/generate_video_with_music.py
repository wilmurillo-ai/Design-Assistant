#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成黄历视频 - 带背景音乐
3张图片每张10秒 + 背景音乐
"""

import subprocess
import os

# 设置工作目录
os.chdir(r"C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\reports")

# 图片文件
images = [
    "20260415_黄历.png",
    "20260415_黄历_养生.png",
    "20260415_黄历_故事.png"
]

# 音频文件
audio = r"C:\Users\liuyan\.openclaw\workspace\video\佛门清净.mp3"

# 输出视频
output = "20260415_黄历_视频_带音乐.mp4"

# 检查文件是否存在
for img in images:
    if not os.path.exists(img):
        print(f"错误：找不到图片 {img}")
        exit(1)

if not os.path.exists(audio):
    print(f"错误：找不到音频 {audio}")
    exit(1)

print("正在生成30秒黄历视频（带背景音乐）...")
print(f"图片: {images}")
print(f"音频: {audio}")
print(f"输出: {output}")

# FFmpeg命令：3张图片（每张10秒）+ 背景音乐循环
cmd = [
    "ffmpeg", "-y",
    "-stream_loop", "2", "-i", audio,  # 循环音频2次（30秒）
    "-loop", "1", "-i", images[0],
    "-loop", "1", "-i", images[1],
    "-loop", "1", "-i", images[2],
    "-filter_complex",
    f"[0:a]volume=0.3[a];[1:v]scale=1080:1400,trim=duration=10,fade=t=out:st=9:d=1[v0];"
    f"[2:v]scale=1080:1400,trim=duration=10,fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v1];"
    f"[3:v]scale=1080:1400,trim=duration=10,fade=t=in:st=0:d=1[v2];"
    f"[v0][v1][v2]concat=n=3:v=1:a=0[outv]",
    "-map", "[outv]", "-map", "[a]",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "23",
    "-c:a", "aac", "-b:a", "128k",
    "-shortest",
    output
]

# 执行命令
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

if result.returncode == 0:
    print(f"视频生成成功！")
    print(f"文件: {os.path.abspath(output)}")
    size = os.path.getsize(output)
    print(f"文件大小: {size/1024/1024:.2f} MB")
else:
    print(f"生成失败！")
    print(result.stderr)