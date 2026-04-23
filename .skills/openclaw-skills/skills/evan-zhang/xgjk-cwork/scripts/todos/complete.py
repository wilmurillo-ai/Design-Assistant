#!/usr/bin/env python3
"""
todos / complete 脚本
用途：完成待办事项
"""
import sys, os, json, urllib.request, urllib.parse, ssl

API_URL = "https://cwork-web.mediportal.com.cn/cwork/report/todo/complete"

def call_api(token, todo_id, is_complete=True):
    headers = {"access-token": token, "Content-Type": "application/json"}
    body = json.dumps({
        "todoId": todo_id,
        "isComplete": is_complete
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    token = os.environ.get("XG_USER_TOKEN")
    if not token: sys.exit(1)
    todo_id = sys.argv[1] if len(sys.argv) > 1 else ""
    if not todo_id: sys.exit(1)
    is_complete = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else True
    result = call_api(token, todo_id, is_complete)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
