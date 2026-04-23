#!/usr/bin/env python3
"""
plan-create / create-simple 脚本
用途：快速创建一个工作计划汇报 (cwork report/save)
"""
import sys, os, json, urllib.request, urllib.parse, ssl

API_URL = "https://cwork-web.mediportal.com.cn/cwork/report/save"

def call_api(token, title, content):
    headers = {"access-token": token, "Content-Type": "application/json"}
    
    # 构造 cwork 复杂的 reportLevelList 结构
    body_data = {
        "reportType": 3, # 3 代表工作计划
        "isDraft": False,
        "reportLevelList": [
            {
                "levelName": "工作计划",
                "levelTitle": title,
                "resultContent": content,
                "subLevelList": []
            }
        ]
    }
    
    body = json.dumps(body_data).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, headers=headers, method="POST")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    token = os.environ.get("XG_USER_TOKEN")
    if not token: sys.exit(1)
    
    title = sys.argv[1] if len(sys.argv) > 1 else "未命名计划"
    content = sys.argv[2] if len(sys.argv) > 2 else "无内容"
    
    result = call_api(token, title, content)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
