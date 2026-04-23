#!/usr/bin/env python3
"""
DashengDenoiser API Client - Voice enhancement and noise reduction.
Removes background noise from audio files.
Supports queue status check via --queue.
"""

import sys
import argparse
import json
import requests
from pathlib import Path

API_BASE = "https://llmplus.ai.xiaomi.com"
DEFAULT_ENDPOINT = f"{API_BASE}/dasheng/audio/denoise"
METRICS_PATH = "/dasheng/audio/denoise"


def check_queue(api_base: str = API_BASE) -> dict:
    """查询 denoise 服务的排队情况"""
    url = f"{api_base}/metrics?path={METRICS_PATH}"
    response = requests.post(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    active = data.get("active", 0)
    avg_latency_ms = data.get("avg_latency_ms", 0)
    estimated_wait_ms = active * avg_latency_ms

    return {
        "active": active,
        "avg_latency_ms": round(avg_latency_ms, 1),
        "estimated_wait_ms": round(estimated_wait_ms, 1),
        "estimated_wait_sec": round(estimated_wait_ms / 1000, 1),
        "total_processed": data.get("total", 0),
        "min_latency_ms": data.get("min_latency_ms", 0),
        "max_latency_ms": data.get("max_latency_ms", 0),
        "raw": data
    }


def format_queue_status(queue_info: dict) -> str:
    """将排队信息格式化为用户友好的文本"""
    active = queue_info["active"]
    avg_ms = queue_info["avg_latency_ms"]
    wait_sec = queue_info["estimated_wait_sec"]

    if active == 0:
        return f"🟢 当前无排队，服务空闲（平均处理耗时 {avg_ms}ms）"
    elif wait_sec < 5:
        return f"🟢 当前 {active} 个请求处理中，预计等待 {wait_sec}s（平均耗时 {avg_ms}ms）"
    elif wait_sec < 30:
        return f"🟡 当前 {active} 个请求排队中，预计等待约 {wait_sec}s（平均耗时 {avg_ms}ms）"
    else:
        return f"🔴 当前 {active} 个请求排队中，预计等待约 {wait_sec}s（约 {round(wait_sec/60, 1)} 分钟），建议稍后再试"


def denoise_audio(
    input_file: str,
    output_file: str = None,
    endpoint: str = DEFAULT_ENDPOINT,
) -> str:
    """Denoise an audio file."""
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_file}")

    if output_file is None:
        output_file = str(input_path.with_stem(input_path.stem + "_denoised").with_suffix(".wav"))

    suffix = input_path.suffix.lower()
    mime_types = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
    }
    mime_type = mime_types.get(suffix, "audio/wav")

    with open(input_path, "rb") as f:
        files = {"file": (input_path.name, f, mime_type)}
        response = requests.post(endpoint, files=files, timeout=120)

    response.raise_for_status()

    with open(output_file, "wb") as out:
        out.write(response.content)

    return output_file


def main():
    # Handle --queue before argparse
    if len(sys.argv) == 2 and sys.argv[1] == "--queue":
        try:
            queue_info = check_queue()
            print(format_queue_status(queue_info))
            print()
            print(json.dumps(queue_info, indent=2, ensure_ascii=False))
        except requests.exceptions.RequestException as e:
            print(f"Error checking queue: {e}", file=sys.stderr)
            sys.exit(1)
        return

    parser = argparse.ArgumentParser(
        description="DashengDenoiser: Remove background noise from audio files"
    )
    parser.add_argument("input_file", help="Input audio file path")
    parser.add_argument(
        "-o", "--output", default=None,
        help="Output file path (default: <input>_denoised.wav)"
    )
    parser.add_argument(
        "--endpoint", "-e", default=DEFAULT_ENDPOINT,
        help=f"API endpoint (default: {DEFAULT_ENDPOINT})"
    )
    args = parser.parse_args()

    try:
        output = denoise_audio(args.input_file, args.output, args.endpoint)
        output_path = Path(output)
        size_kb = output_path.stat().st_size / 1024
        print(f"✅ Denoised audio saved: {output}")
        print(f"   Size: {size_kb:.1f} KB")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
