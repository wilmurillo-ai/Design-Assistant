#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 客厅整理多个玩具任务（多玩具循环版 - 全区域导航搜索 + 位置去重 + 过滤收纳筐）

工作流程：
0. robot_prepare_pose(mission_summary: "玩具收纳")
1. 搜索收纳筐 → 等待 finish，记录位置 [只执行一次]
2. 导航到客厅多个搜索点，在每个点搜索玩具：
   - 导航到搜索点 1 → 搜索周围玩具
   - 导航到搜索点 2 → 搜索周围玩具
   - 导航到搜索点 3 → 搜索周围玩具
   - ...
3. 对每个找到的玩具（不在收纳筐内、未处理过）：
   - 抓取玩具 → 等待 finish
   - 放置到收纳筐 → 等待 finish
   - 计数 +1
4. 所有搜索点检查完毕后，再次循环搜索确认没有遗漏
5. robot_ending_pose ← 机械臂归位

关键：
- 任务链最开始执行 prepare 任务
- 收纳筐只搜索一次，后续循环重复使用位置
- 所有子任务使用完全相同的 uuid（共享上下文）
- 每个任务有独立的 task_id
- 每个任务必须等待 finish 消息后才执行下一步
- 导航到客厅多个位置，从不同角度搜索
- 记录已处理的玩具位置，避免重复处理
- 过滤掉收纳筐内的玩具（避免重复抓取）
- 任务链最后执行 ending 任务归位机械臂
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

# 最大搜索点数量
MAX_SEARCH_POINTS = 10

# 收纳筐过滤半径（米）- 如果玩具距离收纳筐小于这个距离，认为是筐内的
BASKET_FILTER_RADIUS = 0.5

# 位置去重阈值（米）- 如果两个玩具位置距离小于这个值，认为是同一个玩具
POSITION_DEDUPLICATION_THRESHOLD = 0.3

# 搜索区域列表 - 按优先级排序（玩具收纳区）
SEARCH_AREAS = [
    "地上",
    "地板",
    "地面",
    "玩具收纳区地上",
    "玩具收纳区地板",
    "玩具收纳区地面",
    "收纳区地上",
    "收纳区地板",
    "地毯",
    "角落"
]

# 玩具收纳区搜索点（语义位置）- 机器人会导航到这些位置搜索
TOY_AREA_SEARCH_POINTS = [
    "玩具收纳区",
    "玩具区",
    "收纳区",
    "玩具收纳区中间",
    "玩具收纳区左边",
    "玩具收纳区右边",
    "玩具收纳区前面",
    "玩具收纳区后面",
    "玩具收纳区角落",
    "玩具区角落"
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
    """计算两个位置之间的水平距离（忽略 Z 轴）"""
    dx = pos1["x"] - pos2["x"]
    dy = pos1["y"] - pos2["y"]
    return math.sqrt(dx * dx + dy * dy)

def is_position_duplicate(new_pos: Dict, processed_positions: List[Dict], threshold: float = POSITION_DEDUPLICATION_THRESHOLD) -> bool:
    """
    检查新位置是否已经处理过
    
    Args:
        new_pos: 新位置 {"x": x, "y": y, "z": z}
        processed_positions: 已处理的位置列表
        threshold: 距离阈值（米）
    
    Returns:
        True 如果这个位置已经处理过
        False 如果是新位置
    """
    for old_pos in processed_positions:
        distance = calculate_distance(new_pos, old_pos)
        if distance <= threshold:
            return True
    return False

def is_toy_in_basket(toy_position: Dict, basket_position: Dict, radius: float = BASKET_FILTER_RADIUS) -> bool:
    """
    检查玩具是否在收纳筐内/附近
    
    Args:
        toy_position: 玩具位置 {"x": x, "y": y, "z": z}
        basket_position: 收纳筐位置 {"x": x, "y": y, "z": z}
        radius: 过滤半径（米）
    
    Returns:
        True 如果玩具在收纳筐内/附近，应该跳过
        False 如果玩具在地上，需要收拾
    """
    distance = calculate_distance(toy_position, basket_position)
    return distance <= radius

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

async def robot_prepare_pose(ws, mission_summary: str) -> bool:
    """步骤 0: 机身准备姿态"""
    print(f"\n【准备】robot_prepare_pose")
    print("-" * 70)
    
    task_id = generate_task_id("prepare")
    print(f"task_id: {task_id}")
    print(f"uuid: {TASK_UUID}")
    print(f"mission_summary: {mission_summary}")
    
    request = build_request("robot_prepare_pose", task_id, {
        "mission_summary": mission_summary
    })
    
    await ws.send(json.dumps(request))
    
    # 等待 finish 消息
    result = await wait_for_finish(ws, "准备姿态", timeout=60)
    
    return result["success"]

async def semantic_navigation(ws, goal_name: str) -> bool:
    """导航到指定位置"""
    print(f"\n【导航】前往 {goal_name}")
    print("-" * 70)
    
    task_id = generate_task_id("nav")
    print(f"task_id: {task_id}")
    print(f"uuid: {TASK_UUID}")
    
    request = build_request("semantic_navigation", task_id, {
        "goal": goal_name
    })
    
    await ws.send(json.dumps(request))
    
    # 等待 finish 消息
    result = await wait_for_finish(ws, f"导航到{goal_name}", timeout=120)
    
    return result["success"]

async def search_object_in_area(ws, object_name: str, area_name: str) -> Optional[Dict]:
    """在指定区域搜索物体"""
    print(f"\n【搜索】{object_name} @ {area_name}")
    print("-" * 70)
    
    task_id = generate_task_id("search")
    print(f"task_id: {task_id}")
    print(f"uuid: {TASK_UUID}")
    
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
    result = await wait_for_finish(ws, f"搜索{object_name}({area_name})")
    
    if result["success"]:
        return result["search_data"]
    else:
        return None

async def search_object_multi_area(ws, object_name: str, areas: List[str]) -> Optional[Dict]:
    """
    在多个区域搜索物体，找到第一个就返回
    
    Args:
        ws: WebSocket 连接
        object_name: 搜索的物体名称
        areas: 区域列表，按优先级排序
    
    Returns:
        找到的物体数据，或 None
    """
    for area in areas:
        result = await search_object_in_area(ws, object_name, area)
        if result:
            print(f"✅ 在区域 '{area}' 找到玩具")
            return result
        # 不打印没找到的区域，减少日志噪音
    
    return None

async def accurate_grab(ws, search_data: Dict) -> bool:
    """精准抓取"""
    print("\n【抓取】玩具")
    print("-" * 70)
    
    task_id = generate_task_id("grab")
    print(f"task_id: {task_id}")
    print(f"uuid: {TASK_UUID}")
    
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
    print(f"uuid: {TASK_UUID}")
    
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

async def robot_ending_pose(ws) -> bool:
    """步骤 N: 机身结束姿态（机械臂归位）"""
    print(f"\n【归位】robot_ending_pose")
    print("-" * 70)
    
    task_id = generate_task_id("ending")
    print(f"task_id: {task_id}")
    print(f"uuid: {TASK_UUID}")
    
    request = build_request("robot_ending_pose", task_id, {})
    
    await ws.send(json.dumps(request))
    
    # 等待 finish 消息
    result = await wait_for_finish(ws, "结束姿态", timeout=60)
    
    return result["success"]

async def process_toy_at_location(ws, toy_data: Dict, basket_position: Dict, processed_positions: List[Dict]) -> Tuple[bool, bool]:
    """
    处理找到的玩具
    
    Returns:
        (是否成功收拾，是否应该跳过)
    """
    toy_position = toy_data["position"]
    
    # 检查是否是已处理过的位置（去重）
    if is_position_duplicate(toy_position, processed_positions):
        print(f"🔄 这个位置的玩具已经处理过（距离阈值 {POSITION_DEDUPLICATION_THRESHOLD} 米内）")
        return (False, True)  # 没收拾，但应该跳过
    
    # 检查玩具是否在收纳筐内
    distance = calculate_distance(toy_position, basket_position)
    print(f"\n📏 玩具距离收纳筐：{distance:.2f} 米")
    
    if is_toy_in_basket(toy_position, basket_position):
        print(f"⚠️  玩具在收纳筐内/附近（距离 {distance:.2f} 米），跳过！")
        processed_positions.append(toy_position)
        return (False, True)  # 没收拾，但应该跳过
    
    # 新玩具，开始收拾
    print(f"✅ 新玩具在地上（距离 {distance:.2f} 米），开始收拾...")
    
    await asyncio.sleep(1)
    
    # 抓取玩具
    grab_success = await accurate_grab(ws, toy_data)
    if not grab_success:
        print("❌ 抓取失败，跳过这个玩具")
        processed_positions.append(toy_position)
        return (False, True)
    
    await asyncio.sleep(1)
    
    # 放置到收纳筐
    place_success = await semantic_place(ws, "玩具", "收纳筐")
    if not place_success:
        print("❌ 放置失败")
        processed_positions.append(toy_position)
        return (False, True)
    
    # 记录已处理的位置
    processed_positions.append(toy_position)
    
    await asyncio.sleep(1)
    
    return (True, False)  # 成功收拾

async def main():
    print("=" * 70)
    print("🤖 八界机器人 - 玩具收纳区整理多个玩具（全区域导航搜索 + 位置去重 + 过滤收纳筐）")
    print("=" * 70)
    print(f"📅 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 连接：{WEBSOCKET_URL}")
    print(f"📝 统一 uuid: {TASK_UUID}")
    print(f"🔢 最大循环次数：{MAX_LOOPS}")
    print(f"🎯 过滤半径：{BASKET_FILTER_RADIUS} 米")
    print(f"🔍 搜索区域：{', '.join(SEARCH_AREAS[:5])}...")
    print(f"🗺️  搜索点数：{len(TOY_AREA_SEARCH_POINTS)}")
    print(f"🔄 位置去重阈值：{POSITION_DEDUPLICATION_THRESHOLD} 米")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接到机器人")
        
        # 步骤 0: 准备姿态
        prepare_success = await robot_prepare_pose(ws, "玩具收纳")
        if not prepare_success:
            print("❌ 准备失败，任务终止")
            return False
        
        await asyncio.sleep(1)
        
        # 步骤 1: 搜索收纳筐（只执行一次）
        print("\n" + "=" * 70)
        print("【阶段 1】搜索收纳筐（只执行一次）")
        print("=" * 70)
        
        basket_data = await search_object_in_area(ws, "收纳筐", "客厅")
        if not basket_data:
            print("❌ 未找到收纳筐，任务终止")
            return False
        
        basket_position = basket_data["position"]
        print(f"💾 收纳筐位置已记录：{basket_position}")
        print(f"🛡️  过滤保护：距离收纳筐 {BASKET_FILTER_RADIUS} 米内的玩具将被跳过")
        
        await asyncio.sleep(1)
        
        # 步骤 2: 导航到客厅各个搜索点，全面搜索玩具
        print("\n" + "=" * 70)
        print("【阶段 2】导航到客厅各个搜索点，全面搜索玩具")
        print("=" * 70)
        
        toy_count = 0
        skip_count = 0
        processed_positions: List[Dict] = []
        
        # 第一轮：导航到各个搜索点搜索
        print(f"\n🗺️  开始遍历 {len(TOY_AREA_SEARCH_POINTS)} 个搜索点...")
        print(f"搜索点列表：{TOY_AREA_SEARCH_POINTS}")
        
        points_attempted = 0
        points_successful = 0
        
        for i, search_point in enumerate(TOY_AREA_SEARCH_POINTS, 1):
            points_attempted += 1
            print(f"\n{'='*70}")
            print(f"【搜索点 {i}/{len(TOY_AREA_SEARCH_POINTS)}】{search_point}")
            print(f"{'='*70}")
            
            # 导航到搜索点
            print(f"🚗 正在导航到 {search_point}...")
            nav_success = await semantic_navigation(ws, search_point)
            if not nav_success:
                print(f"⚠️  导航到 {search_point} 失败，继续下一个点")
                continue
            
            points_successful += 1
            print(f"✅ 成功导航到 {search_point}")
            
            await asyncio.sleep(2)
            
            # 在当前位置搜索玩具
            print(f"🔍 开始在 {search_point} 附近搜索玩具...")
            toy_data = await search_object_multi_area(ws, "玩具", SEARCH_AREAS)
            if not toy_data:
                print(f"📍 在 {search_point} 附近没有发现玩具")
                continue
            
            # 处理找到的玩具
            print(f"🎯 发现玩具，开始处理...")
            success, should_skip = await process_toy_at_location(ws, toy_data, basket_position, processed_positions)
            
            if success:
                toy_count += 1
                print(f"✅ 已收拾 {toy_count} 个玩具")
            elif should_skip:
                skip_count += 1
            
            print(f"📊 当前统计：已收拾 {toy_count} 个，跳过 {skip_count} 个")
        
        print(f"\n🗺️  第一阶段完成：尝试了 {points_attempted} 个搜索点，成功导航 {points_successful} 个")
        
        # 第二轮：再次全面搜索，确认没有遗漏
        print("\n" + "=" * 70)
        print("【阶段 3】再次全面搜索，确认没有遗漏")
        print("=" * 70)
        
        loop_count = 0
        consecutive_not_found = 0
        max_consecutive_not_found = 3  # 连续 3 次没找到，认为收拾完了
        
        while loop_count < MAX_LOOPS:
            loop_count += 1
            
            print(f"\n{'='*70}")
            print(f"【确认搜索 #{loop_count}】")
            print(f"{'='*70}")
            
            # 在多个区域搜索玩具
            toy_data = await search_object_multi_area(ws, "玩具", SEARCH_AREAS)
            
            if not toy_data:
                consecutive_not_found += 1
                print(f"🔍 没有找到玩具（连续 {consecutive_not_found}/{max_consecutive_not_found} 次）")
                
                if consecutive_not_found >= max_consecutive_not_found:
                    print(f"\n✅ 确认地上没有玩具了！")
                    break
            else:
                # 处理找到的玩具
                success, should_skip = await process_toy_at_location(ws, toy_data, basket_position, processed_positions)
                
                if success:
                    consecutive_not_found = 0  # 重置计数器
                    toy_count += 1
                    print(f"✅ 又找到并收拾了 1 个玩具！共 {toy_count} 个")
                elif should_skip:
                    # 找到的玩具被跳过（在收纳筐内或已处理），也算作"没找到需要收拾的玩具"
                    consecutive_not_found += 1
                    skip_count += 1
                    print(f"🔍 玩具被跳过（连续 {consecutive_not_found}/{max_consecutive_not_found} 次未找到需要收拾的）")
                    
                    if consecutive_not_found >= max_consecutive_not_found:
                        print(f"\n✅ 确认地上没有需要收拾的玩具了！")
                        break
            
            print(f"📊 当前统计：已收拾 {toy_count} 个，跳过 {skip_count} 个")
        
        # 检查是否达到最大循环次数
        if loop_count >= MAX_LOOPS:
            print(f"\n⚠️  已达到最大循环次数 ({MAX_LOOPS})，任务结束")
        
        # 步骤 4: 结束姿态（机械臂归位）
        print("\n" + "=" * 70)
        print("【阶段 4】机械臂归位")
        print("=" * 70)
        
        ending_success = await robot_ending_pose(ws)
        if not ending_success:
            print("❌ 归位失败")
            return False
        
        # 任务完成统计
        print("\n" + "=" * 70)
        print("✅ 任务完成！")
        print(f"📊 共收拾了 {toy_count} 个玩具")
        print(f"🛡️  跳过 {skip_count} 个玩具（在收纳筐内或已处理）")
        print(f"📍 共处理 {len(processed_positions)} 个唯一位置")
        print(f"🗺️  搜索了 {len(TOY_AREA_SEARCH_POINTS)} 个搜索点")
        print(f"🔍 确认搜索 {loop_count} 轮")
        print("=" * 70)
        
        return True

if __name__ == "__main__":
    asyncio.run(main())
