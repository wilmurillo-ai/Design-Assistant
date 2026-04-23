#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 玩具收纳区整理玩具（v3 - 严格串行版）

工作流程（严格串行）：
0. robot_prepare_pose → 等待 finish
1. search_container(收纳筐 @ 地上) → 等待 finish
   - 成功：继续
   - 失败：任务终止
2. 循环：search(玩具 @ 地上) → 等待 finish
   - 找到：accurate_grab → 等待 finish → semantic_place → 等待 finish → 继续循环
   - 未找到：退出循环
3. robot_ending_pose → 等待 finish

关键：
- 搜索区域只有"地上"
- 每个任务必须等待 finish 后才能执行下一个
- search_container 失败则直接终止任务
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
    """
    等待任务完成，严格遵循协议流程：
    request → response → (notify x N) → finish
    
    必须收到 finish 后才返回，确保严格串行
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
    """
    发送任务并等待 finish，确保严格串行
    """
    request = build_request(name, task_id, data)
    print(f"📤 发送任务：{task_display_name} (task_id={task_id})")
    await ws.send(json.dumps(request))
    result = await wait_for_finish(ws, task_display_name, timeout=timeout)
    return result


async def robot_prepare_pose(ws, mission_summary: str) -> bool:
    """步骤 0: 机身准备姿态"""
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


async def search_container(ws, container_name: str, area_name: str) -> tuple:
    """
    步骤 1: 搜索容器（收纳筐）
    
    严格串行：等待 finish 后才返回
    如果失败，任务链直接终止
    """
    print(f"\n{'='*70}")
    print(f"【步骤 1】搜索收纳筐 (search_container)")
    print(f"{'='*70}")
    
    task_id = generate_task_id("search_container")
    result = await send_task_and_wait(
        ws, "search_container", task_id,
        {
            "object": {
                "item": container_name,
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
        f"搜索容器 ({container_name}@{area_name})", timeout=120
    )
    
    if result["success"]:
        print(f"💾 系统已记录容器位置，后续 search 将自动过滤容器内物体")
        return True, result["search_data"]
    else:
        print(f"❌ 搜索收纳筐失败，任务链终止")
        return False, None


async def search_toy(ws, object_name: str, area_name: str) -> tuple:
    """
    步骤 2.1: 搜索玩具
    
    严格串行：等待 finish 后才返回
    """
    print(f"\n{'='*70}")
    print(f"【步骤 2.1】搜索玩具 (search)")
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
        f"搜索玩具 ({object_name}@{area_name})", timeout=120
    )
    
    return result["success"], result["search_data"]


async def accurate_grab(ws, search_data: Dict) -> bool:
    """
    步骤 2.2: 精准抓取
    
    严格串行：等待 finish 后才返回
    """
    print(f"\n{'='*70}")
    print(f"【步骤 2.2】精准抓取 (accurate_grab)")
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
    """
    步骤 2.3: 放置到收纳筐
    
    严格串行：等待 finish 后才返回
    """
    print(f"\n{'='*70}")
    print(f"【步骤 2.3】放置到收纳筐 (semantic_place)")
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
        f"放置玩具到{container_name}", timeout=180
    )
    
    return result["success"]


async def robot_ending_pose(ws) -> bool:
    """
    步骤 3: 机身结束姿态（机械臂归位）
    
    严格串行：等待 finish 后才返回
    """
    print(f"\n{'='*70}")
    print(f"【步骤 3】机身结束姿态")
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
    print("🤖 八界机器人 - 玩具收纳区整理玩具（v3 - 严格串行版）")
    print("=" * 70)
    print(f"📅 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 连接：{WEBSOCKET_URL}")
    print(f"📝 统一 uuid: {TASK_UUID}")
    print(f"🔍 搜索区域：地上")
    print(f"🔢 最大循环次数：{MAX_LOOPS}")
    print(f"🎯 连续未找到阈值：{MAX_CONSECUTIVE_NOT_FOUND} 次")
    print("=" * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print("✅ 已连接到机器人")
        
        # ========== 步骤 0: 准备姿态 ==========
        prepare_success = await robot_prepare_pose(ws, "玩具收纳")
        if not prepare_success:
            print("❌ 准备姿态失败，任务终止")
            return False
        await asyncio.sleep(1)
        
        # ========== 步骤 1: 搜索收纳筐 ==========
        container_found, container_data = await search_container(ws, "收纳筐", "地上")
        if not container_found:
            print("❌ 搜索收纳筐失败，任务链终止")
            return False
        await asyncio.sleep(1)
        
        # ========== 步骤 2: 循环收拾玩具 ==========
        print(f"\n{'='*70}")
        print(f"【步骤 2】循环收拾玩具（找 → 抓 → 放）")
        print(f"{'='*70}")
        
        toy_count = 0
        consecutive_not_found = 0
        loop_count = 0
        
        while loop_count < MAX_LOOPS:
            loop_count += 1
            print(f"\n>>> 第 {loop_count} 次循环 <<<")
            
            # 步骤 2.1: 搜索玩具（只搜索"地上"）
            search_success, toy_data = await search_toy(ws, "玩具", "地上")
            
            if not search_success or not toy_data:
                consecutive_not_found += 1
                print(f"🔍 未找到玩具（连续 {consecutive_not_found}/{MAX_CONSECUTIVE_NOT_FOUND} 次）")
                
                if consecutive_not_found >= MAX_CONSECUTIVE_NOT_FOUND:
                    print(f"\n✅ 确认地上没有需要收拾的玩具了，退出循环")
                    break
            else:
                # 找到玩具，重置计数器
                consecutive_not_found = 0
                toy_count += 1
                print(f"✅ 找到玩具，开始收拾...（已收拾 {toy_count} 个）")
                
                # 步骤 2.2: 抓取
                await asyncio.sleep(1)
                grab_success = await accurate_grab(ws, toy_data)
                if not grab_success:
                    print("⚠️  抓取失败，继续下一次循环")
                    await asyncio.sleep(1)
                    continue
                
                # 步骤 2.3: 放置
                await asyncio.sleep(1)
                place_success = await semantic_place(ws, "玩具", "收纳筐")
                if not place_success:
                    print("⚠️  放置失败，继续下一次循环")
                
                await asyncio.sleep(1)
            
            print(f"📊 当前统计：收拾 {toy_count} 个，循环 {loop_count} 次")
        
        # ========== 步骤 3: 结束姿态 ==========
        ending_success = await robot_ending_pose(ws)
        if not ending_success:
            print("⚠️  结束姿态失败")
        
        # ========== 任务完成 ==========
        print("\n" + "=" * 70)
        print("✅ 任务完成！")
        print(f"📊 共收拾了 {toy_count} 个玩具")
        print(f"🔄 总循环次数：{loop_count} 次")
        print("=" * 70)
        
        return True


if __name__ == "__main__":
    asyncio.run(main())
