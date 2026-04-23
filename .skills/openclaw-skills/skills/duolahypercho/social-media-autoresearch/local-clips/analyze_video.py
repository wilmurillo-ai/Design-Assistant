#!/usr/bin/env python3
"""
Video Analysis Script - Agent-Based Smart Analysis

Uses Whisper for transcription, then spawns a sub-agent to intelligently
analyze the content and find the best clips.

Usage:
    python analyze_video.py <video_path> [--output analyze.md]
"""

import argparse
import json
import os
import sys
import re
import subprocess
from pathlib import Path

# Try to import whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("ERROR: whisper not installed. Run: pip install openai-whisper")


def load_whisper_model(model_name="tiny"):
    """Load Whisper model."""
    if not WHISPER_AVAILABLE:
        sys.exit("ERROR: whisper not installed")
    
    print(f"Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name)
    return model


def transcribe_video(video_path, model):
    """Transcribe video with Whisper, return full result."""
    print(f"Transcribing: {video_path}")
    
    result = model.transcribe(video_path, word_timestamps=True)
    
    duration = result.get('duration') or (result['segments'][-1]['end'] if result.get('segments') else 0)
    print(f"  Duration: {duration:.1f}s")
    print(f"  Segments: {len(result.get('segments', []))}")
    
    return result


def build_transcript_for_agent(segments, max_length=12000):
    """Build transcript text optimized for agent analysis."""
    transcript_parts = []
    current_time = 0
    
    for seg in segments:
        start = seg.get("start", 0)
        text = seg.get("text", "").strip()
        
        # Add timestamp marker every ~30 seconds
        if start - current_time >= 30:
            minutes = int(start // 60)
            secs = int(start % 60)
            transcript_parts.append(f"\n[{minutes:02d}:{secs:02d}]")
            current_time = start
        
        transcript_parts.append(" " + text)
        
        if len("".join(transcript_parts)) > max_length:
            break
    
    return "".join(transcript_parts)


def format_timestamp(seconds):
    """Format seconds to MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def analyze_with_agent(transcript, video_title, video_duration):
    """
    Spawn a sub-agent to analyze the transcript and find best clips.
    """
    prompt = f"""You are analyzing a transcript from: "{video_title}"

VIDEO DURATION: {video_duration/60:.1f} minutes

Below is the transcript with timestamps. Your task is to find the BEST clips 
that would make engaging, valuable Shorts/Reels/TikTok videos.

Look for segments that are:
1. SELF-CONTAINED - viewer doesn't need prior context to understand
2. VALUABLE - teaches something, changes perspective, gives actionable advice  
3. SURPRISING - challenges assumptions or reveals something counterintuitive
4. MEMORABLE - has a clear point, quote, or takeaway
5. EMOTIONAL - has energy or makes viewer feel something

AVOID:
- Intro small talk / greetings
- End of episode wrap-ups / promos / CTAs
- Segments requiring external context
- Boring explanations of basic concepts
- Sponsor reads

For each good clip (aim for 15-45 seconds), provide:
- Exact start timestamp (in seconds, from the transcript)
- Duration (15-45 seconds)
- A compelling title/hook (max 60 chars)
- Why it's a great clip (what makes it valuable/engaging)
- Brief content summary

Respond in this JSON format:
{{
  "video_theme": "2-3 words describing what this video is about",
  "target_audience": "who would benefit most",
  "clips": [
    {{
      "start": 123.45,
      "duration": 30,
      "title": "Compelling hook/title",
      "why_great": "What makes this clip valuable",
      "summary": "What is said in this segment"
    }}
  ]
}}

Provide at least 5 clips spread throughout the video (not clustered together).

TRANSCRIPT:
{transcript}
"""
    
    print("  Spawning sub-agent for intelligent analysis...")
    
    # Write prompt to temp file
    prompt_file = "/tmp/prism_analysis_prompt.txt"
    with open(prompt_file, "w") as f:
        f.write(prompt)
    
    return prompt_file


def generate_analyze_md(video_path, clips, video_theme="", target_audience="", output_path=None):
    """Generate analyze.md from clip results."""
    video_name = Path(video_path).stem
    
    md = f"""# Analysis: {video_name}

## Video Info
- **Source:** {video_path}
- **Theme:** {video_theme or "Unknown"}
- **Target Audience:** {target_audience or "Unknown"}
- **Clips Found:** {len(clips)}

## Analysis Method
This analysis uses an AI agent to understand the content and find clips that are:
- ✅ Self-contained (don't need prior context)
- ✅ Valuable (teach something or change perspective)
- ✅ Surprising (challenge assumptions)
- ✅ Memorable (clear point or quote)

## Top Recommended Clips

| # | Timestamp | Duration | Title | Why It's Great |
|---|-----------|----------|-------|----------------|
"""
    
    for i, clip in enumerate(clips, 1):
        ts = format_timestamp(clip.get("start", 0))
        duration = clip.get("duration", 0)
        title = clip.get("title", "Untitled")[:50]
        why = clip.get("why_great", "")[:60]
        
        md += f"| {i} | {ts} | {duration}s | {title} | {why} |\n"
    
    md += "\n## Detailed Clip Info\n\n"
    
    for i, clip in enumerate(clips, 1):
        ts = format_timestamp(clip.get("start", 0))
        title = clip.get("title", "Untitled")
        why = clip.get("why_great", "")
        summary = clip.get("summary", "")
        
        md += f"""### Clip {i}: {title}
- **Timestamp:** {ts}
- **Duration:** {clip.get("duration", 0)}s
- **Why it's great:** {why}
- **Content:** {summary}

"""
    
    md += """## Next Steps

1. Review clips above
2. Cut clips with: `ffmpeg -ss <timestamp> -t <duration>`
3. Convert to 9:16 vertical
4. Add captions with Whisper
"""
    
    if output_path:
        with open(output_path, "w") as f:
            f.write(md)
        print(f"Saved: {output_path}")
    
    return md


def find_clips_with_heuristics(segments, min_duration=15, max_duration=45, top_n=10, skip_intro=30):
    """Fallback: improved heuristics if agent fails."""
    if not segments:
        return []
    
    total_duration = segments[-1]["end"] if segments else 0
    outro_start = total_duration - 180
    
    segments = [s for s in segments if s["start"] >= skip_intro and s["start"] <= outro_start]
    
    print(f"  Using heuristic scoring (skipping first {skip_intro}s and last 3min)")
    
    # Build clips
    clips = []
    current = {"start": segments[0]["start"], "end": segments[0]["end"], "text": segments[0]["text"]}
    
    for seg in segments[1:]:
        if seg["start"] - current["end"] < 2:
            current["end"] = seg["end"]
            current["text"] += " " + seg["text"]
        else:
            clips.append(current)
            current = {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
    clips.append(current)
    
    # Score
    scored = []
    for clip in clips:
        duration = clip["end"] - clip["start"]
        if duration < 12 or duration > 60:
            continue
        
        text = clip["text"].lower()
        score = 0
        reasons = []
        
        # High value patterns
        for pattern, pts, label in [
            (r"\b(i think|i believe|in my experience)\b", 18, "personal insight"),
            (r"\b(the truth is|the reality is)\b", 25, "truth"),
            (r"\b(you should|you need to|don't|never)\b", 25, "advice"),
            (r"\b(\d+%|percent|half|third)\b", 18, "data"),
            (r"\b(i learned|i realized|i discovered)\b", 20, "learning"),
            (r"\b(the secret|here's what|the thing is)\b", 20, "key point"),
        ]:
            if re.search(pattern, text):
                score += pts
                reasons.append(label)
        
        # Penalties
        for pattern, pts, label in [
            (r"\b(thank you|thanks for|subscribe)\b", -35, "promo"),
            (r"\b(sponsor|advertisement)\b", -40, "sponsor"),
        ]:
            if re.search(pattern, text):
                score += pts
                reasons.append(label)
        
        if 20 <= duration <= 35:
            score += 15
        
        scored.append({
            "start": clip["start"],
            "end": clip["end"],
            "duration": duration,
            "text": clip["text"][:150],
            "score": max(0, score),
            "reasons": reasons,
        })
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    # Diversity selection
    selected = []
    for c in scored:
        if any(abs(c["start"] - s["start"]) < 90 for s in selected):
            continue
        selected.append(c)
        if len(selected) >= top_n:
            break
    
    return selected


def main():
    parser = argparse.ArgumentParser(description="Smart video analysis with AI agent")
    parser.add_argument("video", help="Input video file")
    parser.add_argument("--output", "-o", default=None, help="Output analyze.md file")
    parser.add_argument("--model", default="tiny", choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--no-agent", action="store_true", help="Skip agent, use heuristics")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--skip-intro", type=int, default=30)
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"ERROR: File not found: {args.video}")
        sys.exit(1)
    
    # Load model and transcribe
    model = load_whisper_model(args.model)
    result = transcribe_video(args.video, model)
    
    duration = result.get('duration', 0)
    video_title = Path(args.video).stem.replace('_', ' ').replace('-', ' ')
    segments = result.get("segments", [])
    
    output_path = args.output or "analyze.md"
    
    if not args.no_agent:
        # Build transcript for agent
        transcript = build_transcript_for_agent(segments)
        
        # Save transcript to temp file for agent
        transcript_file = "/tmp/prism_transcript.txt"
        with open(transcript_file, "w") as f:
            f.write(transcript)
        
        # Spawn sub-agent to analyze
        print("\n" + "="*60)
        print("SPAWNING SUB-AGENT FOR CONTENT ANALYSIS")
        print("="*60)
        print(f"Transcript saved to: {transcript_file}")
        print(f"\nTo analyze, send this message to a new session:\n")
        
        prompt = f"""Analyze the transcript in /tmp/prism_transcript.txt from video "{video_title}" ({duration/60:.1f} min).

Find 5-10 best clips (15-45 seconds each) that are:
- Self-contained (no prior context needed)
- Valuable (teach something, actionable advice)
- Surprising (challenges assumptions)
- Memorable (clear takeaway)

Return JSON with:
{{
  "video_theme": "theme",
  "target_audience": "audience", 
  "clips": [{{"start": seconds, "duration": 30, "title": "hook", "why_great": "reason", "summary": "content"}}]
}}

Respond ONLY with the JSON, no other text."""
        
        print("-" * 60)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 60)
        
        # Write analysis request
        request_file = "/tmp/prism_agent_request.txt"
        with open(request_file, "w") as f:
            f.write(prompt)
        
        print(f"\n✅ Analysis prompt saved to: {request_file}")
        print("Run a sub-agent with this prompt to get intelligent clip recommendations!")
        
    else:
        # Use heuristics
        clips = find_clips_with_heuristics(segments, top_n=args.top, skip_intro=args.skip_intro)
        
        if clips:
            md = generate_analyze_md(args.video, clips, output_path=output_path)
            print("\n" + "="*60)
            print("ANALYSIS COMPLETE")
            print("="*60)
            print(md)
        else:
            print("ERROR: No suitable clips found")
            sys.exit(1)


if __name__ == "__main__":
    main()
