#!/usr/bin/env python3
"""health_check.py — Verify all prerequisites are installed and configured.

Usage:
  python3 health_check.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SKILL_DIR  = Path(__file__).parent.parent.resolve()
CONFIG_DIR = SKILL_DIR / "config"


def check_bin(name: str) -> bool:
    return subprocess.call(
        ["bash", "-lc", f"command -v {name} >/dev/null 2>&1"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ) == 0


def check_file(path: Path, label: str) -> bool:
    ok = path.exists()
    status = "✅" if ok else "❌"
    print(f"  {status} {label}: {path}")
    return ok


def check_json(path: Path) -> bool:
    try:
        data = json.loads(path.read_text())
        return True
    except Exception as e:
        print(f"  ❌ {label}: {path} — {e}")
        return False


def main() -> None:
    errors = 0

    print("=" * 50)
    print("HEALTH CHECK")
    print("=" * 50)

    # ── System tools ──────────────────────────────────────────────────────────
    print("\n🔧 System tools:")
    for tool in ("ffmpeg", "yt-dlp", "python3", "node", "npm"):
        ok = check_bin(tool)
        if not ok:
            print(f"    Install: pip install {tool}" if tool != "node" else "npm install -g ...")
            errors += 1 if not ok else 0

    # ── Python packages ───────────────────────────────────────────────────────
    print("\n📦 Python packages:")
    for pkg in ("whisper",):
        ok = check_bin(pkg)
        if not ok:
            print(f"    Install: pip install openai-whisper")
            errors += 1 if not ok else 0

    # ── Postiz CLI ────────────────────────────────────────────────────────────
    print("\n📤 Postiz CLI:")
    ok = check_bin("postiz")
    if ok:
        print("  ✅ postiz installed")
    else:
        print("  ❌ postiz not found — install: npm install -g postiz")
        errors += 1

    # ── Skill directories ─────────────────────────────────────────────────────
    print("\n📁 Skill structure:")
    for sub in ("social-media-engagement", "postiz-skill", "ai-clipping"):
        ok = check_file(SKILL_DIR / sub, sub)
        errors += 0 if ok else 1

    # ── Scripts ──────────────────────────────────────────────────────────────
    print("\n🔧 Scripts:")
    for script in (
        "discovery.py", "selector.py", "clip_runner.py",
        "posting.py", "engagement.py", "collector.py",
        "evaluator.py", "evolver.py", "tracker.py",
        "health_check.py",
    ):
        ok = check_file(SKILL_DIR / "scripts" / script, script)
        errors += 0 if ok else 1

    # ── Config files ──────────────────────────────────────────────────────────
    print("\n⚙️  Config files:")
    for cfg in ("channels.json", "platforms.json", "strategy.json"):
        path = CONFIG_DIR / cfg
        if check_file(path, cfg):
            check_json(path)
        else:
            errors += 1

    # ── API keys ──────────────────────────────────────────────────────────────
    print("\n🔑 API keys:")
    if os.getenv("POSTIZ_API_KEY"):
        print("  ✅ POSTIZ_API_KEY set")
    else:
        print("  ⚠️  POSTIZ_API_KEY not set (engagement collection will use manual mode)")

    if os.getenv("POSTIZ_TOKEN"):
        print("  ✅ POSTIZ_TOKEN set")
    else:
        print("  ⚠️  POSTIZ_TOKEN not set (metrics collection will use manual mode)")

    # ── Prism ────────────────────────────────────────────────────────────────
    print("\n🎬 Prism:")
    prism_dir = Path(os.getenv("PRISM_DIR", "~/.openclaw/workspace-prism")).expanduser()
    prism_run = prism_dir / "skills" / "prism-clips" / "prism_run.py"
    check_file(prism_run, "prism_run.py")
    if not prism_run.exists():
        print(f"    Prism workspace not found at {prism_dir}")
        errors += 1

    print("\n" + "=" * 50)
    if errors == 0:
        print("✅ All checks passed — ready to run!")
    else:
        print(f"❌ {errors} error(s) — fix the above before running")
    print("=" * 50)


if __name__ == "__main__":
    main()
