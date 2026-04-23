#!/usr/bin/env python3
"""
huiji / get-chat-from-share-id 脚本

用途：
  1) 接收 shareId
  2) 调用 getChatFromShareId 获取分享原文

使用方式：
  python3 get-chat-from-share-id.py <shareId>
  python3 get-chat-from-share-id.py --body '{"shareId":"xxx"}'

说明：
  - 本脚本不负责短链/长链解析。
  - 若用户提供 URL，需先在 Skill 层用 web_fetch 解析得到 shareId，再调用本脚本。

环境变量：
  XG_BIZ_API_KEY   — appKey（必须）
  XG_USER_TOKEN    — access-token（可选）
"""

import json
import os
import re
import sys
import time
from urllib.parse import parse_qs, urlparse
import requests
import warnings

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

def setup_utf8_stdio():
    """Best-effort UTF-8 stdio for Windows console display."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


setup_utf8_stdio()

API_URL = "https://sg-al-ai-voice-assistant.mediportal.com.cn/api/open-api/ai-huiji/meetingChat/getChatFromShareId"
DEFAULT_SHORT_LINK_BASE = "http://s.medihub.cn/p/"
MAX_RETRIES = 3
RETRY_DELAY = 1

# 常见 shareId 形态（UUID）
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def build_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    token = os.environ.get("XG_USER_TOKEN")
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if token:
        headers["access-token"] = token
    if app_key:
        headers["appKey"] = app_key
    if not token and not app_key:
        print(json.dumps({"error": "请至少设置 XG_USER_TOKEN 或 XG_BIZ_API_KEY"}, ensure_ascii=False))
        sys.exit(1)
    return headers


def call_api(body: dict) -> dict:
    headers = build_headers()
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                API_URL,
                json=body,
                headers=headers,
                verify=False,
                allow_redirects=True,
                timeout=60,
            )
            response.raise_for_status()
            return json.loads(response.content.decode("utf-8"))
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    print(json.dumps({"error": f"请求失败（重试{MAX_RETRIES}次）: {last_err}"}, ensure_ascii=False))
    sys.exit(1)


def extract_share_id_from_url(url: str) -> str:
    """从 URL 的 query 或 fragment 中提取 shareId。"""
    try:
        parsed = urlparse(url)
        # 1) 常规 query：...?shareId=xxx
        qs = parse_qs(parsed.query)
        share_id = (qs.get("shareId") or [""])[0].strip()
        if UUID_RE.match(share_id):
            return share_id

        # 2) hash 路由：...#/path?shareId=xxx
        #    先拿 fragment，再截取 ? 后的参数串
        frag = parsed.fragment or ""
        if "?" in frag:
            frag_qs = parse_qs(frag.split("?", 1)[1])
            share_id = (frag_qs.get("shareId") or [""])[0].strip()
            if UUID_RE.match(share_id):
                return share_id
    except Exception:
        pass
    return ""


def resolve_share_id(value: str) -> str:
    """
    支持三种输入：
    1) UUID shareId
    2) 短链 URL（例如 http://s.medihub.cn/p/128eeeOS）
    3) 短码（例如 128eeeOS）
    """
    raw = (value or "").strip()
    if not raw:
        return ""

    # 1) 已经是 UUID
    if UUID_RE.match(raw):
        return raw

    # 2) URL 里已直接包含 shareId
    if raw.startswith("http://") or raw.startswith("https://"):
        sid = extract_share_id_from_url(raw)
        if sid:
            return sid
        short_url = raw
    else:
        # 3) 当作短码，拼成短链 URL
        short_base = os.environ.get("XG_SHARE_SHORT_BASE", DEFAULT_SHORT_LINK_BASE).strip()
        if not short_base:
            short_base = DEFAULT_SHORT_LINK_BASE
        if not short_base.endswith("/"):
            short_base += "/"
        short_url = f"{short_base}{raw}"

    # 请求短链，手动读取重定向头（不自动跟随）
    try:
        resp = requests.get(short_url, allow_redirects=False, timeout=20, verify=False)
    except Exception:
        return ""

    location = (resp.headers.get("Location") or "").strip()
    if not location:
        return ""
    return extract_share_id_from_url(location)


def main():
    args = sys.argv[1:]
    raw_value = None

    if len(args) >= 2 and args[0] == "--body":
        body = json.loads(args[1])
        raw_value = body.get("shareId", "")
    elif len(args) >= 1:
        raw_value = args[0]
    else:
        print(
            json.dumps(
                {
                    "error": "用法: get-chat-from-share-id.py <shareId> | --body '{\"shareId\":\"...\"}'"
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    share_id = resolve_share_id(raw_value)
    if not share_id:
        print(
            json.dumps(
                {
                    "error": (
                        "无法从输入中提取 shareId。"
                        "请传入 shareId、短链 URL，或可解析到 shareId 的短码。"
                    )
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    # 仅提示，不阻断。某些环境可能不是 UUID。
    if not UUID_RE.match(share_id):
        pass

    result = call_api({"shareId": share_id})
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
