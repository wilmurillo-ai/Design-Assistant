#!/usr/bin/env python3
"""
log_insight.py — Lightweight structured logger for Skill Garden

Usage:
    python3 log_insight.py --skill <skill_name> --trigger "<trigger>" --outcome <OK|PARTIAL|FAIL|SLOW|SKIP> --signal "<signal>" [--evidence "<evidence>"] [--flags "<flag1,flag2>"]

Examples:
    # Log a normal success (minimal)
    python3 log_insight.py --skill github-trending-summary --trigger "daily top 5 repos" --outcome OK --signal "Covered: standard case works"

    # Log a failure with detail
    python3 log_insight.py --skill banxuebang-helper --trigger "check homework" --outcome FAIL \
        --signal "Missing: semester config hardcoded" \
        --evidence "API returned empty. Config has 2024-2025 but current is 2025-2026." \
        --flags "missing_coverage,config_stale"

    # Quick OK log
    python3 log_insight.py -s apple-notes -t "create note" -o OK -S "No issues"
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SKILLS_DIR = WORKSPACE / "skills"


def get_log_path(skill_name: str) -> Path:
    """Get or create the usage_log.md path for a skill."""
    skill_dir = SKILLS_DIR / skill_name
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)
    log_path = refs_dir / "usage_log.md"
    if not log_path.exists():
        log_path.write_text("# Usage Log — Skill Garden\n\n")
    return log_path


def format_abbreviated(trigger: str, signal: str) -> str:
    """Format for OK outcomes with no flags."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"## {now}\nTrigger: {trigger}\nOutcome: OK\nSignal: {signal}\n\n"


def format_full(
    trigger: str,
    outcome: str,
    signal: str,
    evidence: str = "",
    flags: str = "",
) -> str:
    """Format for PARTIAL, FAIL, SLOW outcomes."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"## {now}\n\n### Trigger\n{trigger}\n\n### Outcome\n{outcome}\n\n### Signal\n{signal}\n\n"
    if evidence:
        entry += f"### Evidence\n{evidence}\n\n"
    if flags:
        flag_list = ", ".join(f"[{f.strip()}]" for f in flags.split(",") if f.strip())
        entry += f"### Flags\n{flag_list}\n\n"
    return entry


def write_log(
    skill_name: str,
    trigger: str,
    outcome: str,
    signal: str,
    evidence: str = "",
    flags: str = "",
) -> None:
    """Write a log entry to the skill's usage_log.md."""
    log_path = get_log_path(skill_name)

    if outcome == "OK" and not flags and not evidence:
        entry = format_abbreviated(trigger, signal)
    else:
        entry = format_full(trigger, outcome, signal, evidence, flags)

    with open(log_path, "a") as f:
        f.write(entry)

    print(f"[OK] Logged to {log_path}")
    print(f"     {outcome}: {signal[:60]}{'...' if len(signal) > 60 else ''}")


def append_landmark(skill_name: str, event_type: str, description: str) -> None:
    """Append a landmark event to the grower's own memory."""
    grower_log = SKILLS_DIR / "skill-garden" / "references" / "master_log.md"
    if not grower_log.exists():
        return

    now = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n## Landmark: {now}\n{skill_name}: {event_type} — {description}\n"

    with open(grower_log, "a") as f:
        f.write(entry)


def main():
    parser = argparse.ArgumentParser(description="Log a skill usage insight")
    parser.add_argument("-s", "--skill", required=True, help="Skill name")
    parser.add_argument("-t", "--trigger", required=True, help="Trigger description (≤10 words recommended)")
    parser.add_argument("-o", "--outcome", required=True, choices=["OK", "PARTIAL", "FAIL", "SLOW", "SKIP"], help="Outcome")
    parser.add_argument("-S", "--signal", required=True, help="One-line signal/observation")
    parser.add_argument("-e", "--evidence", default="", help="Evidence (1-2 sentences)")
    parser.add_argument("-f", "--flags", default="", help="Comma-separated flags")
    parser.add_argument("-m", "--mark-landmark", default="", help="Also log landmark event: <event_type>")

    args = parser.parse_args()

    if not (SKILLS_DIR / args.skill).exists():
        print(f"[WARN] Skill directory not found: {SKILLS_DIR / args.skill}")
        print(f"       Available skills: {[d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / 'SKILL.md').exists()]}")
        sys.exit(1)

    write_log(args.skill, args.trigger, args.outcome, args.signal, args.evidence, args.flags)

    if args.mark_landmark:
        append_landmark(args.skill, args.mark_landmark, args.signal)


if __name__ == "__main__":
    main()
