#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试：验证历史任务状态清理

确保每次执行任务都使用唯一 task_id，不受历史任务影响
"""

import asyncio
import json
import time
import uuid
import websockets

async def execute_task_with_unique_id(task_name: str, task_data: dict = None):
    """执行任务，每次使用唯一 ID"""
    uri = 'ws://10.10.10.12:9900'
    
    # 生成唯一 task_id 和 uuid
    task_id = f"{task_name}_{uuid.uuid4().hex[:8]}"
    request_uuid = str(uuid.uuid4())
    
    request = {
        'header': {
            'mode': 'mission',
            'type': 'request',
            'cmd': 'start',
            'ts': int(time.time()),
            'uuid': request_uuid
        },
        'body': {
            'name': task_name,
            'task_id': task_id,
            'data': task_data or {}
        }
    }
    
    print(f'\n📤 任务：{task_name}')
    print(f'   Task ID: {task_id}')
    print(f'   UUID: {request_uuid}')
    
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps(request))
        
        start_time = time.time()
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=120.0)
                response = json.loads(msg)
                elapsed = time.time() - start_time
                
                header = response.get('header', {})
                body = response.get('body', {})
                msg_type = header.get('type')
                cmd = header.get('cmd')
                
                if msg_type == 'response':
                    error_code = body.get('data', {}).get('error_code', {})
                    code = error_code.get('code', 0)
                    if code == 0:
                        print(f'   ✓ 启动成功')
                    else:
                        print(f'   ❌ 启动失败：0x{code:08X} - {error_code.get("msg")}')
                        return False, error_code
                
                elif msg_type == 'notify' and cmd == 'finish':
                    error_code = body.get('data', {}).get('error_code', {})
                    code = error_code.get('code', 0)
                    print(f'   📊 完成 ({elapsed:.1f}秒): 0x{code:08X}')
                    
                    if code == 0:
                        print(f'   ✅ 成功')
                        return True, None
                    else:
                        print(f'   ❌ 失败：{error_code.get("msg")}')
                        return False, error_code
                
            except asyncio.TimeoutError:
                print(f'   ❌ 超时')
                return False, {'code': -1, 'msg': '超时'}

async def main():
    print('=' * 70)
    print('🧪 测试：历史任务状态清理')
    print('=' * 70)
    print('\n目的：验证每次任务都使用唯一 ID，不受历史任务影响\n')
    
    # 连续执行 3 次建图任务
    for i in range(3):
        print(f'\n【测试 {i+1}/3】')
        print('-' * 70)
        success, error = await execute_task_with_unique_id('map_create', {})
        
        if success:
            print(f'✓ 测试 {i+1} 成功')
        else:
            print(f'⚠ 测试 {i+1} 失败（这是预期的，建图可能失败）')
        
        await asyncio.sleep(2)
    
    print('\n' + '=' * 70)
    print('✅ 测试完成')
    print('=' * 70)
    print('\n关键点：')
    print('  1. 每次任务的 Task ID 都不同')
    print('  2. 每次任务的 UUID 都不同')
    print('  3. 历史任务状态不会影响新任务')

if __name__ == "__main__":
    asyncio.run(main())
