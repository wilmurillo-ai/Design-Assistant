---
name: bilibili-video-download
description: B站视频下载裁剪压缩工具。下载bilibili视频、裁剪去除边框、压缩到指定大小时使用。支持b23.tv短链和BV号。别名：闹钟视频下载。
---

# 闹钟视频下载

## 依赖

- yt-dlp: pip install yt-dlp, 以 python -m yt_dlp 调用
- ffmpeg/ffprobe: 需在PATH中

## 工作流

### 1. 下载720P视频

固定下载720P分辨率视频(格式ID: 30064+30280):
python -m yt_dlp -f "30064+30280" -o PATH --merge-output-format mp4 URL

说明: 30064为720P视频流,30280为音频流

### 2. 裁剪边框

使用固定裁剪参数直接裁剪:
ffmpeg -y -i IN -vf "crop=792:600:432:56" -c:v libx264 -crf 18 -c:a copy OUT

固定裁剪参数(720p): crop=792:600:432:56

### 3. 剪切视频(固定去除前后各10秒)

**步骤1: 去除前10秒**
ffmpeg -y -i IN -ss 00:00:10 -c:v libx264 -crf 18 -c:a copy TEMP

**步骤2: 获取剩余视频时长**
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 TEMP

**步骤3: 去除后10秒(总时长-10)**
ffmpeg -y -i TEMP -t (duration-10) -c:v libx264 -crf 18 -c:a copy OUT

**说明:** 固定去除片头10秒和片尾10秒，总时长减少20秒

### 4. 压缩到目标大小

**目标：压缩到10MB以内**

**步骤1: 获取视频时长**
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 INPUT_VIDEO

**步骤2: 计算动态码率**
使用Python计算码率参数(以目标10MB为例):
```python
target_MB = 10
duration = 217.345783  # 从步骤1获取的实际时长
vbr = int((target_MB * 0.9 * 8 * 1024) / duration - 64)  # 视频码率
maxrate = int(vbr * 1.5)  # 最大码率
bufsize = int(vbr * 2)    # 缓冲大小
# 示例输出: vbr=275k, maxrate=412k, bufsize=550k
```

计算公式:
- 视频码率: vbr = (target_MB * 0.9 * 8 * 1024) / duration - 64
- 最大码率: maxrate = vbr * 1.5
- 缓冲大小: bufsize = vbr * 2

**步骤3: 执行压缩**
使用计算出的参数执行压缩:
ffmpeg -y -i INPUT_VIDEO -c:v libx264 -b:v 275k -maxrate 412k -bufsize 550k -c:a aac -b:a 64k -ar 44100 OUTPUT_VIDEO

**验证压缩结果:**
ffprobe -v error -show_entries format=size -of default=noprint_wrappers=1:nokey=1 OUTPUT_VIDEO

**实际案例参考:**
- 输入视频: 792x600, 时长217秒, 约22.4MB
- 压缩参数: vbr=275k, maxrate=412k, bufsize=550k
- 输出结果: 约9.0MB, 成功压缩到10MB以内

### 5. 一键脚本

scripts/download_and_process.py:
python scripts/download_and_process.py URL --format_id "30064+30280" --crop "792:600:432:56" --max_size_mb 10
参数: url, --format_id, --crop, --max_size_mb(10), --filename(bilibili_video), --output_dir(Documents)
