#!/usr/bin/env python3
"""
Prism Video Analysis Pipeline

Step 1: Download video + get YouTube transcript (fast, free)
Step 2: Analyze transcript to find best clips
Step 3: Cut clips and convert to 9:16
Step 4: Add Whisper captions to final clips (only on short clips!)

Usage:
    python prism_run.py --url "https://youtube.com/watch?v=..."
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def download_video(url, output_folder):
    """Download video (video only, no transcript)."""
    print(f"\n📥 Downloading video...")
    print(f"   URL: {url}")
    
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=webm]+bestaudio[ext=m4a]/best[ext=webm]/best",
        "--output", f"{output_folder}/raw/source.%(ext)s",
        "--no-write-subs",
        "--no-write-auto-subs",
        url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ❌ Error: {result.stderr}")
        return False
    
    # Find downloaded file
    for ext in ['webm', 'mp4', 'mkv']:
        video_path = Path(f"{output_folder}/raw/source.{ext}")
        if video_path.exists():
            print(f"   ✅ Downloaded: {video_path}")
            return str(video_path)
    
    print("   ❌ Video file not found")
    return False


def download_transcript(url, output_folder):
    """Download YouTube transcript (auto-captions)."""
    print(f"\n📝 Getting YouTube transcript...")
    
    # Try to get transcript with yt-dlp
    cmd = [
        "yt-dlp",
        "--write-subs",
        "--write-auto-subs", 
        "--skip-download",
        "--output", f"{output_folder}/raw/transcript",
        "--sub-lang", "en",
        url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Look for transcript files
    transcript_path = None
    for ext in ['vtt', 'srt', 'json']:
        for f in Path(f"{output_folder}/raw").glob(f"*.{ext}"):
            if 'transcript' in f.name.lower() or 'english' in f.name.lower():
                transcript_path = str(f)
                break
        if transcript_path:
            break
    
    if transcript_path:
        print(f"   ✅ Transcript: {transcript_path}")
        return transcript_path
    
    # Try alternate method - extract with yt-dlp
    cmd2 = [
        "yt-dlp",
        "--skip-download",
        "--print", "%(subs)s",
        url
    ]
    result2 = subprocess.run(cmd2, capture_output=True, text=True)
    print(f"   Subs info: {result2.stdout[:200]}")
    
    print("   ⚠️ No transcript found - will use fallback")
    return None


def get_video_info(url):
    """Get video title and duration."""
    cmd = [
        "yt-dlp",
        "--print", "%(title)s|%(duration)s",
        "--no-download",
        url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        parts = result.stdout.strip().split('|')
        if len(parts) >= 2:
            try:
                duration = int(parts[1])
                minutes = duration // 60
                return parts[0], duration, f"{minutes} min"
            except:
                return parts[0], 0, "Unknown"
    return "Unknown Video", 0, "Unknown"


def create_status_json(folder, stage, url, video_id=None, title=None):
    """Create/update status.json."""
    status = {
        "updated_at": "2026-03-09T12:00:00",
        "stage": stage,
        "url": url,
    }
    if video_id:
        status["video_id"] = video_id
    if title:
        status["title"] = title
    
    status_path = Path(folder) / "status.json"
    with open(status_path, "w") as f:
        json.dump(status, f, indent=2)
    
    return status_path


def main():
    parser = argparse.ArgumentParser(description="Prism - Smart Video Clip Generator")
    parser.add_argument("--url", required=True, help="YouTube URL")
    parser.add_argument("--folder", default=None, help="Output folder name")
    parser.add_argument("--video-only", action="store_true", help="Only download video, skip transcript")
    
    args = parser.parse_args()
    
    url = args.url
    
    # Extract video ID
    video_id = None
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    
    # Get video info
    title, duration, duration_str = get_video_info(url)
    print(f"\n🎬 Video: {title}")
    print(f"   Duration: {duration_str}")
    print(f"   ID: {video_id}")
    
    # Create folder
    if args.folder:
        folder_name = args.folder
    else:
        safe_title = title[:50].replace("/", "-").replace(":", "-")
        folder_name = f"{safe_title}_{video_id}"
    
    base_folder = Path.home() / ".openclaw" / "workspace-prism" / "clips" / folder_name
    base_folder.mkdir(parents=True, exist_ok=True)
    (base_folder / "raw").mkdir(exist_ok=True)
    
    print(f"\n📁 Folder: {base_folder}")
    
    # Create status
    create_status_json(base_folder, "DOWNLOADING", url, video_id, title)
    
    # Step 1: Download video
    video_path = download_video(url, base_folder)
    if not video_path:
        create_status_json(base_folder, "FAILED_DOWNLOAD", url, video_id, title)
        sys.exit(1)
    
    # Step 2: Download transcript (unless skipped)
    transcript_path = None
    if not args.video_only:
        transcript_path = download_transcript(url, base_folder)
    
    # Update status
    if transcript_path:
        create_status_json(base_folder, "READY_TO_ANALYZE", url, video_id, title)
    else:
        create_status_json(base_folder, "NO_TRANSCRIPT", url, video_id, title)
    
    print(f"\n✅ DOWNLOAD COMPLETE")
    print(f"   Video: {video_path}")
    print(f"   Transcript: {transcript_path or 'Not available'}")
    print(f"\n📋 NEXT STEPS:")
    if transcript_path:
        print(f"   1. Review transcript: {transcript_path}")
        print(f"   2. Run analysis to find best clips")
        print(f"   3. Cut clips and add captions")
    else:
        print(f"   1. Run Whisper on video to generate transcript")
        print(f"   2. Analyze for best clips")
        print(f"   3. Cut clips and add captions")


if __name__ == "__main__":
    main()
