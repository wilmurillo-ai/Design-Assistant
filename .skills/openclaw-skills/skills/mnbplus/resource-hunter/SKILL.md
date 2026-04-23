---
name: resource-hunter
description: Find the best public download route for movies, TV, anime, music, software, books, pan links, magnets, and public video URLs. Uses high-recall routing, quality-aware ranking, source health, and stable JSON output without login, cookies, or API keys.
---

# Resource Hunter

Public resource discovery for agents.  
Use it to find the best public download route, not to bypass access controls.

## Use this skill when the user wants to

- Find public pan links, torrent results, or magnets
- Compare releases for quality, confidence, and source health
- Search movies, TV, anime, music, software, or books
- Inspect a public video URL and optionally download it if the machine is ready
- Get compact chat output or structured JSON for downstream tools

## Do not use this skill for

- Login-only sites, private accounts, cookies, invite-only trackers, or private libraries
- DRM, captchas, bypassing access controls, or restricted content
- Guarantees about legality, permanence, or long-term availability

## What this skill gives the agent

- High-recall multi-source search across pan and torrent channels
- Tiered ranking: `top`, `related`, and suppressed risky recall
- Quality-aware sorting with title-family matching, season/episode checks, and release parsing
- Live source health, degraded-source penalties, and circuit breaking
- JSON v3 output with `canonical_identity`, `evidence`, `source_health`, and `upstream_source`

## Main entrypoint

```bash
SKILL_DIR="$(openclaw skills path resource-hunter)/scripts"
python3 "$SKILL_DIR/hunt.py" search "<query>"
```

## Quick start

```bash
python3 "$SKILL_DIR/hunt.py" search "Oppenheimer 2023" --4k
python3 "$SKILL_DIR/hunt.py" search "Breaking Bad S01E01" --tv
python3 "$SKILL_DIR/hunt.py" search "Attack on Titan" --anime --sub
python3 "$SKILL_DIR/hunt.py" search "Jay Chou Fantasy lossless" --music
python3 "$SKILL_DIR/hunt.py" search "Adobe Photoshop 2024" --software --channel pan
python3 "$SKILL_DIR/hunt.py" video probe "https://www.bilibili.com/video/BV..."
python3 "$SKILL_DIR/hunt.py" benchmark
```

## Default routing

- Movie: pan first, torrent second
- TV: EZTV/TPB first, then pan supplements
- Anime: Nyaa first, then pan supplements
- Music, software, book: pan first, torrent fallback
- Public video URL: skip search and route directly to `video probe` / `video info`

## Output contract

- Default text: only `top` and `related` results are shown
- Risky recall stays suppressed in text and is still available in JSON
- `--json`: JSON v3 with `schema_version`, `query`, `intent`, `plan`, `results`, `suppressed`, `warnings`, `source_status`, and `meta`
- `--json-version 2`: temporary compatibility mode for older consumers

## Runtime requirements

- Search, ranking, and source diagnostics: no API keys required
- Public video inspect/probe: `yt-dlp` optional but recommended
- Public video download/subtitle: requires both `yt-dlp` and `ffmpeg`

## Agent rules

- Prefer the main `hunt.py` entrypoint over lower-level wrappers
- Use `--quick` when the user wants a short answer
- Use `--json` when another tool or script will consume the output
- If the input is a public video URL, do not search pan/torrent first; go straight to the video pipeline
- If the user asks to actually download a public video URL, first verify `yt-dlp` and `ffmpeg` are installed; otherwise return the route plus the missing dependency requirement
- If the user wants only pan or only torrent, set `--channel pan` or `--channel torrent`
- Prefer benchmark-backed changes over heuristic tweaks without regression coverage

## Legacy compatibility

Legacy wrappers still exist for one compatibility cycle:

```bash
python3 "$SKILL_DIR/pansou.py" "<query>"
python3 "$SKILL_DIR/torrent.py" "<query>"
python3 "$SKILL_DIR/video.py" info "<url>"
```

## References

- Detailed usage: `references/usage.md`
- Internal architecture and JSON schema: `references/architecture.md`
- Source coverage and routing notes: `references/sources.md`
