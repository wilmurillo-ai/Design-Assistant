#!/usr/bin/env python3
"""
plan-create / create-simple 脚本
用途：创建高级工作任务
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

API_URL = "https://sg-al-cwork-web.mediportal.com.cn/open-api/work-report/open-platform/report/plan/create"

def _parse_emp_id_list(raw):
    if not raw:
        return []
    values = []
    for item in raw.split(","):
        item = item.strip()
        if item:
            values.append(int(item))
    return values

def call_api(app_key, payload):
    headers = {"appKey": app_key, "Content-Type": "application/json"}
    
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
    parser.add_argument("--main", required=True)
    parser.add_argument("--needful", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--type-id", type=int, default=9999)
    parser.add_argument("--report-emp-ids", required=True)
    parser.add_argument("--owner-emp-ids", default="")
    parser.add_argument("--assist-emp-ids", default="")
    parser.add_argument("--supervisor-emp-ids", default="")
    parser.add_argument("--copy-emp-ids", default="")
    parser.add_argument("--observer-emp-ids", default="")
    parser.add_argument("--end-time", type=int, required=True)
    parser.add_argument("--push-now", type=int, default=1, choices=[0, 1])
    args = parser.parse_args()

    payload = {
        "main": args.main,
        "needful": args.needful,
        "target": args.target,
        "typeId": args.type_id,
        "reportEmpIdList": _parse_emp_id_list(args.report_emp_ids),
        "ownerEmpIdList": _parse_emp_id_list(args.owner_emp_ids),
        "assistEmpIdList": _parse_emp_id_list(args.assist_emp_ids),
        "supervisorEmpIdList": _parse_emp_id_list(args.supervisor_emp_ids),
        "copyEmpIdList": _parse_emp_id_list(args.copy_emp_ids),
        "observerEmpIdList": _parse_emp_id_list(args.observer_emp_ids),
        "endTime": args.end_time,
        "pushNow": args.push_now,
    }

    result = call_api(app_key, payload)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
