#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成黄历视频 - 带背景音乐（音量加大版）
"""

import subprocess
import os

os.chdir(r"C:\Users\liuyan\.openclaw\workspace\skills\almanac-creator\reports")

# 文件
images = [
    "20260415_黄历.png",
    "20260415_黄历_养生.png",
    "20260415_黄历_故事.png"
]
audio = r"C:\Users\liuyan\.openclaw\workspace\video\佛门清净.mp3"
output = "20260415_黄历_视频_音乐增强.mp4"

print("生成音量增强版视频...")

# 音量提高到60% (0.6)
cmd = [
    "ffmpeg", "-y",
    "-stream_loop", "2", "-i", audio,
    "-loop", "1", "-i", images[0],
    "-loop", "1", "-i", images[1],
    "-loop", "1", "-i", images[2],
    "-filter_complex",
    "[0:a]volume=0.6[a];[1:v]scale=1080:1400,trim=duration=10,fade=t=out:st=9:d=1[v0];"
    "[2:v]scale=1080:1400,trim=duration=10,fade=t=in:st=0:d=1,fade=t=out:st=9:d=1[v1];"
    "[3:v]scale=1080:1400,trim=duration=10,fade=t=in:st=0:d=1[v2];"
    "[v0][v1][v2]concat=n=3:v=1:a=0[outv]",
    "-map", "[outv]", "-map", "[a]",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "23",
    "-c:a", "aac", "-b:a", "128k",
    "-shortest",
    output
]

result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

if result.returncode == 0:
    size = os.path.getsize(output)
    print(f"生成成功！文件大小: {size/1024/1024:.2f} MB")
    print(f"音量: 60%")
else:
    print(f"生成失败: {result.stderr}")