#!/usr/bin/env python3
"""
todos / get-list 脚本
用途：获取待办事项列表
"""
import sys, os, json, urllib.request, urllib.parse, ssl

API_URL = "https://cwork-web.mediportal.com.cn/cwork/report/todo/list"

def call_api(token, page_index=1, page_size=10, status=""):
    headers = {"access-token": token, "Content-Type": "application/json"}
    query = f"?pageIndex={page_index}&pageSize={page_size}&status={status}"
    req = urllib.request.Request(API_URL + query, headers=headers, method="GET")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    token = os.environ.get("XG_USER_TOKEN")
    if not token: sys.exit(1)
    status = sys.argv[1] if len(sys.argv) > 1 else ""
    result = call_api(token, status=status)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
