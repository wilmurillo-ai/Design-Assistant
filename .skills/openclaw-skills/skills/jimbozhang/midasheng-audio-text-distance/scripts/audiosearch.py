#!/usr/bin/env python3
"""
AudioSearch API Client - Multilingual audio-text retrieval using GLAP.
Computes similarity scores between audio files and text descriptions.
Supports queue status check via --queue.
"""

import sys
import argparse
import json
import requests
from pathlib import Path

API_BASE = "https://llmplus.ai.xiaomi.com"
DEFAULT_ENDPOINT = f"{API_BASE}/dasheng/audio/search"
METRICS_PATH = "/dasheng/audio/search"


def check_queue(api_base: str = API_BASE) -> dict:
    """查询 search 服务的排队情况"""
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


def search_audio(
    audio_files: list,
    text_labels: str,
    endpoint: str = DEFAULT_ENDPOINT,
) -> dict:
    """Search/match audio files against text descriptions."""
    for f in audio_files:
        if not Path(f).exists():
            raise FileNotFoundError(f"Audio file not found: {f}")

    files_list = []
    for f in audio_files:
        p = Path(f)
        suffix = p.suffix.lower()
        mime_types = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".m4a": "audio/mp4",
            ".ogg": "audio/ogg",
            ".flac": "audio/flac",
        }
        mime = mime_types.get(suffix, "audio/wav")
        files_list.append(("files", (p.name, open(p, "rb"), mime)))

    data = {"text": text_labels}

    try:
        response = requests.post(endpoint, files=files_list, data=data, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"API request failed ({e.response.status_code}): {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error: {e}")
    finally:
        for _, (_, fh, _) in files_list:
            fh.close()


def main():
    # Handle --queue before argparse (since it conflicts with required positional args)
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
        description="AudioSearch: Match audio files against text descriptions using GLAP"
    )
    parser.add_argument("audio_files", nargs="+", help="Audio file paths (mp3, wav, etc.)")
    parser.add_argument(
        "--text", "-t", required=True,
        help="Comma-separated text labels (e.g., 'Speech,Music,Noise')"
    )
    parser.add_argument(
        "--endpoint", "-e", default=DEFAULT_ENDPOINT,
        help=f"API endpoint (default: {DEFAULT_ENDPOINT})"
    )
    args = parser.parse_args()

    try:
        result = search_audio(args.audio_files, args.text, args.endpoint)
        print("Audio-Text Similarity Search Results")
        print("=" * 60)

        if isinstance(result, dict):
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(result)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
