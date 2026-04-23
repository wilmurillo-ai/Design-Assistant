#!/usr/bin/env python3
"""prism_run.py — deterministic, end-to-end clip generator

Goal: take a YouTube URL and produce validated short-form clips in /final with
Whisper captions + title overlay GUARANTEED.

Design principles:
- Single entrypoint (no prompt ambiguity)
- Stage-based status.json + logs (observability)
- Idempotent + resumable (skip completed stages)
- Hard validation gate before writing to /final

Outputs (in per-video folder):
- raw/              downloaded source video
- analysis/         full transcript json, analyze.md/json
- segments/         cut source segments (pre-caption)
- final/            finished vertical captioned clips
- status.json       live pipeline status
- result.json       final manifest for posting (includes best_clip)
- run.log           full logs (when running in --background)

Usage:
  python3 prism_run.py --url "https://youtube.com/watch?v=..."
  python3 prism_run.py --url "..." --background
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace-prism"))
SKILL_DIR = WORKSPACE / "skills" / "prism-clips"
ADD_CAPTIONS = SKILL_DIR / "add_captions.py"
DEFAULT_OUTDIR = WORKSPACE / "clips"

STOPWORDS = {
    "a","an","and","are","as","at","be","but","by","because","for","from","has","have","he","her","hers",
    "him","his","i","if","in","into","is","it","its","it's","me","my","mine","not","of","on","or",
    "our","ours","she","so","that","the","their","theirs","them","then","there","these","they","this",
    "those","to","too","was","we","were","what","when","where","which","who","why","will","with","you",
    "your","yours","yourself","yourselves","im","i'm","you're","we're","they're","can't","dont","don't",
}

VIRAL_TRIGGERS = {
    "emotional": [
        "truth", "secret", "crazy", "insane", "shocking", "surprising", "unbelievable",
        "worst", "best", "mistake", "failure", "success", "money", "rich", "poor",
        "respect", "power", "control", "fear", "confidence",
    ],
    "questions": ["why", "what", "who", "how", "when", "where"],
    "transitions": ["here's", "the thing is", "bottom line", "real talk", "listen", "now", "turns out"],
}

WEIGHTS = {
    "emotional": 30,
    "bold": 25,
    "question": 15,
    "transition": 10,
    "density": 10,
}


def _run(cmd: List[str], *, timeout: Optional[int] = None, capture: bool = True, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, timeout=timeout, capture_output=capture, text=text)


def _require_bin(name: str) -> None:
    ok = subprocess.call(["bash", "-lc", f"command -v {shlex.quote(name)} >/dev/null 2>&1"]) == 0
    if not ok:
        raise RuntimeError(f"Missing required binary: {name}")


def _safe_name(s: str, max_len: int = 80) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("/", "-")
    s = re.sub(r"[\s\t\n\r]+", " ", s).strip()
    s = re.sub(r"[^\w\s\-\!\,\.&\(\)\[\]]+", "", s)
    s = s.replace(" ", "_")
    if len(s) > max_len:
        s = s[:max_len].rstrip("_")
    return s or "video"


def _iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def _ffprobe_duration(path: Path) -> Optional[float]:
    p = _run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1",
        str(path),
    ])
    if p.returncode != 0:
        return None
    try:
        return float(p.stdout.strip())
    except Exception:
        return None


def _ffprobe_has_audio(path: Path) -> bool:
    p = _run([
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name",
        "-of", "csv=p=0",
        str(path),
    ])
    return bool(p.stdout.strip())


def _ffprobe_video_info(path: Path) -> Dict[str, Any]:
    p = _run([
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json",
        str(path),
    ])
    if p.returncode != 0:
        return {}
    try:
        j = json.loads(p.stdout)
        st = (j.get("streams") or [{}])[0]
        return {"width": st.get("width"), "height": st.get("height")}
    except Exception:
        return {}


def _ffprobe_av_durations(path: Path) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """Return (format_dur, video_dur, audio_dur) in seconds when available."""
    p = _run([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,duration",
        "-of",
        "json",
        str(path),
    ])
    if p.returncode != 0:
        return None, None, None

    try:
        j = json.loads(p.stdout)
    except Exception:
        return None, None, None

    fmt_dur = None
    try:
        fmt_dur = float(((j.get("format") or {}).get("duration") or "").strip())
    except Exception:
        fmt_dur = None

    v_dur = None
    a_dur = None
    for st in j.get("streams") or []:
        try:
            d = float((st.get("duration") or "").strip())
        except Exception:
            d = None
        if st.get("codec_type") == "video" and v_dur is None:
            v_dur = d
        if st.get("codec_type") == "audio" and a_dur is None:
            a_dur = d

    return fmt_dur, v_dur, a_dur


def _ffmpeg_yavg(path: Path, t: float) -> Optional[float]:
    """Sample average luma at a timestamp.

    This is a cheap proxy to detect "black screen" outputs without decoding the whole file.
    """
    cmd = [
        "ffmpeg",
        "-v",
        "info",
        "-ss",
        str(max(0.0, t)),
        "-i",
        str(path),
        "-frames:v",
        "1",
        "-vf",
        "signalstats,metadata=print",
        "-f",
        "null",
        "-",
    ]
    p = _run(cmd, timeout=60, capture=True)
    out = (p.stderr or "") + "\n" + (p.stdout or "")
    # ffmpeg metadata prints keys like: lavfi.signalstats.YAVG=23.1033
    # NOTE: do NOT double-escape dots here; we want to match literal '.' characters.
    m = re.search(r"lavfi\.signalstats\.YAVG=([0-9.]+)", out)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _ffmpeg_yavg_portrait_centre(path: Path, t: float) -> Optional[float]:
    """Sample average luma at a timestamp, cropped to the centre 50 % of the frame.

    This skips the top and bottom letterbox bars that dominate portrait composites,
    giving a reliable reading of the actual video content brightness.
    """
    cmd = [
        "ffmpeg",
        "-v",
        "info",
        "-ss",
        str(max(0.0, t)),
        "-i",
        str(path),
        "-frames:v",
        "1",
        "-vf",
        "crop=iw:ih/2:0:ih/4,signalstats,metadata=print",
        "-f",
        "null",
        "-",
    ]
    p = _run(cmd, timeout=60, capture=True)
    out = (p.stderr or "") + "\n" + (p.stdout or "")
    m = re.search(r"lavfi\.signalstats\.YAVG=([0-9.]+)", out)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _looks_like_black_screen(path: Path) -> bool:
    """Heuristic: sample a few frames; if all are near-black, treat as bad output.

    Portrait composites (9:16 letterbox) use centre-crop sampling to skip the
    black letterbox bars.  Standard full-frame sampling is used as a fallback
    for non-portrait or pre-cropped clips.
    """
    dur = _ffprobe_duration(path)
    if not dur or dur < 2:
        return False

    ts = [min(0.8, dur * 0.1), dur * 0.5, max(0.8, dur - 0.8)]

    # Primary: sample the centre 50 % of the frame — skips letterbox bars.
    ys_portrait = [_ffmpeg_yavg_portrait_centre(path, t) for t in ts]
    ys_portrait = [y for y in ys_portrait if y is not None]
    if len(ys_portrait) >= 2 and not all(y < 18.0 for y in ys_portrait):
        return False  # content band is bright enough

    # Fallback: full-frame sampling (original behaviour for non-portrait clips).
    ys_full = [y for y in (_ffmpeg_yavg(path, t) for t in ts) if y is not None]
    if len(ys_full) < 2:
        return False

    return all(y < 18.0 for y in ys_full)


def _silence_ratio_sample(path: Path, start: float, duration: float) -> Optional[float]:
    """Return approx silence ratio for a sample window using ffmpeg silencedetect.

    We treat detected silence durations as silent, and compute silent/total.
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-ss", str(max(0.0, start)),
        "-t", str(duration),
        "-i", str(path),
        "-af", "silencedetect=n=-45dB:d=0.8",
        "-f", "null",
        "-",
    ]
    p = _run(cmd, timeout=int(duration) + 60, capture=True)
    out = (p.stderr or "") + "\n" + (p.stdout or "")
    if p.returncode not in (0, 1):
        return None

    # Sum all "silence_duration: X" occurrences
    silent = 0.0
    for m in re.finditer(r"silence_duration:\s*([0-9.]+)", out):
        try:
            silent += float(m.group(1))
        except Exception:
            pass
    silent = max(0.0, min(silent, duration))
    return silent / duration if duration > 0 else None


@dataclass
class Candidate:
    start: float
    end: float
    score: float
    title: str
    text: str


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z']{1,}", text.lower())
    return [w for w in words if w not in STOPWORDS]


def _pick_topic(text: str) -> str:
    toks = _tokenize(text)
    if not toks:
        return "Power"

    freq: Dict[str, int] = {}
    for t in toks:
        freq[t] = freq.get(t, 0) + 1
    top = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    topic = " ".join([w.title() for w, _ in top[:2]]).strip()
    return topic or "Power"


def _sanitize_title(title: str) -> str:
    """Normalize hook/title text for on-screen rendering."""
    title = (title or "").strip()
    # Strip wrapping quotes (straight + curly)
    title = title.strip("\"'“”‘’`“”")
    # Avoid first-person POV in on-screen hooks (reads awkward out of context).
    title = re.sub(r"\b(i|me|my|mine|we|our|ours)\b", "", title, flags=re.I)
    # Collapse whitespace
    title = re.sub(r"\s{2,}", " ", title).strip()
    # Trim trailing punctuation that looks awkward as a big hook
    title = re.sub(r"[\s\-–—:;,.!?]+$", "", title).strip()
    return title


def _compact_hook(title: str, *, max_chars: int = 52, max_words: int = 10) -> str:
    """Make a hook short, readable, and safe for the overlay."""
    t = _sanitize_title(title)
    if not t:
        return "Clip"

    words = t.split()
    if len(words) > max_words:
        words = words[:max_words]
    t = " ".join(words)

    if len(t) <= max_chars:
        return t

    # Try removing common filler words to fit.
    filler = {"the", "a", "an", "about", "what", "why", "how", "youre", "you're", "is", "are", "to", "of", "for"}
    pruned = [w for w in words if w.lower() not in filler]
    if pruned:
        t2 = " ".join(pruned)
        if len(t2) <= max_chars:
            return t2

    # Last resort: hard truncate
    return t[:max_chars].rstrip()


def _is_bad_hook(hook: str) -> bool:
    """Detect hooks that are usually weak / feel "too AI" or too temporal."""
    h_orig = (hook or "").strip()
    h = h_orig.lower()
    if not h:
        return True

    # Placeholder / failure hooks
    if h == "clip" or h == "a clip":
        return True

    # Avoid time-comparison / year hooks like "2020 vs now"
    if re.search(r"\b(19|20)\d{2}\b", h):
        return True
    if " vs " in h or " versus " in h:
        return True
    if h.endswith("now") or h.startswith("now "):
        return True

    # Generic / templated fillers
    if "what you're missing" in h or "things you should know" in h:
        return True
    if h.startswith("the problem with"):
        return True
    if h.startswith("the truth about"):
        return True
    if "this changes everything" in h:
        return True
    if "you won't believe" in h:
        return True
    if h.startswith("breaking:"):
        return True
    if "things to know" in h:
        return True

    # BANNED CTAs (SOUL.md Champion Playbook — enforced here for Prism hook generation)
    banned_cta_phrases = [
        "more clips like this",
        "more clips daily",
        "more videos like this",
        "follow for more",
        "follow me for",
        "subscribe for more",
        "like and follow",
        "more content like this",
    ]
    for phrase in banned_cta_phrases:
        if phrase in h:
            return True

    # UFO / conspiracy / shock-bait framing
    ufo_keywords = ["ufo", "alien", "extraterrestrial", "aliens"]
    if h_orig.startswith("breaking") and any(kw in h for kw in ufo_keywords):
        return True
    if any(kw in h for kw in ufo_keywords) and any(
        bad in h for bad in ["footage", "leaked", "secret", "cover-up", "hidden", "they don't want"]
    ):
        return True

    # First-person POV tends to be bad out of context
    if re.search(r"\b(i|me|my|mine|we|our|ours)\b", h):
        return True

    # Too vague (e.g., "debate decline")
    if "decline" in h and len(h.split()) <= 2:
        return True

    # Too many stopwords => meaningless
    toks = _tokenize(h)
    if len(toks) == 0:
        return True

    return False


def _generate_hook(text: str) -> str:
    """Fallback hook generator (used when LLM selector fails).

    Goal: an on-screen hook that tells the viewer what the clip is about.
    Must be short + specific (suitable for large on-screen overlay).
    """
    tl = (text or "").lower()
    topic = _pick_topic(text)

    # Numbers in text (avoid "X things to know" templates)
    num_match = re.search(r"\b(\d{1,3})\b", text or "")
    if num_match:
        n = num_match.group(1)
        return _compact_hook(f"{n} habits that work")

    # Domain-ish keywords
    if "reality" in tl and ("illusion" in tl or "not real" in tl):
        return _compact_hook("Reality Isn't What You Think")
    if "evolution" in tl and "reality" in tl:
        return _compact_hook("Evolution Hid Reality")
    if "conscious" in tl or "consciousness" in tl:
        return _compact_hook("Consciousness Is The Mystery")
    if "ai" in tl or "artificial intelligence" in tl:
        return _compact_hook("AI Is Closer Than You Think")
    if "debate stage" in tl or "debate" in tl and "performance" in tl:
        return _compact_hook("Debate Performance Drop")
    if "side-by-side" in tl or "side by side" in tl:
        return _compact_hook("Debate Performance Drop")
    if "startup" in tl or "founder" in tl or "saas" in tl:
        return _compact_hook(f"Startup Mistakes: {topic}")

    # Better generic templates (avoid "What You're Missing")
    if "secret" in tl or "they don't want" in tl or "hiding" in tl:
        return _compact_hook(f"They're Hiding {topic}")
    if "mistake" in tl:
        return _compact_hook(f"The Mistake About {topic}")
    if "respect" in tl:
        return _compact_hook("Why Respect Disappears")

    # Last resort: default to an educational, non-clickbait frame.
    # Avoid the banned template "the problem with X".
    return _compact_hook(f"how {topic.lower()} works")


def _score_text(text: str) -> Tuple[float, List[str]]:
    tl = text.lower()
    score = 0.0
    reasons: List[str] = []

    if any(w in tl for w in VIRAL_TRIGGERS["emotional"]):
        score += WEIGHTS["emotional"]
        reasons.append("emotional")

    if any(ch.isdigit() for ch in text):
        score += WEIGHTS["bold"]
        reasons.append("number")

    if any(q in tl for q in VIRAL_TRIGGERS["questions"]):
        score += WEIGHTS["question"]
        reasons.append("question")

    if any(t in tl for t in VIRAL_TRIGGERS["transitions"]):
        score += WEIGHTS["transition"]
        reasons.append("transition")

    # density: more content words => better
    toks = _tokenize(text)
    if toks:
        score += min(WEIGHTS["density"], len(toks) / 25.0 * WEIGHTS["density"])
        reasons.append("dense")

    return score, reasons


def _format_ts(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def analyze_transcript(transcript: Dict[str, Any], *, clip_duration: float, top_n: int, skip_intro: float) -> List[Candidate]:
    """Generate candidate clip windows from the FULL transcript.

    Robustness goals:
    - Avoid intro-heavy picks (skip_intro)
    - Prefer information-dense windows (token threshold)
    - Enforce diversity across the whole video timeline (bucket selection)
    - Enforce non-overlap (min_sep)
    """

    segs = transcript.get("segments") or []
    if not segs:
        return []

    # Estimate video duration from transcript
    try:
        video_end = float(segs[-1].get("end", segs[-1].get("start", 0)))
    except Exception:
        video_end = 0.0
    video_end = max(video_end, 1.0)

    # Build anchors after skip_intro
    anchors = [s for s in segs if float(s.get("start", 0)) >= skip_intro]
    if not anchors:
        anchors = segs

    MIN_SCORE = 18.0
    MIN_TOKENS = 18

    windows: List[Candidate] = []

    # For each anchor start, gather text within [start, start+clip_duration]
    # Note: this iterates a lot; acceptable for daily batch.
    for s in anchors:
        start = float(s.get("start", 0))
        end = start + clip_duration

        texts = []
        for t in segs:
            ts = float(t.get("start", 0))
            if ts < start:
                continue
            if ts > end:
                break
            txt = (t.get("text") or "").strip()
            if txt:
                texts.append(txt)

        if not texts:
            continue

        window_text = " ".join(texts)

        toks = _tokenize(window_text)
        if len(toks) < MIN_TOKENS:
            continue

        score, _reasons = _score_text(window_text)
        if score < MIN_SCORE:
            continue

        title = _generate_hook(window_text)
        if not title:
            continue

        windows.append(Candidate(start=start, end=end, score=score, title=title, text=window_text))

    if not windows:
        return []

    windows.sort(key=lambda c: c.score, reverse=True)

    # Diversity buckets across full duration
    bucket_count = 8
    bucket_best: Dict[int, Candidate] = {}

    for c in windows:
        b = int((c.start / video_end) * bucket_count)
        b = max(0, min(bucket_count - 1, b))
        prev = bucket_best.get(b)
        if (prev is None) or (c.score > prev.score):
            bucket_best[b] = c

    diverse = list(bucket_best.values())
    diverse.sort(key=lambda c: c.score, reverse=True)

    # Greedy non-overlap selection (diverse-first, then global fill)
    selected: List[Candidate] = []
    min_sep = max(20.0, clip_duration * 0.65)

    def can_add(cand: Candidate) -> bool:
        for s in selected:
            if abs(cand.start - s.start) < min_sep:
                return False
        return True

    for pool in (diverse, windows):
        for c in pool:
            if len(selected) >= top_n:
                break
            if can_add(c):
                selected.append(c)
        if len(selected) >= top_n:
            break

    selected.sort(key=lambda c: c.start)
    return selected[:top_n]




def _extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Best-effort JSON extraction (handles code fences / preamble)."""
    t = (text or "").strip()
    if not t:
        return None
    try:
        return json.loads(t)
    except Exception:
        pass
    # Try to extract first {...} block
    i = t.find("{")
    j = t.rfind("}")
    if i >= 0 and j > i:
        try:
            return json.loads(t[i:j+1])
        except Exception:
            return None
    return None


def _timed_window_text(segs: List[Dict[str, Any]], start: float, end: float, *, mark_every: float = 8.0, max_chars: int = 900) -> str:
    """Build compact transcript text for [start,end] with periodic timestamps."""
    parts: List[str] = []
    last_mark = None
    for s in segs:
        try:
            ts = float(s.get('start', 0.0))
        except Exception:
            continue
        if ts < start:
            continue
        if ts > end:
            break
        if last_mark is None or (ts - last_mark) >= mark_every:
            parts.append(f"\n[{_format_ts(ts)}]")
            last_mark = ts
        txt = (s.get('text') or '').strip()
        if txt:
            parts.append(' ' + txt)
        if sum(len(p) for p in parts) >= max_chars:
            break
    out = ''.join(parts).strip()
    if len(out) > max_chars:
        out = out[:max_chars].rstrip() + '…'
    return out


def _snap_end_to_segments(segs: List[Dict[str, Any]], start: float, *, max_end: float, min_end: float) -> float:
    """Snap an end time to the nearest segment boundary <= max_end (but >= min_end).

    Helps produce punchier clips that end cleanly on a sentence boundary.
    """
    best = None
    for s in segs:
        try:
            ss = float(s.get('start', 0.0))
            se = float(s.get('end', 0.0))
        except Exception:
            continue
        if se < min_end:
            continue
        if se <= max_end:
            best = se
        if ss > max_end:
            break
    return float(best) if best is not None else float(max_end)


def _call_openclaw_agent(agent_id: str, message: str, *, timeout_s: int = 180) -> str:
    """Call an OpenClaw agent turn via CLI and return stdout text."""
    cmd = [
        'openclaw', 'agent',
        '--agent', agent_id,
        '--message', message,
        '--timeout', str(timeout_s),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s + 30)
    if p.returncode != 0:
        err = (p.stderr or p.stdout or '').strip()[-800:]
        raise RuntimeError(f"selector agent failed (rc={p.returncode}): {err}")
    return (p.stdout or '').strip()


def llm_select_clips(
    transcript: Dict[str, Any],
    heuristic_candidates: List[Candidate],
    *,
    agent_id: str,
    want: int,
    video_title: Optional[str] = None,
    min_dur: float = 15.0,
    max_dur: float = 45.0,
    max_candidates: int = 24,
    window_dur: float = 45.0,
) -> List[Candidate]:
    """Use an OpenClaw "sub-agent" to pick the best short clips.

    We do NOT send the full transcript (too large). Instead:
    - generate a limited set of high-scoring heuristic windows
    - include a compact timed transcript for each window
    - ask the agent to pick/refine start/end within constraints

    Returns a list of Candidate objects sorted by score desc (best first).
    """

    segs = transcript.get('segments') or []
    if not segs or not heuristic_candidates:
        return []

    # Rank by heuristic score; take top N windows for the LLM to choose from.
    ranked = sorted(heuristic_candidates, key=lambda c: c.score, reverse=True)
    ranked = ranked[:max(8, max_candidates)]

    # Build prompt payload
    lines: List[str] = []
    lines.append("You are ClipSelector. Pick the BEST short clips for TikTok/Reels/Shorts.")
    lines.append("")
    lines.append("Hard constraints:")
    if video_title:
        lines.append(f"Context video title (NOT the hook): {video_title}")
        lines.append("The on-screen hook should summarize the CLIP, not repeat the video title.")
        lines.append("")
    lines.append(f"- Each clip duration must be between {min_dur:.0f} and {max_dur:.0f} seconds")
    lines.append("- Must be self-contained (no missing context)")
    lines.append("- Avoid intro/outro, sponsor reads, greetings")
    lines.append("- Prefer segments with a clear hook + punchline/insight")
    lines.append("")
    lines.append("You will be given candidate WINDOWS with timed transcript excerpts.")
    lines.append("Pick up to the requested number of clips. You may shorten inside a window, but do not go outside it.")
    lines.append("")
    lines.append("Return ONLY valid JSON (no markdown, no prose) in exactly this schema:")
    lines.append("{")
    lines.append('  "clips": [')
    lines.append('    {"start": 123.4, "end": 156.7, "hook": "On-screen hook (<=52 chars)", "why": "1 sentence", "window_rank": 1}')
    lines.append('  ]')
    lines.append("}")
    lines.append("")
    lines.append("Hook rules (VERY IMPORTANT):")
    lines.append("- This is NOT the YouTube video title")
    lines.append("- It should sound like a HUMAN talking (not a news headline)")
    lines.append("- Prefer educational / helpful framing: 'how X works', 'how to do Y with X', 'X helps you do Y'")
    lines.append("- 6–10 words, <=52 characters (we render it as 2 lines max)")
    lines.append("- Sentence case (no ALL CAPS, no Title Case)")
    lines.append("- No quotes, no emoji, minimal punctuation")
    lines.append("- No first-person POV (avoid I/me/my/we/our)")
    lines.append("- Must be SPECIFIC to the clip (include 1 concrete noun from transcript)")
    lines.append("- It must STAND ALONE as a summary: if someone only reads the hook, they should understand the point")
    lines.append("- Avoid year/vs/now framing (e.g., '2020 vs now')")
    lines.append("- Avoid generic clickbait templates: 'The Truth About', 'This Changes Everything', 'You Won't Believe'")
    lines.append("- Prefer TAKEAWAY hooks (not teases). Avoid vague framing like 'why I...'")
    lines.append("- Good examples:")
    lines.append("  - 'how ai agents find answers'")
    lines.append("  - 'how to price a startup product'")
    lines.append("  - 'this habit fixes focus'")
    lines.append("  - 'pricing kills startups'")
    lines.append("- Bad examples:")
    lines.append("  - '40 things to know'")
    lines.append("  - 'the problem with X'")
    lines.append("  - '2020 vs now'")
    lines.append("")
    lines.append("ABSOLUTE BANS — hooks containing any of these phrases will be REJECTED:")
    lines.append("- 'more clips like this' / 'more clips daily' / 'more videos like this'")
    lines.append("- 'follow for more' / 'follow me for' / 'subscribe for more' / 'like and follow'")
    lines.append("- UFO/alien/extraterrestrial + 'BREAKING' or 'footage' or 'leaked' or 'secret' framing")
    lines.append("- Any hook that sounds like a follow/subscribe CTA rather than a standalone insight")
    lines.append("")
    lines.append("Duration preference:")
    lines.append(f"- Must be {min_dur:.0f}-{max_dur:.0f}s")
    lines.append("- Prefer 22-35s unless longer is necessary")
    lines.append("")
    lines.append(f"Requested clips: {want}")
    lines.append("")

    for idx, c in enumerate(ranked, 1):
        ws = float(c.start)
        we = float(c.end)
        # Clamp window end to ws+window_dur (in case heuristic used different)
        if we <= ws:
            we = ws + window_dur
        excerpt = _timed_window_text(segs, ws, we, max_chars=900)
        lines.append(f"WINDOW {idx} (rank {idx})")
        lines.append(f"- window_start: {ws:.2f}")
        lines.append(f"- window_end: {we:.2f}")
        lines.append(f"- heuristic_score: {c.score:.1f}")
        lines.append(f"- suggested_hook (optional, may be wrong): {c.title}")
        lines.append("- transcript:")
        lines.append(excerpt)
        lines.append("")

        # Safety: keep CLI message under typical arg limits
        if sum(len(x) + 1 for x in lines) > 28000:
            break

    prompt = "\n".join(lines).strip()

    raw = _call_openclaw_agent(agent_id, prompt, timeout_s=180)
    obj = _extract_json_object(raw)
    if not obj or not isinstance(obj, dict):
        return []
    clips = obj.get('clips')
    if not isinstance(clips, list):
        return []

    out: List[Candidate] = []
    for clip in clips:
        if not isinstance(clip, dict):
            continue
        try:
            st = float(clip.get('start'))
            en = float(clip.get('end'))
        except Exception:
            continue
        if en <= st:
            continue
        dur = en - st
        if dur < min_dur - 0.5 or dur > max_dur + 0.5:
            continue

        # Window rank used to map back to the original ranked windows
        w_rank = clip.get('window_rank')
        try:
            w_rank_i = int(w_rank or 1)
        except Exception:
            w_rank_i = 1
        w_rank_i = max(1, min(w_rank_i, len(ranked)))

        raw_hook = str((clip.get('hook') or clip.get('title') or '')).strip()[:160]
        hook = _compact_hook(raw_hook, max_chars=52, max_words=10)

        # If the LLM produced a weak hook, regenerate from the window transcript.
        if _is_bad_hook(hook):
            try:
                window_text = str(ranked[w_rank_i - 1].text or "")
                hook2 = _compact_hook(_generate_hook(window_text), max_chars=52, max_words=10)
                if not _is_bad_hook(hook2):
                    hook = hook2
            except Exception:
                pass

        # Map back to heuristic score (best-effort) to keep ranking stable.
        base_score = 0.0
        try:
            base_score = float(ranked[w_rank_i - 1].score)
        except Exception:
            base_score = 0.0

        # If the agent returns full-window clips every time, trim to a punchier default length.
        # We still respect max_dur and never exceed the original window end.
        try:
            window_end = float(ranked[w_rank_i - 1].end)
        except Exception:
            window_end = en

        # Produce varied (but punchy) durations instead of always maxing the window.
        # Deterministic target in ~24-35s range based on timestamp.
        target_dur = min(max_dur, max(min_dur, 24.0 + float(int(st) % 12)))
        if (en - st) > (target_dur + 1.0):
            hard_max = min(window_end, st + target_dur)
            hard_min = st + min_dur
            en = _snap_end_to_segments(segs, st, max_end=hard_max, min_end=hard_min)

        text = str(clip.get('why') or '').strip()
        out.append(Candidate(start=st, end=en, score=base_score + 1000.0, title=hook, text=text))

    out.sort(key=lambda c: c.score, reverse=True)
    # Hard cap to requested
    return out[:max(0, want)]


def _hook_score(h: str) -> int:
    """Rule-based score for choosing among multiple hook options."""
    if _is_bad_hook(h):
        return -10_000
    hh = h.strip()
    hlow = hh.lower()

    score = 0
    # Prefer short, readable hooks (now allowing 2 lines)
    n = len(hh)
    if 14 <= n <= 40:
        score += 8
    elif n <= 52:
        score += 4
    else:
        score -= 8

    # Reward specificity a bit (unique non-stopword tokens)
    toks = _tokenize(hlow)
    score += min(10, len(set(toks)) * 2)

    # Conversational glue (but not too generic)
    if any(x in hlow for x in ["why", "here's", "this", "stop", "don't"]):
        score += 2

    # Penalize overly templated words
    if any(x in hlow for x in ["truth", "secret", "exposed", "unbelievable"]):
        score -= 2

    # Avoid punctuation that looks like a headline
    if any(x in hh for x in [":", "—", "–"]):
        score -= 3

    return score


def _refine_hooks_batch(agent_id: str, transcript: Dict[str, Any], candidates: List[Candidate], *, max_items: int = 24) -> int:
    """One extra LLM pass to rewrite hooks into a more human, specific style.

    Returns number of candidates updated.
    """
    segs = transcript.get("segments") or []
    if not segs or not candidates:
        return 0

    take = min(max_items, len(candidates))
    items = []
    for i in range(take):
        c = candidates[i]
        excerpt = _timed_window_text(segs, float(c.start), float(c.end), max_chars=420)
        items.append({
            "idx": i + 1,
            "current_hook": c.title,
            "transcript": excerpt,
        })

    prompt_lines = []
    prompt_lines.append("You are HookWriter. Rewrite on-screen hooks for short video clips.")
    prompt_lines.append("")
    prompt_lines.append("Goal: write a STANDALONE takeaway hook that summarizes the clip.")
    prompt_lines.append("If someone reads ONLY the hook, they should understand the point.")
    prompt_lines.append("")
    prompt_lines.append("Preferred hook patterns (choose the best fit):")
    prompt_lines.append("- how X works (education)")
    prompt_lines.append("- how to do Y with X (actionable)")
    prompt_lines.append("- X helps you do Y (benefit)")
    prompt_lines.append("- the real reason X happens (explanation)")
    prompt_lines.append("")
    prompt_lines.append("Constraints:")
    prompt_lines.append("- 6–10 words, <=52 characters (2 lines max)")
    prompt_lines.append("- sentence case (not Title Case)")
    prompt_lines.append("- no first-person POV (avoid I/me/my/we)")
    prompt_lines.append("- no years / no 'vs' / no 'now'")
    prompt_lines.append("- must include 1 concrete noun from the transcript")
    prompt_lines.append("- avoid templates: 'things to know', 'the problem with', 'the truth about'")
    prompt_lines.append("")
    prompt_lines.append("ABSOLUTE BANS — output MUST NOT contain any of these phrases:")
    prompt_lines.append("- 'more clips like this' / 'more clips daily' / 'more videos like this'")
    prompt_lines.append("- 'follow for more' / 'follow me for' / 'subscribe for more' / 'like and follow'")
    prompt_lines.append("- UFO/alien/extraterrestrial combined with BREAKING/footage/leaked/secret framing")
    prompt_lines.append("")
    prompt_lines.append("Return ONLY valid JSON in this schema:")
    prompt_lines.append("{")
    prompt_lines.append('  "hooks": [')
    prompt_lines.append('    {"idx": 1, "options": ["hook A", "hook B", "hook C"]}')
    prompt_lines.append('  ]')
    prompt_lines.append("}")
    prompt_lines.append("")
    prompt_lines.append("Input:")
    prompt_lines.append(json.dumps({"items": items}, ensure_ascii=False))

    raw = _call_openclaw_agent(agent_id, "\n".join(prompt_lines), timeout_s=120)
    obj = _extract_json_object(raw)
    if not obj or not isinstance(obj, dict):
        return 0

    hooks = obj.get("hooks")
    if not isinstance(hooks, list):
        return 0

    updated = 0
    for hobj in hooks:
        if not isinstance(hobj, dict):
            continue
        try:
            idx = int(hobj.get("idx"))
        except Exception:
            continue
        if idx < 1 or idx > take:
            continue
        opts = hobj.get("options")
        if not isinstance(opts, list) or not opts:
            continue
        opts = [str(x).strip() for x in opts if str(x).strip()]
        if not opts:
            continue

        best = max(opts, key=_hook_score)
        best = _compact_hook(best, max_chars=52, max_words=10)
        if _is_bad_hook(best):
            continue

        candidates[idx - 1].title = best
        updated += 1

    return updated



def write_analyze_md(folder: Path, candidates: List[Candidate]) -> None:
    lines = []
    lines.append(f"# Prism Analyze — Viral Clip Candidates")
    lines.append("")
    lines.append("| # | Timestamp | Hook | Description | File |")
    lines.append("|---|-----------|------|-------------|------|")

    for i, c in enumerate(candidates, 1):
        ts = _format_ts(c.start)
        desc = (c.text[:120] + "…") if len(c.text) > 120 else c.text
        file = f"segments/clip_{i:03d}.mp4"
        hook = c.title.replace("|", "-")
        desc = desc.replace("|", "-")
        lines.append(f"| {i} | {ts} | \"{hook}\" | {desc} | {file} |")

    (folder / "analysis").mkdir(parents=True, exist_ok=True)
    (folder / "analyze.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _download_title_and_id(url: str) -> Tuple[str, str]:
    # Use yt-dlp to extract title + id without downloading
    p = _run(["yt-dlp", "--print", "title", "--print", "id", url], timeout=120)
    if p.returncode != 0:
        # fallback: parse v=... from URL
        vid = "unknown"
        m = re.search(r"v=([A-Za-z0-9_\-]+)", url)
        if m:
            vid = m.group(1)
        return ("video", vid)
    lines = [ln.strip() for ln in (p.stdout or "").splitlines() if ln.strip()]
    if len(lines) >= 2:
        return lines[0], lines[1]
    if len(lines) == 1:
        return lines[0], "unknown"
    return "video", "unknown"


def _yt_dlp_download(url: str, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    tmpl = str(raw_dir / "source.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestvideo+bestaudio/best",
        "-o", tmpl,
        "--no-playlist",
        url,
    ]
    p = _run(cmd, timeout=None, capture=False, text=True)
    if p.returncode != 0:
        raise RuntimeError("yt-dlp download failed")

    # Find the downloaded file
    for f in raw_dir.glob("source.*"):
        if f.is_file() and f.stat().st_size > 0:
            return f
    # fallback: any media file
    for f in raw_dir.iterdir():
        if f.suffix.lower() in (".mp4", ".webm", ".mkv") and f.stat().st_size > 0:
            return f
    raise FileNotFoundError("Downloaded video not found in raw/")


def _whisper_transcribe(video_path: Path, out_dir: Path, model: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "whisper",
        str(video_path),
        "--model", model,
        "--language", "en",
        "--word_timestamps", "True",
        "--output_format", "json",
        "--output_dir", str(out_dir),
    ]

    p = _run(cmd, timeout=None, capture=False, text=True)
    if p.returncode != 0:
        raise RuntimeError("Whisper transcription failed")

    # whisper names output after stem
    expected = out_dir / f"{video_path.stem}.json"
    if expected.exists():
        return expected

    # fallback: first json in out_dir
    for f in out_dir.glob("*.json"):
        return f

    raise FileNotFoundError("Whisper JSON output not found")


def _extract_segment(source: Path, out_path: Path, start: float, duration: float, *, pre_roll: float = 2.5) -> float:
    """Extract a clip segment with a small pre-roll to avoid mid-sentence cuts.

    Returns the actual start used.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    actual_start = max(0.0, float(start) - float(pre_roll))

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(actual_start),
        "-i", str(source),
        "-t", str(max(1.0, duration)),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(out_path),
    ]
    p = _run(cmd, timeout=int(duration) + 120, capture=True)
    if p.returncode != 0 or not out_path.exists() or out_path.stat().st_size < 50_000:
        raise RuntimeError(f"Failed to extract segment: {out_path.name}: {p.stderr[-400:] if p.stderr else ''}")

    return actual_start


def _portrait_crop_box(
    w: int,
    h: int,
    *,
    cx: float,
    cy: float,
    face_w: Optional[float] = None,
    target_aspect: float = 9.0 / 16.0,
) -> Tuple[int, int, int, int]:
    """Compute a static crop box (x,y,cw,ch) that yields a 9:16 portrait frame.

    If face_w is provided, we zoom so the face is reasonably large; otherwise we do a centered fill-crop.
    """
    # Base crop that fits the aspect inside the source
    if (w / max(1.0, h)) >= target_aspect:
        base_h = h
        base_w = int(round(base_h * target_aspect))
    else:
        base_w = w
        base_h = int(round(base_w / target_aspect))

    crop_w, crop_h = base_w, base_h

    # Optional zoom based on face size
    if face_w and face_w > 0:
        # Less aggressive zoom = smoother + fewer bad crops.
        desired_face_ratio = 0.26  # face width as fraction of crop width
        desired_w = int(round(face_w / desired_face_ratio))
        # Try to zoom in, but never exceed base crop or become too tiny.
        # Keep at least ~72% of the base crop width to avoid over-zoom.
        crop_w = max(int(base_w * 0.72), min(base_w, desired_w))
        crop_h = int(round(crop_w / target_aspect))
        if crop_h > h:
            crop_h = h
            crop_w = int(round(crop_h * target_aspect))

    crop_w = min(crop_w, w)
    crop_h = min(crop_h, h)

    x = int(round(cx - crop_w / 2))
    y = int(round(cy - crop_h / 2))
    x = max(0, min(x, w - crop_w))
    y = max(0, min(y, h - crop_h))
    return x, y, crop_w, crop_h


def _detect_speaker_face(seg_path: Path) -> Dict[str, Any]:
    """Best-effort face-based speaker center detection.

    Returns:
      { ok, confidence, cx, cy, face_w, face_h, reason?, multi_face_ratio? }

    Uses OpenCV Haar cascade + a simple motion proxy between frames.
    Conservative by design: if we suspect a 2-person shot, we disable smartzoom
    to avoid confidently cropping the wrong person.
    """
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        return {"ok": False, "confidence": 0.0}

    cap = cv2.VideoCapture(str(seg_path))
    if not cap.isOpened():
        return {"ok": False, "confidence": 0.0}

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
    dur = (frames / fps) if (fps and frames) else (_ffprobe_duration(seg_path) or 0.0)

    if w <= 0 or h <= 0 or dur <= 0.5:
        cap.release()
        return {"ok": False, "confidence": 0.0}

    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Sample up to 10 timestamps across the clip
    n = 12
    ts = [0.4 + (dur - 0.8) * i / max(1, n - 1) for i in range(n)]

    picks: List[Tuple[float, float, float, float]] = []  # cx,cy,fw,fh
    multi_face_frames = 0
    face_frames = 0

    for t in ts:
        cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, t) * 1000.0)
        ok1, frame1 = cap.read()
        if not ok1 or frame1 is None:
            continue

        t2 = min(dur - 0.01, t + 0.35)
        cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, t2) * 1000.0)
        ok2, frame2 = cap.read()
        frame2 = frame2 if ok2 else None

        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY) if frame2 is not None else None

        faces = cascade.detectMultiScale(gray1, scaleFactor=1.1, minNeighbors=6, minSize=(90, 90))
        if faces is None or len(faces) == 0:
            continue

        face_frames += 1

        # Detect obvious 2-person shot: two large faces in the same frame.
        if len(faces) >= 2:
            areas = sorted([float(fw * fh) for (_, _, fw, fh) in faces], reverse=True)
            if len(areas) >= 2 and areas[1] >= areas[0] * 0.60:
                multi_face_frames += 1

        best = None
        best_score = -1e9
        for (x, y, fw, fh) in faces:
            # Plausibility filters to reduce false positives (e.g., microphones).
            if fh <= 0 or fw <= 0:
                continue
            aspect = float(fh) / float(fw)
            if not (0.75 <= aspect <= 1.65):
                continue
            # Faces are rarely in the very bottom of a podcast frame.
            if y > (h * 0.62):
                continue

            x2 = max(0, min(int(x), w - 1))
            y2 = max(0, min(int(y), h - 1))
            x3 = max(1, min(int(x + fw), w))
            y3 = max(1, min(int(y + fh), h))
            roi1 = gray1[y2:y3, x2:x3]
            if roi1.size:
                mean_luma = float(np.mean(roi1))
                if mean_luma < 35.0:
                    continue

            area = (fw * fh) / float(max(1, w * h))
            motion = 0.0
            if gray2 is not None:
                roi2 = gray2[y2:y3, x2:x3]
                if roi1.size and roi2.size:
                    motion = float(np.mean(np.abs(roi2.astype(np.int16) - roi1.astype(np.int16)))) / 255.0

            score = (motion * 2.0) + (area * 0.6)
            if score > best_score:
                best_score = score
                best = (x, y, fw, fh)

        if best is None:
            continue

        x, y, fw, fh = best
        cx = float(x + fw / 2)
        cy = float(y + fh / 2)
        picks.append((cx, cy, float(fw), float(fh)))

    cap.release()

    confidence = len(picks) / float(len(ts)) if ts else 0.0
    multi_face_ratio = (multi_face_frames / float(max(1, face_frames))) if face_frames else 0.0

    # If we strongly suspect a 2-person shot, do NOT smartzoom (letterbox is safer).
    if multi_face_ratio >= 0.25:
        return {"ok": False, "confidence": confidence, "multi_face_ratio": multi_face_ratio, "reason": "multi-face"}

    # Be conservative: only enable smartzoom when we see faces consistently.
    if confidence < 0.65:
        return {"ok": False, "confidence": confidence, "multi_face_ratio": multi_face_ratio, "reason": "low-confidence"}

    # Median center is stable and avoids jitter
    import statistics as stats

    cx = float(stats.median([p[0] for p in picks]))
    cy = float(stats.median([p[1] for p in picks]))
    fw = float(stats.median([p[2] for p in picks]))
    fh = float(stats.median([p[3] for p in picks]))

    return {
        "ok": True,
        "confidence": float(confidence),
        "multi_face_ratio": float(multi_face_ratio),
        "cx": cx,
        "cy": cy,
        "face_w": fw,
        "face_h": fh,
        "width": w,
        "height": h,
    }


def _crop_to_portrait_ffmpeg(in_path: Path, out_path: Path, *, x: int, y: int, w: int, h: int) -> bool:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    vf = f"crop={w}:{h}:{x}:{y},scale=1080:1920"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(in_path),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "19",
        "-c:a",
        "copy",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    p = _run(cmd, timeout=120, capture=True)
    return p.returncode == 0 and out_path.exists() and out_path.stat().st_size > 80_000


def _blur_fill_portrait_ffmpeg(in_path: Path, out_path: Path, *, ss: Optional[float] = None, t: Optional[float] = None) -> bool:
    """Full-screen 9:16 using blurred background + centered original (safe fallback)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Background: scale to fill, crop, blur, slightly darken.
    # Foreground: scale to fit inside 1080x1920.
    fc = (
        "[0:v]"
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "boxblur=10:1,"
        "eq=brightness=-0.05:saturation=1.05[bg];"
        "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )

    cmd = ["ffmpeg", "-y"]
    if ss is not None:
        cmd += ["-ss", str(max(0.0, ss))]
    cmd += ["-i", str(in_path)]
    if t is not None:
        cmd += ["-t", str(max(0.05, t))]

    cmd += [
        "-filter_complex", fc,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(out_path),
    ]
    p = _run(cmd, timeout=180, capture=True)
    return p.returncode == 0 and out_path.exists() and out_path.stat().st_size > 80_000


def _crop_has_face(seg_path: Path, *, x: int, y: int, w: int, h: int) -> Tuple[bool, float]:
    """Validate that the chosen crop likely contains a face.

    Returns (ok, ratio_seen). If not ok, we should not trust smartzoom.
    """
    try:
        import cv2  # type: ignore
    except Exception:
        return True, 1.0  # can't validate; don't block

    cap = cv2.VideoCapture(str(seg_path))
    if not cap.isOpened():
        return False, 0.0

    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frames = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
    dur = (frames / fps) if (fps and frames) else (_ffprobe_duration(seg_path) or 0.0)

    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # sample 5 frames
    ts = [0.4, 0.9, 1.6, max(2.2, dur * 0.5), max(0.8, dur - 0.8)]
    ts = [t for t in ts if t < max(0.2, dur - 0.05)]
    if not ts:
        ts = [0.4]

    seen = 0
    total = 0

    for t in ts:
        cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, t) * 1000.0)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        total += 1

        # clamp crop to frame
        xx = max(0, min(int(x), max(0, W - 1)))
        yy = max(0, min(int(y), max(0, H - 1)))
        ww = max(1, min(int(w), W - xx))
        hh = max(1, min(int(h), H - yy))

        roi = frame[yy:yy + hh, xx:xx + ww]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(90, 90))
        if faces is not None and len(faces) > 0:
            seen += 1

    cap.release()

    ratio = (seen / float(total)) if total else 0.0
    # If we rarely see a face in the crop, it's not a usable smartzoom.
    return (ratio >= 0.6), ratio


def _shot_boundaries(seg_path: Path, *, sample_fps: float = 2.0, thresh: float = 0.35, min_gap: float = 1.0) -> List[float]:
    """Detect hard cuts using histogram distance on sampled frames."""
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        return [0.0, float(_ffprobe_duration(seg_path) or 0.0)]

    dur = float(_ffprobe_duration(seg_path) or 0.0)
    if dur <= 0.5:
        return [0.0, dur]

    cap = cv2.VideoCapture(str(seg_path))
    if not cap.isOpened():
        return [0.0, dur]

    times = []
    step = max(0.2, 1.0 / max(0.1, sample_fps))
    t = 0.0
    while t < dur:
        times.append(t)
        t += step

    prev_hist = None
    cuts: List[float] = []
    last_cut = 0.0

    for tt in times:
        cap.set(cv2.CAP_PROP_POS_MSEC, tt * 1000.0)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        small = cv2.resize(frame, (320, 180))
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0], None, [32], [0, 180])
        hist = cv2.normalize(hist, hist).flatten()

        if prev_hist is not None:
            d = float(cv2.compareHist(prev_hist.astype(np.float32), hist.astype(np.float32), cv2.HISTCMP_BHATTACHARYYA))
            if d > thresh and (tt - last_cut) >= min_gap:
                cuts.append(tt)
                last_cut = tt
        prev_hist = hist

    cap.release()

    bounds = [0.0] + cuts + [dur]
    # ensure monotonic + min segment length
    out: List[float] = [bounds[0]]
    for x in bounds[1:]:
        if x - out[-1] >= 0.6:
            out.append(x)
    if out[-1] < dur:
        out.append(dur)
    return out


def _render_crop_part(seg_path: Path, out_path: Path, *, ss: float, t: float, crop: Tuple[int, int, int, int]) -> bool:
    x, y, w, h = crop
    vf = f"crop={w}:{h}:{x}:{y},scale=1080:1920"
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(max(0.0, ss)),
        "-i", str(seg_path),
        "-t", str(max(0.05, t)),
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(out_path),
    ]
    p = _run(cmd, timeout=180, capture=True)
    return p.returncode == 0 and out_path.exists() and out_path.stat().st_size > 80_000


def _concat_parts(parts: List[Path], out_path: Path) -> bool:
    if not parts:
        return False
    if len(parts) == 1:
        try:
            parts[0].replace(out_path)
            return out_path.exists()
        except Exception:
            pass

    lst = out_path.with_suffix(".concat.txt")
    lines = [f"file '{p.as_posix()}'" for p in parts]
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(lst),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(out_path),
    ]
    p = _run(cmd, timeout=240, capture=True)
    ok = p.returncode == 0 and out_path.exists() and out_path.stat().st_size > 100_000
    try:
        lst.unlink()
    except Exception:
        pass
    return ok


def _active_speaker_bbox(seg_path: Path, *, ss: float, ee: float) -> Optional[Tuple[float, float, float, float, float]]:
    """Return (cx,cy,fw,fh,conf) for the active speaker within [ss,ee]."""
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        return None

    dur = float(_ffprobe_duration(seg_path) or 0.0)
    ss = max(0.0, min(ss, dur))
    ee = max(ss + 0.05, min(ee, dur))

    cap = cv2.VideoCapture(str(seg_path))
    if not cap.isOpened():
        return None

    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    if not W or not H:
        cap.release()
        return None

    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # sample up to 12 frames inside the shot
    shot_len = ee - ss
    n = max(6, min(12, int(shot_len / 0.6) + 1))
    ts = [ss + (shot_len * i / max(1, n - 1)) for i in range(n)]

    picks_left: List[Tuple[float, float, float, float, float]] = []
    picks_right: List[Tuple[float, float, float, float, float]] = []

    prev_gray = None

    for tt in ts:
        cap.set(cv2.CAP_PROP_POS_MSEC, tt * 1000.0)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(90, 90))
        if faces is None or len(faces) == 0:
            prev_gray = gray
            continue

        best = None
        best_score = -1e9
        for (x, y, fw, fh) in faces:
            # plausibility filters
            if fh <= 0 or fw <= 0:
                continue
            aspect = float(fh) / float(fw)
            if not (0.75 <= aspect <= 1.65):
                continue
            if y > (H * 0.62):
                continue

            x2 = max(0, min(int(x), W - 1))
            y2 = max(0, min(int(y), H - 1))
            x3 = max(1, min(int(x + fw), W))
            y3 = max(1, min(int(y + fh), H))
            roi = gray[y2:y3, x2:x3]
            if roi.size:
                if float(np.mean(roi)) < 35.0:
                    continue

            area = (fw * fh) / float(max(1, W * H))
            mouth_motion = 0.0
            if prev_gray is not None:
                # mouth region motion proxy
                my1 = int(y2 + (y3 - y2) * 0.62)
                mouth1 = gray[my1:y3, x2:x3]
                mouth0 = prev_gray[my1:y3, x2:x3] if prev_gray.shape == gray.shape else None
                if mouth0 is not None and mouth1.size and mouth0.size:
                    mouth_motion = float(np.mean(np.abs(mouth1.astype(np.int16) - mouth0.astype(np.int16)))) / 255.0

            score = (mouth_motion * 2.2) + (area * 0.7)
            if score > best_score:
                best_score = score
                best = (x, y, fw, fh, score)

        prev_gray = gray
        if best is None:
            continue

        x, y, fw, fh, score = best
        cx = float(x + fw / 2)
        cy = float(y + fh / 2)

        if cx < (W / 2.0):
            picks_left.append((cx, cy, float(fw), float(fh), float(score)))
        else:
            picks_right.append((cx, cy, float(fw), float(fh), float(score)))

    cap.release()

    picks = picks_left if sum(p[4] for p in picks_left) >= sum(p[4] for p in picks_right) else picks_right
    if not picks:
        return None

    import statistics as stats
    cx = float(stats.median([p[0] for p in picks]))
    cy = float(stats.median([p[1] for p in picks]))
    fw = float(stats.median([p[2] for p in picks]))
    fh = float(stats.median([p[3] for p in picks]))

    conf = len(picks) / float(len(ts)) if ts else 0.0
    return (cx, cy, fw, fh, float(conf))


def _prepare_portrait_segment(seg_path: Path, out_path: Path, *, portrait_mode: str = "letterbox") -> Tuple[Path, Dict[str, Any]]:
    """Create a 9:16 portrait clip.

    Modes:
      - letterbox (default): no blur. Keep the original segment and let add_captions.py letterbox
        it onto a clean black 9:16 canvas.
      - smartzoom: (currently treated as letterbox) reserved for future crop/tracking.
      - blurfill: deprecated/disabled (mapped to letterbox)

    Returns: (path_to_use, meta)
    """
    portrait_mode = (portrait_mode or "letterbox").lower().strip()
    if portrait_mode not in ("letterbox", "blurfill", "smartzoom"):
        portrait_mode = "letterbox"

    # blurfill is deprecated/disabled: treat it as clean letterbox.
    if portrait_mode == "blurfill":
        portrait_mode = "letterbox"

    # No-blur mode: keep segment as-is. add_captions.py will render onto a
    # black 9:16 canvas.
    if portrait_mode in ("letterbox", "smartzoom"):
        return seg_path, {"layout": "letterbox", "reason": f"{portrait_mode}-mode"}

    info = _ffprobe_video_info(seg_path)
    W, H = int(info.get("width") or 0), int(info.get("height") or 0)
    if not W or not H:
        return seg_path, {"layout": "passthrough", "reason": "no-video-stream"}

    dur = float(_ffprobe_duration(seg_path) or 0.0)
    if dur <= 0.5:
        return seg_path, {"layout": "passthrough", "reason": "too-short"}

    # Blurfill is disabled above; we should never reach a blurfill path here.
    bounds = _shot_boundaries(seg_path)
    # Cap complexity
    if len(bounds) > 8:
        bounds = [0.0, dur]

    parts: List[Path] = []
    shots_meta: List[Dict[str, Any]] = []

    for si in range(len(bounds) - 1):
        ss = float(bounds[si])
        ee = float(bounds[si + 1])
        if ee - ss < 0.6:
            continue

        sp = _active_speaker_bbox(seg_path, ss=ss, ee=ee)
        if sp is None:
            # safe full-screen fallback
            part = out_path.with_name(out_path.stem + f"_s{si:02d}_blur.mp4")
            if _blur_fill_portrait_ffmpeg(seg_path, part, ss=ss, t=ee - ss):
                parts.append(part)
                shots_meta.append({"start": ss, "end": ee, "layout": "blurfill", "reason": "no-face"})
            continue

        cx, cy, fw, fh, conf = sp
        # require high confidence to crop; otherwise blurfill
        if conf < 0.72:
            part = out_path.with_name(out_path.stem + f"_s{si:02d}_blur.mp4")
            if _blur_fill_portrait_ffmpeg(seg_path, part, ss=ss, t=ee - ss):
                parts.append(part)
                shots_meta.append({"start": ss, "end": ee, "layout": "blurfill", "reason": "low-conf", "face_conf": conf})
            continue

        # headroom
        cy = max(0.0, cy - (H * 0.06))

        x, y, cw, ch = _portrait_crop_box(W, H, cx=cx, cy=cy, face_w=fw)

        # crop must actually contain a face
        ok_face, ratio = _crop_has_face(seg_path, x=x, y=y, w=cw, h=ch)
        if not ok_face:
            part = out_path.with_name(out_path.stem + f"_s{si:02d}_blur.mp4")
            if _blur_fill_portrait_ffmpeg(seg_path, part, ss=ss, t=ee - ss):
                parts.append(part)
                shots_meta.append({"start": ss, "end": ee, "layout": "blurfill", "reason": "crop-no-face", "crop_face_ratio": ratio})
            continue

        part = out_path.with_name(out_path.stem + f"_s{si:02d}.mp4")
        if _render_crop_part(seg_path, part, ss=ss, t=ee - ss, crop=(x, y, cw, ch)):
            parts.append(part)
            shots_meta.append({"start": ss, "end": ee, "layout": "smartzoom", "face_conf": conf, "crop": [x, y, cw, ch], "crop_face_ratio": ratio})
        else:
            # blurfill fallback
            part = out_path.with_name(out_path.stem + f"_s{si:02d}_blur.mp4")
            if _blur_fill_portrait_ffmpeg(seg_path, part, ss=ss, t=ee - ss):
                parts.append(part)
                shots_meta.append({"start": ss, "end": ee, "layout": "blurfill", "reason": "crop-failed"})

    if not parts:
        blurred = out_path.with_name(out_path.stem + "_blurfill.mp4")
        if _blur_fill_portrait_ffmpeg(seg_path, blurred):
            return blurred, {"layout": "blurfill", "reason": "no-parts", "src": [W, H]}
        return seg_path, {"layout": "letterbox", "reason": "no-parts"}

    out_ok = _concat_parts(parts, out_path)

    # cleanup intermediate parts
    for p in parts:
        try:
            if p.exists() and p != out_path:
                p.unlink()
        except Exception:
            pass

    if out_ok:
        return out_path, {"layout": "shot_speaker", "shots": len(shots_meta), "shots_meta": shots_meta[:6], "src": [W, H]}

    blurred = out_path.with_name(out_path.stem + "_blurfill.mp4")
    if _blur_fill_portrait_ffmpeg(seg_path, blurred):
        return blurred, {"layout": "blurfill", "reason": "concat-failed", "src": [W, H]}

    return seg_path, {"layout": "letterbox", "reason": "concat-failed"}


def _apply_look_ffmpeg(in_path: Path, out_path: Path, *, look: str) -> bool:
    """Apply a lightweight, 'viral' color grade.

    Must be failure-tolerant; if this fails we fall back to the ungraded video.
    """
    look = (look or "auto").lower()
    if look == "none":
        return False

    # Subtle defaults (avoid destroying skin tones)
    if look in ("auto", "dark"):
        vf = "eq=contrast=1.08:brightness=-0.035:saturation=1.12,vignette=PI/5"
    elif look == "punchy":
        vf = "eq=contrast=1.12:brightness=-0.02:saturation=1.20,unsharp=5:5:0.8:3:3:0.0"
    else:  # clean
        vf = "eq=contrast=1.04:brightness=-0.015:saturation=1.06"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(in_path),
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(out_path),
    ]
    p = _run(cmd, timeout=180, capture=True)
    return p.returncode == 0 and out_path.exists() and out_path.stat().st_size > 100_000


def _render_final(segment_path: Path, final_path: Path, title: str, whisper_model: str, *, look: str = "auto") -> Path:
    """Render captions+hook to a temporary file and return the temp path.

    Caller is responsible for validation + moving into final_path.
    This prevents corrupted/partial renders from polluting /final.
    """
    final_path.parent.mkdir(parents=True, exist_ok=True)

    # Keep a valid media extension so ffmpeg/moviepy can infer the muxer.
    # (".mp4.tmp" can fail with "use a standard extension".)
    tmp_path = final_path.with_name(final_path.stem + ".tmp" + final_path.suffix)
    if tmp_path.exists():
        try:
            tmp_path.unlink()
        except Exception:
            pass

    # Render captions/hook IN-PROCESS to minimize multi-script mismatch and failure modes.
    # (We still rely on ffmpeg under the hood via MoviePy, but we avoid a separate Python subprocess.)
    try:
        import importlib.util

        mod_name = "_prism_add_captions"
        mod = sys.modules.get(mod_name)
        if mod is None:
            spec = importlib.util.spec_from_file_location(mod_name, str(ADD_CAPTIONS))
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Could not import add_captions module from {ADD_CAPTIONS}")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)  # type: ignore

        # Call the library entrypoint
        mod.add_captions_to_video(
            video_path=str(segment_path),
            subtitle_path=None,
            output_path=str(tmp_path),
            title=title,
            use_whisper=True,
            whisper_model=whisper_model,
        )

    except Exception as e:
        raise RuntimeError(f"add_captions failed: {final_path.name}: {e}")

    if not tmp_path.exists() or tmp_path.stat().st_size < 100_000:
        raise RuntimeError(f"add_captions failed: {final_path.name}: output missing/small")

    # Apply post look (optional). Failure-tolerant.
    graded = tmp_path.with_name(tmp_path.stem + "_look.mp4")
    try:
        if _apply_look_ffmpeg(tmp_path, graded, look=look):
            try:
                tmp_path.unlink()
            except Exception:
                pass
            graded.replace(tmp_path)
    except Exception:
        try:
            if graded.exists():
                graded.unlink()
        except Exception:
            pass

    return tmp_path


def _validate_final(path: Path, *, min_dur: float = 15, max_dur: float = 45) -> Tuple[bool, str]:
    dur = _ffprobe_duration(path)
    if dur is None:
        return False, "no-duration"
    if not (min_dur <= dur <= max_dur):
        return False, f"bad-duration:{dur:.1f}s"

    fmt_dur, v_dur, a_dur = _ffprobe_av_durations(path)
    # Catch cases where audio is full-length but video stream is truncated (often shows as "black" thumbnails).
    if v_dur is not None and abs(v_dur - dur) > 1.0:
        return False, f"video-truncated:{v_dur:.1f}s"
    if a_dur is not None and abs(a_dur - dur) > 1.0:
        return False, f"audio-duration-mismatch:{a_dur:.1f}s"
    if v_dur is not None and a_dur is not None and abs(v_dur - a_dur) > 1.0:
        return False, f"av-mismatch:v{v_dur:.1f}/a{a_dur:.1f}"

    info = _ffprobe_video_info(path)
    w, h = info.get("width"), info.get("height")
    if not w or not h:
        return False, "no-video-stream"

    ratio = float(w) / float(h)
    if not (0.50 <= ratio <= 0.70):
        return False, f"bad-aspect:{w}x{h}"

    if path.stat().st_size < 200_000:
        return False, "too-small"

    # Ensure the file actually decodes at mid-point (catches truncated video streams)
    if _ffmpeg_yavg(path, dur * 0.5) is None:
        return False, "no-frame-mid"

    if _looks_like_black_screen(path):
        return False, "black-screen"

    return True, "OK"


def run_pipeline(url: str, outdir: Path, *, num_clips: int, clip_duration: float, skip_intro: float,
                 whisper_full_model: str, whisper_clip_model: str, pre_roll: float = 2.5,
                 selector: str = 'llm', selector_agent: str = 'prism', selector_max_candidates: int = 24,
                 min_clip_dur: float = 15.0, max_clip_dur: float = 45.0,
                 look: str = 'auto',
                 portrait_mode: str = 'blurfill',
                 resume: bool = True) -> Dict[str, Any]:

    _require_bin("yt-dlp")
    _require_bin("ffmpeg")
    _require_bin("ffprobe")
    _require_bin("whisper")

    title, vid = _download_title_and_id(url)
    folder = outdir / f"{_safe_name(title)}_{vid}"

    raw_dir = folder / "raw"
    analysis_dir = folder / "analysis"
    segments_dir = folder / "segments"
    final_dir = folder / "final"

    # Ensure stage directories exist early (prevents resume scan crashes)
    raw_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    segments_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    status_path = folder / "status.json"
    result_path = folder / "result.json"

    def set_status(stage: str, **extra: Any) -> None:
        data = {
            "updated_at": _iso_now(),
            "stage": stage,
            "url": url,
            "video_id": vid,
            "title": title,
            "folder": str(folder),
            "portrait_mode": portrait_mode,
            # PID of the active Prism worker (useful for stuck detection / safe restarts).
            "pid": os.getpid(),
        }
        data.update(extra)
        _atomic_write_json(status_path, data)

    folder.mkdir(parents=True, exist_ok=True)

    set_status("PRECHECK")

    # ---------------------------
    # DOWNLOAD
    # ---------------------------
    source_path: Optional[Path] = None
    if resume:
        for f in raw_dir.glob("source.*"):
            if f.is_file() and f.stat().st_size > 0:
                source_path = f
                break
        if not source_path:
            # legacy downloads
            media = [p for p in raw_dir.iterdir() if p.suffix.lower() in (".mp4", ".webm", ".mkv")]
            if media:
                source_path = sorted(media, key=lambda p: p.stat().st_size, reverse=True)[0]

    if not source_path:
        set_status("DOWNLOADING")
        source_path = _yt_dlp_download(url, raw_dir)

    set_status("DOWNLOADED", source=str(source_path), size_mb=round(source_path.stat().st_size / (1024 * 1024), 1))

    # ---------------------------
    # AUDIO CHECK
    # ---------------------------
    set_status("AUDIO_CHECK")

    if not _ffprobe_has_audio(source_path):
        set_status("FAILED_NO_AUDIO_STREAM")
        return {"ok": False, "folder": str(folder), "reason": "no-audio-stream"}

    dur = _ffprobe_duration(source_path) or 0.0
    samples = []
    for st in [0.0, max(0.0, dur * 0.5 - 30), max(0.0, dur - 90)]:
        ratio = _silence_ratio_sample(source_path, st, 60.0)
        if ratio is not None:
            samples.append(ratio)
    # If all samples are extremely silent, treat as no voice
    if samples and all(r > 0.93 for r in samples):
        set_status("FAILED_NO_VOICE", silence_samples=samples)
        return {"ok": False, "folder": str(folder), "reason": "no-voice"}

    set_status("AUDIO_OK", silence_samples=samples)

    # ---------------------------
    # FULL TRANSCRIPT
    # ---------------------------
    transcript_json: Optional[Path] = None
    transcript_path = analysis_dir / "transcript.json"
    if resume and transcript_path.exists() and transcript_path.stat().st_size > 10_000:
        transcript_json = transcript_path
    else:
        set_status("TRANSCRIBING", whisper_model=whisper_full_model)
        wjson = _whisper_transcribe(source_path, analysis_dir, whisper_full_model)
        # normalize name
        if wjson != transcript_path:
            transcript_path.write_text(wjson.read_text(encoding="utf-8"), encoding="utf-8")
        transcript_json = transcript_path

    set_status("TRANSCRIBED", transcript=str(transcript_json))

    transcript = json.loads(transcript_json.read_text(encoding="utf-8"))

    # ---------------------------
    # ANALYZE FULL VIDEO
    # ---------------------------
    set_status("ANALYZING")

    if selector == 'llm':
        pre_roll = 0.0
    candidate_pool = analyze_transcript(
        transcript,
        clip_duration=clip_duration,
        top_n=max(num_clips * 10, 60),  # extra slack so we can skip bad/silent segments
        skip_intro=skip_intro,
    )

    if not candidate_pool:
        set_status("FAILED_NO_CANDIDATES")
        return {"ok": False, "folder": str(folder), "reason": "no-candidates"}

    # Write a human-readable table for debugging/inspection (top 20)
    write_analyze_md(folder, candidate_pool[:20])

    # Optional: LLM-powered clip selection (spawns an OpenClaw agent turn)
    llm_selected: List[Candidate] = []
    if selector == 'llm':
        set_status('SELECTING', selector_agent=selector_agent)
        try:
            llm_selected = llm_select_clips(
                transcript,
                candidate_pool,
                agent_id=selector_agent,
                want=max(num_clips, 1),
                video_title=title,
                min_dur=min_clip_dur,
                max_dur=max_clip_dur,
                max_candidates=selector_max_candidates,
                window_dur=min(clip_duration, max_clip_dur),
            )
        except Exception as e:
            # Fall back to heuristics silently; we still keep observability in status.json
            set_status('SELECTING_FAILED', error=str(e)[:300])
            llm_selected = []

        if llm_selected:
            # Prefer LLM picks first, but keep heuristic candidates as backup for validation failures.
            def _near(a: float, b: float) -> bool:
                return abs(a - b) < 5.0

            merged: List[Candidate] = []
            for c in llm_selected + candidate_pool:
                if any(_near(c.start, m.start) for m in merged):
                    continue
                merged.append(c)
            candidate_pool = merged
            set_status('SELECTED', llm_clips=len(llm_selected), merged_candidates=len(candidate_pool))

    # Hard cap candidates to avoid pathological long runs when many candidates fail validation.
    # This keeps cron runs predictable and prevents “retry forever” behavior.
    max_candidates = max(int(selector_max_candidates) * 4, int(num_clips) * 20)
    if len(candidate_pool) > max_candidates:
        candidate_pool = candidate_pool[:max_candidates]
        set_status("CANDIDATES_TRIMMED", candidates=len(candidate_pool), max_candidates=max_candidates)

    # Optional hook refinement pass (1 extra LLM call per video) to make hooks sound human.
    # This reduces "headline-y" or templated hooks and enforces our guardrails.
    if selector == "llm":
        try:
            set_status("HOOK_REFINING", agent=selector_agent)
            updated = _refine_hooks_batch(
                selector_agent,
                transcript,
                candidate_pool,
                max_items=min(len(candidate_pool), max(int(num_clips) * 6, 24)),
            )
            if updated:
                set_status("HOOK_REFINED", updated=updated)
        except Exception as e:
            set_status("HOOK_REFINE_FAILED", error=str(e)[:200])

    analyze_json_path = analysis_dir / "analyze.json"
    _atomic_write_json(
        analyze_json_path,
        {
            "generated_at": _iso_now(),
            "url": url,
            "video_id": vid,
            "title": title,
            "clip_duration": clip_duration,
            "skip_intro": skip_intro,
            "selector": selector,
            "selector_agent": selector_agent if selector == "llm" else None,
            "llm_selected": [
                {"start": c.start, "end": c.end, "title": c.title} for c in llm_selected
            ] if selector == "llm" and llm_selected else [],
            "candidate_pool": [
                {
                    "rank": i + 1,
                    "start": c.start,
                    "end": c.end,
                    "score": c.score,
                    "title": c.title,
                    "timestamp": _format_ts(c.start),
                }
                for i, c in enumerate(candidate_pool)
            ],
        },
    )
    set_status("ANALYZED", candidates=len(candidate_pool))

    # ---------------------------
    # EXTRACT + RENDER
    # ---------------------------
    clips_out: List[Dict[str, Any]] = []

    out_index = 0
    for cand in candidate_pool:
        if out_index >= num_clips:
            break

        i = out_index + 1
        seg_path = segments_dir / f"clip_{i:03d}.mp4"
        fin_path = final_dir / f"clip_{i:03d}.mp4"

        # Always re-extract for correctness (prevents stale segment mismatch)
        cand_dur = max(1.0, float(cand.end) - float(cand.start))

        set_status("EXTRACTING", clip=i, start=cand.start, duration=cand_dur, pre_roll=pre_roll)
        actual_start = _extract_segment(source_path, seg_path, cand.start, cand_dur, pre_roll=pre_roll)

        # Clip-level voice gate (reject silent clips even if the full video has voice)
        if not _ffprobe_has_audio(seg_path):
            clips_out.append({
                "index": i,
                "start": actual_start,
                "end": cand.end,
                "duration": clip_duration,
                "score": cand.score,
                "title": cand.title,
                "segment": str(seg_path),
                "final": None,
                "validated": False,
                "validation": "no-audio-in-clip",
            })
            continue

        silence_ratio = _silence_ratio_sample(seg_path, 0.0, min(45.0, cand_dur))
        if silence_ratio is not None and silence_ratio > 0.90:
            clips_out.append({
                "index": i,
                "start": actual_start,
                "end": cand.end,
                "duration": clip_duration,
                "score": cand.score,
                "title": cand.title,
                "segment": str(seg_path),
                "final": None,
                "validated": False,
                "validation": f"too-silent:{silence_ratio:.2f}",
            })
            continue

        # Prepare portrait framing (Strategem A default: framed/blurfill), then render captions+hook.
        portrait_seg = segments_dir / f"clip_{i:03d}_portrait.mp4"
        seg_for_caps, layout_meta = _prepare_portrait_segment(seg_path, portrait_seg, portrait_mode=portrait_mode)

        # Render final (captions + hook) to temp, then validate, then move into /final
        set_status(
            "RENDERING",
            clip=i,
            title=cand.title,
            whisper_model=whisper_clip_model,
            layout=layout_meta.get("layout"),
            face_conf=layout_meta.get("face_conf"),
            crop=layout_meta.get("crop"),
        )
        tmp_final = _render_final(seg_for_caps, fin_path, cand.title, whisper_clip_model, look=look)

        # Validate
        set_status("VALIDATING", clip=i)
        ok, msg = _validate_final(tmp_final, min_dur=min_clip_dur, max_dur=max_clip_dur)

        final_written = None
        if ok:
            try:
                tmp_final.replace(fin_path)
                final_written = str(fin_path)
            except Exception:
                # If atomic replace fails, fall back to copy then delete tmp
                fin_path.write_bytes(tmp_final.read_bytes())
                try:
                    tmp_final.unlink()
                except Exception:
                    pass
                final_written = str(fin_path)
        else:
            try:
                tmp_final.unlink()
            except Exception:
                pass

        clip_row = {
            "index": i,
            "start": actual_start,
            "end": cand.end,
            "duration": cand_dur,
            "score": cand.score,
            "title": cand.title,
            "segment": str(seg_path),
            "segment_for_captions": str(seg_for_caps),
            "layout": layout_meta,
            "final": final_written,
            "validated": ok,
            "validation": msg,
        }
        clips_out.append(clip_row)

        # Only advance the clip slot when we produced a VALID clip.
        if ok:
            out_index += 1

    # ---------------------------
    # FINAL RESULT
    # ---------------------------
    valid = [c for c in clips_out if c["validated"]]
    best = None
    if valid:
        best = sorted(valid, key=lambda x: x.get("score", 0), reverse=True)[0]

    # Generate a cover image for the best clip (used as thumbnail/cover for posting).
    cover_path = None
    if best and best.get("final"):
        try:
            from PIL import Image, ImageDraw, ImageFont  # type: ignore

            cover_dir = folder / "cover"
            cover_dir.mkdir(parents=True, exist_ok=True)
            cover_png = cover_dir / "best.png"

            # extract frame
            d = _ffprobe_duration(Path(best["final"])) or 0.0
            t = 0.9 if d >= 2.0 else max(0.1, d * 0.5)
            p = _run([
                "ffmpeg", "-y",
                "-ss", str(t),
                "-i", str(best["final"]),
                "-frames:v", "1",
                "-q:v", "2",
                str(cover_png),
            ], timeout=60, capture=True)

            if p.returncode == 0 and cover_png.exists() and cover_png.stat().st_size > 10_000:
                img = Image.open(cover_png).convert("RGBA")
                W, H = img.size
                overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                od = ImageDraw.Draw(overlay)

                # dark gradient at bottom for legibility
                for y in range(int(H * 0.35)):
                    yy = H - 1 - y
                    a = int(190 * (y / max(1, int(H * 0.35))))
                    od.line((0, yy, W, yy), fill=(0, 0, 0, a))

                hook = str(best.get("title") or "").strip()[:64]
                if not hook:
                    hook = "Clip"

                # font
                font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
                try:
                    font = ImageFont.truetype(font_path, 86)
                except Exception:
                    font = ImageFont.load_default()

                # wrap to 2 lines
                words = hook.split()
                lines = []
                cur = ""
                for w in words:
                    nxt = (cur + " " + w).strip()
                    if od.textlength(nxt, font=font) < W - 140:
                        cur = nxt
                    else:
                        if cur:
                            lines.append(cur)
                        cur = w
                if cur:
                    lines.append(cur)
                lines = lines[:2]

                # Place text block safely above the bottom edge (avoid clipping descenders).
                stroke_w = 4
                margin_bottom = 90
                line_gap = 12
                max_block_h = int(H * 0.30)

                # Fit-to-area: reduce font size if needed.
                font_size = 86
                while True:
                    try:
                        font = ImageFont.truetype(font_path, font_size)
                    except Exception:
                        font = ImageFont.load_default()

                    # Re-wrap with this font size
                    words = hook.split()
                    lines = []
                    cur = ""
                    for w in words:
                        nxt = (cur + " " + w).strip()
                        if od.textlength(nxt, font=font) < W - 140:
                            cur = nxt
                        else:
                            if cur:
                                lines.append(cur)
                            cur = w
                    if cur:
                        lines.append(cur)
                    lines = lines[:2]

                    bboxes = [od.textbbox((0, 0), ln, font=font, stroke_width=stroke_w) for ln in lines]
                    heights = [(bb[3] - bb[1]) for bb in bboxes]
                    total_h = sum(heights) + (line_gap * max(0, len(lines) - 1))

                    if total_h <= max_block_h or font_size <= 46:
                        break
                    font_size -= 4

                y = int(max(40, H - margin_bottom - total_h))
                for ln, bb in zip(lines, bboxes):
                    tw = od.textlength(ln, font=font)
                    x = int((W - tw) / 2)
                    # shadow + stroke
                    od.text((x + 2, y + 4), ln, font=font, fill=(0, 0, 0, 160))
                    od.text((x, y), ln, font=font, fill=(255, 255, 255, 240), stroke_width=stroke_w, stroke_fill=(0, 0, 0, 180))
                    y += (bb[3] - bb[1]) + line_gap

                img = Image.alpha_composite(img, overlay).convert("RGB")
                img.save(cover_png, format="PNG")
                cover_path = str(cover_png)
                best["cover_image"] = cover_path
        except Exception:
            cover_path = None

    result = {
        "ok": bool(valid),
        "generated_at": _iso_now(),
        "url": url,
        "video_id": vid,
        "title": title,
        "portrait_mode": portrait_mode,
        "folder": str(folder),
        "final_dir": str(final_dir),
        "clips": clips_out,
        "best_clip": best,
        "best_cover": cover_path,
    }
    _atomic_write_json(result_path, result)

    set_status(
        "DONE" if valid else "FAILED_VALIDATION",
        valid_clips=len(valid),
        best_clip=(best or {}).get("final"),
        best_cover=cover_path,
    )

    return result


def spawn_background(args: argparse.Namespace, outdir: Path) -> int:
    # Derive a job folder name early (so caller can monitor status)
    title, vid = _download_title_and_id(args.url)
    folder = outdir / f"{_safe_name(title)}_{vid}"
    folder.mkdir(parents=True, exist_ok=True)
    log_path = folder / "run.log"

    child_cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--url", args.url,
        "--outdir", str(outdir),
        "--num-clips", str(args.num_clips),
        "--clip-duration", str(args.clip_duration),
        "--skip-intro", str(args.skip_intro),
        "--whisper-full-model", args.whisper_full_model,
        "--whisper-clip-model", args.whisper_clip_model,
        "--pre-roll", str(args.pre_roll),
        "--selector", args.selector,
        "--selector-agent", args.selector_agent,
        "--selector-max-candidates", str(args.selector_max_candidates),
        "--min-clip-dur", str(args.min_clip_dur),
        "--max-clip-dur", str(args.max_clip_dur),
        "--look", args.look,
        "--portrait-mode", args.portrait_mode,
        "--no-background",
    ]

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n=== prism_run background started {datetime.now().isoformat(timespec='seconds')} ===\n")
        log.write("CMD: " + " ".join(shlex.quote(x) for x in child_cmd) + "\n")
        log.flush()

        subprocess.Popen(
            child_cmd,
            stdout=log,
            stderr=log,
            start_new_session=True,
        )

    print(json.dumps({"spawned": True, "folder": str(folder), "log": str(log_path)}))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Prism deterministic end-to-end clip runner")
    p.add_argument("--url", required=True, help="YouTube video URL")
    p.add_argument("--outdir", default=str(DEFAULT_OUTDIR), help="Base output directory for clips/")
    p.add_argument("--num-clips", type=int, default=6, help="How many clips to produce")
    p.add_argument("--clip-duration", type=float, default=35.0, help="Heuristic window duration (seconds). Selector refines inside min/max clip dur.")
    p.add_argument("--skip-intro", type=float, default=180.0, help="Skip intro seconds for candidates (default: 180s)")
    p.add_argument("--whisper-full-model", default="base", help="Whisper model for full transcript")
    p.add_argument("--whisper-clip-model", default="tiny", help="Whisper model for per-clip captions")
    p.add_argument("--pre-roll", type=float, default=2.5, help="Seconds to start before candidate moment (default: 2.5)")

    p.add_argument("--look", choices=["auto", "clean", "dark", "punchy", "none"], default="auto", help="Post color grade look (default: auto)")
    p.add_argument(
        "--portrait-mode",
        choices=["letterbox", "blurfill", "smartzoom"],
        default="letterbox",
        help="Portrait framing mode (default: letterbox). blurfill is deprecated/disabled.",
    )

    p.add_argument("--selector", choices=["llm", "heuristic"], default="llm", help="Clip selection strategy")
    p.add_argument("--selector-agent", default="prism", help="OpenClaw agent id to use for LLM selection (default: prism)")
    p.add_argument("--selector-max-candidates", type=int, default=24, help="Max heuristic windows to send to the selector agent")
    p.add_argument("--min-clip-dur", type=float, default=15.0, help="Minimum final clip duration (seconds)")
    p.add_argument("--max-clip-dur", type=float, default=35.0, help="Maximum final clip duration (seconds)")


    bg = p.add_mutually_exclusive_group()
    bg.add_argument("--background", action="store_true", help="Run in background (recommended for long videos)")
    bg.add_argument("--no-background", action="store_true", help="Run in foreground")

    args = p.parse_args()
    outdir = Path(args.outdir).expanduser()

    # Default to background if not specified
    want_bg = args.background or (not args.no_background)
    if want_bg:
        return spawn_background(args, outdir)

    try:
        result = run_pipeline(
            args.url,
            outdir,
            num_clips=args.num_clips,
            clip_duration=args.clip_duration,
            skip_intro=args.skip_intro,
            whisper_full_model=args.whisper_full_model,
            whisper_clip_model=args.whisper_clip_model,
            pre_roll=args.pre_roll,
            selector=args.selector,
            selector_agent=args.selector_agent,
            selector_max_candidates=args.selector_max_candidates,
            min_clip_dur=args.min_clip_dur,
            max_clip_dur=args.max_clip_dur,
            look=args.look,
            portrait_mode=args.portrait_mode,
            resume=True,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("ok") else 2
    except Exception as e:
        # Best-effort: write a minimal failure status if we can infer folder
        try:
            title, vid = _download_title_and_id(args.url)
            folder = outdir / f"{_safe_name(title)}_{vid}"
            _atomic_write_json(folder / "status.json", {
                "updated_at": _iso_now(),
                "stage": "FAILED_EXCEPTION",
                "url": args.url,
                "error": str(e),
                "folder": str(folder),
            })
        except Exception:
            pass
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
