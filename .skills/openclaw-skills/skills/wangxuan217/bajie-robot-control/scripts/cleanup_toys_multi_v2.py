#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 玩具收纳区整理多个玩具任务（多玩具循环版 - v2 修复版）

工作流程：
0. robot_prepare_pose(mission_summary: "玩具收纳")
1. 搜索收纳筐 → 等待 finish，记录位置 [只执行一次]
2. 循环搜索玩具：
   - 搜索玩具（地上、地板、地面等区域）
   - 如果玩具在收纳筐内 → 跳过，计数器 +1
   - 如果位置已处理过 → 跳过，计数器 +1
   - 否则：抓取 → 放置到收纳筐，重置计数器
   - 连续 3 次跳过 → 任务完成
3. robot_ending_pose ← 机械臂归位

关键：
- 任务链最开始执行 prepare 任务
- 收纳筐只搜索一次，后续循环重复使用位置
- 所有子任务使用完全相同的 uuid（共享上下文）
- 每个任务有独立的 task_id
- 每个任务必须等待 finish 消息后才执行下一步
- 记录已处理的玩具位置，避免重复处理
- 过滤掉收纳筐内的玩具（避免重复抓取）
- 连续 3 次没有找到需要收拾的玩具 → 任务完成
- 任务链最后执行 ending 任务归位机械臂
"""

import asyncio
import json
import time
import uuid
import websockets
import math
from typing import Optional, Dict, List

WEBSOCKET_URL = "ws://10.10.10.12:9900"

# 整个任务流程使用相同的 uuid（共享上下文）
TASK_UUID = str(uuid.uuid4())

# 最大循环次数（安全保护）
MAX_LOOPS = 50

# 收纳筐过滤半径（米）- 如果玩具距离收纳筐小于这个距离，认为是筐内的（已经装好的）
# 注意：这个值要小，避免把地上靠近收纳筐的玩具误判为筐内
BASKET_FILTER_RADIUS = 0.15

# 位置去重阈值（米）- 如果两个玩具位置距离小于这个值，认为是同一个玩具
POSITION_DEDUPLICATION_THRESHOLD = 0.3

# 连续跳过阈值 - 连续 3 次没有找到需要收拾的玩具，任务完成
MAX_CONSECUTIVE_SKIP = 3

# 确认搜索轮数 - 收拾完玩具后，额外搜索这么多轮确认没有遗漏
CONFIRM_SEARCH_ROUNDS = 3

# 搜索区域列表 - 全面覆盖玩具收纳区
SEARCH_AREAS = [
    # 通用区域
    "地上",
    "地板",
    "地面",
    "地毯",
    "角落",
    # 玩具收纳区特定区域
    "玩具收纳区地上",
    "玩具收纳区地板",
    "玩具收纳区地面",
    "玩具收纳区",
    # 收纳区特定区域
    "收纳区地上",
    "收纳区地板",
    "收纳区地面",
    "收纳区",
    # 玩具区特定区域
    "玩具区地上",
    "玩具区地板",
    "玩具区地面",
    "玩具区",
    # 其他可能区域
    "玩具收纳区角落",
    "收纳区角落",
    "玩具区角落",
    "客厅地上",
    "客厅地板",
    "客厅地面"
]

# 搜索点列表 - 机器人会尝试导航到这些位置搜索（增加搜索覆盖）
SEARCH_POSITIONS = [
    "玩具收纳区",
    "玩具收纳区中间",
    "玩具收纳区左边",
    "玩具收纳区右边",
    "玩具收纳区前面",
    "玩具收纳区后面"
]

def generate_task_id(prefix: str) -> str:
    """每个任务生成独立的 task_id"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def build_request(name: str, task_id: str, data: dict) -> dict:
    """所有子任务使用相同的 TASK_UUID"""
    return {
        "header": {
            "mode": "mission",
            "type": "request",
            "cmd": "start",
            "ts": int(time.time()),
            "uuid": TASK_UUID  # 统一 uuid
        },
        "body": {
            "name": name,
            "task_id": task_id,
            "data": data
        }
    }

def calculate_distance(pos1: Dict, pos2: Dict) -> float:
    """计算两个位置之间的距离"""
    dx = pos1["x"] - pos2["x"]
    dy = pos1["y"] - pos2["y"]
    return math.sqrt(dx * dx + dy * dy)

def is_position_duplicate(new_pos: Dict, processed_positions: List[Dict], threshold: float = POSITION_DEDUPLICATION_THRESHOLD) -> bool:
    """检查位置是否已处理过"""
    for old_pos in processed_positions:
        if calculate_distance(new_pos, old_pos) <= threshold:
            return True
    return False

def is_toy_in_basket(toy_position: Dict, basket_position: Dict, radius: float = BASKET_FILTER_RADIUS) -> bool:
    """检查玩具是否在收纳筐内"""
    return calculate_distance(toy_position, basket_position) <= radius

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
                print(f"📍 找到物体：位置={data['position']}")
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

async def robot_prepare_pose(ws, mission_summary: str) -> bool:
    """步骤 0: 机身准备姿态"""
    print(f"\n【准备】robot_prepare_pose")
    print("-" * 70)
    
    task_id = generate_task_id("prepare")
    request = build_request("robot_prepare_pose", task_id, {
        "mission_summary": mission_summary
    })
    
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, "准备姿态", timeout=60)
    
    return result["success"]

async def search_object(ws, object_name: str, area_name: str) -> Optional[Dict]:
    """搜索物体（使用 search 任务）"""
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
    result = await wait_for_finish(ws, f"搜索{object_name}({area_name})")
    
    if result["success"]:
        return result["search_data"]
    else:
        return None

async def search_container(ws, container_name: str, area_name: str) -> Optional[Dict]:
    """搜索容器（使用 search_container 任务）"""
    print(f"\n【搜索容器】{container_name} @ {area_name}")
    print("-" * 70)
    
    task_id = generate_task_id("search_container")
    request = build_request("search_container", task_id, {
        "object": {
            "item": container_name,
            "color": "",
            "shape": "",
            "person": ""
        },
        "area_info": [
            {
                "area_id": "",
                "area_name": area_name
            }
        ]
    })
    
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, f"搜索容器{container_name}({area_name})")
    
    if result["success"]:
        return result["search_data"]
    else:
        return None

async def search_object_rotate(ws, object_name: str, area_name: str, angle: int = 0) -> Optional[Dict]:
    """搜索物体（带旋转角度）"""
    print(f"\n【搜索】{object_name} @ {area_name} (旋转{angle}°)")
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
            "area_id": "",
            "angle": angle  # 添加旋转角度
        }
    })
    
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, f"搜索{object_name}({area_name}, {angle}°)")
    
    if result["success"]:
        return result["search_data"]
    else:
        return None

async def search_multi_area(ws, object_name: str, areas: List[str], start_index: int = 0) -> Optional[Dict]:
    """在多个区域搜索物体，找到第一个就返回，从指定索引开始"""
    # 从指定索引开始，循环遍历所有区域
    for i in range(len(areas)):
        area_index = (start_index + i) % len(areas)
        area = areas[area_index]
        result = await search_object(ws, object_name, area)
        if result:
            return result
    return None

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
    result = await wait_for_finish(ws, "抓取玩具", timeout=180)
    
    return result["success"]

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
    result = await wait_for_finish(ws, "放置玩具", timeout=180)
    
    return result["success"]

async def robot_ending_pose(ws) -> bool:
    """步骤 5: 机身结束姿态（机械臂归位）"""
    print(f"\n【归位】robot_ending_pose")
    print("-" * 70)
    
    task_id = generate_task_id("ending")
    request = build_request("robot_ending_pose", task_id, {})
    
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, "结束姿态", timeout=60)
    
    return result["success"]

async def main():
    print("=" * 70)
    print("🤖 八界机器人 - 玩具收纳区整理玩具（多玩具循环版 - v2 修复版）")
    print("=" * 70)
    print(f"📅 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 连接：{WEBSOCKET_URL}")
    print(f"📝 统一 uuid: {TASK_UUID}")
    print(f"🔢 最大循环次数：{MAX_LOOPS}")
    print(f"🎯 过滤半径：{BASKET_FILTER_RADIUS} 米")
    print(f"🔍 搜索区域：{', '.join(SEARCH_AREAS)}")
    print(f"🔄 位置去重阈值：{POSITION_DEDUPLICATION_THRESHOLD} 米")
    print(f"⏹️  连续跳过阈值：{MAX_CONSECUTIVE_SKIP} 次")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接到机器人")
        
        # 步骤 0: 准备姿态
        prepare_success = await robot_prepare_pose(ws, "玩具收纳")
        if not prepare_success:
            print("❌ 准备失败，任务终止")
            return False
        
        await asyncio.sleep(1)
        
        # 步骤 1: 搜索收纳筐（使用 search 接口）
        print("\n" + "=" * 70)
        print("【步骤 1】搜索收纳筐")
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
        consecutive_no_new_toy = 0  # 连续没有新玩具需要收拾的次数
        search_area_index = 0  # 搜索区域起始索引，每次循环轮换
        confirm_search_count = 0  # 确认搜索次数（收拾完玩具后的额外搜索）
        
        loop_count = 0
        while loop_count < MAX_LOOPS:
            loop_count += 1
            print(f"\n{'='*70}")
            print(f"【第 {loop_count} 次循环】")
            print(f"{'='*70}")
            
            # 搜索玩具（从不同区域开始，增加覆盖范围）
            print(f"🔍 从搜索区域 #{search_area_index} 开始搜索...")
            toy_data = await search_multi_area(ws, "玩具", SEARCH_AREAS, search_area_index)
            
            # 轮换搜索起始区域（下次从下一个区域开始）
            search_area_index = (search_area_index + 1) % len(SEARCH_AREAS)
            
            if not toy_data:
                # 真正没找到玩具
                print(f"🔍 没有找到玩具")
                consecutive_no_new_toy += 1
            else:
                # 找到了玩具
                toy_position = toy_data["position"]
                
                # 检查是否重复
                if is_position_duplicate(toy_position, processed_positions):
                    print(f"🔄 位置已处理过，跳过")
                    skip_count += 1
                    consecutive_no_new_toy += 1  # 没有新玩具
                # 检查是否在收纳筐内（如果有收纳筐位置）
                elif basket_position and is_toy_in_basket(toy_position, basket_position):
                    distance = calculate_distance(toy_position, basket_position)
                    print(f"⚠️  玩具在收纳筐内（距离 {distance:.2f} 米），跳过")
                    skip_count += 1
                    processed_positions.append(toy_position)  # 记录位置，避免重复
                    # 注意：在收纳筐内的玩具不增加连续计数器！
                    # 因为这说明搜索功能正常，只是这个玩具不需要收拾
                    print(f"📊 连续没有新玩具次数不变（收纳筐内玩具不算）")
                else:
                    # 新玩具，收拾
                    print(f"✅ 新玩具，开始收拾...")
                    await asyncio.sleep(1)
                    
                    if await accurate_grab(ws, toy_data):
                        await asyncio.sleep(1)
                        await semantic_place(ws, "玩具", "收纳筐")
                    
                    processed_positions.append(toy_position)
                    toy_count += 1
                    consecutive_no_new_toy = 0  # 有新玩具，重置计数器
                    confirm_search_count = 0  # 重置确认搜索计数
                    print(f"🔍 收拾完玩具，开始 {CONFIRM_SEARCH_ROUNDS} 轮确认搜索...")
                    await asyncio.sleep(1)
            
            # 检查是否达到连续没有新玩具阈值
            print(f"\n📊 统计：收拾 {toy_count} 个，跳过 {skip_count} 个，连续没有新玩具 {consecutive_no_new_toy}/{MAX_CONSECUTIVE_SKIP} 次，确认搜索 {confirm_search_count}/{CONFIRM_SEARCH_ROUNDS} 轮")
            
            if consecutive_no_new_toy >= MAX_CONSECUTIVE_SKIP:
                # 达到阈值，开始确认搜索
                confirm_search_count += 1
                if confirm_search_count >= CONFIRM_SEARCH_ROUNDS:
                    print(f"\n✅ 确认地上没有需要收拾的玩具了！（连续 {consecutive_no_new_toy} 次没有新玩具 + {confirm_search_count} 轮确认搜索）")
                    break
                else:
                    print(f"🔍 继续确认搜索 #{confirm_search_count + 1}/{CONFIRM_SEARCH_ROUNDS}...")
        
        # 检查是否达到最大循环次数
        if loop_count >= MAX_LOOPS:
            print(f"\n⚠️  已达到最大循环次数 ({MAX_LOOPS})，任务结束")
        
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
        print(f"🔁 循环 {loop_count} 次")
        print("=" * 70)
        
        return True

if __name__ == "__main__":
    asyncio.run(main())
