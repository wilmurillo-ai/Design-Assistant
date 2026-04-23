# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import urllib.request
import urllib.error
import argparse

def volcengine_web_search(query: str, search_type: str = "web", api_key: str = None) -> dict:
    """
    调用火山引擎联网搜索 API。
    """
    if not query or not str(query).strip():
        raise ValueError("query is empty. 搜索词不能为空。")

    if not search_type or not str(search_type).strip():
        raise ValueError("search type is empty. 搜索类型不能为空。")

    url = "https://open.feedcoopapi.com/search_api/web_search"
    key = api_key or os.getenv("VOLC_SEARCH_API_KEY") or os.getenv("VOLCENGINE_SEARCH_API_KEY")
    if not key:
        raise ValueError("未找到 API Key，请配置环境变量 VOLC_SEARCH_API_KEY。")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }

    # 注意这里的键名已经按之前排查的情况适配
    payload = {
        "Query": query,
        "SearchType": search_type,
        "UserLocation": {
            "Type": "approximate",
            "Country": "中国"
        }
    }
    if search_type == "web_summary":
        payload["NeedSummary"] = True

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as response:
            text_data = response.read().decode("utf-8")

            # 处理流式返回
            if "data:{" in text_data or "data: {" in text_data:
                full_content = ""
                last_metadata = {}
                for line in text_data.split('\n'):
                    line = line.strip()
                    if line.startswith("data:"):
                        json_str = line[5:].strip()
                        if not json_str: continue

                        try:
                            chunk = json.loads(json_str)
                            last_metadata = chunk

                            # 安全提取流式增量文本
                            choices = (chunk.get("Result") or {}).get("Choices", [])
                            if choices:
                                delta_content = choices[0].get("Delta", {}).get("Content", "")
                                if delta_content:
                                    full_content += delta_content
                        except json.JSONDecodeError:
                            continue

                # 拼装为普通结构
                if last_metadata and last_metadata.get("Result"):
                    choices = last_metadata["Result"].get("Choices", [])
                    if choices:
                        choices[0]["Message"] = {
                            "Role": "assistant",
                            "Content": full_content
                        }
                return last_metadata

            else:
                return json.loads(text_data)

    except urllib.error.HTTPError as e:
        return {"HTTP_Error": e.code, "Details": e.read().decode("utf-8")}
    except Exception as e:
        return {"Exception": str(e)}

def main():
    parser = argparse.ArgumentParser(description="火山引擎联网搜索 Skill 脚本")
    parser.add_argument("-q", "--query", type=str, required=True, help="想要搜索的关键词或问题")
    parser.add_argument("-t", "--type", type=str, default="web", choices=["web", "image", "web_summary"], help="搜索类型")
    parser.add_argument("-k", "--key", type=str, default=None, help="你的 API Key")

    args = parser.parse_args()

    try:
        print(f"正在进行联网搜索: [{args.query}] (模式: {args.type}) ...\n")
        result = volcengine_web_search(query=args.query, search_type=args.type, api_key=args.key)

        # 增加安全拦截，如果 Result 是 None 就不去尝试提取 Summary
        if result and result.get("Result"):
            print("======== 搜索成功 ========")
            if args.type == "web_summary":
                # 安全链式调用提取最终文本
                summary = result.get("Result", {}).get("Choices", [{}])[0].get("Message", {}).get("Content", "")
                print("\n【AI 总结结果】:\n" + summary + "\n")
            else:
                print(json.dumps(result, indent=4, ensure_ascii=False))
        else:
            print("======== 搜索失败或返回异常 ========")
            # 打印原始返回以便排查错误（比如 10400）
            print(json.dumps(result, indent=4, ensure_ascii=False))

    except ValueError as ve:
        print(f"\n[参数错误] {ve}")

if __name__ == "__main__":
    main()