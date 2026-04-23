#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 完整测试：搜索 + 抓取 + 放置
"""

import asyncio
import json
import time
import uuid
import websockets
from typing import Optional, Dict

WEBSOCKET_URL = "ws://10.10.10.12:9900"

def generate_task_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def generate_uuid() -> str:
    return str(uuid.uuid4())

def build_request(name: str, task_id: str, data: Dict, cmd: str = "start") -> Dict:
    return {
        "header": {
            "mode": "mission",
            "type": "request",
            "cmd": cmd,
            "ts": int(time.time()),
            "uuid": generate_uuid()
        },
        "body": {
            "name": name,
            "task_id": task_id,
            "data": data
        }
    }

async def search_object(ws, object_name: str, area_name: str) -> Optional[Dict]:
    """搜索物体"""
    print(f"\n【搜索】{object_name} @ {area_name}")
    print("-" * 70)
    
    task_id = generate_task_id("search")
    request = build_request("search", task_id, {
        "object": {
            "item": object_name,
            "color": "",
            "shape": "",
            "person": "",
            "type": [],
            "subtype": []
        },
        "area": {
            "area_name": area_name,
            "area_id": ""
        }
    })
    
    await ws.send(json.dumps(request))
    
    search_data = None
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=120.0)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            code = body["data"]["error_code"]["code"]
            print(f"启动：0x{code:08X}")
        
        elif header["type"] == "notify":
            data = body["data"]
            if "position" in data:
                search_data = data
                print(f"📍 找到{object_name}:")
                print(f"   位置：{data['position']}")
            elif header["cmd"] == "finish":
                code = body["data"]["error_code"]["code"]
                msg = body["data"]["error_code"].get("msg", "")
                print(f"完成：0x{code:08X} - {msg}")
                break
        
        if header["cmd"] == "finish":
            break
    
    return search_data

async def accurate_grab(ws, search_data: Dict) -> bool:
    """精准抓取"""
    print("\n【抓取】")
    print("-" * 70)
    
    task_id = generate_task_id("grab")
    grab_data = {
        "object": {
            "rag_id": "",
            "item": "玩具",
            "color": "",
            "shape": "",
            "person": ""
        },
        "position": search_data["position"],
        "orientation": search_data["orientation"],
        "box_length": search_data["box_length"],
        "frame_id": search_data["frame_id"]
    }
    
    request = build_request("accurate_grab", task_id, grab_data)
    
    print(f"抓取位置：{search_data['position']}")
    await ws.send(json.dumps(request))
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=180.0)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            code = body["data"]["error_code"]["code"]
            print(f"启动：0x{code:08X}")
        
        elif header["type"] == "notify":
            data = body["data"]
            if "summary" in data:
                print(f"执行中：{data['summary']}")
        
        if header["cmd"] == "finish":
            code = body["data"]["error_code"]["code"]
            msg = body["data"]["error_code"].get("msg", "")
            print(f"完成：0x{code:08X} - {msg}")
            return code == 0
    
    return False

async def semantic_place(ws, object_name: str, container_name: str) -> bool:
    """放置到容器"""
    print(f"\n【放置】{object_name} → {container_name}")
    print("-" * 70)
    
    task_id = generate_task_id("place")
    request = build_request("semantic_place", task_id, {
        "area_id": "",
        "area_name": container_name,
        "object_name": object_name,
        "direction": "里"
    })
    
    await ws.send(json.dumps(request))
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=180.0)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            code = body["data"]["error_code"]["code"]
            print(f"启动：0x{code:08X}")
        
        elif header["type"] == "notify":
            data = body["data"]
            if "summary" in data:
                print(f"执行中：{data['summary']}")
        
        if header["cmd"] == "finish":
            code = body["data"]["error_code"]["code"]
            msg = body["data"]["error_code"].get("msg", "")
            print(f"完成：0x{code:08X} - {msg}")
            return code == 0
    
    return False

async def main():
    print("=" * 70)
    print("🤖 八界机器人 - 完整任务测试")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接")
        
        # 步骤 1: 搜索玩具
        toy_data = await search_object(ws, "玩具", "地上")
        if not toy_data:
            print("❌ 未找到玩具")
            return
        
        await asyncio.sleep(2)
        
        # 步骤 2: 搜索收纳筐
        basket_data = await search_object(ws, "收纳筐", "客厅")
        if not basket_data:
            print("❌ 未找到收纳筐")
            return
        
        await asyncio.sleep(2)
        
        # 步骤 3: 抓取玩具
        grab_success = await accurate_grab(ws, toy_data)
        if not grab_success:
            print("❌ 抓取失败")
            return
        
        await asyncio.sleep(2)
        
        # 步骤 4: 放置到收纳筐
        place_success = await semantic_place(ws, "玩具", "收纳筐")
        if not place_success:
            print("❌ 放置失败")
            return
        
        print("\n" + "=" * 70)
        print("✅ 任务完成！")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
