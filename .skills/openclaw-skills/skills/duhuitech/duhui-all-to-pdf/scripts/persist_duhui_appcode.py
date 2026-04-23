#!/usr/bin/env python3
"""Persist DUHUI_DOC_TO_PDF_APPCODE into a shell startup file."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from pathlib import Path

APP_CODE_ENV = "DUHUI_DOC_TO_PDF_APPCODE"
MARKET_URL = "https://market.aliyun.com/detail/cmapi00044564"
BEGIN_MARKER = "# >>> duhui-all-to-pdf >>>"
END_MARKER = "# <<< duhui-all-to-pdf <<<"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Persist Duhui AppCode into a shell startup file.",
    )
    parser.add_argument(
        "appcode",
        nargs="?",
        help=f"AppCode to persist. Defaults to ${APP_CODE_ENV} when omitted.",
    )
    parser.add_argument(
        "--shell-file",
        help="Shell startup file to update. Defaults to a file inferred from $SHELL.",
    )
    return parser.parse_args(argv)


def emit_json(payload: dict[str, str]) -> None:
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def resolve_appcode(raw_appcode: str | None) -> str:
    appcode = raw_appcode or os.environ.get(APP_CODE_ENV, "")
    appcode = appcode.strip()
    if not appcode:
        raise ValueError(
            f"AppCode is required. Get it from Alibaba Cloud Marketplace: {MARKET_URL}"
        )
    if "\n" in appcode or "\r" in appcode:
        raise ValueError("AppCode cannot contain line breaks")
    return appcode


def default_shell_file() -> Path:
    home = Path.home()
    shell_name = Path(os.environ.get("SHELL", "")).name

    if shell_name == "zsh":
        return home / ".zshrc"
    if shell_name == "bash":
        bash_profile = home / ".bash_profile"
        if bash_profile.exists():
            return bash_profile
        return home / ".bashrc"
    return home / ".profile"


def resolve_shell_file(raw_shell_file: str | None) -> Path:
    if raw_shell_file:
        return Path(raw_shell_file).expanduser().resolve()
    return default_shell_file()


def build_env_block(appcode: str) -> str:
    quoted_appcode = shlex.quote(appcode)
    return (
        f"{BEGIN_MARKER}\n"
        f"export {APP_CODE_ENV}={quoted_appcode}\n"
        f"{END_MARKER}\n"
    )


def upsert_env_block(shell_file: Path, block: str) -> None:
    existing = ""
    if shell_file.exists():
        existing = shell_file.read_text(encoding="utf-8")

    marker_pattern = re.compile(
        rf"{re.escape(BEGIN_MARKER)}\n.*?\n{re.escape(END_MARKER)}\n?",
        re.DOTALL,
    )
    export_pattern = re.compile(
        rf"(?m)^[ \t]*export[ \t]+{re.escape(APP_CODE_ENV)}=.*(?:\n)?"
    )

    if marker_pattern.search(existing):
        updated = marker_pattern.sub(block, existing, count=1)
    elif export_pattern.search(existing):
        updated = export_pattern.sub(block, existing, count=1)
    else:
        updated = existing
        if updated and not updated.endswith("\n"):
            updated += "\n"
        if updated:
            updated += "\n"
        updated += block

    shell_file.parent.mkdir(parents=True, exist_ok=True)
    shell_file.write_text(updated, encoding="utf-8")


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        appcode = resolve_appcode(args.appcode)
        shell_file = resolve_shell_file(args.shell_file)
        upsert_env_block(shell_file, build_env_block(appcode))
        emit_json(
            {
                "status": "success",
                "env_var": APP_CODE_ENV,
                "shell_file": str(shell_file),
                "source_command": f"source {shlex.quote(str(shell_file))}",
            }
        )
        return 0
    except (OSError, ValueError) as exc:
        emit_json(
            {
                "status": "error",
                "reason": str(exc),
                "env_var": APP_CODE_ENV,
                "market_url": MARKET_URL,
            }
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
