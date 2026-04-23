#!/usr/bin/env python3
"""Standalone client for ClawHub skill APIs.

Usage examples:
  python skill_client.py send-code --phone 13800138000
  python skill_client.py login --phone 13800138000 --verify-code 123456
  python skill_client.py message --user-id u_xxx --session-id s_xxx --html '<p>你好</p>'
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


def _load_env_file(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue
            key, value = raw.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _post_json(url: str, payload: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url=url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": {"status": e.code, "body": body}}
    except urllib.error.URLError as e:
        return {"error": {"status": "NETWORK", "body": str(e)}}


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print(f"[ERROR] Missing required env: {name}")
        sys.exit(1)
    return value


def cmd_send_code(args: argparse.Namespace) -> None:
    site_base_url = _require_env("SITE_BASE_URL").rstrip("/")
    url = f"{site_base_url}/chainlit/send-verification-code"
    result = _post_json(url, {"phone": args.phone})
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_login(args: argparse.Namespace) -> None:
    api_base_url = _require_env("API_BASE_URL").rstrip("/")
    token = _require_env("CLAWHUB_SKILL_TOKEN")
    payload: Dict[str, Any] = {
        "phone": args.phone,
        "verify_code": args.verify_code,
    }
    if args.session_id:
        payload["session_id"] = args.session_id

    url = f"{api_base_url}/session/login"
    result = _post_json(url, payload, token=token)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_message(args: argparse.Namespace) -> None:
    api_base_url = _require_env("API_BASE_URL").rstrip("/")
    token = _require_env("CLAWHUB_SKILL_TOKEN")
    payload: Dict[str, Any] = {
        "user_id": args.user_id,
        "session_id": args.session_id,
        "html_payload": args.html,
        "stream": args.stream,
    }
    if args.trace_id:
        payload["metadata"] = {"trace_id": args.trace_id, "source": "clawhub_client"}

    url = f"{api_base_url}/session/message"
    result = _post_json(url, payload, token=token)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Standalone client for ClawHub skill")
    parser.add_argument("--env", default=".env", help="Path to env file, default: .env")

    sub = parser.add_subparsers(dest="command", required=True)

    p_send = sub.add_parser("send-code", help="Send verification code")
    p_send.add_argument("--phone", required=True, help="Phone number, e.g. 13800138000")
    p_send.set_defaults(func=cmd_send_code)

    p_login = sub.add_parser("login", help="Login and create session")
    p_login.add_argument("--phone", required=True)
    p_login.add_argument("--verify-code", required=True)
    p_login.add_argument("--session-id", default="")
    p_login.set_defaults(func=cmd_login)

    p_msg = sub.add_parser("message", help="Send HTML message")
    p_msg.add_argument("--user-id", required=True)
    p_msg.add_argument("--session-id", required=True)
    p_msg.add_argument("--html", required=True, help="HTML payload")
    p_msg.add_argument("--stream", action="store_true", help="Enable stream mode")
    p_msg.add_argument("--trace-id", default="")
    p_msg.set_defaults(func=cmd_message)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    _load_env_file(args.env)
    args.func(args)


if __name__ == "__main__":
    main()
