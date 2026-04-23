#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 玩具收纳区整理玩具任务（简化版 - 原地搜索）

工作流程：
0. robot_prepare_pose(mission_summary: "玩具收纳")
1. 搜索收纳筐 → 记录位置
2. 循环搜索玩具：
   - 搜索玩具（地上、地板、地面等区域）
   - 如果玩具在收纳筐内 → 跳过
   - 如果位置已处理过 → 跳过
   - 否则：抓取 → 放置到收纳筐
3. 连续 3 次没找到需要收拾的玩具 → 任务完成
4. robot_ending_pose (机械臂归位)

关键：
- 所有子任务使用相同的 uuid（共享上下文）
- 每个任务有独立的 task_id
- 每个任务必须等待 finish 消息后才执行下一步
- 记录已处理的玩具位置，避免重复处理
- 过滤掉收纳筐内的玩具
"""

import asyncio
import json
import time
import uuid
import websockets
import math
from typing import Optional, Dict, List, Tuple

WEBSOCKET_URL = "ws://10.10.10.12:9900"

# 整个任务流程使用相同的 uuid（共享上下文）
TASK_UUID = str(uuid.uuid4())

# 最大循环次数（安全保护）
MAX_LOOPS = 50

# 收纳筐过滤半径（米）
BASKET_FILTER_RADIUS = 0.5

# 位置去重阈值（米）
POSITION_DEDUPLICATION_THRESHOLD = 0.3

# 搜索区域列表
SEARCH_AREAS = ["地上", "地板", "地面", "地毯", "角落"]

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

def calculate_distance(pos1: Dict, pos2: Dict) -> float:
    dx = pos1["x"] - pos2["x"]
    dy = pos1["y"] - pos2["y"]
    return math.sqrt(dx * dx + dy * dy)

def is_position_duplicate(new_pos: Dict, processed_positions: List[Dict], threshold: float = POSITION_DEDUPLICATION_THRESHOLD) -> bool:
    for old_pos in processed_positions:
        if calculate_distance(new_pos, old_pos) <= threshold:
            return True
    return False

def is_toy_in_basket(toy_position: Dict, basket_position: Dict, radius: float = BASKET_FILTER_RADIUS) -> bool:
    return calculate_distance(toy_position, basket_position) <= radius

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
                print(f"❌ {task_name}启动失败：0x{code:08X}")
                return {"success": False, "error_code": code}
        
        elif header["type"] == "notify":
            data = body["data"]
            if "position" in data:
                search_data = data
                print(f"📍 找到物体：位置={data['position']}")
        
        if header["cmd"] == "finish":
            code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            print(f"✅ {task_name}完成：0x{code:08X} - {msg_text}")
            return {"success": code == 0, "error_code": code, "search_data": search_data}
    
    return {"success": False, "error_code": -1}

async def robot_prepare_pose(ws, mission_summary: str) -> bool:
    print(f"\n【准备】robot_prepare_pose")
    print("-" * 70)
    task_id = generate_task_id("prepare")
    request = build_request("robot_prepare_pose", task_id, {"mission_summary": mission_summary})
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, "准备姿态", timeout=60)
    return result["success"]

async def search_object(ws, object_name: str, area_name: str) -> Optional[Dict]:
    print(f"\n【搜索】{object_name} @ {area_name}")
    print("-" * 70)
    task_id = generate_task_id("search")
    request = build_request("search", task_id, {
        "object": {"item": object_name, "color": "", "shape": "", "person": "", "type": [], "subtype": []},
        "area": {"area_name": area_name, "area_id": ""}
    })
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, f"搜索{object_name}({area_name})")
    return result["search_data"] if result["success"] else None

async def search_multi_area(ws, object_name: str, areas: List[str]) -> Optional[Dict]:
    for area in areas:
        result = await search_object(ws, object_name, area)
        if result:
            return result
    return None

async def accurate_grab(ws, search_data: Dict) -> bool:
    print("\n【抓取】玩具")
    print("-" * 70)
    task_id = generate_task_id("grab")
    grab_data = {
        "object": {"rag_id": "", "item": "玩具", "color": "", "shape": "", "person": ""},
        "position": search_data["position"],
        "orientation": search_data["orientation"],
        "box_length": search_data["box_length"],
        "frame_id": search_data["frame_id"]
    }
    print(f"抓取位置：{search_data['position']}")
    request = build_request("accurate_grab", task_id, grab_data)
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, "抓取玩具", timeout=180)
    return result["success"]

async def semantic_place(ws, object_name: str, container_name: str) -> bool:
    print(f"\n【放置】{object_name} → {container_name}")
    print("-" * 70)
    task_id = generate_task_id("place")
    request = build_request("semantic_place", task_id, {
        "area_id": "", "area_name": container_name, "object_name": object_name, "direction": "里"
    })
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, "放置玩具", timeout=180)
    return result["success"]

async def robot_ending_pose(ws) -> bool:
    print(f"\n【归位】robot_ending_pose")
    print("-" * 70)
    task_id = generate_task_id("ending")
    request = build_request("robot_ending_pose", task_id, {})
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, "结束姿态", timeout=60)
    return result["success"]

async def main():
    print("=" * 70)
    print("🤖 八界机器人 - 玩具收纳区整理玩具（简化版）")
    print("=" * 70)
    print(f"📅 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 连接：{WEBSOCKET_URL}")
    print(f"📝 统一 uuid: {TASK_UUID}")
    print(f"🔢 最大循环次数：{MAX_LOOPS}")
    print(f"🎯 过滤半径：{BASKET_FILTER_RADIUS} 米")
    print(f"🔍 搜索区域：{', '.join(SEARCH_AREAS)}")
    print(f"🔄 位置去重阈值：{POSITION_DEDUPLICATION_THRESHOLD} 米")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接到机器人")
        
        # 步骤 0: 准备姿态
        if not await robot_prepare_pose(ws, "玩具收纳"):
            print("❌ 准备失败，任务终止")
            return False
        await asyncio.sleep(1)
        
        # 步骤 1: 搜索收纳筐（可选）
        print("\n" + "=" * 70)
        print("【步骤 1】搜索收纳筐（可选）")
        print("=" * 70)
        basket_data = await search_object(ws, "收纳筐", "客厅")
        basket_position = None
        if basket_data:
            basket_position = basket_data["position"]
            print(f"💾 收纳筐位置：{basket_position}")
        else:
            print("⚠️  未找到收纳筐，将使用默认过滤半径")
        await asyncio.sleep(1)
        
        # 步骤 2: 循环收拾玩具
        print("\n" + "=" * 70)
        print("【步骤 2】循环收拾玩具")
        print("=" * 70)
        
        toy_count = 0
        skip_count = 0
        processed_positions: List[Dict] = []
        consecutive_not_found = 0
        max_consecutive_not_found = 3
        
        loop_count = 0
        while loop_count < MAX_LOOPS:
            loop_count += 1
            print(f"\n{'='*70}")
            print(f"【第 {loop_count} 次循环】")
            print(f"{'='*70}")
            
            # 搜索玩具
            toy_data = await search_multi_area(ws, "玩具", SEARCH_AREAS)
            
            if not toy_data:
                consecutive_not_found += 1
                print(f"🔍 没有找到玩具（连续 {consecutive_not_found}/{max_consecutive_not_found} 次）")
            else:
                toy_position = toy_data["position"]
                
                # 检查是否重复
                if is_position_duplicate(toy_position, processed_positions):
                    print(f"🔄 位置已处理过，跳过")
                    consecutive_not_found += 1
                    skip_count += 1
                # 检查是否在收纳筐内（如果有收纳筐位置）
                elif basket_position and is_toy_in_basket(toy_position, basket_position):
                    distance = calculate_distance(toy_position, basket_position)
                    print(f"⚠️  玩具在收纳筐内（距离 {distance:.2f} 米），跳过")
                    consecutive_not_found += 1
                    skip_count += 1
                    processed_positions.append(toy_position)  # 记录位置，避免重复
                else:
                    # 新玩具，收拾
                    consecutive_not_found = 0  # 重置计数器
                    toy_count += 1
                    print(f"✅ 新玩具，开始收拾...")
                    await asyncio.sleep(1)
                    
                    if await accurate_grab(ws, toy_data):
                        await asyncio.sleep(1)
                        await semantic_place(ws, "玩具", "收纳筐")
                    
                    processed_positions.append(toy_position)
                    await asyncio.sleep(1)
            
            # 检查是否达到连续跳过阈值
            if consecutive_not_found >= max_consecutive_not_found:
                print(f"\n✅ 确认地上没有需要收拾的玩具了！（连续 {consecutive_not_found} 次跳过）")
                break
            
            print(f"📊 统计：收拾 {toy_count} 个，跳过 {skip_count} 个，已处理 {len(processed_positions)} 个位置")
            
            print(f"📊 统计：收拾 {toy_count} 个，跳过 {skip_count} 个，已处理 {len(processed_positions)} 个位置")
        
        # 步骤 3: 归位
        print("\n" + "=" * 70)
        print("【步骤 3】机械臂归位")
        print("=" * 70)
        await robot_ending_pose(ws)
        
        # 完成
        print("\n" + "=" * 70)
        print("✅ 任务完成！")
        print(f"📊 共收拾了 {toy_count} 个玩具")
        print(f"🛡️  跳过 {skip_count} 个玩具")
        print(f"📍 处理 {len(processed_positions)} 个位置")
        print("=" * 70)
        
        return True

if __name__ == "__main__":
    asyncio.run(main())
