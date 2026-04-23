#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 客厅整理玩具任务（v4 最终版）

工作流程：
1. 搜索收纳筐 → 等待 finish，记录位置
2. 搜索玩具 → 等待 finish，记录位置
3. 抓取玩具 → 等待 finish
4. 放置到收纳筐 → 等待 finish

关键：
- 每个任务有独立的 task_id
- 同一个任务的所有消息共用同一个 uuid
- 每个任务必须等待 finish 消息后才执行下一步
"""

import asyncio
import json
import time
import uuid
import websockets
from typing import Optional, Dict

WEBSOCKET_URL = "ws://10.10.10.12:9900"

def generate_task_id(prefix: str) -> str:
    """每个任务生成独立的 task_id"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def generate_uuid() -> str:
    """同一个任务的所有消息共用同一个 uuid"""
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

async def wait_for_finish(ws, task_name: str, timeout: int = 120) -> dict:
    """
    等待任务完成，返回 finish 消息和 notify 数据
    
    协议流程：
    request → response → (notify x N) → finish
    
    必须等待 finish 后才能执行下一步
    """
    search_data = None
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            code = body["data"]["error_code"]["code"]
            if code == 0:
                print(f"✓ {task_name}任务启动成功")
            else:
                print(f"❌ {task_name}启动失败：0x{code:08X}")
                return {"success": False, "error_code": code}
        
        elif header["type"] == "notify":
            data = body["data"]
            if "position" in data:
                # search 任务会返回位置信息
                search_data = data
                print(f"📍 找到物体:")
                print(f"   位置：{data['position']}")
            elif "summary" in data:
                print(f"执行中：{data['summary']}")
        
        if header["cmd"] == "finish":
            code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            print(f"✅ {task_name}完成：0x{code:08X} - {msg_text}")
            
            return {
                "success": code == 0,
                "error_code": code,
                "search_data": search_data
            }
    
    return {"success": False, "error_code": -1}

async def search_object(ws, object_name: str, area_name: str) -> Optional[Dict]:
    """搜索物体"""
    print(f"\n【搜索】{object_name} @ {area_name}")
    print("-" * 70)
    
    task_id = generate_task_id("search")
    print(f"task_id: {task_id}")
    
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
    
    # 等待 finish 消息
    result = await wait_for_finish(ws, f"搜索{object_name}")
    
    if result["success"]:
        return result["search_data"]
    else:
        return None

async def accurate_grab(ws, search_data: Dict) -> bool:
    """精准抓取"""
    print("\n【抓取】玩具")
    print("-" * 70)
    
    task_id = generate_task_id("grab")
    print(f"task_id: {task_id}")
    
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
    
    print(f"抓取位置：{search_data['position']}")
    
    request = build_request("accurate_grab", task_id, grab_data)
    await ws.send(json.dumps(request))
    
    # 等待 finish 消息
    result = await wait_for_finish(ws, "抓取玩具", timeout=180)
    
    return result["success"]

async def semantic_place(ws, object_name: str, container_name: str) -> bool:
    """放置到容器"""
    print(f"\n【放置】{object_name} → {container_name}")
    print("-" * 70)
    
    task_id = generate_task_id("place")
    print(f"task_id: {task_id}")
    
    request = build_request("semantic_place", task_id, {
        "area_id": "",
        "area_name": container_name,
        "object_name": object_name,
        "direction": "里"
    })
    
    await ws.send(json.dumps(request))
    
    # 等待 finish 消息
    result = await wait_for_finish(ws, "放置玩具", timeout=180)
    
    return result["success"]

async def main():
    print("=" * 70)
    print("🤖 八界机器人 - 客厅整理玩具（v4 最终版）")
    print("=" * 70)
    print(f"📅 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 连接：{WEBSOCKET_URL}")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接到机器人")
        
        # 步骤 1: 搜索收纳筐 → 等待 finish
        basket_data = await search_object(ws, "收纳筐", "客厅")
        if not basket_data:
            print("❌ 未找到收纳筐，任务终止")
            return False
        
        await asyncio.sleep(1)
        
        # 步骤 2: 搜索玩具 → 等待 finish
        toy_data = await search_object(ws, "玩具", "地上")
        if not toy_data:
            print("❌ 未找到玩具，任务终止")
            return False
        
        await asyncio.sleep(1)
        
        # 步骤 3: 抓取玩具 → 等待 finish
        grab_success = await accurate_grab(ws, toy_data)
        if not grab_success:
            print("❌ 抓取失败，任务终止")
            return False
        
        await asyncio.sleep(1)
        
        # 步骤 4: 放置到收纳筐 → 等待 finish
        place_success = await semantic_place(ws, "玩具", "收纳筐")
        if not place_success:
            print("❌ 放置失败")
            return False
        
        print("\n" + "=" * 70)
        print("✅ 任务完成！玩具已整理到收纳筐里")
        print("=" * 70)
        return True

if __name__ == "__main__":
    asyncio.run(main())
