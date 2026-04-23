#!/usr/bin/env python3
"""客户管理年度跟踪表查询脚本"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
import warnings

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings(
    "ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning
)

sys.path.insert(0, str(Path(__file__).parent.parent))
from common.toon_encoder import encode

BASE_URL = os.environ.get(
    "XG_BIZ_API_BASE_URL", "https://erp-web.mediportal.com.cn/erp-open-api"
)
API_PATH = "/bia/open/biz-service/sfe-ws-report/hcpManageYearlyTrackingReport"


def call_api(
    zone_id: str = None,
    year: int = None,
    quarter: int = None,
    page: int = 1,
    count: bool = False,
    max_retries: int = 3,
) -> dict:
    headers = {
        "appKey": os.environ.get("XG_BIZ_API_KEY", ""),
        "Content-Type": "application/json",
    }

    body = {"page": page}
    if zone_id:
        body["zoneId"] = zone_id
    if year is not None:
        body["year"] = year
    if quarter is not None:
        body["quarter"] = quarter

    url = BASE_URL + API_PATH + ("/count" if count else "")

    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                raise RuntimeError(f"API call failed after {max_retries} retries: {e}")


def main():
    parser = argparse.ArgumentParser(description="查询客户管理年度跟踪表")
    parser.add_argument("--zoneId", help="区划ID")
    parser.add_argument("--year", type=int, help="年度")
    parser.add_argument("--quarter", type=int, help="季度")
    parser.add_argument("--page", type=int, default=1, help="页码，默认1")
    parser.add_argument("--count", action="store_true", help="查询总记录数")
    args = parser.parse_args()

    result = call_api(
        zone_id=args.zoneId,
        year=args.year,
        quarter=args.quarter,
        page=args.page,
        count=args.count,
    )

    print(encode(result))


if __name__ == "__main__":
    main()
