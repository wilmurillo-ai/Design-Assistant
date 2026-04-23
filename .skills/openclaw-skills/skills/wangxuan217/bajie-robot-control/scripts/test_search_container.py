#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 search_container 任务
"""

import asyncio
import json
import time
import uuid
import websockets

WEBSOCKET_URL = 'ws://10.10.10.12:9900'

def generate_task_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def build_request(name: str, task_id: str, data: dict) -> dict:
    return {
        'header': {
            'mode': 'mission',
            'type': 'request',
            'cmd': 'start',
            'ts': int(time.time()),
            'uuid': str(uuid.uuid4())
        },
        'body': {
            'name': name,
            'task_id': task_id,
            'data': data
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

async def test_search_container():
    print('=' * 70)
    print('🧪 测试 search_container 任务')
    print('=' * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f'✓ 已连接到机器人：{WEBSOCKET_URL}')
        
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
        
        print(f'\n📤 发送任务：search_container (task_id={task_id})')
        print(f'请求：{json.dumps(request, indent=2, ensure_ascii=False)}')
        await ws.send(json.dumps(request))
        
        print('\n⏳ 等待响应...')
        result = await wait_for_finish(ws, "search_container", timeout=120)
        
        print('\n' + '=' * 70)
        if result['success']:
            print('✅ search_container 成功！')
            if result.get('search_data'):
                print(f'📍 位置：{result["search_data"]["position"]}')
        else:
            print('❌ search_container 失败')
        print('=' * 70)
        
        return result['success']

if __name__ == "__main__":
    success = asyncio.run(test_search_container())
    exit(0 if success else 1)
