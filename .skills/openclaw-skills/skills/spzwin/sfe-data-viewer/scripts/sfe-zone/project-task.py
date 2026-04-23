#!/usr/bin/env python3
"""
sfe-zone / project-task 脚本

用途：查询指定区划的待办任务并输出 TOON 编码结果

使用方式：
  python3 scripts/sfe-zone/project-task.py --tenantId <租户ID> --zoneId <区划ID> --projectId <项目ID> --periodStart <开始日期> --periodEnd <结束日期>

环境变量：
  XG_BIZ_API_KEY / XG_APP_KEY  — appKey（必须）

参数说明：
  --tenantId    租户ID（可选，用户存在多个租户身份时须传入）
  --zoneId      区划ID（必须）
  --projectId   项目ID（必须）
  --periodStart 周期开始时间（必须）
  --periodEnd   周期结束时间（必须）
  --status      状态：0-待处理，1-已完成，2-已取消，3-过期关闭，4-手工关闭（可选）
  --page        页码（可选，默认第1页）
"""

import sys
import os
import json
import argparse
import requests
import warnings

# 禁用 InsecureRequestWarning (因为 verify=False)
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# 引入共享的 TOON 编码器
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from toon_encoder import encode as toon_encode

# 接口完整 URL
API_URL = "https://sg-cwork-api.mediportal.com.cn/sfe-statistic/open-api/statistic/v1/user/zone/projects/task"


def call_api(app_key: str, body: dict, tenant_id: str = None) -> dict:
    """查询指定大区的项目指标值列表"""
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
    parser = argparse.ArgumentParser(description="查询指定区划的待办任务")
    parser.add_argument(
        "--tenantId",
        type=str,
        default=None,
        help="租户ID（可选，用户存在多个租户身份时须传入）",
    )
    parser.add_argument("--zoneId", type=str, required=True, help="区划ID")
    parser.add_argument("--projectId", type=str, required=True, help="项目ID")
    parser.add_argument("--periodStart", type=str, required=True, help="周期开始时间")
    parser.add_argument("--periodEnd", type=str, required=True, help="周期结束时间")
    parser.add_argument(
        "--status", type=int, choices=[0, 1, 2, 3, 4], default=None, help="状态（可选）"
    )
    parser.add_argument("--page", type=int, default=1, help="页码")
    args = parser.parse_args()

    app_key = os.environ.get("XG_BIZ_API_KEY") or os.environ.get("XG_APP_KEY")
    if not app_key:
        print("错误: 请设置环境变量 XG_BIZ_API_KEY 或 XG_APP_KEY", file=sys.stderr)
        sys.exit(1)

    # 构建请求体
    body = {
        "zoneId": args.zoneId,
        "projectId": args.projectId,
        "periodStart": args.periodStart,
        "periodEnd": args.periodEnd,
        "page": args.page,
    }
    if args.status is not None:
        body["status"] = args.status

    # 调用接口
    result = call_api(app_key, body, args.tenantId)

    # TOON 编码输出
    toon_output = toon_encode(result)
    print(toon_output)


if __name__ == "__main__":
    main()
