#!/usr/bin/env python3
"""
sfe-dm / balutamide-daily-feedback 脚本

用途：查询百卢妥日采集反馈数据并输出 TOON 编码结果

使用方式：
  # 查询数据列表
  python3 scripts/sfe-dm/balutamide-daily-feedback.py --periodStart 2025-01-01 --periodEnd 2025-01-31

  # 查询总记录数
  python3 scripts/sfe-dm/balutamide-daily-feedback.py --count --periodStart 2025-01-01 --periodEnd 2025-01-31

环境变量：
  XG_BIZ_API_KEY / XG_APP_KEY  — appKey（必须）

参数说明：
  --count           查询总记录数（可选，默认查询数据列表）
  --zoneId          区划 ID（可选）
  --regionName      大区名称，支持模糊查询（可选）
  --areaName        地区名称，支持模糊查询（可选）
  --periodStart     期间开始日期（可选）
  --periodEnd       期间结束日期（可选）
  --page            页码，默认第 1 页（可选）
"""

import sys
import os
import json
import requests
import warnings
import argparse

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from toon_encoder import encode as toon_encode

# 接口完整 URL
API_URL = "https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm/balutamide-daily-feedback"


def call_api(app_key: str, body: dict, count_mode: bool = False) -> dict:
    """调用接口，返回原始 JSON 响应"""
    url = f"{API_URL}/count" if count_mode else API_URL
    headers = {
        "appKey": app_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url,
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
    parser = argparse.ArgumentParser(description="查询百卢妥日采集反馈数据")
    parser.add_argument("--count", action="store_true", help="查询总记录数")
    parser.add_argument("--zoneId", type=str, default="", help="区划 ID")
    parser.add_argument("--regionName", type=str, default="", help="大区名称")
    parser.add_argument("--areaName", type=str, default="", help="地区名称")
    parser.add_argument("--periodStart", type=str, default="", help="期间开始日期")
    parser.add_argument("--periodEnd", type=str, default="", help="期间结束日期")
    parser.add_argument("--page", type=int, default=1, help="页码，默认第 1 页")
    args = parser.parse_args()

    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")

    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)

    body = {
        "zoneId": args.zoneId,
        "regionName": args.regionName,
        "areaName": args.areaName,
        "periodStart": args.periodStart,
        "periodEnd": args.periodEnd,
        "page": args.page,
    }

    body = {k: v for k, v in body.items() if v}

    result = call_api(app_key, body, count_mode=args.count)
    
    toon_output = toon_encode(result)
    print(toon_output)


if __name__ == "__main__":
    main()
