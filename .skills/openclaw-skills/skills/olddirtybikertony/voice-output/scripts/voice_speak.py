#!/usr/bin/env python3
"""
voice_speak.py — 中枢语音输出（豆包TTS版）

每次调用：
  python3 voice_speak.py "要说的内容"

不依赖任何常驻进程，直接调用豆包TTS 2.0 API，
生成 MP3 后通过 afplay 播放。

触发条件：Tony 消息含语音请求自然语言
（语音回复、用话说、voice reply 等）
"""

import sys
import json
import urllib.request
import subprocess
import uuid
import tempfile
import os
import base64

# ============== 豆包TTS 配置 ==============
APPID = "8982709936"
ACCESS_TOKEN = "gSlkMz98nDVwnHUwiuDefPjwVFtFNrbw"
CLUSTER = "volcano_tts"

# 默认音色
DEFAULT_VOICE = "zh_female_xiaohe_uranus_bigtts"
DEFAULT_EMOTION = "neutral"
DEFAULT_SPEED = 1.0
DEFAULT_PITCH = 1.0
DEFAULT_ENCODING = "mp3"


def tts_synthesize(
    text: str,
    voice_type: str = DEFAULT_VOICE,
    emotion: str = DEFAULT_EMOTION,
    speed_ratio: float = DEFAULT_SPEED,
    pitch_ratio: float = DEFAULT_PITCH,
    encoding: str = DEFAULT_ENCODING,
) -> bytes:
    """调用豆包TTS 2.0 API，返回音频数据（bytes，MP3格式）"""
    url = "https://openspeech.bytedance.com/api/v1/tts"
    reqid = str(uuid.uuid4())

    payload = {
        "app": {
            "appid": APPID,
            "token": ACCESS_TOKEN,
            "cluster": CLUSTER,
        },
        "user": {"uid": "zhongshu_tts"},
        "audio": {
            "voice_type": voice_type,
            "encoding": encoding,
            "speed_ratio": speed_ratio,
            "volume_ratio": 1.0,
            "pitch_ratio": pitch_ratio,
            "emotion": emotion,
        },
        "request": {
            "reqid": reqid,
            "text": text,
            "text_type": "plain",
            "operation": "query",  # 非流式
        },
    }

    headers = {
        "Authorization": f"Bearer; {ACCESS_TOKEN}",  # 分号，不是空格
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())

    if result.get("code") != 3000:
        raise Exception(f"TTS API error: code={result.get('code')}, msg={result.get('message')}")

    # 响应格式：base64 编码的音频数据
    audio_base64 = result.get("data", "")
    if not audio_base64:
        raise Exception("No audio data in response")
    
    return base64.b64decode(audio_base64)


def speak(
    text: str,
    voice_type: str = DEFAULT_VOICE,
    emotion: str = DEFAULT_EMOTION,
    speed_ratio: float = DEFAULT_SPEED,
    pitch_ratio: float = DEFAULT_PITCH,
) -> bool:
    """文字转语音并播放，成功返回 True"""
    if not text or not text.strip():
        return False

    tmp = tempfile.gettempdir()
    tmp_file = os.path.join(tmp, f"voice_{uuid.uuid4().hex}.mp3")

    try:
        audio_data = tts_synthesize(text, voice_type, emotion, speed_ratio, pitch_ratio)
        print(f"[DoubaoTTS] generated {len(audio_data)} bytes", file=sys.stderr)

        with open(tmp_file, "wb") as f:
            f.write(audio_data)

        result = subprocess.run(
            ["afplay", tmp_file],
            capture_output=True,
            timeout=60,
        )

        if result.returncode == 0:
            print(f"[DoubaoTTS] played: {text[:50]}...", file=sys.stderr)
            return True
        else:
            print(f"[DoubaoTTS] play failed: {result.stderr.decode()[:100]}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"[DoubaoTTS ERROR] {e}", file=sys.stderr)
        return False

    finally:
        if os.path.exists(tmp_file):
            try:
                os.unlink(tmp_file)
            except Exception:
                pass


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("用法: voice_speak.py \"要说的内容\" [voice_type] [emotion] [speed] [pitch]")
        print("示例: voice_speak.py \"你好，我是小何\" zh_female_xiaohe_uranus_bigtts happy 1.0 1.0")
        print(f"\n默认音色: {DEFAULT_VOICE}")
        print(f"默认情绪: {DEFAULT_EMOTION}")
        print(f"默认语速: {DEFAULT_SPEED}")
        print(f"默认音调: {DEFAULT_PITCH}")
        sys.exit(0)

    text = sys.argv[1]
    voice_type = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_VOICE
    emotion = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_EMOTION
    speed = float(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_SPEED
    pitch = float(sys.argv[5]) if len(sys.argv) > 5 else DEFAULT_PITCH

    ok = speak(text, voice_type, emotion, speed, pitch)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
