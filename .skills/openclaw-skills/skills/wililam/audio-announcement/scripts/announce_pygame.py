#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio Announcement Player - PyGame Version (Optimized)
使用 pygame.mixer 播放，高质量、低延迟
需要: pip install pygame edge-tts
"""

import os
import sys
import time
import tempfile
import subprocess
import asyncio
from pathlib import Path

try:
    import pygame
except ImportError:
    print("[ERROR] pygame not installed. Run: pip install pygame", file=sys.stderr)
    sys.exit(1)

try:
    import edge_tts
except ImportError:
    print("[ERROR] edge-tts not installed. Run: pip install edge-tts", file=sys.stderr)
    sys.exit(1)

# 配置
CACHE_DIR = os.path.expanduser("~/.cache/audio-announcement")
MAX_RETRIES = 3

# 音色映射
VOICES = {
    "zh": "zh-CN-XiaoxiaoNeural",
    "zh-m": "zh-CN-YunxiNeural",
    "en": "en-US-JennyNeural",
    "en-m": "en-US-GuyNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
}

# 消息前缀
PREFIXES = {
    "task": "任务: ",
    "complete": "完成: ",
    "error": "警告: ",
    "custom": ""
}

# 根据时间调整音量
def get_volume():
    hour = time.localtime().tm_hour
    if 12 <= hour < 14 or hour >= 22 or hour < 8:
        return 0.3  # 午休和夜间降低音量
    return 0.5  # 正常音量

def ensure_dirs():
    os.makedirs(CACHE_DIR, exist_ok=True)

def generate_mp3(text, voice, output_path):
    """使用 edge-tts 生成 MP3 (异步)"""
    async def tts():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    try:
        asyncio.run(tts())
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"[ERROR] TTS generation failed: {e}", file=sys.stderr)
        return False

def play_mp3_pygame(mp3_path, volume=0.5):
    """使用 pygame mixer 播放 MP3，带等待完成"""
    try:
        # 初始化 mixer（只初始化一次，持久化）
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()

        # 等待播放完成（使用更高频率检查，更平滑）
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(30)

        return True
    except Exception as e:
        print(f"[ERROR] Playback failed: {e}", file=sys.stderr)
        return False

def announce(announce_type, message, lang="zh"):
    """主播报函数"""
    voice = VOICES.get(lang, VOICES["zh"])
    volume = get_volume()
    prefix = PREFIXES.get(announce_type, "")
    full_message = prefix + message

    # 创建临时 MP3 文件
    mp3_path = tempfile.mktemp(suffix='.mp3')

    try:
        # 生成语音
        print(f"[INFO] 生成语音: {full_message[:30]}...", file=sys.stderr)
        if not generate_mp3(full_message, voice, mp3_path):
            print("[ERROR] Failed to generate speech", file=sys.stderr)
            return False

        # 播放语音
        if play_mp3_pygame(mp3_path, volume):
            print("[INFO] 播报成功", file=sys.stderr)
            return True
        else:
            print("[ERROR] Playback failed", file=sys.stderr)
            return False

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return False
    finally:
        # 清理临时文件
        if os.path.exists(mp3_path):
            try:
                os.unlink(mp3_path)
            except:
                pass

def main():
    if len(sys.argv) < 3:
        print("用法: python announce_pygame.py <type> <message> [lang]", file=sys.stderr)
        print("示例: python announce_pygame.py complete '任务完成' zh", file=sys.stderr)
        print("", file=sys.stderr)
        print("类型: task, complete, error, custom", file=sys.stderr)
        print("语言: zh, en, ja, ko, es, fr, de", file=sys.stderr)
        sys.exit(1)

    announce_type = sys.argv[1]
    message = sys.argv[2]
    lang = sys.argv[3] if len(sys.argv) > 3 else "zh"

    ensure_dirs()
    success = announce(announce_type, message, lang)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
