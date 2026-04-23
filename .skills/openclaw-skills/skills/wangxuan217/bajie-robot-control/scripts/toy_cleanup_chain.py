#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 玩具收纳任务（任务链）

任务流程：
1. robot_prepare_pose - 准备动作，mission_summary="玩具收纳"
2. search_container - 寻找收纳筐（容器）
3. search - 寻找地上的玩具
4. accurate_grab - 抓取玩具
5. semantic_place - 放置玩具到收纳筐

要求：
- 所有子任务 header 中的 uuid 必须相同（同一任务链）
- 严格串行：收到上一个任务成功的 finish 后才开始下一个
- request 后超过 10 秒没收到 response 就认为子任务失败
- 子任务失败则整个任务链结束
- 任务结束后输出总结，包含每个子任务的成功/失败状态、错误码和说明
- 最后一步是放到"收纳筐"而不是"玩具收纳区"
"""

import asyncio
import json
import sys
import time
import uuid
import websockets

WEBSOCKET_URL = 'ws://10.10.10.12:9900'

# 任务链 uuid - 所有子任务共享
TASK_CHAIN_UUID = str(uuid.uuid4())

# 任务链执行记录
task_chain_record = {
    "uuid": TASK_CHAIN_UUID,
    "steps": []
}


def generate_task_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def build_request(name: str, task_id: str, data: dict) -> dict:
    """构建请求，所有子任务使用相同的 uuid"""
    return {
        'header': {
            'mode': 'mission',
            'type': 'request',
            'cmd': 'start',
            'ts': int(time.time()),
            'uuid': TASK_CHAIN_UUID
        },
        'body': {
            'name': name,
            'task_id': task_id,
            'data': data
        }
    }


async def wait_for_response_and_finish(ws, task_name: str, timeout: int = 120):
    """
    等待任务的 response 和 finish
    1. 发送 request 后必须在 10 秒内收到 response
    2. 必须收到 finish 后才返回
    返回：(success, search_data, error_code, error_msg)
    """
    search_data = None
    error_code = 0
    error_msg = ""
    received_response = False
    
    # 阶段 1: 等待 response（最多 10 秒）
    try:
        msg = await asyncio.wait_for(ws.recv(), timeout=10)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            received_response = True
            code = body["data"]["error_code"]["code"]
            error_code = code
            error_msg = body["data"]["error_code"].get("msg", "")
            if code == 0:
                print(f"  ✓ 启动成功")
            else:
                print(f"  ❌ 启动失败：0x{code:08X} - {error_msg}")
                # 启动失败，继续等待 finish
        else:
            print(f"  ❌ 收到非 response 消息：{header['type']}")
            error_code = 0x99999991
            error_msg = "未收到 response"
    except asyncio.TimeoutError:
        print(f"  ❌ 超过 10 秒未收到 response")
        error_code = 0x99999992
        error_msg = "等待 response 超时 (10 秒)"
        return (False, None, error_code, error_msg)
    
    # 阶段 2: 等待 finish（最多 timeout 秒）
    while True:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
            response = json.loads(msg)
            header = response["header"]
            body = response["body"]
            
            if header["type"] == "notify":
                data = body["data"]
                if "position" in data:
                    search_data = data
                    print(f"  📍 位置：{data['position']}")
                elif "summary" in data:
                    print(f"  📋 {data['summary']}")
                elif "mission_summary" in data:
                    print(f"  📋 任务摘要：{data['mission_summary']}")
            
            if header["cmd"] == "finish":
                code = body["data"]["error_code"]["code"]
                error_code = code
                error_msg = body["data"]["error_code"].get("msg", "")
                print(f"  📊 完成：0x{code:08X} - {error_msg}")
                return (code == 0, search_data, error_code, error_msg)
        
        except asyncio.TimeoutError:
            print(f"  ❌ 等待 finish 超时")
            error_code = 0x99999993
            error_msg = "等待 finish 超时"
            return (False, search_data, error_code, error_msg)


async def execute_task(ws, name: str, data: dict, step_name: str, timeout: int = 120):
    """
    执行单个任务并记录结果
    返回：(success, search_data)
    """
    print(f"\n{'='*70}")
    print(f"{step_name}")
    print(f"{'='*70}")
    
    task_id = generate_task_id(name)
    request = build_request(name, task_id, data)
    
    print(f"📤 任务：{name}")
    print(f"   任务链 uuid: {TASK_CHAIN_UUID}")
    print(f"   任务 id: {task_id}")
    
    await ws.send(json.dumps(request))
    
    success, search_data, error_code, error_msg = await wait_for_response_and_finish(ws, name, timeout)
    
    # 记录到任务链
    step_record = {
        "step_name": step_name,
        "task_name": name,
        "task_id": task_id,
        "success": success,
        "error_code": error_code,
        "error_msg": error_msg
    }
    task_chain_record["steps"].append(step_record)
    
    return (success, search_data)


def print_summary():
    """任务链结束后输出总结"""
    print(f"\n{'='*70}", flush=True)
    print(f"📊 玩具收纳任务 - 任务链执行总结", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"任务链 uuid: {TASK_CHAIN_UUID}", flush=True)
    print(f"执行步骤数：{len(task_chain_record['steps'])}", flush=True)
    print(f"{'-'*70}", flush=True)
    
    for i, step in enumerate(task_chain_record["steps"], 1):
        status = "✅ 成功" if step["success"] else "❌ 失败"
        error_info = ""
        if not step["success"]:
            error_info = f" (错误码：0x{step['error_code']:08X} - {step['error_msg']})"
        
        print(f"步骤 {i}: {step['step_name']}", flush=True)
        print(f"   任务：{step['task_name']}", flush=True)
        print(f"   状态：{status}{error_info}", flush=True)
        print(flush=True)
    
    print(f"{'-'*70}", flush=True)
    
    all_success = all(step["success"] for step in task_chain_record["steps"])
    if all_success:
        print(f"🎉 任务链完成：所有子任务成功！", flush=True)
    else:
        failed_steps = [s for s in task_chain_record["steps"] if not s["success"]]
        print(f"⚠️  任务链未完成：{len(failed_steps)} 个子任务失败", flush=True)
    print(f"{'='*70}", flush=True)
    sys.stdout.flush()
    sys.stderr.flush()


async def main():
    print('='*70)
    print('🤖 八界机器人 - 玩具收纳任务（任务链）')
    print('='*70)
    print(f'任务链 uuid: {TASK_CHAIN_UUID}')
    print('='*70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f'✓ 已连接到机器人：{WEBSOCKET_URL}')
        print(f'开始执行玩具收纳任务链...')
        
        # ========== 步骤 1: robot_prepare_pose - 准备动作 ==========
        success, _ = await execute_task(
            ws,
            "robot_prepare_pose",
            {
                "mission_summary": "玩具收纳"
            },
            "准备动作 (robot_prepare_pose)",
            timeout=60
        )
        if not success:
            print(f"\n⏹️  步骤 1 失败，任务链终止", flush=True)
            print_summary()
            sys.exit(1)
        
        await asyncio.sleep(1)
        
        # ========== 步骤 2: search_container - 寻找收纳筐（容器） ==========
        success, container_data = await execute_task(
            ws,
            "search_container",
            {
                "object": {
                    "item": "收纳筐",
                    "color": "",
                    "shape": "",
                    "person": "",
                    "type": [],
                    "subtype": []
                },
                "area": {
                    "area_name": "",
                    "area_id": ""
                }
            },
            "搜索收纳筐 (search_container)",
            timeout=120
        )
        if not success:
            print(f"\n⏹️  步骤 2 失败，任务链终止", flush=True)
            print_summary()
            sys.exit(1)
        
        await asyncio.sleep(1)
        
        # ========== 步骤 3: search - 寻找地上的玩具 ==========
        success, toy_data = await execute_task(
            ws,
            "search",
            {
                "object": {
                    "item": "玩具",
                    "color": "",
                    "shape": "",
                    "person": "",
                    "type": [],
                    "subtype": []
                },
                "area": {
                    "area_name": "地上",
                    "area_id": ""
                }
            },
            "搜索地上玩具 (search)",
            timeout=120
        )
        if not success:
            print(f"\n⏹️  步骤 3 失败，任务链终止", flush=True)
            print_summary()
            sys.exit(1)
        
        if not toy_data:
            print(f"\n❌ 未获取到玩具位置数据", flush=True)
            # 记录失败
            task_chain_record["steps"][-1]["success"] = False
            task_chain_record["steps"][-1]["error_code"] = 0x99999999
            task_chain_record["steps"][-1]["error_msg"] = "未获取到玩具位置数据"
            print_summary()
            sys.exit(1)
        
        await asyncio.sleep(1)
        
        # ========== 步骤 4: accurate_grab - 抓取玩具 ==========
        grab_data = {
            "object": {
                "rag_id": "",
                "item": "玩具",
                "color": "",
                "shape": "",
                "person": ""
            },
            "position": toy_data["position"],
            "orientation": toy_data["orientation"],
            "box_length": toy_data["box_length"],
            "frame_id": toy_data["frame_id"]
        }
        
        success, _ = await execute_task(
            ws,
            "accurate_grab",
            grab_data,
            "抓取玩具 (accurate_grab)",
            timeout=180
        )
        if not success:
            print(f"\n⏹️  步骤 4 失败，任务链终止", flush=True)
            print_summary()
            sys.exit(1)
        
        await asyncio.sleep(1)
        
        # ========== 步骤 5: semantic_place - 放置玩具到收纳筐 ==========
        place_data = {
            "area_id": "",
            "area_name": "收纳筐",
            "object_name": "玩具",
            "direction": "里"
        }
        
        success, _ = await execute_task(
            ws,
            "semantic_place",
            place_data,
            "放置玩具到收纳筐 (semantic_place)",
            timeout=180
        )
        if not success:
            print(f"\n⏹️  步骤 5 失败，任务链终止", flush=True)
        
        # ========== 任务链结束，输出总结 ==========
        print_summary()
        
        # 直接退出，不等待 WebSocket 优雅关闭
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
