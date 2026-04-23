#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 测试放置任务（修正版）
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

async def test_place_variants():
    print("=" * 70)
    print("🤖 测试不同的放置参数")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接\n")
        
        # 方案 1: 使用 area_name="收纳筐"
        print("【方案 1】area_name='收纳筐'")
        print("-" * 70)
        task_id = generate_task_id("place1")
        request = build_request("semantic_place", task_id, {
            "area_id": "",
            "area_name": "收纳筐",
            "object_name": "玩具",
            "direction": "里"
        })
        await ws.send(json.dumps(request))
        
        while True:
            msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
            response = json.loads(msg)
            header = response["header"]
            body = response["body"]
            
            if header["type"] == "response":
                code = body["data"]["error_code"]["code"]
                print(f"启动：0x{code:08X}")
            
            if header["cmd"] == "finish":
                code = body["data"]["error_code"]["code"]
                msg = body["data"]["error_code"].get("msg", "")
                print(f"完成：0x{code:08X} - {msg}\n")
                break
        
        await asyncio.sleep(2)
        
        # 方案 2: 使用 area_name="客厅" (区域名)
        print("【方案 2】area_name='客厅' (区域)")
        print("-" * 70)
        task_id = generate_task_id("place2")
        request = build_request("semantic_place", task_id, {
            "area_id": "",
            "area_name": "客厅",
            "object_name": "玩具",
            "direction": "里"
        })
        await ws.send(json.dumps(request))
        
        while True:
            msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
            response = json.loads(msg)
            header = response["header"]
            body = response["body"]
            
            if header["type"] == "response":
                code = body["data"]["error_code"]["code"]
                print(f"启动：0x{code:08X}")
            
            if header["cmd"] == "finish":
                code = body["data"]["error_code"]["code"]
                msg = body["data"]["error_code"].get("msg", "")
                print(f"完成：0x{code:08X} - {msg}\n")
                break
        
        await asyncio.sleep(2)
        
        # 方案 3: 先搜索容器，再放置
        print("【方案 3】先 search_container 再 semantic_place")
        print("-" * 70)
        
        # 3.1 搜索容器
        print("步骤 1: search_container")
        task_id = generate_task_id("search_container")
        request = build_request("search_container", task_id, {
            "object": {
                "item": "收纳筐",
                "color": "",
                "shape": "",
                "person": ""
            },
            "area_info": [
                {
                    "area_id": "",
                    "area_name": "客厅"
                }
            ]
        })
        await ws.send(json.dumps(request))
        
        container_data = None
        while True:
            msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
            response = json.loads(msg)
            header = response["header"]
            body = response["body"]
            
            if header["type"] == "response":
                code = body["data"]["error_code"]["code"]
                print(f"启动：0x{code:08X}")
            
            elif header["type"] == "notify" and "position" in body.get("data", {}):
                container_data = body["data"]
                print(f"📍 找到收纳筐：{container_data['position']}")
            
            if header["cmd"] == "finish":
                code = body["data"]["error_code"]["code"]
                msg = body["data"]["error_code"].get("msg", "")
                print(f"完成：0x{code:08X} - {msg}")
                break
        
        if container_data:
            await asyncio.sleep(2)
            
            # 3.2 使用容器信息放置
            print("\n步骤 2: semantic_place (使用容器数据)")
            task_id = generate_task_id("place3")
            request = build_request("semantic_place", task_id, {
                "area_id": "",
                "area_name": "收纳筐",
                "object_name": "玩具",
                "direction": "里"
            })
            await ws.send(json.dumps(request))
            
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
                response = json.loads(msg)
                header = response["header"]
                body = response["body"]
                
                if header["type"] == "response":
                    code = body["data"]["error_code"]["code"]
                    print(f"启动：0x{code:08X}")
                
                if header["cmd"] == "finish":
                    code = body["data"]["error_code"]["code"]
                    msg = body["data"]["error_code"].get("msg", "")
                    print(f"完成：0x{code:08X} - {msg}")
                    break
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(test_place_variants())
