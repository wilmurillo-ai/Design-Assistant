#!/usr/bin/env python3
"""
Viral Video Caption Generator
Takes any video + subtitles → outputs a 9:16 vertical viral clip with title hook + styled captions.

Usage:
    python add_captions.py <video.mp4> <subtitles> <output.mp4> [title]

    subtitles can be:
      - .srt file (YouTube/manual subtitles — uses SRT parser with dedup)
      - .json file (Whisper JSON output — uses exact per-word timestamps, recommended)
      - If omitted or "auto", runs Whisper on the video to generate word-level timestamps

    Options:
      --whisper       Force run Whisper on video instead of using a subtitle file
      --model MODEL   Whisper model to use (default: base). Options: tiny, base, small, medium, large

    - Letterbox layout: full video centered on black 1080x1920 canvas
    - Title hook in the top black bar
    - Captions overlaid on the video itself (one line at a time, word-by-word highlight)
    - If [title] is omitted, uses first subtitle line (or set CONFIG["clip_title"])

Edit CONFIG below to customize style, position, and fonts.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip,
    VideoClip,
    TextClip,
    ImageClip,
    CompositeVideoClip,
    ColorClip,
)


# Regex to match emojis (for clean titles in videos)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+", flags=re.UNICODE
)


def strip_emoji(text):
    """Remove emojis from text - TikTok/YouTube don't render them well in video titles"""
    return EMOJI_PATTERN.sub('', text).strip()


# ============================================================
# CONFIG — Edit these to change style
# ============================================================

CONFIG = {
    # Output dimensions (9:16 portrait for TikTok/Reels/Shorts)
    "video_width": 1080,
    "video_height": 1920,
    # Clip title text (shown at top for full video). None = use first subtitle line.
    "clip_title": None,
    # Title / Hook — rendered in the top black bar
    "title": {
        "font": "/System/Library/Fonts/Supplemental/Impact.ttf",
        "font_size": 48,  # title hook — readable but not overwhelming
        "color": "white",
        "uppercase": False,  # Keep original casing
        "max_chars": 120,
        "chars_per_line": 26,
        "margin_top": 30,  # Min margin from top edge
        "margin_bottom": 10,  # Min margin from bottom of top bar
        # Placement tweak: keep the hook closer to the content (near the top edge of the center video).
        # - If we have a natural top black bar (letterboxed landscape), we anchor near the bottom of that bar.
        # - If not (portrait / no bar), we drop the title strip slightly into the frame.
        "vertical_align": "bottom",  # top|center|bottom
        "near_video_padding": 12,  # extra px above the video (when vertical_align=bottom)
        # Title placement within the TOP padding area (above the sharp center window)
        # 0.0 = very top of the padding area, 1.0 = very bottom of the padding area
        "top_bar_y_ratio": 0.50,

        # New default: title lives OUTSIDE the center video (in top padding area)
        "prefer_on_video": False,

        # Ratio-based positioning (relative to detected main content window) when prefer_on_video=true
        "hook_offset_ratio": 0.08,
        "hook_offset_min_px": 45,
        "hook_offset_max_px": 180,
        # Legacy px fallback (used if ratios are unavailable)
        "on_video_offset": 70,
        "strip_alpha": 110,  # lower alpha = less "shiny" / less blocky
        "render_with_pil": True,
        "bg_style": "pill",  # none|pill|full
        "pill_radius": 28,
        "pill_padding_x": 70,
        "pill_padding_y": 18,
        "strip_y": 420,  # px from top when rendering the overlay strip (portrait/no-bar)
    },
    # Captions — overlaid INSIDE the video area
    # Short keyword bursts (1-3 words) with effects, centered slightly above lower third
    "captions": {
        "font": "/System/Library/Fonts/Supplemental/Impact.ttf",
        "font_size": 60,  # big for impact
        "color": "white",
        "highlight_color": "#FFD700",  # Gold/yellow for the active word
        "stroke_color": "black",
        "stroke_width": 4,  # Thick stroke for readability over video
        "max_width": 860,
        "chars_per_line": 28,
        # Placement: CENTERED vertically, slightly above lower third
        "anchor": "bottom",  # bottom|center|ratio — use bottom for reliability
        "y_ratio": 0.62,  # used when anchor=ratio
        # Ratio-based bottom padding (relative to detected main content window)
        "bottom_padding_ratio": 0.06,
        "bottom_padding_min_px": 40,
        "bottom_padding_max_px": 160,
        # Legacy px fallback
        "bottom_padding": 70,
        "margin_from_video_bottom": 260,  # legacy fallback
        # Keyword burst mode: show only 1-3 key words instead of full sentence
        "word_by_word": False,  # disabled
        "burst_mode": False,  # disabled — use line-by-line karaoke
        "max_burst_words": 3,   # max words per burst
    },
}

# ============================================================
# FONTS — Fallback chain
# ============================================================


def resolve_font(preferred_path):
    """Return the font path if it exists, otherwise fall back."""
    import os

    fallbacks = [
        preferred_path,
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for f in fallbacks:
        if f and os.path.exists(f):
            return f
    return None


# ============================================================
# SRT PARSER — with deduplication
# ============================================================


def parse_srt(srt_file):
    """Parse SRT file → list of {start, end, text}. Deduplicates overlapping repeated text."""
    with open(srt_file, "r") as f:
        content = f.read()

    subs = []
    blocks = content.strip().split("\n\n")

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        try:
            timecode = lines[1]
            text = " ".join(lines[2:])

            match = re.match(
                r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(-?\d{1,2}):(\d{2}):(\d{2}),(\d{3})",
                timecode.strip(),
            )
            if not match:
                continue

            start = (
                int(match.group(1)) * 3600
                + int(match.group(2)) * 60
                + int(match.group(3))
                + int(match.group(4)) / 1000
            )
            end = (
                int(match.group(5)) * 3600
                + int(match.group(6)) * 60
                + int(match.group(7))
                + int(match.group(8)) / 1000
            )

            # Fix invalid end times
            if end <= start or end < 0:
                end = start + 2.5

            # Strip HTML tags
            text = re.sub(r"<[^>]+>", "", text).strip()
            if text and start >= 0:
                subs.append({"start": start, "end": end, "text": text})
        except Exception:
            pass

    # Deduplicate overlapping repeated text
    if not subs:
        return subs

    deduped = [subs[0]]
    for sub in subs[1:]:
        prev = deduped[-1]
        if _text_overlap(prev["text"], sub["text"]) > 0.6:
            prev["end"] = max(prev["end"], sub["end"])
            if len(sub["text"]) > len(prev["text"]):
                prev["text"] = sub["text"]
        else:
            deduped.append(sub)

    return deduped


def _text_overlap(a, b):
    """Return fraction of words in common between two strings."""
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    return len(intersection) / min(len(words_a), len(words_b))


# ============================================================
# WHISPER JSON PARSER — exact per-word timestamps
# ============================================================


def parse_whisper_json(json_path):
    """
    Parse Whisper JSON output (with word_timestamps=True) into a flat list of words.
    Returns list of {"word": str, "start": float, "end": float}.
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    words = []
    for segment in data.get("segments", []):
        for w in segment.get("words", []):
            word_text = w["word"].strip()
            if not word_text:
                continue
            words.append({"word": word_text, "start": w["start"], "end": w["end"]})
    return words


def run_whisper(video_path, model="base", language="en"):
    """
    Run OpenAI Whisper on a video file and return the path to the JSON output.
    Whisper must be installed at /opt/homebrew/bin/whisper or on PATH.
    """
    whisper_bin = "/opt/homebrew/bin/whisper"
    if not os.path.exists(whisper_bin):
        # Try PATH
        whisper_bin = "whisper"

    output_dir = tempfile.mkdtemp(prefix="whisper_")
    basename = os.path.splitext(os.path.basename(video_path))[0]

    cmd = [
        whisper_bin,
        video_path,
        "--model",
        model,
        "--language",
        language,
        "--word_timestamps",
        "True",
        "--output_format",
        "json",
        "--output_dir",
        output_dir,
    ]

    print(f"  Running Whisper ({model} model)...")
    print(f"  Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Whisper stderr: {result.stderr}")
        raise RuntimeError(f"Whisper failed with exit code {result.returncode}")

    json_path = os.path.join(output_dir, f"{basename}.json")
    if not os.path.exists(json_path):
        # Whisper sometimes uses different naming
        json_files = [f for f in os.listdir(output_dir) if f.endswith(".json")]
        if json_files:
            json_path = os.path.join(output_dir, json_files[0])
        else:
            raise FileNotFoundError(f"No JSON output found in {output_dir}")

    print(f"  Whisper output: {json_path}")
    return json_path


# ============================================================
# LETTERBOX — Full video centered, black bars top/bottom
# ============================================================


def letterbox_to_portrait(clip, config):
    """
    Place the full video centered on a 1080x1920 black canvas.
    Returns (composite_clip, video_y, video_h) so overlays know the geometry.
    """
    target_w = config["video_width"]
    target_h = config["video_height"]

    src_w, src_h = clip.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h

    if src_ratio <= target_ratio + 0.05:
        # Already portrait-ish — just resize to fill
        resized = clip.resized((target_w, target_h))
        return resized, 0, target_h

    # Landscape: fit full width, calculate scaled height
    scaled_w = target_w
    scaled_h = int(target_w / src_ratio)

    # Center vertically
    video_y = (target_h - scaled_h) // 2

    # Black background
    bg = ColorClip(size=(target_w, target_h), color=(0, 0, 0))
    bg = bg.with_duration(clip.duration)

    # Resize and center
    resized = clip.resized((scaled_w, scaled_h))
    resized = resized.with_position((0, video_y))

    composite = CompositeVideoClip([bg, resized], size=(target_w, target_h))
    composite = composite.with_duration(clip.duration)
    composite.audio = clip.audio

    return composite, video_y, scaled_h


# ============================================================
# TITLE HOOK — In the top black bar, auto-fits
# ============================================================


def create_title_clip(text, config, duration, bar_top_h, video_y=None, video_h=None):
    """
    Create title text at the top of the video.
    If there's a natural black bar (letterboxed), render into it.
    If not (portrait/pre-letterboxed), create a semi-transparent dark background strip.
    """
    title_cfg = config["title"]
    w = config["video_width"]
    font = resolve_font(title_cfg.get("font"))

    # Process text
    text = text[: title_cfg["max_chars"]].strip()
    if title_cfg.get("uppercase", False):
        text = text.upper()
    wrapped = textwrap.fill(text, width=title_cfg["chars_per_line"])

    max_text_w = w - 120  # horizontal padding
    margin_top = title_cfg.get("margin_top", 30)
    margin_bottom = title_cfg.get("margin_bottom", 20)

    # If no natural black bar, use a fixed height for the title strip
    has_natural_bar = bar_top_h > 50

    # Prefer putting the hook closer to the subject by overlaying *inside the video*
    # (users focus on the center, not the extreme top bar).
    prefer_on_video = bool(title_cfg.get("prefer_on_video", False))
    if has_natural_bar and prefer_on_video:
        # Force overlay mode (same rendering path as portrait/no-bar), but position relative to the video top.
        has_natural_bar = False

    if has_natural_bar:
        available_h = bar_top_h - margin_top - margin_bottom
    else:
        available_h = 160  # Fixed height for the overlay title strip

    font_size = title_cfg["font_size"]
    best_size = font_size
    # Extra padding prevents descenders (g/j/y) from being clipped by TextClip bbox.
    padding_factor = 1.58

    for attempt_size in range(font_size, 20, -4):
        kwargs = dict(
            text=wrapped,
            font_size=attempt_size,
            color=title_cfg["color"],
            size=(max_text_w, None),
            method="caption",
            text_align="center",
        )
        if font:
            kwargs["font"] = font
        probe = TextClip(**kwargs)
        estimated_h = int(probe.size[1] * padding_factor) + 20

        if estimated_h <= available_h:
            best_size = attempt_size
            break
        best_size = attempt_size

    # Render hook entirely in PIL (background + text) for perfect centering.
    # IMPORTANT: For this PIL path, we must size+wrap using PIL metrics (not MoviePy TextClip),
    # otherwise hooks can overflow or look mis-centered on some fonts.
    if bool(title_cfg.get("render_with_pil", True)):
        layers = []

        bg_style = (title_cfg.get("bg_style") or "pill").lower()
        alpha = int(title_cfg.get("strip_alpha", 160) or 160)
        alpha = max(0, min(255, alpha))

        pill_radius = int(title_cfg.get("pill_radius", 28) or 28)
        pad_x = int(title_cfg.get("pill_padding_x", 70) or 70)
        pad_y = int(title_cfg.get("pill_padding_y", 18) or 18)
        stroke_w = int(title_cfg.get("stroke_width", 4) or 4)

        dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

        def _load_font(size: int):
            try:
                return ImageFont.truetype(font, size) if font else ImageFont.load_default()
            except Exception:
                return ImageFont.load_default()

        def _wrap_for_width(t: str, font_obj: ImageFont.FreeTypeFont, max_line_w: int, max_lines: int = 2):
            words = [w for w in re.split(r"\s+", (t or "").strip()) if w]
            if not words:
                return ""
            lines = []
            cur = ""
            for w in words:
                test = (cur + " " + w).strip() if cur else w
                bbox = dummy.textbbox((0, 0), test, font=font_obj)
                tw = int(bbox[2] - bbox[0])
                if tw <= max_line_w:
                    cur = test
                else:
                    if cur:
                        lines.append(cur)
                        cur = w
                    else:
                        # single long token; keep it and force overflow rather than dropping text
                        lines.append(w)
                        cur = ""
                if len(lines) > max_lines:
                    return None
            if cur:
                lines.append(cur)
            if len(lines) > max_lines:
                return None
            return "\n".join(lines)

        # Fit font size + wrapping using PIL metrics.
        # We aim for <=2 lines for readability; we shrink font to make it fit.
        max_lines = int(title_cfg.get("max_lines", 2) or 2)
        max_pill_w = w - 80
        # Effective line width inside the pill
        max_line_w = max(240, int(max_pill_w - (2 * pad_x))) if bg_style == "pill" else int(max_text_w)

        best_size_pil = int(title_cfg.get("font_size", best_size) or best_size)
        best_wrapped = None
        best_font = None

        for attempt_size in range(best_size_pil, 18, -2):
            fnt = _load_font(attempt_size)
            wr = _wrap_for_width(text, fnt, max_line_w=max_line_w, max_lines=max_lines)
            if wr is None:
                continue
            bb = dummy.multiline_textbbox((0, 0), wr, font=fnt, align="center")
            tw = max(1, int(bb[2] - bb[0]))
            th = max(1, int(bb[3] - bb[1]))
            # Height constraint: must fit into the available top region when using natural bars
            if th + (2 * pad_y) + 22 > available_h:
                continue
            best_wrapped = wr
            best_font = fnt
            best_size_pil = attempt_size
            break

        if best_wrapped is None:
            # fallback: use existing char-based wrap at the smallest size
            best_font = _load_font(20)
            best_wrapped = wrapped

        wrapped = best_wrapped
        pil_font = best_font

        bbox = dummy.multiline_textbbox((0, 0), wrapped, font=pil_font, align="center")
        text_w = max(1, int(bbox[2] - bbox[0]))
        text_h_pil = max(1, int(bbox[3] - bbox[1]))

        # Strip height just big enough to contain the pill + a little breathing room.
        strip_h = int(text_h_pil + (2 * pad_y) + 22)
        strip_h = max(strip_h, 90)

        # Decide Y placement
        prefer_on_video = bool(title_cfg.get("prefer_on_video", False))

        # Top padding region end (above the sharp center window)
        # - For natural letterbox: bar_top_h
        # - For blurfill framed content: video_y from content detection
        top_region_end = None
        if (video_y is not None) and (video_y > 50):
            top_region_end = int(video_y)
        elif has_natural_bar and (bar_top_h > 50):
            top_region_end = int(bar_top_h)

        if (not prefer_on_video) and top_region_end and top_region_end > 50:
            # Put title OUTSIDE the sharp center video, inside the top padding area.
            # Position it by ratio within the available top region.
            try:
                r = float(title_cfg.get("top_bar_y_ratio", 0.30) or 0.30)
            except Exception:
                r = 0.30
            r = max(0.0, min(1.0, r))

            avail_top = int(margin_top)
            avail_bottom = int(top_region_end - margin_bottom)

            # The strip is placed within [avail_top .. avail_bottom-strip_h]
            max_y = max(avail_top, avail_bottom - strip_h)
            strip_y = int(avail_top + (max_y - avail_top) * r)
            strip_y = max(avail_top, min(max_y, strip_y))
        else:
            # Overlay inside the content window
            if prefer_on_video and (video_y is not None) and (video_h is not None):
                ratio = float(title_cfg.get("hook_offset_ratio", 0.12) or 0.12)
                off = int(video_h * ratio)
                off_min = int(title_cfg.get("hook_offset_min_px", 40) or 40)
                off_max = int(title_cfg.get("hook_offset_max_px", 160) or 160)
                off = max(off_min, min(off_max, off))
                strip_y = int(video_y + off)
            else:
                strip_y = int(title_cfg.get("strip_y", 0) or 0)
            strip_y = max(0, min(config["video_height"] - strip_h, strip_y))

        strip_img = Image.new("RGBA", (w, strip_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(strip_img)

        if bg_style == "full":
            draw.rectangle([0, 0, w, strip_h], fill=(0, 0, 0, alpha))
        elif bg_style == "pill":
            pill_w = min(w - 80, int(text_w + (2 * pad_x)))
            pill_h = min(strip_h - 10, int(text_h_pil + (2 * pad_y)))
            x0 = int((w - pill_w) / 2)
            y0 = int((strip_h - pill_h) / 2)
            x1 = x0 + pill_w
            y1 = y0 + pill_h
            draw.rounded_rectangle([x0, y0, x1, y1], radius=pill_radius, fill=(0, 0, 0, alpha))

        draw.multiline_text(
            (w / 2, strip_h / 2),
            wrapped,
            font=pil_font,
            fill=(255, 255, 255, 255),
            anchor="mm",
            align="center",
            stroke_width=stroke_w,
            stroke_fill=(0, 0, 0, 255),
        )

        strip_array = np.array(strip_img)
        hook_clip = ImageClip(strip_array).with_duration(duration).with_position((0, strip_y))
        layers.append(hook_clip)
        return layers

    final_kwargs = dict(
        text=wrapped,
        font_size=best_size,
        color=title_cfg["color"],
        size=(max_text_w, None),
        method="caption",
        text_align="center",
    )
    if font:
        final_kwargs["font"] = font
    probe = TextClip(**final_kwargs)
    explicit_h = int(probe.size[1] * padding_factor) + 20

    final_kwargs["size"] = (max_text_w, explicit_h)
    final_kwargs["vertical_align"] = "center"
    text_clip = TextClip(**final_kwargs)

    text_h = text_clip.size[1]

    layers = []

    if not has_natural_bar:
        # Create a semi-transparent dark background strip at the top.
        # For portrait sources (no natural bar), drop the strip *down* a bit so the hook sits
        # closer to the subject (people focus near center, not the extreme top).
        strip_h = text_h + margin_top + margin_bottom + 20

        # If we have a natural top bar but chose prefer_on_video, bar_top_h is the y of the center video.
        # Place the strip inside the video, a bit below that top edge.
        if bool(title_cfg.get("prefer_on_video", False)) and bar_top_h > 50:
            strip_y = int(bar_top_h + int(title_cfg.get("on_video_offset", 60) or 60))
        else:
            strip_y = int(title_cfg.get("strip_y", 0) or 0)

        strip_y = max(0, min(config["video_height"] - strip_h, strip_y))

        # Background behind the hook (avoid a full-width "shiny" banner by default)
        bg_style = (title_cfg.get("bg_style") or "pill").lower()

        alpha = int(title_cfg.get("strip_alpha", 160) or 160)
        alpha = max(0, min(255, alpha))

        if bg_style != "none":
            if bg_style == "full":
                strip_img = Image.new("RGBA", (w, strip_h), (0, 0, 0, alpha))
                # Add a subtle gradient fade at the bottom edge for a cleaner look
                for row in range(min(30, strip_h)):
                    y_row = strip_h - 1 - row
                    fade_alpha = int(alpha * (row / 30))
                    for x in range(w):
                        strip_img.putpixel((x, y_row), (0, 0, 0, fade_alpha))
            else:
                # pill (default): rounded rectangle behind the text only
                strip_img = Image.new("RGBA", (w, strip_h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(strip_img)

                pill_radius = int(title_cfg.get("pill_radius", 28) or 28)
                pad_x = int(title_cfg.get("pill_padding_x", 70) or 70)
                pad_y = int(title_cfg.get("pill_padding_y", 18) or 18)

                # Measure wrapped lines using PIL font for a reasonable pill width.
                try:
                    pil_font = ImageFont.truetype(font, best_size) if font else ImageFont.load_default()
                except Exception:
                    pil_font = ImageFont.load_default()

                dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
                lines_txt = [ln for ln in wrapped.split("\n") if ln.strip()]
                max_line_w = 0
                for ln in lines_txt[:4]:
                    bbox = dummy.textbbox((0, 0), ln, font=pil_font)
                    max_line_w = max(max_line_w, bbox[2] - bbox[0])

                pill_w = min(w - 80, max_line_w + (2 * pad_x))
                pill_h = min(strip_h - 10, text_h + (2 * pad_y))
                x0 = int((w - pill_w) / 2)
                y0 = int((strip_h - pill_h) / 2)
                x1 = x0 + pill_w
                y1 = y0 + pill_h
                draw.rounded_rectangle([x0, y0, x1, y1], radius=pill_radius, fill=(0, 0, 0, alpha))

            strip_array = np.array(strip_img)
            bg_clip = ImageClip(strip_array).with_duration(duration).with_position((0, strip_y))
            layers.append(bg_clip)

        # IMPORTANT: center the text vertically inside the strip/pill (not just a fixed margin)
        # so it doesn't look "off-center" in the container.
        y = strip_y + max(0, int((strip_h - text_h) / 2))
    else:
        # Natural top bar (letterboxed landscape): bias the title toward the bottom of the bar
        # so it visually "hugs" the center video.
        valign = (title_cfg.get("vertical_align") or "center").lower()
        near_video_padding = int(title_cfg.get("near_video_padding", 0) or 0)

        if valign == "top":
            y = margin_top
        elif valign == "bottom":
            y = bar_top_h - margin_bottom - text_h - near_video_padding
            y = max(margin_top, y)
        else:
            y = margin_top + max(0, (available_h - text_h) // 2)

    text_clip = text_clip.with_position(("center", y))
    text_clip = text_clip.with_duration(duration)
    layers.append(text_clip)

    return layers


# ============================================================
# CAPTIONS — PIL-rendered, one line at a time, animated highlight
# ============================================================


def _parse_color(color_str):
    """Convert color string to RGBA tuple."""
    if isinstance(color_str, tuple):
        return color_str if len(color_str) == 4 else (*color_str, 255)
    if color_str.startswith("#"):
        h = color_str.lstrip("#")
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)) + (255,)
    color_map = {
        "white": (255, 255, 255, 255),
        "black": (0, 0, 0, 255),
        "yellow": (255, 255, 0, 255),
        "red": (255, 0, 0, 255),
    }
    return color_map.get(color_str.lower(), (255, 255, 255, 255))


def _wrap_words_to_lines(words, font, max_width):
    """Wrap a list of words into lines that fit within max_width.
    Returns list of lists: [[word_indices_line1], [word_indices_line2], ...]"""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = []
    current_line = []
    current_text = ""

    for i, word in enumerate(words):
        test_text = (current_text + " " + word).strip()
        bbox = dummy.textbbox((0, 0), test_text, font=font)
        w = bbox[2] - bbox[0]

        if w > max_width and current_line:
            lines.append(current_line)
            current_line = [i]
            current_text = word
        else:
            current_line.append(i)
            current_text = test_text

    if current_line:
        lines.append(current_line)

    return lines


def _render_single_line(
    words,
    highlight_idx,
    font,
    font_size,
    max_width,
    color,
    hl_color,
    stroke_color,
    stroke_width,
):
    """
    Render a single line of words as a PIL RGBA image.
    One word (at highlight_idx) is drawn in hl_color, the rest in color.
    Returns an RGBA numpy array.
    """
    dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    color_rgba = _parse_color(color)
    hl_rgba = _parse_color(hl_color)
    stroke_rgba = _parse_color(stroke_color)

    line_height = int(font_size * 1.4)
    img_w = max_width + stroke_width * 2
    img_h = line_height + stroke_width * 2

    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Measure full line width for centering
    line_text = " ".join(words)
    line_bbox = dummy_draw.textbbox((0, 0), line_text, font=font)
    line_w = line_bbox[2] - line_bbox[0]
    x_start = (img_w - line_w) // 2
    y = stroke_width

    # Draw word by word
    x = x_start
    for i, word in enumerate(words):
        word_color = hl_rgba if i == highlight_idx else color_rgba

        draw.text(
            (x, y),
            word,
            font=font,
            fill=word_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_rgba,
        )

        word_bbox = dummy_draw.textbbox((0, 0), word + " ", font=font)
        x += word_bbox[2] - word_bbox[0]

    return np.array(img)


def _render_keyword_frame(words, pil_font, font_size, max_width, color, hl_color,
                           stroke_color, stroke_width):
    """
    Render a single keyword burst frame (1-3 words, large, centered).
    Returns a numpy array (H x W x 4) in RGBA.
    """
    text = " ".join(words)
    # Remove emojis
    text = strip_emoji(text)
    if not text:
        text = " ".join(words)

    img_w = max_width + 40

    # Use a slightly larger font for the burst
    burst_font_size = int(font_size * 1.2)
    try:
        burst_font = ImageFont.truetype(
            "/System/Library/Fonts/Supplemental/Impact.ttf",
            burst_font_size
        )
    except Exception:
        burst_font = pil_font

    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

    # Measure text
    bbox = dummy.textbbox((0, 0), text, font=burst_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    pad_x = 30
    pad_y = 16
    img_h = text_h + pad_y * 2

    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x = (img_w - text_w) // 2 - bbox[0]
    y = pad_y - bbox[1]

    # Thick black stroke for readability
    for sw in [5, 3, 1]:
        for dx, dy in [(sw, 0), (-sw, 0), (0, sw), (0, -sw),
                       (sw, sw), (-sw, -sw), (sw, -sw), (-sw, sw)]:
            draw.text((x + dx, y + dy), text, font=burst_font, fill=(0, 0, 0, 255))

    # White text on top
    draw.text((x, y), text, font=burst_font, fill=(255, 255, 255, 255))

    return np.array(img)


def create_keyword_burst_clips(word_list, config, video_y, video_h):
    """
    KEYWORD BURST MODE — 1-3 word flashes with pop effects.
    Instead of full karaoke sentences, extract 1-3 key words per segment
    and show them briefly with a pop-in/pop animation.
    """
    cap_cfg = config["captions"]
    font_path = resolve_font(cap_cfg.get("font"))
    font_size = cap_cfg["font_size"]
    max_width = cap_cfg["max_width"]
    max_burst_words = cap_cfg.get("max_burst_words", 3)
    color = cap_cfg["color"]
    hl_color = cap_cfg["highlight_color"]
    stroke_color = cap_cfg["stroke_color"]
    stroke_width = cap_cfg["stroke_width"]

    pil_font = (
        ImageFont.truetype(font_path, font_size)
        if font_path
        else ImageFont.load_default()
    )

    if not word_list:
        return []

    # Group words into segments (by Whisper segment boundaries or by time gaps)
    # Each burst shows 1-3 words from the start of each major pause chunk
    segments = []
    current_segment_words = []
    current_segment_start = None

    # Use a gap threshold: if > 0.5s between words, start new segment
    GAP_THRESHOLD = 0.5

    for w in word_list:
        if current_segment_start is None:
            current_segment_start = w["start"]

        if current_segment_words and (w["start"] - current_segment_words[-1]["end"]) > GAP_THRESHOLD:
            # End current segment
            segments.append(current_segment_words)
            current_segment_words = [w]
            current_segment_start = w["start"]
        else:
            current_segment_words.append(w)

    if current_segment_words:
        segments.append(current_segment_words)

    clips = []

    for seg_words in segments:
        # Extract 1-3 words for the burst (prefer first words as they carry the hook)
        burst_words = [w["word"] for w in seg_words[:max_burst_words]]
        if not burst_words:
            continue

        # Clean emojis
        burst_words = [strip_emoji(w) for w in burst_words]
        burst_words = [w for w in burst_words if w]

        if len(burst_words) > max_burst_words:
            burst_words = burst_words[:max_burst_words]

        if not burst_words:
            continue

        seg_start = seg_words[0]["start"]
        seg_end = seg_words[-1]["end"]

        # Short display: use a fraction of the segment duration, capped
        display_duration = min(seg_end - seg_start, 1.5)  # max 1.5s
        display_duration = max(display_duration, 0.4)   # min 0.4s

        try:
            frame = _render_keyword_frame(
                burst_words, pil_font, font_size, max_width,
                color, hl_color, stroke_color, stroke_width
            )
            h, w = frame.shape[:2]

            # Static frame clip with fade in/out via crossfade
            img_clip = (ImageClip(frame)
                        .with_duration(display_duration)
                        .with_start(seg_start))

            # Position based on anchor setting
            anchor = str(cap_cfg.get("anchor", "bottom") or "bottom").lower()
            if anchor == "center":
                y_ratio = float(cap_cfg.get("y_ratio", 0.62) or 0.62)
                content_center_y = video_y + (video_h * y_ratio)
                y = int(content_center_y - (h / 2))
            else:
                # bottom anchor: position in lower third of video
                bottom_ratio = float(cap_cfg.get("bottom_padding_ratio", 0.08) or 0.08)
                y = int(video_y + video_h - (video_h * bottom_ratio) - h)

            y = max(video_y + 10, min(video_y + video_h - h - 10, y))

            img_clip = img_clip.with_position(("center", y))

            # Apply fade in/out using MoviePy 2.x effects API
            from moviepy.video.fx import FadeIn, FadeOut
            img_clip = img_clip.with_effects([FadeIn(0.08), FadeOut(0.15)])

            clips.append(img_clip)

        except Exception as e:
            print(f"  Warning: skipped keyword burst: {e}")

    return clips


def create_word_by_word_clips(word_list, config, video_y, video_h):
    """
    PURE word-by-word display — one word at a time, centered on screen.
    Each word gets its own clip showing only that word.
    """
    cap_cfg = config["captions"]
    font_path = resolve_font(cap_cfg.get("font"))
    font_size = cap_cfg["font_size"]
    max_width = cap_cfg["max_width"]
    color = cap_cfg["color"]
    hl_color = cap_cfg["highlight_color"]
    stroke_color = cap_cfg["stroke_color"]
    stroke_width = cap_cfg["stroke_width"]

    pil_font = (
        ImageFont.truetype(font_path, font_size)
        if font_path
        else ImageFont.load_default()
    )

    if not word_list:
        return []

    clips = []

    # Single-word display: one word centered per clip
    for w in word_list:
        word_text = strip_emoji(w["word"])
        if not word_text:
            word_text = w["word"]
        word_start = w["start"]
        word_end = w["end"]
        word_dur = word_end - word_start

        if word_dur <= 0.05:
            continue

        try:
            # Render the single word (centered, large)
            frame = _render_single_line(
                [word_text],  # single word
                0,            # highlight index 0
                pil_font,
                font_size,
                max_width,
                color,
                hl_color,
                stroke_color,
                stroke_width,
            )
            h, w_frame = frame.shape[:2]

            img_clip = (ImageClip(frame)
                        .with_duration(word_dur)
                        .with_start(word_start))

            # Position: centered, lower third of video
            anchor = str(cap_cfg.get("anchor", "bottom") or "bottom").lower()
            if anchor == "center":
                y_ratio = float(cap_cfg.get("y_ratio", 0.62) or 0.62)
                content_center_y = video_y + (video_h * y_ratio)
                y = int(content_center_y - (h / 2))
            else:
                ratio = float(cap_cfg.get("bottom_padding_ratio", 0.06) or 0.06)
                pad = int(video_h * ratio)
                pad_min = int(cap_cfg.get("bottom_padding_min_px", 40) or 40)
                pad_max = int(cap_cfg.get("bottom_padding_max_px", 160) or 160)
                pad = max(pad_min, min(pad_max, pad))
                video_bottom = video_y + video_h
                y = video_bottom - h - pad

            y = max(video_y + 10, min(video_y + video_h - h - 10, y))
            img_clip = img_clip.with_position(("center", y))

            clips.append(img_clip)

        except Exception as e:
            print(f"  Warning: skipped word clip: {e}")

    return clips


def create_caption_clips(subs, config, video_y, video_h):
    """
    One line at a time, one word highlighted at a time. Zero overlap guaranteed.

    Step 1: Flatten all subtitle blocks into a global list of lines with estimated starts.
    Step 2: Sort by start time, deduplicate near-identical lines.
    Step 3: Force sequential: each line starts exactly when the previous one ends.
    Step 4: Each line is a VideoClip with make_frame animating the word highlight.
            Duration per word = line_duration / word_count.
    """
    cap_cfg = config["captions"]
    font_path = resolve_font(cap_cfg.get("font"))
    font_size = cap_cfg["font_size"]
    max_width = cap_cfg["max_width"]
    color = cap_cfg["color"]
    hl_color = cap_cfg["highlight_color"]
    stroke_color = cap_cfg["stroke_color"]
    stroke_width = cap_cfg["stroke_width"]
    margin_from_bottom = cap_cfg.get("margin_from_video_bottom", 100)

    pil_font = (
        ImageFont.truetype(font_path, font_size)
        if font_path
        else ImageFont.load_default()
    )

    # --- Step 1: Flatten all subs into a global line list ---
    raw_lines = []

    for sub in subs:
        block_duration = sub["end"] - sub["start"]
        if block_duration <= 0:
            continue

        words = sub["text"].split()
        if not words:
            continue

        lines = _wrap_words_to_lines(words, pil_font, max_width)
        total_words = len(words)
        time_cursor = sub["start"]

        for line_indices in lines:
            line_words = [words[i] for i in line_indices]
            n_words = len(line_words)
            estimated_duration = block_duration * (n_words / total_words)

            raw_lines.append(
                {
                    "words": line_words,
                    "text": " ".join(line_words),
                    "start": time_cursor,
                    "estimated_duration": estimated_duration,
                }
            )

            time_cursor += estimated_duration

    if not raw_lines:
        return []

    # --- Step 2: Sort by start time ---
    raw_lines.sort(key=lambda x: x["start"])

    # --- Step 3: Aggressive dedup ---
    # The SRT has heavily overlapping blocks producing the same text multiple times.
    # Check each new line against ALL recent lines (not just the previous one).
    # Skip if the text was already shown recently.
    deduped = [raw_lines[0]]
    seen_texts = {raw_lines[0]["text"].lower()}  # exact text we've already included

    for line in raw_lines[1:]:
        cur_text = line["text"].lower()
        cur_words = set(cur_text.split())

        # Skip exact duplicates
        if cur_text in seen_texts:
            continue

        # Skip if very similar to ANY of the last 5 lines
        is_dup = False
        for prev in deduped[-5:]:
            prev_words = set(prev["text"].lower().split())
            if not prev_words or not cur_words:
                continue
            shared = len(prev_words & cur_words)
            overlap = shared / min(len(prev_words), len(cur_words))
            # High overlap = duplicate (one is a subset/near-subset of the other)
            if overlap >= 0.8:
                # Keep the longer version
                if len(line["words"]) > len(prev["words"]):
                    idx = deduped.index(prev)
                    seen_texts.discard(prev["text"].lower())
                    deduped[idx] = line
                    seen_texts.add(cur_text)
                is_dup = True
                break

        if not is_dup:
            deduped.append(line)
            seen_texts.add(cur_text)

    # Remove single-word lines that are just fragments of adjacent lines
    cleaned = []
    for i, line in enumerate(deduped):
        if len(line["words"]) == 1:
            word = line["words"][0].lower()
            # Check if this single word appears in the previous or next line
            in_prev = i > 0 and word in " ".join(deduped[i - 1]["words"]).lower()
            in_next = (
                i + 1 < len(deduped)
                and word in " ".join(deduped[i + 1]["words"]).lower()
            )
            if in_prev or in_next:
                continue  # Skip fragment
        cleaned.append(line)
    deduped = cleaned

    # --- Step 4: Trust SRT start times, cut previous line short if overlap ---
    # Key principle: each line starts at its SRT-estimated time (stay in sync with speech).
    # If the previous line would still be showing, it gets cut short — NOT pushed later.
    sequenced = []

    for i, line in enumerate(deduped):
        line_start = line["start"]

        # Duration = time until the next line starts (so it disappears right as the next appears)
        if i + 1 < len(deduped):
            duration = deduped[i + 1]["start"] - line_start
        else:
            # Last line: use estimated duration
            duration = line["estimated_duration"]

        # Clamp: minimum 0.15s (skip near-zero junk), maximum 8s
        duration = max(0.15, min(duration, 8.0))

        sequenced.append(
            {
                "words": line["words"],
                "start": line_start,
                "duration": duration,
            }
        )

    # --- Step 5: Create VideoClips ---
    clips = []

    for entry in sequenced:
        line_words = entry["words"]
        line_start = entry["start"]
        line_duration = entry["duration"]
        n_words = len(line_words)
        time_per_word = line_duration / n_words

        try:
            # Pre-render all highlight states
            frames = []
            for w_idx in range(n_words):
                frame = _render_single_line(
                    line_words,
                    w_idx,
                    pil_font,
                    font_size,
                    max_width,
                    color,
                    hl_color,
                    stroke_color,
                    stroke_width,
                )
                frames.append(frame)

            img_h, img_w = frames[0].shape[:2]

            def make_frame(t, _frames=frames, _tpw=time_per_word, _n=n_words):
                idx = min(int(t / _tpw), _n - 1)
                return _frames[idx]

            line_clip = VideoClip(make_frame, duration=line_duration)

            # Position on sharp center video
            anchor = str(cap_cfg.get("anchor", "bottom") or "bottom").lower()
            if anchor == "bottom":
                # Ratio-based padding (scales with the actual content window)
                try:
                    ratio = float(cap_cfg.get("bottom_padding_ratio", 0.06) or 0.06)
                except Exception:
                    ratio = 0.06
                pad = int(video_h * ratio)
                pad_min = int(cap_cfg.get("bottom_padding_min_px", 40) or 40)
                pad_max = int(cap_cfg.get("bottom_padding_max_px", 160) or 160)
                pad = max(pad_min, min(pad_max, pad))

                # Legacy px fallback
                if pad <= 0:
                    pad = int(cap_cfg.get("bottom_padding", 70) or 70)

                video_bottom = video_y + video_h
                y = video_bottom - img_h - pad
            else:
                y_ratio = cap_cfg.get("y_ratio")
                if y_ratio is not None:
                    try:
                        y_ratio_f = float(y_ratio)
                    except Exception:
                        y_ratio_f = 0.78
                    y = int(video_y + (video_h * y_ratio_f) - (img_h / 2))
                else:
                    video_bottom = video_y + video_h
                    y = video_bottom - img_h - margin_from_bottom

            # Clamp to stay inside the center video region
            y = max(video_y + 10, y)
            y = min(video_y + video_h - img_h - 10, y)

            line_clip = line_clip.with_position(("center", y))
            line_clip = line_clip.with_start(line_start)

            clips.append(line_clip)

        except Exception as e:
            print(f"  Warning: skipped caption line: {e}")

    return clips


# ============================================================
# CAPTIONS FROM WHISPER — exact per-word timestamps, no estimation
# ============================================================


def create_caption_clips_from_words(word_list, config, video_y, video_h):
    """
    Create caption clips from Whisper word-level timestamps.
    Groups words into display lines, uses exact start/end per word for highlight timing.

    No dedup needed — Whisper gives clean, non-overlapping word list.
    No timing estimation — each word has its own start/end from Whisper.

    Strategy:
      1. Group words into display lines that fit within max_width.
      2. Each line appears when its first word starts, disappears when its last word ends.
      3. Word highlight follows exact Whisper timestamps within each line.
    """
    cap_cfg = config["captions"]
    font_path = resolve_font(cap_cfg.get("font"))
    font_size = cap_cfg["font_size"]
    max_width = cap_cfg["max_width"]
    color = cap_cfg["color"]
    hl_color = cap_cfg["highlight_color"]
    stroke_color = cap_cfg["stroke_color"]
    stroke_width = cap_cfg["stroke_width"]
    margin_from_bottom = cap_cfg.get("margin_from_video_bottom", 100)

    pil_font = (
        ImageFont.truetype(font_path, font_size)
        if font_path
        else ImageFont.load_default()
    )

    if not word_list:
        return []

    # --- Step 1: Group words into display lines by pixel width ---
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = []  # Each: {"words": [...], "starts": [...], "ends": [...]}
    current_line_words = []
    current_line_text = ""

    for w in word_list:
        test_text = (current_line_text + " " + w["word"]).strip()
        bbox = dummy.textbbox((0, 0), test_text, font=pil_font)
        text_w = bbox[2] - bbox[0]

        if text_w > max_width and current_line_words:
            # Finalize current line
            lines.append(
                {
                    "words": [x["word"] for x in current_line_words],
                    "starts": [x["start"] for x in current_line_words],
                    "ends": [x["end"] for x in current_line_words],
                }
            )
            current_line_words = [w]
            current_line_text = w["word"]
        else:
            current_line_words.append(w)
            current_line_text = test_text

    if current_line_words:
        lines.append(
            {
                "words": [x["word"] for x in current_line_words],
                "starts": [x["start"] for x in current_line_words],
                "ends": [x["end"] for x in current_line_words],
            }
        )

    if not lines:
        return []

    # --- Step 2: Create VideoClips with exact word highlight timing ---
    clips = []

    for i, line in enumerate(lines):
        words = line["words"]
        word_starts = line["starts"]
        word_ends = line["ends"]
        n_words = len(words)

        # Line appears when first word starts, disappears when next line starts
        line_start = word_starts[0]
        if i + 1 < len(lines):
            line_end = lines[i + 1]["starts"][0]
        else:
            line_end = word_ends[-1] + 0.3

        line_duration = line_end - line_start
        if line_duration <= 0.05:
            continue

        try:
            # Pre-render all highlight states
            frames = []
            for w_idx in range(n_words):
                frame = _render_single_line(
                    words,
                    w_idx,
                    pil_font,
                    font_size,
                    max_width,
                    color,
                    hl_color,
                    stroke_color,
                    stroke_width,
                )
                frames.append(frame)

            img_h, img_w = frames[0].shape[:2]

            # Build highlight schedule: for each word, the time offset within the line
            # when it should be highlighted
            word_offsets = [ws - line_start for ws in word_starts]

            def make_frame(t, _frames=frames, _offsets=word_offsets, _n=n_words):
                # Find which word should be highlighted at time t
                idx = 0
                for j in range(_n - 1, -1, -1):
                    if t >= _offsets[j]:
                        idx = j
                        break
                return _frames[idx]

            line_clip = VideoClip(make_frame, duration=line_duration)

            # Position on sharp center video
            anchor = str(cap_cfg.get("anchor", "bottom") or "bottom").lower()
            if anchor == "bottom":
                # Ratio-based padding (scales with the actual content window)
                try:
                    ratio = float(cap_cfg.get("bottom_padding_ratio", 0.06) or 0.06)
                except Exception:
                    ratio = 0.06
                pad = int(video_h * ratio)
                pad_min = int(cap_cfg.get("bottom_padding_min_px", 40) or 40)
                pad_max = int(cap_cfg.get("bottom_padding_max_px", 160) or 160)
                pad = max(pad_min, min(pad_max, pad))

                # Legacy px fallback
                if pad <= 0:
                    pad = int(cap_cfg.get("bottom_padding", 70) or 70)

                video_bottom = video_y + video_h
                y = video_bottom - img_h - pad
            else:
                y_ratio = cap_cfg.get("y_ratio")
                if y_ratio is not None:
                    try:
                        y_ratio_f = float(y_ratio)
                    except Exception:
                        y_ratio_f = 0.78
                    y = int(video_y + (video_h * y_ratio_f) - (img_h / 2))
                else:
                    video_bottom = video_y + video_h
                    y = video_bottom - img_h - margin_from_bottom

            # Clamp to stay inside the center video region
            y = max(video_y + 10, y)
            y = min(video_y + video_h - img_h - 10, y)

            line_clip = line_clip.with_position(("center", y))
            line_clip = line_clip.with_start(line_start)

            clips.append(line_clip)

        except Exception as e:
            print(f"  Warning: skipped caption line: {e}")

    return clips


def create_short_burst_clips(word_list, config, video_y, video_h):
    """
    SHORT CLIPS / TIKTOK STYLE — Short word bursts (2-4 content words only).
    Strips filler words. Each burst: pop-in → hold → pop-out.
    Groups consecutive content words into brief bursts timed to speech.
    """
    cap_cfg = config["captions"]
    font_path = resolve_font(cap_cfg.get("font"))
    font_size = cap_cfg["font_size"]
    max_width = cap_cfg["max_width"]
    color = cap_cfg["color"]
    hl_color = cap_cfg["highlight_color"]
    stroke_color = cap_cfg["stroke_color"]
    stroke_width = cap_cfg["stroke_width"]

    # Filler words to strip
    filler = set(w.lower() for w in cap_cfg.get("filler_words", []))

    pil_font = (
        ImageFont.truetype(font_path, font_size)
        if font_path
        else ImageFont.load_default()
    )

    if not word_list:
        return []

    # --- Step 1: Strip filler words, keep only content words ---
    content_words = []
    for w in word_list:
        word_text = strip_emoji(w["word"]).strip()
        if word_text and word_text.lower() not in filler:
            content_words.append(w)

    if not content_words:
        return []

    # --- Step 2: Group into bursts of 2-4 content words ---
    words_per_burst = int(cap_cfg.get("words_per_caption_group", 3))
    bursts = []
    current = []
    current_start = content_words[0]["start"]

    for i, w in enumerate(content_words):
        current.append(w)
        if len(current) >= words_per_burst:
            bursts.append({
                "words": current,
                "start": current[0]["start"],
                "end": current[-1]["end"],
            })
            current = []
            if i < len(content_words) - 1:
                current_start = content_words[i + 1]["start"]

    if current:
        bursts.append({
            "words": current,
            "start": current[0]["start"],
            "end": current[-1]["end"],
        })

    if not bursts:
        return []

    # --- Step 3: Create pop-animated burst clips ---
    clips = []
    from moviepy.video.fx import FadeIn, FadeOut

    for burst in bursts:
        burst_words = burst["words"]
        burst_start = burst["start"]
        burst_end = burst["end"]
        burst_dur = burst_end - burst_start

        if burst_dur <= 0.1:
            continue

        # Build text: just the content words joined
        text = " ".join(strip_emoji(w["word"]).strip() for w in burst_words)

        if not text:
            continue

        # Render the text
        bbox = pil_font.getbbox(text)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        pad_x = 30
        pad_y = 14
        img_w = text_w + pad_x * 2
        img_h = text_h + pad_y * 2

        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        x = pad_x - bbox[0]
        y = pad_y - bbox[1]

        # Thick stroke
        for sw in [6, 4, 2]:
            for dx, dy in [(sw, 0), (-sw, 0), (0, sw), (0, -sw),
                           (sw, sw), (-sw, -sw), (sw, -sw), (-sw, sw)]:
                draw.text((x + dx, y + dy), text, font=pil_font, fill=(0, 0, 0, 255))
        draw.text((x, y), text, font=pil_font, fill=(255, 255, 255, 255))

        frame = np.array(img)
        h, w_frame = frame.shape[:2]

        # Pop animation: scale up fast, hold, scale down — with manual RGBA fade
        def make_pop_frame(t, _frame=frame, _dur=burst_dur, _orig_h=h, _orig_w=w_frame):
            progress = min(t / _dur, 1.0)

            # Pop scale curve
            if progress < 0.3:
                scale = 0.5 + 0.5 * (progress / 0.3)
            else:
                scale = 1.0 - 0.5 * ((progress - 0.3) / 0.7)

            new_w = max(1, int(_orig_w * scale))
            new_h = max(1, int(_orig_h * scale))
            import cv2
            scaled = cv2.resize(_frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

            # Manual fade in/out on alpha channel
            fade_pct = progress
            if fade_pct < 0.06:
                fade_pct = fade_pct / 0.06  # 0→1 in first 6%
            elif fade_pct > 0.9:
                fade_pct = (1.0 - fade_pct) / 0.1  # 1→0 in last 10%
            else:
                fade_pct = 1.0
            fade_pct = max(0.0, min(1.0, fade_pct))

            if scaled.shape[2] == 4:  # RGBA
                scaled = scaled.copy()
                scaled[:,:,3] = (scaled[:,:,3].astype(float) * fade_pct).astype(np.uint8)

            return scaled

        burst_clip = VideoClip(make_pop_frame, duration=burst_dur)

        # Position: center, slightly below middle (lower third)
        y_ratio = float(cap_cfg.get("y_ratio", 0.62) or 0.62)
        content_center_y = video_y + (video_h * y_ratio)
        y = int(content_center_y - (h / 2))
        y = max(video_y + 10, min(video_y + video_h - h - 10, y))

        burst_clip = burst_clip.with_position(("center", y))
        burst_clip = burst_clip.with_start(burst_start)

        clips.append(burst_clip)

    return clips




# ============================================================
# CONTENT DETECTION — Find actual video in pre-letterboxed frames
# ============================================================


def _detect_content_area(clip, target_w, target_h):
    """Detect the main (sharp) content region in a pre-framed 9:16 clip.

    Why: some portrait clips are generated with a *sharp* center video and *blurred*
    top/bottom fill. Brightness-based "black bar" detection fails there.

    Strategy:
    1) Try classic black-bar detection (brightness threshold)
    2) If it looks like full-frame content, fall back to an edge-energy scan to find
       the sharpest contiguous band (usually the center window).

    Returns (content_y, content_h).
    """
    try:
        sample_time = min(1.0, clip.duration * 0.1)
        frame = clip.get_frame(sample_time)
        h = frame.shape[0]

        # --- 1) brightness-based black-bar detection ---
        # Only trust this when the bars are *truly* near-black and low-texture.
        # Blurfill/top-bottom content can be dark but still contains video, so
        # brightness-only detection would mis-detect the "content" region.
        row_brightness = np.mean(frame, axis=(1, 2))
        threshold = 15
        content_rows = np.where(row_brightness > threshold)[0]
        if len(content_rows) > 0:
            first_row = int(content_rows[0])
            last_row = int(content_rows[-1])
            content_y_guess = max(0, first_row - 2)
            content_h_guess = min(target_h, last_row + 2) - content_y_guess
        else:
            content_y_guess, content_h_guess = 0, target_h

        def _bar_is_true_black(bar_arr) -> bool:
            if bar_arr is None:
                return False
            if bar_arr.size == 0:
                return True
            gray_bar = np.mean(bar_arr.astype("float32"), axis=2)
            mean = float(gray_bar.mean())
            std = float(gray_bar.std())
            # Edge energy: true black bars have almost no high-frequency content.
            gx = np.abs(np.diff(gray_bar, axis=1))
            edge = float(gx.mean()) if gx.size else 0.0
            return (mean < 18.0) and (std < 10.0) and (edge < 2.0)

        # If we found meaningful bars, only accept if BOTH bars look like real black bars.
        if content_h_guess < target_h * 0.95:
            top_bar = frame[:content_y_guess, :, :] if content_y_guess > 0 else None
            bottom_start = int(content_y_guess + content_h_guess)
            bottom_bar = frame[bottom_start:, :, :] if bottom_start < target_h else None
            if _bar_is_true_black(top_bar) and _bar_is_true_black(bottom_bar):
                return content_y_guess, content_h_guess
            # Otherwise: it's likely a pre-framed/blurfill clip; fall through to edge-energy detection.

        # --- 2) edge-energy detection for blurfill layouts ---
        # The sharp center window has higher high-frequency detail than blurred fill.
        gray = np.mean(frame.astype("float32"), axis=2)
        gx = np.abs(np.diff(gray, axis=1))
        row_energy = gx.mean(axis=1)  # length ~h

        # Smooth the per-row energy to reduce noise.
        win = 31
        if h < win:
            win = max(7, (h // 2) * 2 + 1)
        kernel = np.ones(win, dtype="float32") / float(win)
        smooth = np.convolve(row_energy, kernel, mode="same")

        # Find the *best band* by sliding-window sum (more robust than thresholding).
        csum = np.cumsum(np.concatenate([[0.0], smooth.astype("float64")]))

        center = h / 2.0
        # Typical blurfill layouts have a sharp 16:9 window in the center.
        # For 1080x1920, a 16:9 window is ~608px tall (~0.316h).
        expected_h = int(target_w * 9 / 16)
        # Keep candidate heights near expected; very tall windows tend to "eat" blurred regions.
        candidates_h = sorted({
            expected_h,
            int(expected_h * 1.10),
            int(expected_h * 1.25),
            int(h * 0.28),
            int(h * 0.32),
            int(h * 0.36),
            int(h * 0.40),
            int(h * 0.44),
        })

        best = None
        best_score = -1.0

        for wh in candidates_h:
            if wh <= 0 or wh >= h:
                continue
            # Slide by a stride to speed up; still accurate enough for overlay anchoring.
            stride = max(1, int(h * 0.005))  # ~1% of height
            for a in range(0, h - wh, stride):
                b = a + wh
                energy_sum = float(csum[b] - csum[a])
                energy_mean = energy_sum / max(1.0, float(wh))
                mid = (a + b) / 2.0
                center_bonus = 1.0 - min(1.0, abs(mid - center) / center)

                # Penalize bands hugging the edges (usually blurfill padding).
                edge_penalty = 1.0
                margin = int(h * 0.08)
                if a < margin:
                    edge_penalty *= 0.88
                if b > (h - margin):
                    edge_penalty *= 0.88

                # Prefer sharp windows near the center.
                score = energy_mean * (0.60 + 0.40 * center_bonus) * edge_penalty
                if score > best_score:
                    best_score = score
                    best = (a, b)

        if not best:
            return 0, target_h

        a, b = best
        if (b - a) > int(h * 0.92):
            return 0, target_h

        content_y = max(0, int(a) - 6)
        content_h = min(target_h, int(b) + 6) - content_y
        return content_y, content_h

    except Exception as e:
        print(f"  Warning: content detection failed ({e}), using full frame")
        return 0, target_h


# ============================================================
# MAIN PIPELINE
# ============================================================


def add_captions_to_video(
    video_path,
    subtitle_path,
    output_path,
    config=None,
    title=None,
    use_whisper=False,
    whisper_model="base",
):
    """
    Full pipeline:
      1. Load video
      2. Letterbox to 9:16 (black bars top/bottom, full frame visible)
      3. Parse subtitles (Whisper JSON or SRT) or run Whisper
      4. Title hook in top bar (auto-fits)
      5. Captions overlaid on video (inside the frame)
      6. Composite and render

    subtitle_path: .json (Whisper) or .srt file. If use_whisper=True, runs Whisper on video.
    """
    if config is None:
        config = CONFIG

    target_w = config["video_width"]
    target_h = config["video_height"]

    # 1. Load video
    print(f"Loading: {video_path}")
    raw_clip = VideoFileClip(video_path)
    src_w, src_h = raw_clip.size
    original_fps = raw_clip.fps
    print(f"  Source: {src_w}x{src_h}, {raw_clip.duration:.1f}s, {original_fps:.1f}fps")

    # 2. Letterbox
    base_clip, video_y, video_h = letterbox_to_portrait(raw_clip, config)
    bar_top_h = video_y
    bar_bottom_y = video_y + video_h
    bar_bottom_h = target_h - bar_bottom_y
    print(f"  Layout: {target_w}x{target_h} letterbox")
    print(
        f"  Video at y={video_y}, h={video_h} | top bar={bar_top_h}px, bottom bar={bar_bottom_h}px"
    )

    # Detect pre-letterboxed videos: if the input is already 9:16 but was originally
    # a landscape video with baked-in black bars, the content sits in the center.
    # We detect this by sampling the first frame and finding non-black rows.
    if video_y == 0 and video_h == target_h:
        content_y, content_h = _detect_content_area(raw_clip, target_w, target_h)
        if content_h < target_h * 0.95:  # Significant framed/blurfill padding detected
            print(
                f"  Detected pre-letterboxed video: content at y={content_y}, h={content_h}"
            )
            video_y = content_y
            video_h = content_h
            bar_top_h = video_y
            bar_bottom_y = video_y + video_h
            bar_bottom_h = target_h - bar_bottom_y

    # 3. Parse subtitles — auto-detect format or run Whisper
    word_list = None  # Whisper word-level data
    subs = None  # SRT-style segments

    if use_whisper:
        print(f"Running Whisper on: {video_path}")
        json_path = run_whisper(video_path, model=whisper_model)
        word_list = parse_whisper_json(json_path)
        print(f"  {len(word_list)} words with exact timestamps")
    elif subtitle_path and subtitle_path.lower().endswith(".json"):
        print(f"Loading Whisper JSON: {subtitle_path}")
        word_list = parse_whisper_json(subtitle_path)
        print(f"  {len(word_list)} words with exact timestamps")
    elif subtitle_path and subtitle_path.lower().endswith(".srt"):
        print(f"Loading SRT: {subtitle_path}")
        subs = parse_srt(subtitle_path)
        print(f"  {len(subs)} caption segments (after dedup)")
    else:
        # Default: try to run Whisper
        print(f"No subtitle file provided, running Whisper on: {video_path}")
        json_path = run_whisper(video_path, model=whisper_model)
        word_list = parse_whisper_json(json_path)
        print(f"  {len(word_list)} words with exact timestamps")

    # 4. Title hook (in top black bar)
    title_text = title if title is not None else config.get("clip_title")
    if title_text is None:
        if word_list:
            # Use first few words from Whisper as default title
            first_words = [w["word"] for w in word_list[:12]]
            title_text = " ".join(first_words)
        elif subs:
            title_text = subs[0]["text"]
    
    # Strip emojis from title - videos don't render emojis well
    if title_text:
        title_text = strip_emoji(title_text)
    
    all_clips = [base_clip]

    if title_text:
        title_layers = create_title_clip(
            title_text, config, raw_clip.duration, bar_top_h, video_y=video_y, video_h=video_h
        )
        all_clips.extend(title_layers)
        display = title_text[:60] + ("..." if len(title_text) > 60 else "")
        prefer_on_video = bool(config.get("title", {}).get("prefer_on_video", False))
        if (not prefer_on_video) and (video_y is not None) and (video_y > 50):
            print(f'  Title: "{display}" (top padding area above center video)')
        elif (bar_top_h > 50) and (not prefer_on_video):
            print(f'  Title: "{display}" (top black bar)')
        else:
            print(f'  Title: "{display}" (on-video overlay)')

    # 5. Captions (overlaid on video frame)
    if word_list:
        if config["captions"].get("burst_mode", False):
            caption_clips = create_short_burst_clips(
                word_list, config, video_y, video_h
            )
            print(f"  {len(caption_clips)} short bursts (Whisper word-level)")
        elif config["captions"].get("word_by_word", False):
            caption_clips = create_word_by_word_clips(
                word_list, config, video_y, video_h
            )
            print(f"  {len(caption_clips)} word-by-word clips (Whisper word-level)")
        elif config["captions"].get("keyword_burst", False):
            caption_clips = create_keyword_burst_clips(
                word_list, config, video_y, video_h
            )
            print(f"  {len(caption_clips)} keyword bursts (Whisper word-level)")
        else:
            caption_clips = create_caption_clips_from_words(
                word_list, config, video_y, video_h
            )
            print(f"  {len(caption_clips)} caption lines (Whisper word-level)")
    else:
        if config["captions"].get("burst_mode", False):
            caption_clips = create_short_burst_clips(
                [{"word": s["text"], "start": s["start"], "end": s["end"]}
                 for s in subs], config, video_y, video_h
            )
            print(f"  {len(caption_clips)} short bursts (SRT)")
        elif config["captions"].get("keyword_burst", False):
            caption_clips = create_word_by_word_clips(
                [{"word": s["text"], "start": s["start"], "end": s["end"]}
                 for s in subs], config, video_y, video_h
            )
            print(f"  {len(caption_clips)} word-by-word clips (SRT)")
        else:
            caption_clips = create_caption_clips(subs, config, video_y, video_h)
            print(f"  {len(caption_clips)} caption lines (SRT)")

    all_clips.extend(caption_clips)

    # 6. Composite and render
    final = CompositeVideoClip(all_clips, size=(target_w, target_h))
    final = final.with_duration(raw_clip.duration)

    print(f"Rendering: {output_path}")

    # MoviePy defaults can produce files that some mobile apps preview as black.
    # Enforce the most compatible H.264 packaging (yuv420p + faststart) and a sane FPS.
    render_fps = original_fps
    try:
        if not render_fps or render_fps < 10 or render_fps > 120:
            render_fps = 30
    except TypeError:
        render_fps = 30

    threads = max(1, (os.cpu_count() or 4) - 1)

    # Prevent MoviePy from littering CWD with clip_###TEMP_MPY_*.mp4 artifacts.
    # Force temp audio files into an isolated temp dir and clean it up.
    tmp_audio_dir = tempfile.mkdtemp(prefix="mpy_audio_")
    tmp_audio_file = os.path.join(tmp_audio_dir, f"audio_{os.getpid()}.m4a")

    try:
        final.write_videofile(
            output_path,
            fps=render_fps,
            codec="libx264",
            audio_codec="aac",
            audio_bitrate="128k",
            preset="medium",
            threads=threads,
            temp_audiofile=tmp_audio_file,
            temp_audiofile_path=tmp_audio_dir,
            remove_temp=True,
            ffmpeg_params=[
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
            ],
            logger="bar",
        )
    finally:
        shutil.rmtree(tmp_audio_dir, ignore_errors=True)

    print(f"Done → {output_path}")


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Viral Video Caption Generator — Always uses Whisper for word-level captions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic (auto-runs Whisper):
  python add_captions.py video.mp4 --title "How Mark Cuban Finds Winners" output.mp4

  # With custom Whisper model:
  python add_captions.py video.mp4 --title "Hook" output.mp4 --model base
""",
    )
    parser.add_argument("video", help="Input video file")
    parser.add_argument("output", help="Output video file")
    parser.add_argument(
        "--title", 
        default=None, 
        help="On-screen hook text to display at top of video (REQUIRED). Alias: --hook"
    )
    parser.add_argument(
        "--hook",
        default=None,
        help="Alias for --title (preferred name)."
    )
    parser.add_argument(
        "--model",
        default="tiny",
        help="Whisper model (tiny, base, small, medium, large). Default: tiny",
    )

    args = parser.parse_args()

    # Normalize hook alias
    if args.hook and not args.title:
        args.title = args.hook

    # Validate required arguments
    if not args.title:
        parser.error("ERROR: --hook/--title is REQUIRED for the on-screen hook.\n"
                    "  python add_captions.py video.mp4 --hook \"YOUR HOOK\" output.mp4")

    add_captions_to_video(
        video_path=args.video,
        subtitle_path=None,  # Not needed - always runs Whisper
        output_path=args.output,
        title=args.title,
        use_whisper=True,  # Always use Whisper
        whisper_model=args.model,
    )
