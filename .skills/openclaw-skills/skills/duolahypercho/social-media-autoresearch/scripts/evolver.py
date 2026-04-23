#!/usr/bin/env python3
"""evolver.py — Update SOUL.md champion block after KEEP verdict.

Usage:
  python3 evolver.py --version 3 --change "storytelling hooks" --metric-delta "+18%"
  python3 evolver.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent.resolve()
SOUL_FILE = Path("SOUL.md")  # agent's SOUL.md in their workspace


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


CHAMPION_TEMPLATE = """<!-- AUTO:CHAMPION START v{version} -->
## Content Strategy (Champion v{version})
**Primary Metric:** {metric}
**Baseline:** {baseline}
**Engagement Baseline:** {engagement}
**Strategy:**
{strategy_lines}
**Changelog:**
{changelog}
<!-- AUTO:CHAMPION END -->"""


def find_champion_block(text: str) -> tuple[int, int]:
    """Find start and end of AUTO:CHAMPION block. Returns (start, end) line indices."""
    lines = text.splitlines()
    start = end = -1
    for i, line in enumerate(lines):
        if "<!-- AUTO:CHAMPION START" in line:
            start = i
        if start >= 0 and "<!-- AUTO:CHAMPION END -->" in line:
            end = i
            break
    return start, end


def get_current_version(text: str) -> int:
    m = re.search(r"AUTO:CHAMPION START v(\d+)", text)
    return int(m.group(1)) if m else 1


def update_champion(
    version: int,
    change: str,
    metric: str,
    baseline: str,
    engagement: str,
    experiment_id: str,
    metric_delta: str,
) -> None:
    """Update the AUTO:CHAMPION block in SOUL.md."""

    if not SOUL_FILE.exists():
        print(f"ERROR: SOUL.md not found at {SOUL_FILE}", file=sys.stderr)
        sys.exit(1)

    text = SOUL_FILE.read_text()
    start, end = find_champion_block(text)

    new_version = version + 1
    changelog_entry = f"- v{new_version}: {change} ({metric_delta}, {experiment_id}) ← KEEP"

    if start >= 0 and end > start:
        # Replace existing block
        old_block = "\n".join(text.splitlines()[start:end+1])
        # Get old strategy section
        old_lines = text.splitlines()[start:end]
        strategy_lines = []
        in_strategy = False
        for line in old_lines:
            if "**Strategy:**" in line:
                in_strategy = True
                strategy_lines.append(line)
            elif in_strategy and line.strip().startswith("**") and "Strategy" not in line:
                in_strategy = False
            elif in_strategy:
                strategy_lines.append(line)

        # Get changelog
        changelog_lines = []
        in_changelog = False
        for line in old_lines:
            if "**Changelog:**" in line:
                in_changelog = True
                changelog_lines.append(line)
            elif in_changelog and line.strip().startswith("**"):
                in_changelog = False
            elif in_changelog:
                changelog_lines.append(line)

        new_block_lines = [
            f"<!-- AUTO:CHAMPION START v{new_version} -->",
            f"## Content Strategy (Champion v{new_version})",
            f"**Primary Metric:** {metric}",
            f"**Baseline:** {baseline}",
            f"**Engagement Baseline:** {engagement}",
            "",
        ]
        for sl in strategy_lines[1:]:  # skip the header
            new_block_lines.append(sl)

        new_block_lines.extend(["", "**Changelog:**"])
        for cl in changelog_lines[1:]:  # skip the header
            new_block_lines.append(cl)
        new_block_lines.append(f"- v{new_version}: {change} ({metric_delta}, {experiment_id}) ← KEEP")
        new_block_lines.append("<!-- AUTO:CHAMPION END -->")

        new_block = "\n".join(new_block_lines)
        new_text = text.replace(old_block, new_block)

    else:
        # No existing block — create one
        new_block = CHAMPION_TEMPLATE.format(
            version=new_version,
            metric=metric,
            baseline=baseline,
            engagement=engagement,
            strategy_lines="",
            changelog=f"- v{new_version}: {change} ({metric_delta}, {experiment_id}) ← KEEP",
        )
        new_text = text + "\n\n" + new_block

    SOUL_FILE.write_text(new_text)
    print(f"✅ Updated SOUL.md — Champion v{new_version}")
    print(f"   Change: {change}")
    print(f"   File: {SOUL_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evolve SOUL.md champion after KEEP verdict")
    parser.add_argument("--version", type=int, help="Current champion version")
    parser.add_argument("--change",  required=True, help="What changed (e.g. 'storytelling hooks')")
    parser.add_argument("--metric-delta", default="", help="Metric change (e.g. '+18%')")
    parser.add_argument("--experiment-id", default="EXP-XXX", help="Experiment ID")
    parser.add_argument("--metric", default="views_48h", help="Primary metric name")
    parser.add_argument("--baseline", default="TBD", help="New baseline value")
    parser.add_argument("--engagement", default="TBD", help="Engagement baseline")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(f"[DRY RUN] Would update champion to v{(args.version or 1)+1}")
        print(f"   Change: {args.change}")
        return

    if not SOUL_FILE.exists():
        print(f"ERROR: SOUL.md not found at {SOUL_FILE}", file=sys.stderr)
        print("   Run this from the agent's workspace directory.", file=sys.stderr)
        sys.exit(1)

    current_v = args.version
    if not current_v:
        text = SOUL_FILE.read_text()
        current_v = get_current_version(text)

    update_champion(
        version=current_v,
        change=args.change,
        metric=args.metric,
        baseline=args.baseline,
        engagement=args.engagement,
        experiment_id=args.experiment_id,
        metric_delta=args.metric_delta,
    )


if __name__ == "__main__":
    main()
