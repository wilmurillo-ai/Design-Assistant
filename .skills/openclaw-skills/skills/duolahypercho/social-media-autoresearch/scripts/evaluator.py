#!/usr/bin/env python3
"""evaluator.py — Evaluate experiment results and apply KEEP/MODIFY/KILL verdict.

Usage:
  python3 evaluator.py                    # Check and apply verdict on active experiment
  python3 evaluator.py --dry-run        # Show verdict without applying
  python3 evaluator.py --baseline 1200 # Override baseline for evaluation
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR    = Path(__file__).parent.parent.resolve()
DATA_DIR     = SKILL_DIR / "data"
EXP_DIR      = DATA_DIR / "experiments"
EXP_DIR.mkdir(parents=True, exist_ok=True)
ACTIVE_FILE  = EXP_DIR / "active.md"
ARCHIVE_DIR  = EXP_DIR / "archive"
ARCHIVE_DIR.mkdir(exist_ok=True)
ENG_DIR      = DATA_DIR / "engagement"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_active_md() -> str | None:
    if ACTIVE_FILE.exists():
        return ACTIVE_FILE.read_text()
    return None


def parse_frontmatter(text: str) -> dict:
    """Parse YAML-like frontmatter from markdown."""
    data = {}
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if in_fm and ":" in line:
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip()
    return data


def get_metric(post_ids: list[str], metric: str = "views") -> float | None:
    """Get average metric from engagement files for given post_ids."""
    if not post_ids:
        return None

    totals = {}
    counts = {}

    for f in ENG_DIR.glob("*.json"):
        try:
            records = json.loads(f.read_text())
        except Exception:
            continue
        for rec in records:
            pid = rec.get("post_id", "")
            if pid in post_ids:
                val = rec.get(metric, 0)
                if val and isinstance(val, (int, float)):
                    totals[pid] = totals.get(pid, 0) + val
                    counts[pid] = counts.get(pid, 0) + 1

    if not totals:
        return None

    avg = sum(totals.values()) / len(totals)
    return avg


def evaluate_experiment(
    baseline: float,
    threshold: float = 0.10,
) -> tuple[str, float]:
    """Evaluate active experiment against baseline.

    Returns: (verdict, improvement_pct)
    """
    text = read_active_md()
    if not text:
        return "NO_EXPERIMENT", 0.0

    fm = parse_frontmatter(text)
    status = fm.get("Status", "ACTIVE")

    if status not in ("ACTIVE", "EVALUATING"):
        return f"NOT_ACTIVE({status})", 0.0

    # Get evaluation date
    eval_date_str = fm.get("Evaluation Date", "")
    if eval_date_str:
        try:
            eval_date = datetime.strptime(eval_date_str, "%Y-%m-%d")
            if datetime.now() < eval_date:
                days_left = (eval_date - datetime.now()).days
                return f"TOO_EARLY({days_left}d_left)", 0.0
        except ValueError:
            pass

    # Extract post IDs from active.md
    post_ids = []
    for line in text.splitlines():
        if "post_id:" in line.lower() or "post_" in line:
            import re
            found = re.findall(r"post_[a-zA-Z0-9]+", line)
            post_ids.extend(found)

    # Get metric
    metric_avg = get_metric(post_ids)
    if metric_avg is None:
        return "NO_METRICS", 0.0

    improvement = (metric_avg - baseline) / baseline

    if improvement >= threshold:
        verdict = "KEEP"
    elif improvement >= -threshold:
        verdict = "MODIFY"
    else:
        verdict = "KILL"

    return verdict, improvement


def apply_verdict(verdict: str, improvement: float) -> None:
    """Archive the experiment with verdict and reset active.md."""
    text = read_active_md()
    if not text:
        return

    filename = f"EXP-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{verdict}.md"
    archive_path = ARCHIVE_DIR / filename
    verdict_content = text + f"\n\n## Verdict\n\n**Verdict:** {verdict}\n**Improvement:** {improvement:.1%}\n**Evaluated:** {now_iso()}\n"
    archive_path.write_text(verdict_content)
    ACTIVE_FILE.write_text("---\nStatus: ARCHIVED\n---\n")

    # Reset selector (mark all SELECTED back to DISCOVERED)
    videos_file = DATA_DIR / "videos.json"
    if videos_file.exists():
        data = json.loads(videos_file.read_text())
        for v in data.get("videos", []):
            if v.get("status") == "SELECTED":
                v["status"] = "DISCOVERED"
                v.setdefault("pipeline_log", []).append({
                    "step": "RESET",
                    "timestamp": now_iso(),
                    "note": f"Experiment {verdict}, reset to DISCOVERED",
                })
        videos_file.write_text(json.dumps(data, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate active experiment")
    parser.add_argument("--dry-run", action="store_true", help="Show verdict without applying")
    parser.add_argument("--baseline", type=float, help="Override baseline")
    parser.add_argument("--threshold", type=float, default=0.10, help="KEEP threshold (default: 0.10)")
    args = parser.parse_args()

    baseline = args.baseline if args.baseline else 1200

    verdict, improvement = evaluate_experiment(baseline, args.threshold)

    print(f"\n{'='*50}")
    print(f"EXPERIMENT EVALUATION")
    print(f"{'='*50}")
    print(f"Verdict:     {verdict}")
    print(f"Improvement: {improvement:.1%}")
    print(f"Baseline:    {baseline}")

    if args.dry_run:
        print("\n[DRY RUN — no changes applied]")
        return

    if verdict == "NO_EXPERIMENT":
        print("\nNo active experiment found.")
        return

    if verdict.startswith("TOO_EARLY"):
        return

    if verdict == "NO_METRICS":
        print("\n⚠️  No metrics collected yet. Wait for data.")
        return

    apply_verdict(verdict, improvement)
    print(f"\n✅ Verdict applied: {verdict}")
    print(f"   Archived to: experiments/archive/")


if __name__ == "__main__":
    main()
