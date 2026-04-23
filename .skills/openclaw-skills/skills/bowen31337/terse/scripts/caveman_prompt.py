#!/usr/bin/env python3
"""
caveman_prompt.py — Generate caveman-mode prefixed prompts for sub-agents.

Usage:
    uv run python caveman_prompt.py --level full "explain why this fails"
    uv run python caveman_prompt.py --level lite "summarize this PR"
    uv run python caveman_prompt.py "quick question"  # defaults to full

Levels: lite | full (default) | ultra
"""

import argparse
import sys

PREFIXES = {
    "lite": (
        "Be concise. Skip filler phrases, pleasantries, and unnecessary hedging. "
        "Keep technical terms and code verbatim."
    ),
    "full": (
        "CAVEMAN MODE: Omit articles, filler, pleasantries. Use fragments. "
        "Steps as bare imperatives. Keep code/errors verbatim. No apologies. No \"I\". Just signal."
    ),
    "ultra": (
        "ULTRA CAVEMAN: Max compress. Drop ALL non-essential words. Labels only. "
        "No sentences. Keep code verbatim."
    ),
}


def build_prompt(task: str, level: str = "full") -> str:
    prefix = PREFIXES.get(level, PREFIXES["full"])
    return f"{prefix}\n\n{task}"


def main():
    parser = argparse.ArgumentParser(description="Generate caveman-mode prompt prefix")
    parser.add_argument("task", nargs="?", help="Task text (or pipe via stdin)")
    parser.add_argument(
        "--level",
        choices=["lite", "full", "ultra"],
        default="full",
        help="Compression level (default: full)",
    )
    parser.add_argument(
        "--prefix-only",
        action="store_true",
        help="Output only the prefix, not the full prompt",
    )
    args = parser.parse_args()

    # Get task from arg or stdin
    if args.task:
        task = args.task
    elif not sys.stdin.isatty():
        task = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    if args.prefix_only:
        print(PREFIXES.get(args.level, PREFIXES["full"]))
    else:
        print(build_prompt(task, args.level))


if __name__ == "__main__":
    main()
