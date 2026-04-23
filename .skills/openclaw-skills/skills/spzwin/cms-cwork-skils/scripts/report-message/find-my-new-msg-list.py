#!/usr/bin/env python3
"""
report-message / find-my-new-msg-list 脚本
用途：获取当前用户的新消息列表
"""
import argparse
import json
import os
import sys
import requests
import warnings

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/open-platform/report/findMyNewMsgList"
DEFAULT_CLIENT_LIMIT = 200
MAX_CLIENT_LIMIT = 500


def _resolve_app_key() -> str:
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        return ""
    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)
    return app_key


def call_api(app_key: str, msg_type):
    params = {}
    if msg_type is not None:
        params["msgType"] = msg_type
    
    headers = {"appKey": app_key}
    
    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            verify=False,
            allow_redirects=True,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        raise Exception(f"请求失败: {exc}")



def _resolve_client_limit(client_limit):
    if client_limit is None:
        return DEFAULT_CLIENT_LIMIT
    return min(client_limit, MAX_CLIENT_LIMIT)


def _apply_client_limit(result, client_limit):
    effective_limit = _resolve_client_limit(client_limit)
    data = result.get("data")
    if not isinstance(data, dict):
        return result
    msg_list = data.get("msgList")
    if not isinstance(msg_list, list):
        return result
    data["serverReturnedSize"] = len(msg_list)
    data["msgList"] = msg_list[:effective_limit]
    data["clientLimit"] = effective_limit
    data["clientReturnedSize"] = len(data["msgList"])
    data["defaultClientLimit"] = DEFAULT_CLIENT_LIMIT
    data["maxClientLimit"] = MAX_CLIENT_LIMIT
    if client_limit is not None:
        data["requestedClientLimit"] = client_limit
    return result


def _emit_result(result, output_file):
    text = json.dumps(result, ensure_ascii=False)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as handle:
            handle.write(text)
    print(text)


def main():
    app_key = _resolve_app_key()
    parser = argparse.ArgumentParser()
    parser.add_argument("--msg-type", type=int)
    parser.add_argument("--client-limit", type=int)
    parser.add_argument("--output-file", default="")
    args = parser.parse_args()
    result = call_api(app_key, args.msg_type)
    result = _apply_client_limit(result, args.client_limit)
    _emit_result(result, args.output_file)


if __name__ == "__main__":
    main()
