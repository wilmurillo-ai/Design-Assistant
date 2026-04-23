#!/usr/bin/env python3
# FILE_META
# INPUT:  .trajectory.json files + API key
# OUTPUT: server submission confirmation + manifest.json updates
# POS:    skill scripts — Step 4, depends on lib/auth.py and lib/paths.py
# MISSION: Upload converted trajectories to the ClawTraces collection server.
"""Submit converted trajectory files to the ClawTraces collection server.

Usage:
    python submit.py [--output-dir PATH] [--count-only]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

sys.path.insert(0, os.path.dirname(__file__))

from lib.auth import get_server_url, get_stored_key, handle_401, get_ssl_context, _format_connection_error

from lib.paths import get_default_output_dir

DEFAULT_OUTPUT_DIR = get_default_output_dir()
MANIFEST_FILENAME = "manifest.json"


def load_manifest(output_dir: str) -> dict:
    """Load the submission manifest."""
    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"submitted": {}, "rejected": {}}


def save_manifest(output_dir: str, manifest: dict):
    """Save the submission manifest (atomic write via tmp+rename)."""
    manifest_path = os.path.join(output_dir, MANIFEST_FILENAME)
    tmp_path = manifest_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, manifest_path)


def _fix_mojibake(text: str) -> str:
    """Fix GBK→Latin-1 mojibake in a single string.

    On Chinese Windows, text may be double-encoded: GBK bytes interpreted as
    Latin-1 (each byte 0x80-0xFF mapped to the same Unicode code point), then
    saved as UTF-8. This reverses that: encode as Latin-1 to recover the raw
    GBK bytes, then decode as GBK to get correct Chinese.
    """
    try:
        raw = text.encode("latin-1")
        return raw.decode("gbk")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def _fix_mojibake_recursive(obj):
    """Recursively fix mojibake in all string values of a JSON object."""
    if isinstance(obj, str):
        return _fix_mojibake(obj)
    if isinstance(obj, list):
        return [_fix_mojibake_recursive(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _fix_mojibake_recursive(v) for k, v in obj.items()}
    return obj


def _repair_mojibake(file_path: str) -> bool:
    """Detect and fix mojibake in a JSON file. Returns True if file was repaired."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Quick check: if no chars in 0x80-0xFF range, no mojibake possible
    if not any("\x80" <= ch <= "\xff" for ch in content):
        return False

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return False

    fixed = _fix_mojibake_recursive(data)
    fixed_content = json.dumps(fixed, ensure_ascii=False, indent=2)

    if fixed_content == json.dumps(data, ensure_ascii=False, indent=2):
        return False

    # Re-save the repaired file
    tmp_path = file_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)
    os.replace(tmp_path, file_path)
    return True


def _load_stats(trajectory_path: str) -> str | None:
    """Load the stats JSON file that corresponds to a trajectory file."""
    stats_path = trajectory_path.replace(".trajectory.json", ".stats.json").replace(".openai.json", ".stats.json")
    if not os.path.isfile(stats_path):
        return None
    with open(stats_path, "r", encoding="utf-8") as f:
        return f.read()


def upload_file(server_url: str, secret_key: str, file_path: str, force: bool = False) -> dict:
    """Upload a trajectory file to the server, with optional stats.

    Args:
        force: If True, overwrite existing submission with same session_id.
    """
    filename = os.path.basename(file_path)

    # Repair mojibake before upload (trajectory + stats)
    repaired = []
    if _repair_mojibake(file_path):
        repaired.append(os.path.basename(file_path))
    stats_path = file_path.replace(".trajectory.json", ".stats.json").replace(".openai.json", ".stats.json")
    if os.path.isfile(stats_path) and _repair_mojibake(stats_path):
        repaired.append(os.path.basename(stats_path))
    if repaired:
        print(f"  [encoding] Fixed mojibake in: {', '.join(repaired)}")

    with open(file_path, "rb") as f:
        file_data = f.read()

    stats_json = _load_stats(file_path)

    boundary = "----ClawTracesBoundary9876543210"
    parts = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/json\r\n"
        f"\r\n"
    ).encode("utf-8") + file_data + b"\r\n"

    if stats_json:
        parts += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="stats"\r\n'
            f"Content-Type: application/json\r\n"
            f"\r\n"
            f"{stats_json}\r\n"
        ).encode("utf-8")

    if force:
        parts += (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="force"\r\n'
            f"\r\n"
            f"true\r\n"
        ).encode("utf-8")

    body = parts + f"--{boundary}--\r\n".encode("utf-8")

    url = f"{server_url}/upload"
    req = Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Secret-Key": secret_key,
            "User-Agent": "ClawTraces/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30, context=get_ssl_context()) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 401:
            handle_401()
            return {"error": "unauthorized"}
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(error_body)
            if "error" not in parsed:
                parsed["error"] = f"HTTP {e.code}"
            return parsed
        except (json.JSONDecodeError, ValueError):
            return {"error": f"HTTP {e.code}", "detail": error_body}
    except URLError as e:
        return {"error": _format_connection_error(e.reason)}


def query_count(server_url: str, secret_key: str) -> dict:
    """Query the server for submission count."""
    url = f"{server_url}/count"
    req = Request(url, headers={"X-Secret-Key": secret_key, "User-Agent": "ClawTraces/1.0"}, method="GET")

    try:
        with urlopen(req, timeout=10, context=get_ssl_context()) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 401:
            handle_401()
            return {"error": "unauthorized"}
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(error_body)
            if "error" not in parsed:
                parsed["error"] = f"HTTP {e.code}"
            return parsed
        except (json.JSONDecodeError, ValueError):
            return {"error": f"HTTP {e.code}", "detail": error_body}
    except URLError as e:
        return {"error": _format_connection_error(e.reason)}


def submit_all(
    output_dir: str,
    server_url: str,
    secret_key: str,
    filenames: list[str] | None = None,
) -> dict:
    """Submit trajectory files.

    Args:
        filenames: If provided, only upload these specific filenames (still
            skipping ones already recorded in manifest). If None, scan the
            whole output_dir — this legacy behavior is only used by the
            standalone `python submit.py` entry point.

    Returns summary dict with success_count, error_count, total.
    """
    manifest = load_manifest(output_dir)
    submitted = manifest.get("submitted", {})

    if filenames is None:
        candidate_files = [
            f for f in os.listdir(output_dir)
            if f.endswith(".trajectory.json")
        ]
    else:
        candidate_files = [
            f for f in filenames
            if os.path.isfile(os.path.join(output_dir, f))
        ]

    new_files = [f for f in candidate_files if f not in submitted]

    if not new_files:
        count_result = query_count(server_url, secret_key)
        return {
            "success_count": 0,
            "error_count": 0,
            "new_files": 0,
            "server_total": count_result.get("count", "unknown"),
            "workspace_threshold": count_result.get("workspace_threshold", 5),
            "workspace_submitted": count_result.get("workspace_submitted", False),
            "workspace_force_required": count_result.get("workspace_force_required", False),
        }

    success_count = 0
    error_count = 0
    auth_failed = False

    for filename in new_files:
        file_path = os.path.join(output_dir, filename)

        print(f"  Uploading: {filename}...", end=" ", flush=True)

        result = upload_file(server_url, secret_key, file_path)

        if result.get("error") == "unauthorized":
            print("FAILED (unauthorized)")
            error_count += 1
            auth_failed = True
            break
        elif result.get("error") == "account_disabled":
            msg = result.get("message", "账号已被禁用")
            print(f"FAILED ({msg})")
            error_count += 1
            auth_failed = True
            break
        elif result.get("error") == "workspace_required":
            msg = result.get("message", "需要先提交 Workspace 配置才能继续")
            print(f"STOPPED ({msg})")
            error_count += 1
            break
        elif result.get("error") in ("daily_limit_exceeded", "total_limit_exceeded"):
            msg = result.get("message", result["error"])
            print(f"STOPPED ({msg})")
            error_count += 1
            break
        elif result.get("error") == "duplicate":
            # Already on server — record in manifest to avoid retrying
            print("OK (already submitted)")
            success_count += 1
            submitted[filename] = {
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "server_response": "duplicate",
            }
            manifest["submitted"] = submitted
            save_manifest(output_dir, manifest)
        elif "error" in result:
            print(f"FAILED ({result.get('message') or result['error']})")
            error_count += 1
        else:
            print("OK")
            success_count += 1
            submitted[filename] = {
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "server_response": result.get("status", "ok"),
            }
            manifest["submitted"] = submitted
            save_manifest(output_dir, manifest)

    # Only query server count if auth is still valid
    server_total: int | str = "unknown"
    workspace_threshold = 5
    workspace_submitted = False
    daily_count: int | str = "unknown"
    daily_submission_limit = 0
    total_submission_limit = 0
    workspace_force_required = False
    if not auth_failed:
        count_result = query_count(server_url, secret_key)
        server_total = count_result.get("count", "unknown")
        workspace_threshold = count_result.get("workspace_threshold", 5)
        workspace_submitted = count_result.get("workspace_submitted", False)
        workspace_force_required = count_result.get("workspace_force_required", False)
        daily_count = count_result.get("daily_count", "unknown")
        daily_submission_limit = count_result.get("daily_submission_limit", 0)
        total_submission_limit = count_result.get("total_submission_limit", 0)

    return {
        "success_count": success_count,
        "error_count": error_count,
        "new_files": len(new_files),
        "server_total": server_total,
        "workspace_threshold": workspace_threshold,
        "workspace_submitted": workspace_submitted,
        "workspace_force_required": workspace_force_required,
        "daily_count": daily_count,
        "daily_submission_limit": daily_submission_limit,
        "total_submission_limit": total_submission_limit,
    }


def resubmit_one(session_id: str, output_dir: str, server_url: str, secret_key: str) -> dict:
    """Force-resubmit a single session by session_id.

    Finds the trajectory file in output_dir, uploads with force=True to overwrite
    the existing server record.

    Returns dict with status info.
    """
    # Find trajectory file matching this session_id
    target_filename = f"{session_id}.trajectory.json"
    file_path = os.path.join(output_dir, target_filename)

    if not os.path.isfile(file_path):
        return {"error": f"trajectory file not found: {target_filename}"}

    print(f"  Re-uploading: {target_filename} (force)...", end=" ", flush=True)
    result = upload_file(server_url, secret_key, file_path, force=True)

    if result.get("error") == "unauthorized":
        print("FAILED (unauthorized)")
        return {"error": "unauthorized"}
    elif "error" in result:
        print(f"FAILED ({result['error']})")
        return result
    else:
        updated = result.get("updated", False)
        print("OK (overwritten)" if updated else "OK (new)")

        # Update manifest
        manifest = load_manifest(output_dir)
        submitted = manifest.get("submitted", {})
        submitted[target_filename] = {
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "server_response": "updated" if updated else "ok",
        }
        manifest["submitted"] = submitted
        save_manifest(output_dir, manifest)

        return {
            "status": "ok",
            "updated": updated,
            "total_count": result.get("total_count", "unknown"),
        }


def main():
    parser = argparse.ArgumentParser(description="Submit trajectory files to collection server")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, help="Directory with .trajectory.json files")
    parser.add_argument("--count-only", action="store_true", help="Only query submission count")
    parser.add_argument("--resubmit", metavar="SESSION_ID", help="Force-resubmit a specific session by ID")
    args = parser.parse_args()

    key = get_stored_key()
    if not key:
        print("Not authenticated. Please run /clawtraces to authenticate first.", file=sys.stderr)
        sys.exit(1)

    server_url = get_server_url()

    if args.count_only:
        result = query_count(server_url, key)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"Total submitted: {result.get('count', 0)}")
        return

    if args.resubmit:
        result = resubmit_one(args.resubmit, args.output_dir, server_url, key)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"Resubmit done. Your total submissions: {result.get('total_count', 'unknown')}")
        return

    result = submit_all(args.output_dir, server_url, key)
    print(f"\nDone: {result['success_count']} uploaded, {result['error_count']} failed")
    print(f"Your total submissions: {result['server_total']}")

    daily_limit = result.get("daily_submission_limit", 0)
    total_limit = result.get("total_submission_limit", 0)
    if daily_limit > 0:
        print(f"Daily quota: {result.get('daily_count', '?')}/{daily_limit}")
    if total_limit > 0:
        print(f"Total quota: {result['server_total']}/{total_limit}")


if __name__ == "__main__":
    main()
