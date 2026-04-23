#!/usr/bin/env python3
"""
sfe-zone / project-plan 脚本

用途：查询指定区划的计划编制数据并输出 TOON 编码结果

使用方式：
  python3 scripts/sfe-zone/project-plan.py --zoneId <区划ID> --projectId <项目ID> --periodStart <开始日期> --periodEnd <结束日期>

环境变量：
  XG_BIZ_API_KEY / XG_APP_KEY  — appKey（必须）

可选参数：
  --tenantId  租户ID，用户存在多个租户身份时须传入

注意：此接口需要必填参数 zoneId、projectId、periodStart、periodEnd
"""

import sys
import os
import json
import argparse
import requests
import warnings

# 引入共享的 TOON 编码器
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from toon_encoder import encode as toon_encode

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# 接口完整 URL
API_URL = "https://sg-cwork-api.mediportal.com.cn/sfe-statistic/open-api/statistic/v1/user/zone/projects/plan"


def call_api(app_key: str, body: dict, tenant_id: str = None) -> dict:
    """查询指定大区的项目计划值列表"""
    headers = {
        "X-APP-KEY": app_key,
        "Content-Type": "application/json",
    }
    if tenant_id:
        headers["X-TENANT-ID"] = tenant_id

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
    parser = argparse.ArgumentParser(description="查询指定区划的计划编制数据")
    parser.add_argument("--zoneId", required=True, help="区划ID")
    parser.add_argument("--projectId", required=True, help="项目ID")
    parser.add_argument("--periodStart", required=True, help="期间开始日期")
    parser.add_argument("--periodEnd", required=True, help="期间结束日期")
    parser.add_argument("--tenantId", help="租户ID（用户存在多个租户身份时须传入）")
    args = parser.parse_args()

    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)

    body = {
        "zoneId": args.zoneId,
        "projectId": args.projectId,
        "periodStart": args.periodStart,
        "periodEnd": args.periodEnd,
    }

    result = call_api(app_key, body, args.tenantId)
    toon_output = toon_encode(result)
    print(toon_output)


if __name__ == "__main__":
    main()
