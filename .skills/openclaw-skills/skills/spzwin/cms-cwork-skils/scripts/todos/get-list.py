#!/usr/bin/env python3
"""
todos / get-list 脚本
用途：获取待办事项列表
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

API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/todoTask/todoList"

def call_api(app_key, page_index=1, page_size=10, type_filter="", execution_result="", body_json=""):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    if body_json:
        payload = json.loads(body_json)
    else:
        payload = {
            "pageIndex": page_index,
            "pageSize": page_size
        }
        valid_types = {"plan", "sign", "lead", "feedback", "file_audit"}
        if type_filter and type_filter.lower() in valid_types:
            payload["type"] = type_filter.lower()
        if execution_result:
            payload["executionResult"] = execution_result
        
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
    parser.add_argument("--type", default="")
    parser.add_argument("--execution-result", default="")
    parser.add_argument("--body-json", default="")
    args = parser.parse_args()
    result = call_api(
        app_key,
        page_index=args.page_index,
        page_size=args.page_size,
        type_filter=args.type,
        execution_result=args.execution_result,
        body_json=args.body_json,
    )
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
