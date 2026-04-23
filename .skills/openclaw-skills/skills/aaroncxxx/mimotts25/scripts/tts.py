#!/usr/bin/env python3
"""MiMo TTS 2.5 — 小米大模型语音合成"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://api.xiaomimimo.com/v1"
MODEL = "mimo-v2-tts"

VOICES = ["mimo_default", "default_zh", "default_en"]


def synthesize(text: str, voice: str, api_key: str, style: str | None = None,
               user_msg: str | None = None, fmt: str = "wav") -> bytes:
    """Call MiMo TTS API and return raw audio bytes."""
    assistant_content = text
    if style:
        assistant_content = f"<style>{style}</style>{text}"

    messages = []
    if user_msg:
        messages.append({"role": "user", "content": user_msg})
    messages.append({"role": "assistant", "content": assistant_content})

    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "audio": {"format": fmt, "voice": voice},
    }).encode()

    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        print(f"API error {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)

    audio_b64 = body["choices"][0]["message"]["audio"]["data"]
    return base64.b64decode(audio_b64)


def main():
    parser = argparse.ArgumentParser(description="MiMo TTS 2.5 语音合成")
    parser.add_argument("text", help="要合成的文本")
    parser.add_argument("-o", "--output", default="output.wav",
                        help="输出文件路径 (default: output.wav)")
    parser.add_argument("-v", "--voice", default="mimo_default", choices=VOICES,
                        help="音色预设 (default: mimo_default)")
    parser.add_argument("-s", "--style", default=None,
                        help="风格标签, e.g. '开心', '东北话', '悄悄话'")
    parser.add_argument("-f", "--format", default="wav", choices=["wav"],
                        help="音频格式 (default: wav)")
    parser.add_argument("--user-msg", default=None,
                        help="可选的用户角色上下文消息")
    parser.add_argument("--api-key", default=None,
                        help="API Key (或设置 MIMO_API_KEY 环境变量)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("MIMO_API_KEY")
    if not api_key:
        print("Error: 请提供 --api-key 或设置 MIMO_API_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    audio = synthesize(
        text=args.text,
        voice=args.voice,
        api_key=api_key,
        style=args.style,
        user_msg=args.user_msg,
        fmt=args.format,
    )

    with open(args.output, "wb") as f:
        f.write(audio)

    print(f"已保存 {len(audio)} 字节 → {args.output}")


if __name__ == "__main__":
    main()
