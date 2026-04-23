#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 寻找收纳筐（容器）并将手上的玩具放进去

流程：
1. 使用 search_container 搜索收纳筐（专用容器搜索任务）
2. 使用 semantic_place 将手上的玩具放置到收纳筐

注意：
- 手上已有玩具，不需要抓取
- 收纳筐属于容器，使用 search_container 任务
- 遵循串行执行原则
- 失败最多重试 1 次
"""

import asyncio
import json
import time
import uuid
import websockets

WEBSOCKET_URL = 'ws://10.10.10.12:9900'

async def wait_for_task(ws, task_name: str, timeout: int = 120) -> dict:
    """等待任务完成，返回结果"""
    search_data = None
    
    while True:
        msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
        response = json.loads(msg)
        header = response["header"]
        body = response["body"]
        
        if header["type"] == "response":
            code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            if code == 0:
                print(f'✓ {task_name}任务启动成功')
            else:
                print(f'❌ {task_name}启动失败：0x{code:08X} - {msg_text}')
                return {"success": False, "error_code": code}
        
        elif header["type"] == "notify":
            data = body["data"]
            if "position" in data:
                search_data = data
                print(f'📍 找到收纳筐！')
                print(f'   position: {data["position"]}')
            elif "summary" in data:
                print(f'📋 执行中：{data["summary"]}')
        
        if header["cmd"] == "finish":
            code = body["data"]["error_code"]["code"]
            msg_text = body["data"]["error_code"].get("msg", "")
            print(f'📊 {task_name}完成：0x{code:08X} - {msg_text}')
            return {"success": code == 0, "error_code": code, "search_data": search_data}


async def search_container(ws, timeout: int = 120):
    """使用 search_container 任务搜索收纳筐"""
    print('\n【步骤 1】寻找收纳筐（使用 search_container）')
    print('-' * 70)
    
    task_id = f'search_container_{uuid.uuid4().hex[:8]}'
    request = {
        'header': {
            'mode': 'mission',
            'type': 'request',
            'cmd': 'start',
            'ts': int(time.time()),
            'uuid': str(uuid.uuid4())
        },
        'body': {
            'name': 'search_container',
            'task_id': task_id,
            'data': {
                'object': {
                    'item': '收纳筐',
                    'color': '',
                    'shape': '',
                    'person': '',
                    'type': [],
                    'subtype': []
                },
                'area': {
                    'area_name': '',
                    'area_id': ''
                }
            }
        }
    }
    
    print(f'Task ID: {task_id}')
    print('搜索目标：收纳筐 (使用 search_container 任务)')
    await ws.send(json.dumps(request))
    return await wait_for_task(ws, "搜索收纳筐", timeout=timeout)


async def semantic_place(ws, max_retries: int = 2) -> bool:
    """放置玩具到收纳筐"""
    print('\n【步骤 2】将手上的玩具放到收纳筐')
    print('-' * 70)
    
    for attempt in range(max_retries):
        if attempt > 0:
            print(f'\n🔄 重试放置（第 {attempt + 1} 次尝试）')
            await asyncio.sleep(2)
        
        task_id = f'place_{uuid.uuid4().hex[:8]}'
        request = {
            'header': {
                'mode': 'mission',
                'type': 'request',
                'cmd': 'start',
                'ts': int(time.time()),
                'uuid': str(uuid.uuid4())
            },
            'body': {
                'name': 'semantic_place',
                'task_id': task_id,
                'data': {
                    'area_id': '',
                    'area_name': '玩具收纳区',
                    'object_name': '玩具',
                    'direction': '里'
                }
            }
        }
        
        print(f'Task ID: {task_id}')
        print(f'放置目标：玩具收纳区 (里)')
        print(f'放置物品：玩具')
        
        await ws.send(json.dumps(request))
        result = await wait_for_task(ws, "放置玩具", timeout=180)
        
        if result['success']:
            return True
        
        if attempt < max_retries - 1:
            print('⚠️  放置失败，准备重试...')
    
    return False


async def main():
    print('=' * 70)
    print('🤖 八界机器人 - 寻找收纳筐并放置玩具')
    print('=' * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        print(f'✓ 已连接到机器人：{WEBSOCKET_URL}')
        
        # 步骤 1: 使用 search_container 搜索收纳筐（增加超时到 120 秒）
        container_result = await search_container(ws, timeout=120)
        if not container_result['success']:
            print('\n❌ 任务失败：未找到收纳筐')
            print('=' * 70)
            return False
        
        await asyncio.sleep(2)
        
        # 步骤 2: 放置玩具（最多尝试 2 次）
        place_success = await semantic_place(ws, max_retries=2)
        
        # 完成
        print('\n' + '=' * 70)
        print('📊 任务总结')
        print('=' * 70)
        if place_success:
            print('✅ 成功！玩具已放到收纳筐中')
        else:
            print('❌ 放置失败，已达到最大重试次数')
        print('=' * 70)
        
        return place_success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
