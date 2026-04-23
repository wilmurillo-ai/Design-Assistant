---
name: prism-clips
description: Deterministic end-to-end YouTube → viral Shorts/TikTok/Reels clips generator. Use when creating vertical clips that MUST have Whisper captions + a strong title hook overlay, must analyze the full video (not just intro), must reject no-voice videos/clips, and must output only validated files to /final with status.json/result.json for monitoring.
---

# Prism Clips (Deterministic)

## Single Entry Point (ONLY)

Run **`prism_run.py`**. Do not use any other scripts in this skill.

```bash
python3 prism_run.py --url "https://youtube.com/watch?v=..."          # background by default
python3 prism_run.py --url "..." --no-background                     # foreground
```

Legacy code is archived under `legacy/` and must not be called.

## Guarantees (enforced by code)
- Whisper captions on every output clip (no optional flag)
- Title hook overlay is required (hard fail if missing)
- Full-video transcript analysis (not partial)
- Intro avoidance: skips first N seconds (default 180s)
- Rejects **no-voice** videos + rejects **silent** extracted clips
- Writes only validated outputs to `final/`
- Emits machine-readable progress + results:
  - `status.json`
  - `result.json` (includes `best_clip`)

## Output Layout (per video)

`~/.openclaw/workspace-prism/clips/<safe_title>_<video_id>/`
- `raw/source.webm` — downloaded source
- `analysis/transcript.json` — full Whisper JSON
- `analysis/analyze.json` — candidate pool + scores
- `analyze.md` — human-readable table (debug)
- `segments/clip_###.mp4` — extracted segments (pre-caption)
- `final/clip_###.mp4` — final outputs (captions + title)
- `status.json` — current stage
- `result.json` — final manifest (`clips[]`, `best_clip`)
- `run.log` — full logs (background mode)

## Tuning Flags

```bash
python3 prism_run.py --url "..." \
  --num-clips 6 \
  --clip-duration 55 \
  --skip-intro 180 \
  --portrait-mode letterbox \
  --pre-roll 2.5 \
  --whisper-full-model base \
  --whisper-clip-model tiny
```

Notes:
- `--portrait-mode`: `letterbox` (default, clean black bars). `blurfill` is deprecated/disabled.
- `--whisper-full-model`: accuracy for full transcript (default `base`)
- `--whisper-clip-model`: speed for per-clip captions (default `tiny`)

## Monitoring / Debug
- Check: `status.json` → `stage`
- If background run: tail `run.log`
- Posting should use: `result.json.best_clip.final` (must be under `/final/`)
