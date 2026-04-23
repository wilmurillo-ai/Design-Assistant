#!/usr/bin/env python3
"""
Download YouTube video using yt-dlp.
Outputs video path and basic metadata as JSON.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def download_video(url: str, output_dir: str, format: str = "bestvideo+bestaudio/best") -> dict:
    """
    Download a YouTube video using yt-dlp.
    
    Args:
        url: YouTube video URL
        output_dir: Directory to save the video
        format: Format selector for yt-dlp
    
    Returns:
        dict with video_path, title, duration, and metadata
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Template for output filename
    output_template = str(output_dir / "%(title)s.%(ext)s")
    
    cmd = [
        "yt-dlp",
        "-f", format,
        "-o", output_template,
        "--write-info-json",
        "--print-json",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        metadata = json.loads(result.stdout.strip())
        
        video_path = None
        # Find the downloaded file
        for ext in ["mp4", "mkv", "webm"]:
            candidate = output_dir / f"{metadata.get('title', 'video')}.{ext}"
            if candidate.exists():
                video_path = str(candidate)
                break
        
        # If not found by title, search for most recent file
        if not video_path:
            files = list(output_dir.glob("*.*"))
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            if files:
                video_path = str(files[0])
        
        return {
            "success": True,
            "video_path": video_path,
            "title": metadata.get("title", "Unknown"),
            "duration": metadata.get("duration", 0),
            "uploader": metadata.get("uploader", "Unknown"),
            "upload_date": metadata.get("upload_date", ""),
            "view_count": metadata.get("view_count", 0),
            "description": metadata.get("description", "")[:500]  # Truncate
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Download failed: {e.stderr}",
            "stdout": e.stdout
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "yt-dlp not found. Install with: pip install yt-dlp"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"Failed to parse metadata: {e}"
        }


def main():
    parser = argparse.ArgumentParser(description="Download YouTube video")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("-o", "--output", default="./downloads", help="Output directory")
    parser.add_argument("-f", "--format", default="bestvideo+bestaudio/best", 
                        help="Format selector (default: best)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    result = download_video(args.url, args.output, args.format)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["success"]:
            print(f"✓ Downloaded: {result['title']}")
            print(f"  Path: {result['video_path']}")
            print(f"  Duration: {result['duration']}s")
            print(f"  Uploader: {result['uploader']}")
        else:
            print(f"✗ Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
