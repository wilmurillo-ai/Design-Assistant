#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 玩具收纳任务

任务流程：
1. search_container - 寻找收纳筐（容器）
2. search - 寻找地上的玩具
3. accurate_grab - 抓取玩具
4. semantic_place - 放置玩具到收纳筐

要求：
- 严格串行：等上一个任务 finish 后才开始下一个
- 所有任务 header 中的 uuid 必须相同（同一任务链）
- 任何一步失败直接结束
- 任务链完全结束后再输出各步骤执行结果（只输出一次）
"""

import asyncio
import json
import time
import uuid
import websockets

WEBSOCKET_URL = 'ws://10.10.10.12:9900'

# 任务链 uuid - 所有任务共享
TASK_CHAIN_UUID = str(uuid.uuid4())

# 步骤结果记录
step_results = {}


def generate_task_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def build_request(name: str, task_id: str, data: dict) -> dict:
    """构建请求，所有任务使用相同的 uuid"""
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


async def wait_for_finish(ws, step_display: str, timeout: int = 120):
    """等待任务完成"""
    search_data = None
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            code = body["data"]["error_code"]["code"]
            if code == 0:
                print(f"✓ 启动成功")
            else:
                msg_text = body["data"]["error_code"].get("msg", "")
                print(f"❌ 启动失败：0x{code:08X} - {msg_text}")
                return (False, None, code)
        
        elif header["type"] == "notify":
            data = body["data"]
            if "position" in data:
                search_data = data
                print(f"📍 位置：{data['position']}")
            elif "summary" in data:
                print(f"📋 {data['summary']}")
        
        if header["cmd"] == "finish":
            code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            print(f"📊 完成：0x{code:08X} - {msg_text}")
            return (code == 0, search_data, code)


async def run_task(ws, name: str, data: dict, step_key: str, step_display: str, timeout: int = 120):
    """执行单个任务并记录结果"""
    print(f"\n{'='*70}")
    print(f"{step_display}")
    print(f"{'='*70}")
    
    task_id = generate_task_id(name)
    request = build_request(name, task_id, data)
    
    print(f"📤 任务：{name} (uuid={TASK_CHAIN_UUID[:8]}...)")
    await ws.send(json.dumps(request))
    
    success, search_data, code = await wait_for_finish(ws, step_display, timeout)
    
    if success:
        step_results[step_key] = "✅ 成功"
    else:
        step_results[step_key] = f"❌ 失败 (0x{code:08X})"
    
    return (success, search_data)


async def main():
    global step_results
    
    print('='*70)
    print('🤖 八界机器人 - 玩具收纳任务')
    print('='*70)
    print(f'任务链 uuid: {TASK_CHAIN_UUID}')
    print('='*70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f'✓ 已连接到机器人：{WEBSOCKET_URL}')
        
        # ========== 步骤 1: 搜索收纳筐（容器） ==========
        success, container_data = await run_task(
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
            "step1_search_container",
            "【步骤 1】搜索收纳筐 (search_container)",
            timeout=120
        )
        if not success:
            print(f"\n⏹️  步骤 1 失败，任务链终止")
            print_report()
            return False
        
        await asyncio.sleep(2)
        
        # ========== 步骤 2: 搜索地上玩具 ==========
        success, toy_data = await run_task(
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
            "step2_search_toy",
            "【步骤 2】搜索地上玩具 (search)",
            timeout=120
        )
        if not success:
            print(f"\n⏹️  步骤 2 失败，任务链终止")
            print_report()
            return False
        
        if not toy_data:
            print(f"\n❌ 未获取到玩具位置")
            step_results["step2_search_toy"] = "❌ 失败 (无位置数据)"
            print_report()
            return False
        
        await asyncio.sleep(2)
        
        # ========== 步骤 3: 抓取玩具 ==========
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
        
        success, _ = await run_task(
            ws,
            "accurate_grab",
            grab_data,
            "step3_accurate_grab",
            "【步骤 3】抓取玩具 (accurate_grab)",
            timeout=180
        )
        if not success:
            print(f"\n⏹️  步骤 3 失败，任务链终止")
            print_report()
            return False
        
        await asyncio.sleep(2)
        
        # ========== 步骤 4: 放置玩具到收纳筐 ==========
        place_data = {
            "area_id": "",
            "area_name": "收纳筐",
            "object_name": "玩具",
            "direction": "里"
        }
        
        success, _ = await run_task(
            ws,
            "semantic_place",
            place_data,
            "step4_semantic_place",
            "【步骤 4】放置玩具到收纳筐 (semantic_place)",
            timeout=180
        )
        if not success:
            print(f"\n⏹️  步骤 4 失败，任务链终止")
        
        # ========== 任务链结束，输出执行报告 ==========
        print_report()
        
        return success


def print_report():
    """任务链完全结束后，输出执行报告（只输出一次）"""
    print(f"\n{'='*70}")
    print(f"📊 玩具收纳任务 - 执行报告")
    print(f"{'='*70}")
    print(f"任务链 uuid: {TASK_CHAIN_UUID}")
    print(f"{'-'*70}")
    print(f"步骤 1 - 搜索收纳筐 (search_container):  {step_results.get('step1_search_container', '未执行')}")
    print(f"步骤 2 - 搜索地上玩具 (search):         {step_results.get('step2_search_toy', '未执行')}")
    print(f"步骤 3 - 抓取玩具 (accurate_grab):      {step_results.get('step3_accurate_grab', '未执行')}")
    print(f"步骤 4 - 放置玩具 (semantic_place):    {step_results.get('step4_semantic_place', '未执行')}")
    print(f"{'-'*70}")
    
    all_success = all(
        step_results.get(k, "").startswith("✅")
        for k in ["step1_search_container", "step2_search_toy", "step3_accurate_grab", "step4_semantic_place"]
    )
    if all_success:
        print(f"🎉 任务完成：所有步骤成功！")
    else:
        print(f"⚠️  任务未完成：有步骤失败")
    print(f"{'='*70}")


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
