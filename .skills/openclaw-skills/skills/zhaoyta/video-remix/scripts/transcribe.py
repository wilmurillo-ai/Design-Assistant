#!/usr/bin/env python3
"""
Transcribe video/audio to text using Whisper.
Outputs transcript with timestamps.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import whisper
except ImportError:
    whisper = None


def transcribe_video(video_path: str, model: str = "base", language: str = None) -> dict:
    """
    Transcribe video/audio file using Whisper.
    
    Args:
        video_path: Path to video/audio file
        model: Whisper model size (tiny, base, small, medium, large)
        language: Source language code (e.g., 'en', 'zh'), None for auto-detect
    
    Returns:
        dict with transcript, segments with timestamps
    """
    if whisper is None:
        return {
            "success": False,
            "error": "Whisper not installed. Install with: pip install openai-whisper"
        }
    
    video_path = Path(video_path)
    if not video_path.exists():
        return {
            "success": False,
            "error": f"File not found: {video_path}"
        }
    
    try:
        print(f"Loading Whisper model: {model}...", file=sys.stderr)
        model_obj = whisper.load_model(model)
        
        print(f"Transcribing {video_path.name}...", file=sys.stderr)
        options = {
            "word_timestamps": True,
            "verbose": False
        }
        if language:
            options["language"] = language
        
        result = model_obj.transcribe(str(video_path), **options)
        
        # Format segments with timestamps
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": round(seg["start"], 2),
                "end": round(seg["end"], 2),
                "text": seg["text"].strip()
            })
        
        return {
            "success": True,
            "language": result.get("language", "unknown"),
            "duration": result.get("segments", [-1])[-1].get("end", 0) if result.get("segments") else 0,
            "full_text": result.get("text", ""),
            "segments": segments,
            "segment_count": len(segments)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Transcribe video/audio to text")
    parser.add_argument("video_path", help="Path to video/audio file")
    parser.add_argument("-m", "--model", default="base", 
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("-l", "--language", default=None, 
                        help="Source language code (auto-detect if not specified)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-o", "--output", help="Save transcript to file")
    
    args = parser.parse_args()
    
    result = transcribe_video(args.video_path, args.model, args.language)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Transcript saved to: {args.output}", file=sys.stderr)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["success"]:
            print(f"✓ Transcribed: {result['segment_count']} segments")
            print(f"  Language: {result['language']}")
            print(f"  Duration: {result['duration']:.1f}s")
            print("\n--- Transcript ---")
            for seg in result["segments"][:10]:  # Show first 10 segments
                print(f"[{seg['start']:.1f}-{seg['end']:.1f}] {seg['text']}")
            if result["segment_count"] > 10:
                print(f"... ({result['segment_count'] - 10} more segments)")
        else:
            print(f"✗ Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
