#!/usr/bin/env python3
"""
user-search / search-emp 脚本

用途：根据姓名模糊搜索企业内部员工

使用方式：
 python3 scripts/user-search/search-emp.py "张三"

环境变量：
 XG_USER_TOKEN — access-token（必须）
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl

# 接口完整 URL
API_URL = "https://cwork-web.mediportal.com.cn/user/search/emp"


def call_api(token: str, name: str) -> dict:
    """调用搜索接口，返回原始 JSON 响应"""
    headers = {
        "access-token": token,
        "Content-Type": "application/json",
    }

    # Query 参数拼接到 URL
    url = f"{API_URL}?name={urllib.parse.quote(name)}"

    req = urllib.request.Request(url, headers=headers, method="GET")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    token = os.environ.get("XG_USER_TOKEN")

    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)

    # 从命令行参数获取搜索关键词
    name = sys.argv[1] if len(sys.argv) > 1 else ""

    if not name:
        print("错误: 请提供搜索姓名作为参数", file=sys.stderr)
        sys.exit(1)

    # 1. 调用接口，获取原始 JSON
    result = call_api(token, name)

    # 2. 输出结果
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
