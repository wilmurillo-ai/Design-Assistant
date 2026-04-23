#!/usr/bin/env python3
"""Run lightweight local evaluators for NBA_TR and print cloud smoke prompts."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PYCOMPILE_TARGETS = [
    ROOT / "NBA_TR" / "tools" / "nba_pulse_core.py",
    ROOT / "NBA_TR" / "tools" / "nba_pulse_router.py",
    ROOT / "NBA_TR" / "tools" / "nba_today_command.py",
    ROOT / "NBA_TR" / "tests" / "test_nba_tools.py",
    ROOT / "NBA_TR" / "tests" / "test_nba_pulse_router.py",
]

UNITTEST_MODULES = [
    "NBA_TR.tests.test_nba_tools",
    "NBA_TR.tests.test_nba_pulse_router",
]

SMOKE_PROMPTS = [
    "给我今天的 NBA 赛况，按上海时区",
    "给我明天的 NBA 赛况，按上海时区",
    "今天比赛谁得分最高，按上海时区",
    "活塞vs森林狼前瞻",
    "给我今天湖人的比赛走势，按上海时区",
    "复盘今天黄蜂的比赛，按上海时区",
    "明天活塞伤病报告",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run lightweight local verification for NBA_TR.")
    parser.add_argument("--skip-pycompile", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    return parser.parse_args(argv)


def run_step(title: str, command: list[str]) -> None:
    print(f"\n== {title} ==")
    print("$ " + " ".join(command))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        raise SystemExit(result.returncode)
    if result.stderr:
        print(result.stderr.rstrip())


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.skip_pycompile:
        run_step(
            "py_compile",
            [sys.executable, "-m", "py_compile", *[str(path) for path in PYCOMPILE_TARGETS]],
        )
    if not args.skip_tests:
        run_step(
            "unittest",
            [sys.executable, "-m", "unittest", *UNITTEST_MODULES],
        )

    print("\n== Recommended OpenClaw Smoke Prompts ==")
    for prompt in SMOKE_PROMPTS:
        print(f"- {prompt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
