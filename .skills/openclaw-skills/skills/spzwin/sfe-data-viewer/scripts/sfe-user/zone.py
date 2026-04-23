#!/usr/bin/env python3
"""
sfe-user / zone 脚本

用途：查询用户授权的区划列表并输出 TOON 编码结果

使用方式：
  python3 scripts/sfe-user/zone.py [--status <状态>] [--tenantId <租户ID>]

环境变量：
  XG_BIZ_API_KEY / XG_APP_KEY  — appKey（必须）

可选参数：
  --status    状态：1-启用，0-禁用（默认查询启用的区划）
  --tenantId  租户ID，用户存在多个租户身份时须传入
"""

import sys
import os
import json
import requests
import warnings
import argparse

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# 引入共享的 TOON 编码器
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from toon_encoder import encode as toon_encode

# 接口完整 URL
API_URL = "https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/zone"


def call_api(app_key: str, body: dict, tenant_id: str = None) -> dict:
    """调用接口，返回原始 JSON 响应"""
    headers = {
        "appKey": app_key,
        "Content-Type": "application/json",
    }
    if tenant_id:
        headers["tenantId"] = tenant_id

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
        return response.json()
    except Exception as e:
        print(f"错误: 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="查询用户授权的区划列表")
    parser.add_argument("--status", type=int, default=1, help="状态：1-启用，0-禁用")
    parser.add_argument("--tenantId", help="租户ID（用户存在多个租户身份时须传入）")
    args = parser.parse_args()

    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)

    body = {"status": args.status}
    result = call_api(app_key, body, args.tenantId)
    toon_output = toon_encode(result)
    print(toon_output)


if __name__ == "__main__":
    main()
