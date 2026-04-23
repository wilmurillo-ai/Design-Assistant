#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 测试 restore 任务（整理物品）
"""

import asyncio
import json
import time
import uuid
import websockets

WEBSOCKET_URL = "ws://10.10.10.12:9900"

def generate_task_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def generate_uuid() -> str:
    return str(uuid.uuid4())

def build_request(name: str, task_id: str, data: dict) -> dict:
    return {
        "header": {
            "mode": "mission",
            "type": "request",
            "cmd": "start",
            "ts": int(time.time()),
            "uuid": generate_uuid()
        },
        "body": {
            "name": name,
            "task_id": task_id,
            "data": data
        }
    }

async def test_restore():
    print("=" * 70)
    print("🤖 测试 restore 任务（整理物品）")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接\n")
        
        # 使用 restore 任务整理桌子
        print("【测试】restore - 整理桌子")
        print("-" * 70)
        
        task_id = generate_task_id("restore")
        request = build_request("restore", task_id, {
            "name": "SortDesk",
            "area_info": {
                "area_name": "桌子",
                "area_id": ""
            },
            "object_info": {
                "object_name": ""
            }
        })
        
        print("发送请求:")
        print(json.dumps(request, indent=2, ensure_ascii=False))
        await ws.send(json.dumps(request))
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=120.0)
                response = json.loads(msg)
                header = response["header"]
                body = response["body"]
                
                if header["type"] == "response":
                    code = body["data"]["error_code"]["code"]
                    print(f"\n启动：0x{code:08X}")
                
                elif header["type"] == "notify":
                    data = body["data"]
                    if "summary" in data:
                        print(f"执行中：{data['summary']}")
                
                if header["cmd"] == "finish":
                    code = body["data"]["error_code"]["code"]
                    msg = body["data"]["error_code"].get("msg", "")
                    print(f"完成：0x{code:08X} - {msg}")
                    break
            except asyncio.TimeoutError:
                print("超时")
                break
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(test_restore())
