#!/usr/bin/env python3
"""autonomous_loop.py — Master 8-step autonomous social media loop.

Runs the complete end-to-end pipeline:
  1. DISCOVER   — scan channels + RSS for new videos
  2. SELECT     — pick the best DISCOVERED video
  3. CLIP       — generate clips (Prism or Wayin)
  4. POST       — post to platforms via Postiz
  5. ENGAGE     — browser engagement on YouTube/TikTok/Instagram
  6. COLLECT    — pull metrics from Postiz
  7. EVALUATE   — check experiment verdict
  8. EVOLVE     — update SOUL.md if KEEP

Usage:
  python3 autonomous_loop.py              # Run full pipeline
  python3 autonomous_loop.py --steps 1,2   # Run only steps 1-2
  python3 autonomous_loop.py --dry-run    # Show what would run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent.resolve()
SCRIPTS  = SKILL_DIR / "scripts"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_step(name: str, script: Path, args: list[str] | None = None) -> int:
    cmd = [sys.executable, str(script)] + (args or [])
    print(f"\n{'='*50}")
    print(f"STEP: {name}")
    print(f"{'='*50}")
    print(f"Running: {' '.join(cmd[:3])} ...")
    result = subprocess.run(cmd, cwd=str(SCRIPTS.parent))
    return result.returncode


STEPS = {
    1: ("DISCOVER",   SCRIPTS / "discovery.py",      []),
    2: ("SELECT",     SCRIPTS / "selector.py",         []),
    3: ("CLIP",       SCRIPTS / "clip_runner.py",      ["--no-wait"]),
    4: ("POST",       SCRIPTS / "posting.py",           []),
    5: ("ENGAGE",     SCRIPTS / "engagement.py",        ["all"]),
    6: ("COLLECT",    SCRIPTS / "collector.py",         ["--source", "postiz", "--days", "1"]),
    7: ("EVALUATE",   SCRIPTS / "evaluator.py",        []),
    8: ("EVOLVE",     SCRIPTS / "evolver.py",          []),
}


def run_steps(step_nums: list[int], dry_run: bool = False) -> None:
    print(f"\n{'#'*50}")
    print(f"# AUTONOMOUS LOOP — {now_iso()}")
    print(f"# Running steps: {step_nums}")
    print(f"{'#'*50}")

    results = {}
    for n in step_nums:
        if n not in STEPS:
            print(f"Unknown step: {n}")
            continue
        name, script, args = STEPS[n]

        if dry_run:
            print(f"\n[DRY RUN] Would run: {script} {' '.join(args)}")
            results[n] = 0
            continue

        rc = run_step(name, script, args)
        results[n] = rc

        if rc != 0:
            print(f"\n⚠️  Step {n} ({name}) returned code {rc}")
            print(f"    Continuing to next step...")

    # Summary
    print(f"\n{'='*50}")
    print("LOOP COMPLETE")
    print(f"{'='*50}")
    print(f"Results: { {STEPS[n][0]: r for n, r in results.items()} }")
    print(f"Next run: +6 hours")


def main() -> None:
    parser = argparse.ArgumentParser(description="Master autonomous social media loop")
    parser.add_argument(
        "--steps",
        default="1,2,3,4,5,6",
        help="Comma-separated step numbers (default: 1,2,3,4,5,6)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run all 8 steps including evaluation + evolution",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would run without executing",
    )
    args = parser.parse_args()

    if args.full:
        step_nums = list(range(1, 9))
    else:
        step_nums = [int(s.strip()) for s in args.steps.split(",")]

    run_steps(step_nums, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
