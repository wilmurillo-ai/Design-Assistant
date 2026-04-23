#!/usr/bin/env python3
"""
Rebuild the daily log index from existing log files.

Usage:
    python rebuild_index.py /path/to/project-root

Scans memory/*.md date-named files (or legacy memory/daily/*.md), extracts metadata
a fresh memory/index.md. Also generates monthly rollups for months
older than 60 days.
"""

import re
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path


def extract_log_metadata(log_path: Path) -> dict:
    """Extract metadata from a daily log file's header and sections."""
    text = log_path.read_text(encoding="utf-8")
    date = log_path.stem  # YYYY-MM-DD

    # Extract threads from header
    threads_match = re.search(r"Thread\(s\) active:\s*(.+)", text)
    threads = threads_match.group(1).strip() if threads_match else "—"

    # Extract key topics from summary (first 200 chars of Session Summary)
    summary_match = re.search(r"## Session Summary\n+(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if summary_match:
        summary_text = summary_match.group(1).strip()[:200]
        # Extract nouns/topics — simplified: take first few meaningful words
        words = [w for w in summary_text.split() if len(w) > 3 and w[0].islower()]
        topics = ", ".join(words[:5]) if words else "general"
    else:
        topics = "—"

    # Count decisions
    decision_count = len(re.findall(r"^\|(?!\s*-)", text, re.MULTILINE)) - 1  # subtract header
    decision_count = max(0, decision_count)

    # Extract mood
    mood_match = re.search(r"## Emotional/Tonal Notes\n+(.*?)(?=\n##|\Z)", text, re.DOTALL)
    mood = mood_match.group(1).strip()[:30] if mood_match else "—"

    return {
        "date": date,
        "threads": threads,
        "topics": topics,
        "decisions": decision_count,
        "mood": mood,
    }


def rebuild_index(root: str):
    root = Path(root).resolve()

    # Support new layout (memory/) and legacy layout (memory/daily/)
    date_glob = "[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"
    new_dir = root / "memory"
    legacy_dir = root / "memory" / "daily"

    log_files = sorted(new_dir.glob(date_glob), reverse=True)
    if not log_files and legacy_dir.exists():
        log_files = sorted(legacy_dir.glob("*.md"), reverse=True)

    if not log_files:
        print("No daily log files found in memory/ or memory/daily/.")
        return

    today = datetime.now(timezone.utc)
    cutoff = today - timedelta(days=60)
    cutoff_str = cutoff.strftime("%Y-%m")

    recent_entries = []
    monthly_buckets = defaultdict(list)

    for log_path in log_files:
        meta = extract_log_metadata(log_path)
        month = meta["date"][:7]  # YYYY-MM

        if month >= cutoff_str:
            recent_entries.append(meta)
        else:
            monthly_buckets[month].append(meta)

    # Build index content
    lines = [
        "# Daily Log Index\n",
        f"> Auto-generated. Rebuilt: {today.strftime('%Y-%m-%d')}",
        f"> Total logs: {len(log_files)}\n",
        "| Date | Threads Touched | Key Topics | Decisions | Mood/Tone |",
        "|------|-----------------|------------|-----------|-----------|",
    ]

    for entry in recent_entries:
        lines.append(
            f"| {entry['date']} | {entry['threads']} | {entry['topics']} "
            f"| {entry['decisions']} | {entry['mood']} |"
        )

    lines.append("\n## Monthly Rollups\n")
    if monthly_buckets:
        lines.append("| Month | Sessions | Key Threads | Major Decisions |")
        lines.append("|-------|----------|-------------|-----------------|")
        for month in sorted(monthly_buckets.keys(), reverse=True):
            entries = monthly_buckets[month]
            all_threads = set()
            total_decisions = 0
            for e in entries:
                all_threads.update(t.strip() for t in e["threads"].split(",") if t.strip() != "—")
                total_decisions += e["decisions"]
            threads_str = ", ".join(sorted(all_threads)) if all_threads else "—"
            lines.append(f"| {month} | {len(entries)} | {threads_str} | {total_decisions} |")
    else:
        lines.append("(No months old enough for rollup yet)")

    index_path = root / "memory" / "index.md"
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Index rebuilt: {index_path} ({len(log_files)} logs indexed)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rebuild_index.py /path/to/project-root")
        sys.exit(1)
    rebuild_index(sys.argv[1])
