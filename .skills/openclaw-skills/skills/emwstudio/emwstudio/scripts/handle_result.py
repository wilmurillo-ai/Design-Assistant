#!/usr/bin/env python3
"""
处理工作流运行结果
用法: python3 handle_result.py <RESULT_JSON>
"""

import sys
import json


def handle_result(result_json: str) -> dict:
    """处理工作流运行结果并返回相应的操作指令"""
    try:
        result = json.loads(result_json)
    except json.JSONDecodeError:
        return {
            "action": "error",
            "message": "无法解析结果JSON"
        }
    
    status = result.get("status", "UNKNOWN")
    task_id = result.get("taskId", "unknown")
    
    if status == "TIMEOUT":
        return {
            "action": "notify",
            "message": f"工作流仍在运行中，但运行已超时未完成，建议稍后手动查询taskId {task_id}的状态",
            "taskId": task_id
        }
    
    elif status == "FAILED":
        error_message = result.get("errorMessage", "unknown error")
        return {
            "action": "notify",
            "message": f"工作流运行失败，原因：{error_message}",
            "taskId": task_id
        }
    
    elif status == "SUCCESS":
        results = result.get("results", [])
        if results and len(results) > 0:
            url = results[0].get("url", "").strip()
            output_type = results[0].get("outputType", "")
            if url:
                return {
                    "action": "message",
                    "message": "亲爱的，工作流已经运行完成～快看看吧～🎬",
                    "media": url,
                    "outputType": output_type,
                    "taskId": task_id
                }
            else:
                return {
                    "action": "notify",
                    "message": f"工作流运行成功，但未获取到结果URL。taskId: {task_id}",
                    "taskId": task_id
                }
        else:
            return {
                "action": "notify",
                "message": f"工作流运行成功，但结果为空。taskId: {task_id}",
                "taskId": task_id
            }
    
    else:
        return {
            "action": "notify",
            "message": f"未知的工作流状态：{status}。taskId: {task_id}",
            "taskId": task_id
        }


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 handle_result.py <RESULT_JSON>", file=sys.stderr)
        sys.exit(1)
    
    result_json = sys.argv[1]
    
    try:
        output = handle_result(result_json)
        print(json.dumps(output, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            "action": "error",
            "message": str(e)
        }, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
