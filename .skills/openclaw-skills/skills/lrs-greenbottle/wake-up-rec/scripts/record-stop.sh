#!/bin/bash
# 录屏停止脚本 - 延迟9秒后停止录制

echo "⏳ 延迟9秒后停止录屏..."
sleep 9

# 停止所有ffmpeg录屏进程
killall ffmpeg 2>/dev/null

echo "✅ 录屏已停止"
