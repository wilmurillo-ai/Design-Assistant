#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 客厅整理玩具任务

任务流程：
1. 订阅机器人状态
2. 导航到客厅
3. 搜索玩具（获取位置）
4. 搜索收纳筐（获取位置）
5. 抓取玩具
6. 放置到收纳筐
7. 循环直到所有玩具处理完
"""

import asyncio
import json
import time
import uuid
import websockets
from typing import Optional, Dict, Any

# ========== 配置 ==========
WEBSOCKET_URL = "ws://10.10.10.12:9900"

# ========== 协议工具函数 ==========

def generate_task_id(prefix: str) -> str:
    """生成唯一任务 ID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def generate_uuid() -> str:
    """生成唯一 UUID"""
    return str(uuid.uuid4())

def build_request(name: str, task_id: str, data: Dict, cmd: str = "start") -> Dict:
    """构建请求消息"""
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

def build_event_request(name: str, task_id: str, data: Dict, cmd: str = "subscribe") -> Dict:
    """构建事件请求消息"""
    return {
        "header": {
            "mode": "event",
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

# ========== 任务执行函数 ==========

async def subscribe_robot_state(ws):
    """步骤 1: 订阅机器人状态"""
    print("\n【步骤 1】订阅机器人状态")
    print("-" * 70)
    
    task_id = generate_task_id("subscribe")
    request = build_event_request("robot_info", task_id, {})
    
    await ws.send(json.dumps(request))
    
    # 等待响应或 report 消息
    try:
        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
        response = json.loads(msg)
        header = response["header"]
        
        print(f"收到消息类型：{header.get('type')}")
        
        if header["type"] == "response" or header["type"] == "notify":
            print("✅ 订阅成功")
            return True
        else:
            print(f"⚠️  收到未知类型：{header}")
            return True  # 继续执行
    except asyncio.TimeoutError:
        print("⚠️  订阅响应超时，继续执行")
        return True  # 继续执行，订阅不是必须的

async def get_robot_state_oneshot(ws) -> Optional[Dict]:
    """获取机器人单次状态（电量、位置等）"""
    print("\n【电量检查】")
    print("-" * 70)
    
    task_id = generate_task_id("oneshot")
    request = build_event_request("robot_info", task_id, {
        "topics": ["pos", "battery", "workState"]
    })
    
    await ws.send(json.dumps(request))
    
    msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
    response = json.loads(msg)
    
    if response["header"]["type"] == "response":
        data = response["body"]["data"]
        battery = data.get("battery", {})
        pos = data.get("pos", {})
        
        print(f"📍 位置：{pos.get('room', '未知')}")
        print(f"🔋 电量：{battery.get('value', 0)}%")
        
        if battery.get('value', 100) < 30:
            print("⚠️  电量低于 30%，建议先回充")
            return {"low_battery": True, **data}
        
        return {"low_battery": False, **data}
    else:
        print("❌ 获取状态失败")
        return None

async def navigate_to_living_room(ws) -> bool:
    """步骤 2: 导航到客厅"""
    print("\n【步骤 2】导航到客厅")
    print("-" * 70)
    
    task_id = generate_task_id("nav")
    request = build_request("semantic_navigation", task_id, {
        "goal": "客厅",
        "goal_id": ""
    })
    
    await ws.send(json.dumps(request))
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            error_code = body["data"]["error_code"]["code"]
            if error_code == 0:
                print("✓ 导航任务启动成功")
            else:
                print(f"❌ 导航启动失败：0x{error_code:08X}")
                return False
        
        elif header["type"] == "notify" and header["cmd"] == "notify":
            # 导航进度通知
            summary = body["data"].get("summary", "")
            if summary:
                print(f"📍 导航中：{summary}")
        
        elif header["type"] == "notify" and header["cmd"] == "finish":
            error_code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            
            if error_code == 0:
                print("✅ 已到达客厅")
                return True
            else:
                print(f"❌ 导航失败：0x{error_code:08X} - {msg_text}")
                return False
    
    return False

async def search_object(ws, object_name: str, area_name: str) -> Optional[Dict]:
    """步骤 3/4: 搜索物体（返回 notify 数据）"""
    print(f"\n【搜索】{object_name}")
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
        msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            error_code = body["data"]["error_code"]["code"]
            if error_code == 0:
                print(f"✓ 搜索{object_name}任务启动成功")
            else:
                print(f"❌ 搜索启动失败：0x{error_code:08X}")
                return None
        
        elif header["type"] == "notify" and header["cmd"] == "notify":
            # 搜索到物体的 6D 位姿数据
            search_data = body["data"]
            print(f"📍 找到{object_name}:")
            print(f"   位置：{search_data.get('position', {})}")
            print(f"   朝向：{search_data.get('orientation', {})}")
            print(f"   尺寸：{search_data.get('box_length', {})}")
        
        elif header["type"] == "notify" and header["cmd"] == "finish":
            error_code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            
            if error_code == 0:
                print(f"✅ {object_name}搜索完成")
            else:
                print(f"❌ {object_name}搜索失败：0x{error_code:08X} - {msg_text}")
            
            break
    
    return search_data

async def accurate_grab(ws, search_data: Dict) -> bool:
    """步骤 5: 精准抓取（使用 search 返回的完整数据）"""
    print("\n【步骤 5】抓取玩具")
    print("-" * 70)
    
    task_id = generate_task_id("grab")
    
    # 构建抓取数据 - 完全使用 search 返回的数据
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
    
    print("抓取数据:")
    print(json.dumps(grab_data, indent=2, ensure_ascii=False))
    
    request = build_request("accurate_grab", task_id, grab_data)
    
    await ws.send(json.dumps(request))
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=180.0)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            error_code = body["data"]["error_code"]["code"]
            if error_code == 0:
                print("✓ 抓取任务启动成功")
            else:
                print(f"❌ 抓取启动失败：0x{error_code:08X}")
                return False
        
        elif header["type"] == "notify" and header["cmd"] == "notify":
            summary = body["data"].get("summary", "")
            if summary:
                print(f"🤖 抓取中：{summary}")
        
        elif header["type"] == "notify" and header["cmd"] == "finish":
            error_code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            
            print(f"📊 完成：0x{error_code:08X} - {msg_text}")
            
            if error_code == 0:
                print("✅ 抓取成功！")
                return True
            else:
                print("❌ 抓取失败")
                return False
    
    return False

async def semantic_place(ws, object_name: str, container_name: str, direction: str = "里") -> bool:
    """步骤 6: 推荐放置"""
    print(f"\n【步骤 6】放置{object_name}到{container_name}")
    print("-" * 70)
    
    task_id = generate_task_id("place")
    request = build_request("semantic_place", task_id, {
        "area_id": "",
        "area_name": container_name,
        "object_name": object_name,
        "direction": direction
    })
    
    await ws.send(json.dumps(request))
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=180.0)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            error_code = body["data"]["error_code"]["code"]
            if error_code == 0:
                print("✓ 放置任务启动成功")
            else:
                print(f"❌ 放置启动失败：0x{error_code:08X}")
                return False
        
        elif header["type"] == "notify" and header["cmd"] == "notify":
            summary = body["data"].get("summary", "")
            if summary:
                print(f"🤖 放置中：{summary}")
        
        elif header["type"] == "notify" and header["cmd"] == "finish":
            error_code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            
            print(f"📊 完成：0x{error_code:08X} - {msg_text}")
            
            if error_code == 0:
                print(f"✅ 已将{object_name}放到{container_name}{direction}！")
                return True
            else:
                print(f"❌ 放置失败")
                return False
    
    return False

# ========== 主任务流程 ==========

async def cleanup_toys_task():
    """主任务：客厅整理玩具"""
    print("=" * 70)
    print("🤖 八界机器人 - 客厅整理玩具任务")
    print("=" * 70)
    print(f"📅 时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 连接：{WEBSOCKET_URL}")
    print("=" * 70)
    
    try:
        async with websockets.connect(WEBSOCKET_URL) as ws:
            print("✅ 已连接到机器人")
            
            # 步骤 1: 订阅状态
            await subscribe_robot_state(ws)
            
            # 步骤 1.5: 检查电量
            state = await get_robot_state_oneshot(ws)
            if state and state.get("low_battery"):
                print("⚠️  电量不足，建议先回充")
                # 可以选择回充或继续
            
            # 步骤 2: 导航到客厅
            if not await navigate_to_living_room(ws):
                print("❌ 导航失败，任务终止")
                return False
            
            # 步骤 3: 搜索玩具
            toy_data = await search_object(ws, "玩具", "地上")
            if not toy_data:
                print("❌ 未找到玩具，任务终止")
                return False
            
            # 步骤 4: 搜索收纳筐
            basket_data = await search_object(ws, "收纳筐", "客厅")
            if not basket_data:
                print("❌ 未找到收纳筐，任务终止")
                return False
            
            # 步骤 5: 抓取玩具
            if not await accurate_grab(ws, toy_data):
                print("❌ 抓取失败，任务终止")
                return False
            
            # 步骤 6: 放置到收纳筐
            if not await semantic_place(ws, "玩具", "收纳筐", "里"):
                print("❌ 放置失败，任务终止")
                return False
            
            print("\n" + "=" * 70)
            print("✅ 任务完成！客厅的玩具已整理到收纳筐里")
            print("=" * 70)
            return True
            
    except websockets.exceptions.ConnectionClosed:
        print("\n❌ 连接断开")
        return False
    except asyncio.TimeoutError:
        print("\n❌ 超时")
        return False
    except Exception as e:
        print(f"\n❌ 异常：{e}")
        return False

if __name__ == "__main__":
    asyncio.run(cleanup_toys_task())
