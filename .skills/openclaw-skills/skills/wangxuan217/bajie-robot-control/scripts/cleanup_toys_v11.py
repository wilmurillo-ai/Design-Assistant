#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 玩具收纳区整理玩具（v5 - 简化版，跳过收纳筐搜索）

工作流程（严格串行）：
0. robot_prepare_pose → 等待 finish
1. 循环：search(玩具 @ 地上) → 等待 finish
   - 找到：accurate_grab → 等待 finish → semantic_place(收纳筐) → 等待 finish → 继续循环
   - 未找到：退出循环
2. robot_ending_pose → 等待 finish

说明：
- 跳过收纳筐搜索步骤
- semantic_place 会自动找到收纳筐
"""

import asyncio
import json
import time
import uuid
import websockets
from typing import Optional, Dict

WEBSOCKET_URL = "ws://10.10.10.12:9900"
TASK_UUID = str(uuid.uuid4())
MAX_LOOPS = 50
MAX_CONSECUTIVE_NOT_FOUND = 3


def generate_task_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def build_request(name: str, task_id: str, data: dict) -> dict:
    return {
        "header": {
            "mode": "mission",
            "type": "request",
            "cmd": "start",
            "ts": int(time.time()),
            "uuid": TASK_UUID
        },
        "body": {
            "name": name,
            "task_id": task_id,
            "data": data
        }
    }


async def wait_for_finish(ws, task_name: str, timeout: int = 120) -> dict:
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
                print(f"❌ {task_name}启动失败：0x{code:08X} - {body['data']['error_code'].get('msg', '')}")
                return {"success": False, "error_code": code}
        
        elif header["type"] == "notify":
            data = body["data"]
            if "position" in data:
                search_data = data
                print(f"📍 找到物体：位置={data['position']}")
            elif "summary" in data:
                print(f"📋 执行中：{data['summary']}")
        
        if header["cmd"] == "finish":
            code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            print(f"✅ {task_name}完成：0x{code:08X} - {msg_text}")
            return {"success": code == 0, "error_code": code, "search_data": search_data}
    
    return {"success": False, "error_code": -1}


async def send_task_and_wait(ws, name: str, task_id: str, data: dict, task_display_name: str, timeout: int = 120) -> dict:
    request = build_request(name, task_id, data)
    print(f"📤 发送任务：{task_display_name} (task_id={task_id})")
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, task_display_name, timeout=timeout)
    return result


async def robot_prepare_pose(ws, mission_summary: str) -> bool:
    print(f"\n{'='*70}")
    print(f"【步骤 0】机身准备姿态")
    print(f"{'='*70}")
    
    task_id = generate_task_id("prepare")
    result = await send_task_and_wait(
        ws, "robot_prepare_pose", task_id,
        {"mission_summary": mission_summary},
        "准备姿态", timeout=60
    )
    return result["success"]


async def search_toy(ws, object_name: str, area_name: str) -> tuple:
    print(f"\n{'='*70}")
    print(f"【搜索】{object_name} @ {area_name}")
    print(f"{'='*70}")
    
    task_id = generate_task_id("search")
    result = await send_task_and_wait(
        ws, "search", task_id,
        {
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
        },
        f"搜索{object_name}", timeout=120
    )
    return result["success"], result["search_data"]


async def accurate_grab(ws, search_data: Dict) -> bool:
    print(f"\n{'='*70}")
    print(f"【抓取】玩具")
    print(f"{'='*70}")
    
    task_id = generate_task_id("grab")
    grab_data = {
        "object": {"rag_id": "", "item": "玩具", "color": "", "shape": "", "person": ""},
        "position": search_data["position"],
        "orientation": search_data["orientation"],
        "box_length": search_data["box_length"],
        "frame_id": search_data["frame_id"]
    }
    
    print(f"抓取位置：{search_data['position']}")
    result = await send_task_and_wait(
        ws, "accurate_grab", task_id,
        grab_data,
        "精准抓取", timeout=180
    )
    return result["success"]


async def semantic_place(ws, object_name: str, container_name: str) -> bool:
    print(f"\n{'='*70}")
    print(f"【放置】{object_name} → {container_name}")
    print(f"{'='*70}")
    
    task_id = generate_task_id("place")
    result = await send_task_and_wait(
        ws, "semantic_place", task_id,
        {
            "area_id": "",
            "area_name": container_name,
            "object_name": object_name,
            "direction": "里"
        },
        f"放置到{container_name}", timeout=180
    )
    return result["success"]


async def robot_ending_pose(ws) -> bool:
    print(f"\n{'='*70}")
    print(f"【归位】机身结束姿态")
    print(f"{'='*70}")
    
    task_id = generate_task_id("ending")
    result = await send_task_and_wait(
        ws, "robot_ending_pose", task_id,
        {},
        "结束姿态", timeout=60
    )
    return result["success"]


async def main():
    print("=" * 70)
    print("🤖 八界机器人 - 玩具收纳（v5 - 简化版）")
    print("=" * 70)
    print(f"📅 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 连接：{WEBSOCKET_URL}")
    print(f"📝 统一 uuid: {TASK_UUID}")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接到机器人")
        
        # 步骤 0: 准备姿态
        if not await robot_prepare_pose(ws, "玩具收纳"):
            print("❌ 准备失败，任务终止")
            return False
        await asyncio.sleep(1)
        
        # 步骤 1: 循环收拾玩具
        print(f"\n{'='*70}")
        print(f"【主循环】搜索 → 抓取 → 放置")
        print(f"{'='*70}")
        
        toy_count = 0
        consecutive_not_found = 0
        loop_count = 0
        
        while loop_count < MAX_LOOPS:
            loop_count += 1
            print(f"\n>>> 第 {loop_count} 次循环 <<<")
            
            # 搜索玩具
            search_success, toy_data = await search_toy(ws, "玩具", "地上")
            
            if not search_success or not toy_data:
                consecutive_not_found += 1
                print(f"🔍 未找到玩具（连续 {consecutive_not_found}/{MAX_CONSECUTIVE_NOT_FOUND} 次）")
                
                if consecutive_not_found >= MAX_CONSECUTIVE_NOT_FOUND:
                    print(f"\n✅ 确认地上没有玩具了")
                    break
            else:
                consecutive_not_found = 0
                toy_count += 1
                print(f"✅ 找到玩具，开始收拾...（已收拾 {toy_count} 个）")
                
                # 抓取
                await asyncio.sleep(1)
                if await accurate_grab(ws, toy_data):
                    # 放置
                    await asyncio.sleep(1)
                    await semantic_place(ws, "玩具", "收纳筐")
                
                await asyncio.sleep(1)
            
            print(f"📊 当前：收拾 {toy_count} 个，循环 {loop_count} 次")
        
        # 步骤 2: 归位
        await robot_ending_pose(ws)
        
        print("\n" + "=" * 70)
        print("✅ 任务完成！")
        print(f"📊 共收拾了 {toy_count} 个玩具")
        print("=" * 70)
        return True


if __name__ == "__main__":
    asyncio.run(main())
