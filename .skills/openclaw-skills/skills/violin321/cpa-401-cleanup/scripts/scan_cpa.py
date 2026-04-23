#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

WHAM_USAGE_URL = "https://chatgpt.com/backend-api/wham/usage"
DEFAULT_USER_AGENT = "codex_cli_rs/0.76.0"


def get_arg_or_env(value, env_name):
    return value or os.environ.get(env_name, "")


def mgmt_headers(token, json_body=False):
    headers = {"Authorization": f"Bearer {token}"}
    if json_body:
        headers["Content-Type"] = "application/json"
    return headers


def fetch_json(url, headers, timeout=15, method="GET", body=None):
    req = urllib.request.Request(url, headers=headers, method=method)
    if body is not None:
        req.data = json.dumps(body).encode("utf-8")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", "ignore")
        return resp.status, json.loads(raw)


def compact_text(value, limit=300):
    text = str(value).replace("\n", " ").strip()
    return text[:limit]


def extract_name(item):
    return item.get("name") or item.get("label") or item.get("account") or item.get("email") or item.get("id")


def probe_one(base_url, token, item, timeout, user_agent):
    name = extract_name(item)
    payload = {"method": "GET", "url": WHAM_USAGE_URL, "headers": {"User-Agent": user_agent}, "name": name}
    url = f"{base_url.rstrip('/')}/v0/management/api-call"
    try:
        status, data = fetch_json(url, mgmt_headers(token, json_body=True), timeout=timeout, method="POST", body=payload)
        text = json.dumps(data, ensure_ascii=False)
        low = text.lower()
        is_401 = status == 401 or '401' in low or 'unauthorized' in low or 'invalid_grant' in low
        is_quota = any(x in low for x in ['limit_reached', 'quota', 'exhausted'])
        return {
            "name": name,
            "provider": item.get("provider", ""),
            "disabled": bool(item.get("disabled", False)),
            "probe_http_status": status,
            "is_invalid_401": bool(is_401),
            "is_quota_limited": bool(is_quota and not is_401),
            "probe_excerpt": compact_text(text),
            "source": item,
        }
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        low = body.lower()
        return {
            "name": name,
            "provider": item.get("provider", ""),
            "disabled": bool(item.get("disabled", False)),
            "probe_http_status": e.code,
            "is_invalid_401": bool(e.code == 401 or 'unauthorized' in low or 'invalid_grant' in low),
            "is_quota_limited": bool(('limit_reached' in low or 'quota' in low or 'exhausted' in low) and e.code != 401),
            "probe_excerpt": compact_text(body),
            "source": item,
        }
    except Exception as e:
        return {
            "name": name,
            "provider": item.get("provider", ""),
            "disabled": bool(item.get("disabled", False)),
            "probe_http_status": None,
            "is_invalid_401": False,
            "is_quota_limited": False,
            "probe_excerpt": compact_text(repr(e)),
            "source": item,
        }


def main():
    ap = argparse.ArgumentParser(description="Scan CPA auth inventory and export 401/quota lists")
    ap.add_argument("--base-url")
    ap.add_argument("--token")
    ap.add_argument("--target-type", default="codex")
    ap.add_argument("--provider", default="")
    ap.add_argument("--workers", type=int, default=30)
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    ap.add_argument("--out-dir", default="/tmp/cpa-scan")
    args = ap.parse_args()

    base_url = get_arg_or_env(args.base_url, "CPA_BASE_URL")
    token = get_arg_or_env(args.token, "CPA_TOKEN")
    if not base_url or not token:
        print("Missing --base-url/CPA_BASE_URL or --token/CPA_TOKEN", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    status, data = fetch_json(f"{base_url.rstrip('/')}/v0/management/auth-files", mgmt_headers(token), timeout=args.timeout)
    files = data.get("files", []) if isinstance(data, dict) else []
    filtered = []
    for item in files:
        item_type = str(item.get("type") or item.get("provider") or "")
        provider = str(item.get("provider") or "")
        if args.target_type and args.target_type not in item_type and args.target_type != provider:
            # preserve common CPA shape where provider=codex
            if str(item.get("provider") or "") != args.target_type and str(item.get("type") or "") != args.target_type:
                continue
        if args.provider and provider != args.provider:
            continue
        filtered.append(item)

    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as ex:
        futs = [ex.submit(probe_one, base_url, token, item, args.timeout, args.user_agent) for item in filtered]
        for fut in as_completed(futs):
            results.append(fut.result())

    invalid_401 = [r for r in results if r.get("is_invalid_401")]
    quota = [r for r in results if r.get("is_quota_limited")]
    summary = {
        "base_url": base_url,
        "total_files": len(files),
        "filtered_files": len(filtered),
        "invalid_401_count": len(invalid_401),
        "quota_count": len(quota),
        "out_dir": str(out_dir),
    }

    (out_dir / "cpa_inventory.json").write_text(json.dumps(files, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "cpa_401_accounts.json").write_text(json.dumps(invalid_401, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "cpa_quota_accounts.json").write_text(json.dumps(quota, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "scan_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
