#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 客厅整理玩具任务（修正版工作流）

工作流程：
1. 搜索收纳筐，记录位置
2. 搜索玩具
3. 抓取玩具
4. 导航到收纳筐位置
5. 放置玩具到收纳筐
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

async def search_object(ws, object_name: str, area_name: str) -> Optional[Dict]:
    """搜索物体，返回位置信息"""
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
            if code == 0:
                print(f"✓ 搜索{object_name}任务启动成功")
            else:
                print(f"❌ 启动失败：0x{code:08X}")
                return None
        
        elif header["type"] == "notify":
            data = body["data"]
            if "position" in data:
                search_data = data
                print(f"📍 找到{object_name}:")
                print(f"   位置：{data['position']}")
                print(f"   朝向：{data['orientation']}")
                print(f"   尺寸：{data['box_length']}")
                print(f"   frame_id: {data['frame_id']}")
        
        if header["cmd"] == "finish":
            code = body["data"]["error_code"]["code"]
            msg = body["data"]["error_code"].get("msg", "")
            print(f"完成：0x{code:08X} - {msg}")
            break
    
    return search_data

async def accurate_grab(ws, search_data: Dict) -> bool:
    """精准抓取"""
    print("\n【抓取】玩具")
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
    
    print(f"抓取位置：{search_data['position']}")
    
    request = build_request("accurate_grab", task_id, grab_data)
    await ws.send(json.dumps(request))
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=180.0)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            code = body["data"]["error_code"]["code"]
            if code == 0:
                print("✓ 抓取任务启动成功")
            else:
                print(f"❌ 启动失败：0x{code:08X}")
                return False
        
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

async def navigate_to_position(ws, basket_position: Dict) -> bool:
    """导航到收纳筐位置附近"""
    print("\n【导航】到收纳筐位置")
    print("-" * 70)
    
    # 使用 point_navigation 导航到具体坐标
    # 注意：这里需要把收纳筐的位置作为目标
    # 但由于 semantic_navigation 使用区域名，我们先尝试用语义导航到收纳筐
    
    task_id = generate_task_id("nav")
    request = build_request("semantic_navigation", task_id, {
        "goal": "收纳筐",
        "goal_id": ""
    })
    
    print(f"目标位置：{basket_position['position']}")
    await ws.send(json.dumps(request))
    
    while True:
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
                return False
        
        elif header["type"] == "notify":
            data = body["data"]
            if "summary" in data:
                print(f"📍 导航中：{data['summary']}")
        
        if header["cmd"] == "finish":
            code = body["data"]["error_code"]["code"]
            msg = body["data"]["error_code"].get("msg", "")
            print(f"完成：0x{code:08X} - {msg}")
            return code == 0
    
    return False

async def place_to_container(ws, object_name: str, container_name: str) -> bool:
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
            if code == 0:
                print("✓ 放置任务启动成功")
            else:
                print(f"❌ 启动失败：0x{code:08X}")
                return False
        
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
    print("🤖 八界机器人 - 客厅整理玩具（修正工作流）")
    print("=" * 70)
    print(f"📅 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 连接：{WEBSOCKET_URL}")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接到机器人")
        
        # 步骤 1: 先搜索收纳筐，记录位置
        basket_data = await search_object(ws, "收纳筐", "客厅")
        if not basket_data:
            print("❌ 未找到收纳筐，任务终止")
            return False
        
        # 保存收纳筐位置
        basket_position = basket_data["position"]
        print(f"\n💾 已记录收纳筐位置：{basket_position}")
        
        await asyncio.sleep(2)
        
        # 步骤 2: 搜索玩具
        toy_data = await search_object(ws, "玩具", "地上")
        if not toy_data:
            print("❌ 未找到玩具，任务终止")
            return False
        
        await asyncio.sleep(2)
        
        # 步骤 3: 抓取玩具
        grab_success = await accurate_grab(ws, toy_data)
        if not grab_success:
            print("❌ 抓取失败，任务终止")
            return False
        
        await asyncio.sleep(2)
        
        # 步骤 4: 导航到收纳筐位置
        nav_success = await navigate_to_position(ws, basket_data)
        if not nav_success:
            print("❌ 导航失败，任务终止")
            return False
        
        await asyncio.sleep(2)
        
        # 步骤 5: 放置玩具到收纳筐
        place_success = await place_to_container(ws, "玩具", "收纳筐")
        if not place_success:
            print("❌ 放置失败")
            return False
        
        print("\n" + "=" * 70)
        print("✅ 任务完成！玩具已整理到收纳筐里")
        print("=" * 70)
        return True

if __name__ == "__main__":
    asyncio.run(main())
