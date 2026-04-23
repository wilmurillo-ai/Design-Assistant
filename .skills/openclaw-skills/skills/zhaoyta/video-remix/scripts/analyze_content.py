#!/usr/bin/env python3
"""
Analyze video transcript and generate clip metadata.
Identifies interesting segments/topics for clipping.
"""

import argparse
import json
import re
import sys
from typing import List, Dict


def analyze_segments(segments: List[Dict], min_clip_duration: float = 15.0, 
                     max_clip_duration: float = 120.0) -> List[Dict]:
    """
    Analyze transcript segments and identify clip-worthy moments.
    
    Uses heuristics to find:
    - Topic transitions
    - High-energy moments (exclamation, questions)
    - Complete thoughts/statements
    - Natural pause points
    
    Args:
        segments: List of transcript segments with start/end/text
        min_clip_duration: Minimum clip length in seconds
        max_clip_duration: Maximum clip length in seconds
    
    Returns:
        List of clip metadata with start, end, topic, summary
    """
    clips = []
    current_topic = None
    topic_start = 0
    topic_sentences = []
    
    # Keywords that might indicate topic changes
    transition_words = [
        "now", "next", "let's", "moving on", "another thing",
        "important", "key point", "remember", "note that",
        "first", "second", "third", "finally", "in conclusion",
        "however", "therefore", "because", "so", "but"
    ]
    
    for i, seg in enumerate(segments):
        text = seg["text"].lower()
        
        # Check for topic transitions
        is_transition = any(word in text for word in transition_words)
        
        # Check if segment is a question or exclamation (potentially engaging)
        is_engaging = "?" in seg["text"] or "!" in seg["text"]
        
        # Calculate current topic duration
        current_duration = seg["end"] - topic_start
        
        # Start new clip if:
        # 1. We hit a transition word and current clip is long enough
        # 2. Current clip exceeds max duration
        # 3. This is the first segment
        should_start_new = (
            (is_transition and current_duration >= min_clip_duration) or
            current_duration >= max_clip_duration or
            i == 0
        )
        
        if should_start_new and i > 0:
            # Save previous clip
            if topic_sentences:
                clip_text = " ".join(topic_sentences)
                clips.append({
                    "start": round(topic_start, 2),
                    "end": round(segments[i-1]["end"], 2),
                    "duration": round(segments[i-1]["end"] - topic_start, 2),
                    "topic": current_topic or f"Segment {len(clips) + 1}",
                    "summary": clip_text[:200] + ("..." if len(clip_text) > 200 else ""),
                    "highlights": [s for s in topic_sentences if "?" in s or "!" in s][:3]
                })
            
            # Start new topic
            topic_start = seg["start"]
            topic_sentences = [seg["text"]]
            
            # Try to extract topic from first sentence
            first_sentence = seg["text"].strip()
            if len(first_sentence) < 100:
                current_topic = first_sentence.rstrip(".")
            else:
                current_topic = f"Segment {len(clips) + 2}"
        else:
            topic_sentences.append(seg["text"])
    
    # Don't forget the last clip
    if topic_sentences:
        clip_text = " ".join(topic_sentences)
        if len(clip_text.strip()) > 20:  # Minimum content
            clips.append({
                "start": round(topic_start, 2),
                "end": round(segments[-1]["end"], 2),
                "duration": round(segments[-1]["end"] - topic_start, 2),
                "topic": current_topic or f"Segment {len(clips) + 1}",
                "summary": clip_text[:200] + ("..." if len(clip_text) > 200 else ""),
                "highlights": [s for s in topic_sentences if "?" in s or "!" in s][:3]
            })
    
    # Filter clips that are too short
    clips = [c for c in clips if c["duration"] >= min_clip_duration]
    
    # Add clip index
    for i, clip in enumerate(clips):
        clip["clip_id"] = i + 1
        clip["order"] = i
    
    return clips


def analyze_content(transcript_data: dict, min_duration: float = 15.0, 
                    max_duration: float = 120.0, max_clips: int = 10) -> dict:
    """
    Main analysis function.
    
    Args:
        transcript_data: Output from transcribe.py
        min_duration: Minimum clip duration
        max_duration: Maximum clip duration
        max_clips: Maximum number of clips to generate
    
    Returns:
        Analysis result with clips metadata
    """
    if not transcript_data.get("success"):
        return {
            "success": False,
            "error": transcript_data.get("error", "Invalid transcript data")
        }
    
    segments = transcript_data.get("segments", [])
    if not segments:
        return {
            "success": False,
            "error": "No segments to analyze"
        }
    
    clips = analyze_segments(segments, min_duration, max_duration)
    
    # Limit number of clips
    if len(clips) > max_clips:
        clips = clips[:max_clips]
    
    return {
        "success": True,
        "source_language": transcript_data.get("language", "unknown"),
        "total_duration": transcript_data.get("duration", 0),
        "total_segments": transcript_data.get("segment_count", 0),
        "clips_generated": len(clips),
        "clips": clips,
        "full_transcript": transcript_data.get("full_text", "")
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze transcript and generate clip metadata")
    parser.add_argument("transcript_file", help="JSON transcript file from transcribe.py")
    parser.add_argument("--min-duration", type=float, default=15.0, 
                        help="Minimum clip duration in seconds (default: 15)")
    parser.add_argument("--max-duration", type=float, default=120.0,
                        help="Maximum clip duration in seconds (default: 120)")
    parser.add_argument("--max-clips", type=int, default=10,
                        help="Maximum number of clips (default: 10)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-o", "--output", help="Save analysis to file")
    
    args = parser.parse_args()
    
    # Load transcript
    try:
        with open(args.transcript_file, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.transcript_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    result = analyze_content(transcript_data, args.min_duration, args.max_duration, args.max_clips)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Analysis saved to: {args.output}", file=sys.stderr)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["success"]:
            print(f"✓ Analysis complete")
            print(f"  Total duration: {result['total_duration']:.1f}s")
            print(f"  Clips generated: {result['clips_generated']}")
            print("\n--- Clips ---")
            for clip in result["clips"]:
                print(f"\n[Clip {clip['clip_id']}] {clip['topic'][:50]}...")
                print(f"  Time: {clip['start']:.1f}s - {clip['end']:.1f}s ({clip['duration']:.1f}s)")
                print(f"  Summary: {clip['summary'][:80]}...")
        else:
            print(f"✗ Error: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
