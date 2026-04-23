#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 导航到客厅
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

async def navigate_to_living_room():
    print("=" * 70)
    print("🤖 八界机器人 - 导航到客厅")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接到机器人\n")
        
        print("【任务】semantic_navigation - 客厅")
        print("-" * 70)
        
        task_id = generate_task_id("nav")
        request = build_request("semantic_navigation", task_id, {
            "goal": "客厅",
            "goal_id": ""
        })
        
        print("发送请求...")
        await ws.send(json.dumps(request))
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=120.0)
                response = json.loads(msg)
                header = response["header"]
                body = response["body"]
                
                if header["type"] == "response":
                    code = body["data"]["error_code"]["code"]
                    if code == 0:
                        print("✓ 导航任务启动成功")
                    else:
                        print(f"❌ 启动失败：0x{code:08X}")
                
                elif header["type"] == "notify":
                    data = body["data"]
                    if "summary" in data:
                        print(f"📍 导航中：{data['summary']}")
                
                if header["cmd"] == "finish":
                    code = body["data"]["error_code"]["code"]
                    msg = body["data"]["error_code"].get("msg", "")
                    print(f"\n完成：0x{code:08X} - {msg}")
                    
                    if code == 0:
                        print("\n✅ 已到达客厅！")
                    else:
                        print("\n❌ 导航失败")
                    break
                    
            except asyncio.TimeoutError:
                print("⏱️  超时")
                break
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(navigate_to_living_room())
