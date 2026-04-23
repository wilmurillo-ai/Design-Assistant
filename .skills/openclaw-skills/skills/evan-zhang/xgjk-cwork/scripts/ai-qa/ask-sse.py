#!/usr/bin/env python3
"""
ai-qa / ask-sse 脚本
用途：CWork AI 知识库问答 (SSE 流式输出并合并为最终 JSON)
"""
import sys, os, json, urllib.request, urllib.parse, ssl

API_URL = "https://cwork-web.mediportal.com.cn/cwork/report/aiSseQa"

def call_api_sse(token, content, notebook_id=""):
    headers = {"access-token": token, "Accept": "text/event-stream"}
    query = f"?content={urllib.parse.quote(content)}&notebookId={notebook_id}"
    req = urllib.request.Request(API_URL + query, headers=headers, method="GET")
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE

    full_response = ""
    with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
        for line in resp:
            line_str = line.decode("utf-8").strip()
            if line_str.startswith("data:"):
                data_content = line_str[5:].strip()
                if data_content == "[DONE]":
                    break
                full_response += data_content
    
    return {"resultCode": 1, "data": {"answer": full_response}}

def main():
    token = os.environ.get("XG_USER_TOKEN")
    if not token: sys.exit(1)
    content = sys.argv[1] if len(sys.argv) > 1 else ""
    if not content: sys.exit(1)
    notebook_id = sys.argv[2] if len(sys.argv) > 2 else ""
    
    # 获取并输出合并后的 JSON
    result = call_api_sse(token, content, notebook_id)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__": main()
