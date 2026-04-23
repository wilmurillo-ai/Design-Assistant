#!/usr/bin/env python3
"""
report-detail / get-info 脚本
用途：获取单篇汇报的结构化详情
"""
import sys, os, json, urllib.request, urllib.parse, ssl

API_URL = "https://cwork-web.mediportal.com.cn/cwork/report/info"

def call_api(token, report_id):
    headers = {"access-token": token, "Content-Type": "application/json"}
    query = f"?reportId={urllib.parse.quote(report_id)}"
    req = urllib.request.Request(API_URL + query, headers=headers, method="GET")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    token = os.environ.get("XG_USER_TOKEN")
    if not token: sys.exit(1)
    report_id = sys.argv[1] if len(sys.argv) > 1 else ""
    if not report_id:
        print("错误: 请提供 reportId 作为参数", file=sys.stderr)
        sys.exit(1)
    result = call_api(token, report_id)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
