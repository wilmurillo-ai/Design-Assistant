#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 玩具收纳任务

完整流程：
1. search_container - 寻找收纳筐（容器）
2. search - 寻找地上的玩具
3. accurate_grab - 抓取玩具
4. semantic_place - 放置玩具到收纳筐

关键要求：
- 严格串行：等上一个任务 finish 后才开始下一个
- 所有任务 header 中的 uuid 必须相同（同一任务链）
- 任何一步失败直接结束
"""

import asyncio
import json
import time
import uuid
import websockets

WEBSOCKET_URL = 'ws://10.10.10.12:9900'

# 任务链 uuid - 所有任务共享
TASK_CHAIN_UUID = str(uuid.uuid4())

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
            'uuid': TASK_CHAIN_UUID  # 同一任务链，uuid 相同
        },
        'body': {
            'name': name,
            'task_id': task_id,
            'data': data
        }
    }

async def wait_for_finish(ws, task_name: str, timeout: int = 120) -> dict:
    """等待任务完成，严格遵循协议流程"""
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
            print(f"📊 {task_name}完成：0x{code:08X} - {msg_text}")
            return {"success": code == 0, "error_code": code, "search_data": search_data}


async def search_container(ws) -> dict:
    """步骤 1: 搜索收纳筐（容器）"""
    print(f"\n{'='*70}")
    print(f"【步骤 1】搜索收纳筐 (search_container)")
    print(f"{'='*70}")
    
    task_id = generate_task_id("search_container")
    request = build_request("search_container", task_id, {
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
    })
    
    print(f"📤 发送任务 (uuid={TASK_CHAIN_UUID[:8]}...)")
    await ws.send(json.dumps(request))
    
    return await wait_for_finish(ws, "搜索收纳筐", timeout=120)


async def search_toy(ws) -> dict:
    """步骤 2: 搜索地上的玩具"""
    print(f"\n{'='*70}")
    print(f"【步骤 2】搜索地上玩具 (search)")
    print(f"{'='*70}")
    
    task_id = generate_task_id("search")
    request = build_request("search", task_id, {
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
    })
    
    print(f"📤 发送任务 (uuid={TASK_CHAIN_UUID[:8]}...)")
    print(f"搜索区域：地上")
    await ws.send(json.dumps(request))
    
    return await wait_for_finish(ws, "搜索玩具", timeout=120)


async def accurate_grab(ws, search_data: dict) -> dict:
    """步骤 3: 抓取玩具"""
    print(f"\n{'='*70}")
    print(f"【步骤 3】抓取玩具 (accurate_grab)")
    print(f"{'='*70}")
    
    task_id = generate_task_id("accurate_grab")
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
    
    request = build_request("accurate_grab", task_id, grab_data)
    
    print(f"📤 发送任务 (uuid={TASK_CHAIN_UUID[:8]}...)")
    print(f"抓取位置：{search_data['position']}")
    await ws.send(json.dumps(request))
    
    return await wait_for_finish(ws, "抓取玩具", timeout=180)


async def semantic_place(ws) -> dict:
    """步骤 4: 放置玩具到收纳筐"""
    print(f"\n{'='*70}")
    print(f"【步骤 4】放置玩具到收纳筐 (semantic_place)")
    print(f"{'='*70}")
    
    task_id = generate_task_id("semantic_place")
    request = build_request("semantic_place", task_id, {
        "area_id": "",
        "area_name": "玩具收纳区",
        "object_name": "玩具",
        "direction": "里"
    })
    
    print(f"📤 发送任务 (uuid={TASK_CHAIN_UUID[:8]}...)")
    print(f"放置目标：玩具收纳区 (里)")
    await ws.send(json.dumps(request))
    
    return await wait_for_finish(ws, "放置玩具", timeout=180)


async def main():
    print('='*70)
    print('🤖 八界机器人 - 玩具收纳任务')
    print('='*70)
    print(f'任务链 uuid: {TASK_CHAIN_UUID}')
    
    # 记录各步骤结果
    results = {
        "step1_search_container": None,
        "step2_search_toy": None,
        "step3_accurate_grab": None,
        "step4_semantic_place": None
    }
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f'✓ 已连接到机器人：{WEBSOCKET_URL}')
        
        # 步骤 1: 搜索收纳筐
        result = await search_container(ws)
        results["step1_search_container"] = "✅ 成功" if result["success"] else f"❌ 失败 (0x{result.get('error_code', 0):08X})"
        if not result["success"]:
            print(f"\n❌ 任务终止：搜索收纳筐失败")
            goto_report(results)
            return False
        
        await asyncio.sleep(2)
        
        # 步骤 2: 搜索地上玩具
        result = await search_toy(ws)
        results["step2_search_toy"] = "✅ 成功" if result["success"] else f"❌ 失败 (0x{result.get('error_code', 0):08X})"
        if not result["success"]:
            print(f"\n❌ 任务终止：搜索玩具失败")
            goto_report(results)
            return False
        
        toy_data = result.get("search_data")
        if not toy_data:
            print(f"\n❌ 任务终止：未获取到玩具位置")
            results["step2_search_toy"] = "❌ 失败 (无位置数据)"
            goto_report(results)
            return False
        
        await asyncio.sleep(2)
        
        # 步骤 3: 抓取玩具
        result = await accurate_grab(ws, toy_data)
        results["step3_accurate_grab"] = "✅ 成功" if result["success"] else f"❌ 失败 (0x{result.get('error_code', 0):08X})"
        if not result["success"]:
            print(f"\n❌ 任务终止：抓取玩具失败")
            goto_report(results)
            return False
        
        await asyncio.sleep(2)
        
        # 步骤 4: 放置玩具
        result = await semantic_place(ws)
        results["step4_semantic_place"] = "✅ 成功" if result["success"] else f"❌ 失败 (0x{result.get('error_code', 0):08X})"
        
        # 完成报告
        goto_report(results)
        
        return result["success"]


def goto_report(results):
    """输出任务报告"""
    print(f"\n{'='*70}")
    print(f"📊 玩具收纳任务 - 执行报告")
    print(f"{'='*70}")
    print(f"任务链 uuid: {TASK_CHAIN_UUID}")
    print(f"{'-'*70}")
    print(f"步骤 1 - 搜索收纳筐 (search_container): {results['step1_search_container']}")
    print(f"步骤 2 - 搜索地上玩具 (search):        {results['step2_search_toy']}")
    print(f"步骤 3 - 抓取玩具 (accurate_grab):     {results['step3_accurate_grab']}")
    print(f"步骤 4 - 放置玩具 (semantic_place):    {results['step4_semantic_place']}")
    print(f"{'-'*70}")
    
    all_success = all(r and r.startswith("✅") for r in results.values())
    if all_success:
        print(f"🎉 任务完成：所有步骤成功！")
    else:
        print(f"⚠️  任务未完成：有步骤失败")
    print(f"{'='*70}")


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
