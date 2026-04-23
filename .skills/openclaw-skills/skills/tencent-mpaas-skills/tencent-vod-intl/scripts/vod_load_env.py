#!/usr/bin/env python3
"""
vod_load_env.py — Tencent Cloud VOD Skill Environment Variable Auto-Loader

Features:
  Scans the following files, and if any of the specified environment variable
  KEYs are found in a file, all KEY=VALUE lines from that file are loaded into
  the current process's os.environ (without overwriting existing values):
    /etc/environment
    /etc/profile
    ~/.bashrc
    ~/.profile
    ~/.bash_profile
    ~/.env

  Target variables (if any one of these exists in a file, that file will be loaded):
    TENCENTCLOUD_SECRET_ID       (required)
    TENCENTCLOUD_SECRET_KEY      (required)
    TENCENTCLOUD_VOD_AIGC_TOKEN  (optional, dedicated to AIGC LLM Chat)
    TENCENTCLOUD_VOD_SUB_APP_ID  (optional, sub-application ID)

Usage (calling from other scripts):
    from vod_load_env import ensure_env_loaded
    ensure_env_loaded()
"""

import os
import re
import sys

# Target variables to detect
_TARGET_VARS = {
    "TENCENTCLOUD_SECRET_ID",
    "TENCENTCLOUD_SECRET_KEY",
    "TENCENTCLOUD_VOD_AIGC_TOKEN",
    "TENCENTCLOUD_VOD_SUB_APP_ID",
}

# Required variables (error if missing)
_REQUIRED_VARS = [
    "TENCENTCLOUD_SECRET_ID",
    "TENCENTCLOUD_SECRET_KEY",
]

# Optional variables (only needed in specific scenarios)
_OPTIONAL_VARS = {
    "TENCENTCLOUD_VOD_AIGC_TOKEN": "Dedicated to AIGC LLM Chat (vod_aigc_chat.py)",
    "TENCENTCLOUD_VOD_SUB_APP_ID": "Used for sub-application operations (can be overridden via --sub-app-id parameter)",
}

# List of candidate files to scan (ordered by priority)
_ENV_FILES = [
    "/etc/environment",
    "/etc/profile",
    os.path.expanduser("~/.bashrc"),
    os.path.expanduser("~/.profile"),
    os.path.expanduser("~/.bash_profile"),
    os.path.expanduser("~/.env"),
]

# Regex for KEY=VALUE lines (supports quoted values)
_KV_RE = re.compile(
    r"""^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(['"]?)(.*?)\2\s*$"""
)


def _parse_env_file(filepath: str) -> dict:
    """
    Parse a shell-style environment variable file and return a {key: value} dict.
    Supports:
      KEY=value
      export KEY=value
      KEY="value with spaces"
      KEY='value'
      # comment lines (ignored)
    """
    result = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                m = _KV_RE.match(line)
                if m:
                    key = m.group(1)
                    value = m.group(3)
                    result[key] = value
    except (OSError, IOError):
        pass
    return result


def _file_contains_target(parsed: dict) -> bool:
    """Check whether the parsed result contains at least one target variable."""
    return bool(_TARGET_VARS & set(parsed.keys()))


def load_env_files(verbose: bool = False) -> dict:
    """
    Scan all candidate files and load the contents of files containing target
    variables into os.environ. Existing environment variables will not be
    overwritten (setdefault semantics).

    Returns: dict of newly loaded variables {key: value}
    """
    newly_loaded = {}

    for filepath in _ENV_FILES:
        if not os.path.isfile(filepath):
            if verbose:
                print(f"[load_env] Skipping (not found): {filepath}", file=sys.stderr)
            continue

        parsed = _parse_env_file(filepath)

        if not _file_contains_target(parsed):
            if verbose:
                print(f"[load_env] Skipping (no target variables): {filepath}", file=sys.stderr)
            continue

        if verbose:
            print(f"[load_env] Loading file: {filepath}", file=sys.stderr)

        for key, value in parsed.items():
            if key not in os.environ:
                os.environ[key] = value
                newly_loaded[key] = value
                if verbose:
                    display = value[:4] + "****" if len(value) > 4 else "****"
                    print(f"[load_env]   Set {key}={display}", file=sys.stderr)
            else:
                if verbose:
                    print(f"[load_env]   Skipping (already exists): {key}", file=sys.stderr)

    return newly_loaded


def check_required_vars(required: list = None) -> list:
    """
    Check whether the required environment variables are set.
    Returns a list of missing variable names (empty list means all are set).
    """
    if required is None:
        required = _REQUIRED_VARS
    return [k for k in required if not os.environ.get(k)]


def _print_setup_hint(missing_vars: list) -> None:
    """Print detailed configuration guidance to the user when environment variable loading fails."""
    env_files_str = "\n".join(f"    • {f}" for f in _ENV_FILES)
    missing_str = "\n".join(f"    {k}=<your_value>" for k in missing_vars)
    hint = f"""
╔══════════════════════════════════════════════════════════════════╗
║            Tencent Cloud VOD Environment Variables Not Configured ║
╚══════════════════════════════════════════════════════════════════╝

The following environment variables are missing:
{missing_str}

Credentials can be obtained from the Tencent Cloud Console: https://console.cloud.tencent.com/cam/capi
VOD Console: https://console.cloud.tencent.com/vod

[Configuration] Please add the above variables to any of the following files,
then restart the conversation:
{env_files_str}

  Example (using ~/.profile):
    # Required (all scripts)
    export TENCENTCLOUD_SECRET_ID=<your SecretId>
    export TENCENTCLOUD_SECRET_KEY=<your SecretKey>

    # Optional (dedicated to AIGC LLM Chat)
    export TENCENTCLOUD_VOD_AIGC_TOKEN=<your AIGC Token>

    # Optional (sub-application ID, can also be specified via --sub-app-id)
    export TENCENTCLOUD_VOD_SUB_APP_ID=<your sub-application ID>

⚠️  Security Notice: Please configure credentials through a secure channel (e.g., by directly editing the config file).

After configuration, please restart the conversation.
"""
    print(hint, file=sys.stderr)


def ensure_env_loaded(
    required: list = None,
    verbose: bool = False,
) -> bool:
    """
    Ensure that the required environment variables are loaded.

    Execution flow:
      1. Check whether required variables are already in os.environ
      2. If any are missing, scan candidate files and load them
      3. Check again and return whether all are ready

    Parameters:
      required  — list of variables that must be present; defaults to checking SECRET_ID / SECRET_KEY
      verbose   — whether to print loading logs to stderr

    Returns: True if all required variables are ready, False if any are still missing
    """
    if required is None:
        required = _REQUIRED_VARS

    missing_before = check_required_vars(required)
    if not missing_before:
        return True

    if verbose:
        print(
            f"[load_env] Missing variables detected: {missing_before}, starting scan of environment variable files...",
            file=sys.stderr,
        )

    load_env_files(verbose=verbose)

    missing_after = check_required_vars(required)
    if missing_after:
        return False

    if verbose:
        print("[load_env] All required variables have been loaded.", file=sys.stderr)
    return True


# ─── When run standalone: diagnostic mode ──────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan system environment variable files and load Tencent Cloud VOD required variables (diagnostic mode)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed loading logs"
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only check current environment variable status, do not load"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulate execution, show operations that would be performed without actually loading environment variables"
    )
    args = parser.parse_args()

    if args.check_only:
        print("=== Tencent Cloud VOD Environment Variable Status ===\n")
        print("[Required Variables]")
        all_required_ok = True
        for var in _REQUIRED_VARS:
            val = os.environ.get(var, "")
            if val:
                display = val[:4] + "****" if len(val) > 4 else "****"
                status = f"✅ Set ({display})"
            else:
                status = "❌ Not set"
                all_required_ok = False
            print(f"  {var}: {status}")

        print("\n[Optional Variables]")
        for var, desc in _OPTIONAL_VARS.items():
            val = os.environ.get(var, "")
            if val:
                display = val[:4] + "****" if len(val) > 4 else "****"
                status = f"✅ Set ({display})"
            else:
                status = f"⚪ Not set ({desc})"
            print(f"  {var}: {status}")

        print()
        if all_required_ok:
            print("✅ All required variables are configured. VOD Skill is ready to use.")
            sys.exit(0)
        else:
            print("❌ Required variables are not fully configured. Please configure them as instructed and retry.")
            sys.exit(1)

    # Dry-run mode: only display operation summary
    if args.dry_run:
        print("=== Dry-run ===\n")
        print("Operation: Scan and load Tencent Cloud VOD environment variables")
        print("\nEnvironment variable files to be scanned:")
        for filepath in _ENV_FILES:
            print(f"  - {filepath}")

        print("\nEnvironment variables to be looked up:")
        for var in _REQUIRED_VARS:
            val = os.environ.get(var, "")
            if val:
                display = val[:4] + "****" if len(val) > 4 else "****"
                print(f"  - {var}: ✅ Set ({display})  [required]")
            else:
                print(f"  - {var}: ❌ Not set (will attempt to load)  [required]")
        for var in _OPTIONAL_VARS:
            val = os.environ.get(var, "")
            if val:
                display = val[:4] + "****" if len(val) > 4 else "****"
                print(f"  - {var}: ✅ Set ({display})  [optional]")
            else:
                print(f"  - {var}: ⚪ Not set  [optional]")

        print("\nNo environment variables will actually be loaded. Remove the --dry-run flag to perform the actual operation.")
        sys.exit(0)

    print("=== Scanning Environment Variable Files ===", flush=True)
    newly = load_env_files(verbose=True)
    sys.stderr.flush()

    print("\n=== Load Results ===")
    print("[Required Variables]")
    all_required_ok = True
    for var in _REQUIRED_VARS:
        val = os.environ.get(var, "")
        if val:
            display = val[:4] + "****" if len(val) > 4 else "****"
            status = f"✅ Set ({display})"
        else:
            status = "❌ Not set"
            all_required_ok = False
        print(f"  {var}: {status}")

    print("[Optional Variables]")
    for var, desc in _OPTIONAL_VARS.items():
        val = os.environ.get(var, "")
        if val:
            display = val[:4] + "****" if len(val) > 4 else "****"
            status = f"✅ Set ({display})"
        else:
            status = f"⚪ Not set ({desc})"
        print(f"  {var}: {status}")

    if newly:
        print(f"\n{len(newly)} new variable(s) loaded this time: {list(newly.keys())}")
    else:
        print("\nNo new variables loaded (all already set or no target variables found in files)")

    if not all_required_ok:
        _print_setup_hint([v for v in _REQUIRED_VARS if not os.environ.get(v)])
        sys.exit(1)
    else:
        print("\n✅ All required variables are configured. VOD Skill is ready to use.")