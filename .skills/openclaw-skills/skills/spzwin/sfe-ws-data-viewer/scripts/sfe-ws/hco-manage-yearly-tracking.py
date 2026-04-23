#!/usr/bin/env python3
"""医院管理年度跟踪表查询脚本"""

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
API_PATH = "/bia/open/biz-service/sfe-ws-report/hcoManageYearlyTrackingReport"


def call_api(
    zone_id: str = None,
    region_name: str = None,
    area_name: str = None,
    territory_name: str = None,
    year: str = None,
    page: int = 1,
    count: bool = False,
    max_retries: int = 3,
) -> dict:
    headers = {
        "appKey": os.environ.get("XG_BIZ_API_KEY", ""),
        "Content-Type": "application/json",
    }

    body = {"page": page}
    if zone_id is not None:
        body["zoneId"] = zone_id
    if region_name is not None:
        body["regionName"] = region_name
    if area_name is not None:
        body["areaName"] = area_name
    if territory_name is not None:
        body["territoryName"] = territory_name
    if year is not None:
        body["year"] = year

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
    parser = argparse.ArgumentParser(description="查询医院管理年度跟踪表")
    parser.add_argument("--zoneId", help="区划ID")
    parser.add_argument("--regionName", help="大区名称，支持模糊查询")
    parser.add_argument("--areaName", help="地区名称，支持模糊查询")
    parser.add_argument("--territoryName", help="辖区名称，支持模糊查询")
    parser.add_argument("--year", type=str, help="年度")
    parser.add_argument("--page", type=int, default=1, help="页码，默认1")
    parser.add_argument("--count", action="store_true", help="查询总记录数")
    args = parser.parse_args()

    result = call_api(
        zone_id=args.zoneId,
        region_name=args.regionName,
        area_name=args.areaName,
        territory_name=args.territoryName,
        year=args.year,
        page=args.page,
        count=args.count,
    )

    print(encode(result))


if __name__ == "__main__":
    main()
