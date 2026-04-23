#!/usr/bin/env python3
"""
inbox / get-list 脚本
用途：获取收件箱汇报列表
"""
import argparse
import sys
import os
import json
import requests
import warnings

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key

API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/report/record/inbox"

def call_api(app_key, page_index=1, page_size=10, body_json=""):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    if body_json:
        payload = json.loads(body_json)
    else:
        payload = {
            "pageIndex": page_index,
            "pageSize": page_size
        }
    
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            verify=False,
            allow_redirects=True,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        raise Exception(f"请求失败: {exc}")


def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-index", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=10)
    parser.add_argument("--body-json", default="")
    args = parser.parse_args()
    result = call_api(
        app_key,
        page_index=args.page_index,
        page_size=args.page_size,
        body_json=args.body_json,
    )
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
