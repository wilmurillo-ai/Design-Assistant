#!/usr/bin/env python3
"""
file-service / upload-file 脚本
用途：上传本地文件并返回资源 ID
"""
import argparse
import json
import os
import sys
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


API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/cwork-file/uploadWholeFile"


def call_api(app_key: str, file_path: str):
    if not os.path.isfile(file_path):
        print(f"错误: 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)

    headers = {
        "appKey": app_key,
    }
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            response = requests.post(
                API_URL,
                files=files,
                headers=headers,
                verify=False,
                allow_redirects=True,
                timeout=120,
            )
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        raise Exception(f"请求失败: {exc}")



def main():
    parser = argparse.ArgumentParser(description="上传本地文件并返回资源 ID")
    parser.add_argument("file_path", nargs="?", default="", help="本地文件路径，兼容旧的位置参数用法")
    parser.add_argument("--file", dest="file_path_opt", default="", help="本地文件路径")
    args = parser.parse_args()
    file_path = args.file_path_opt or args.file_path
    if not file_path:
        parser.error("请提供文件路径作为参数")
    app_key = _resolve_app_key()
    result = call_api(app_key, file_path)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
