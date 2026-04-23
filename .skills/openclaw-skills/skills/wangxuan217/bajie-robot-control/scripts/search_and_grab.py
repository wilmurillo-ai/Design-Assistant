#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 搜索并抓取玩具

流程：
1. 使用 search 搜索地上玩具
2. 获取 search 返回的位置数据（position, orientation, box_length, frame_id）
3. 直接使用这些位置数据调用 accurate_grab
"""

import asyncio
import json
import time
import uuid
import websockets

async def search_and_grab():
    """搜索并抓取玩具"""
    uri = 'ws://10.10.10.12:9900'
    
    print('=' * 70)
    print('🤖 八界机器人 - 搜索并抓取玩具')
    print('=' * 70)
    
    async with websockets.connect(uri) as ws:
        # ========== 步骤 1: 搜索玩具 ==========
        print('\n【步骤 1】搜索地上玩具')
        print('-' * 70)
        
        search_task_id = f'search_{uuid.uuid4().hex[:8]}'
        search_request = {
            'header': {
                'mode': 'mission',
                'type': 'request',
                'cmd': 'start',
                'ts': int(time.time()),
                'uuid': str(uuid.uuid4())
            },
            'body': {
                'name': 'search',
                'task_id': search_task_id,
                'data': {
                    'object': {
                        'item': '玩具',
                        'color': '',
                        'shape': '',
                        'person': '',
                        'type': [],
                        'subtype': []
                    },
                    'area': {
                        'area_name': '地上',
                        'area_id': ''
                    }
                }
            }
        }
        
        print(f'Task ID: {search_task_id}')
        await ws.send(json.dumps(search_request))
        
        # 保存 search 返回的位置数据
        search_position_data = None
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
                response = json.loads(msg)
                header = response.get('header', {})
                body = response.get('body', {})
                msg_type = header.get('type')
                cmd = header.get('cmd')
                
                if msg_type == 'response':
                    error_code = body.get('data', {}).get('error_code', {})
                    code = error_code.get('code', 0)
                    if code == 0:
                        print('✓ 搜索任务启动成功')
                    else:
                        print(f'❌ 启动失败：0x{code:08X} - {error_code.get("msg")}')
                        return False
                
                elif msg_type == 'notify' and cmd == 'notify':
                    # 保存 search 返回的完整位置数据
                    search_position_data = body.get('data', {})
                    print(f'\n📍 找到玩具！')
                    print(f'   position: {search_position_data.get("position")}')
                    print(f'   orientation: {search_position_data.get("orientation")}')
                    print(f'   box_length: {search_position_data.get("box_length")}')
                    print(f'   frame_id: {search_position_data.get("frame_id")}')
                
                elif msg_type == 'notify' and cmd == 'finish':
                    error_code = body.get('data', {}).get('error_code', {})
                    code = error_code.get('code', 0)
                    msg_text = error_code.get('msg', '')
                    
                    print(f'\n📊 搜索完成')
                    print(f'   错误码：0x{code:08X}')
                    print(f'   错误信息：{msg_text}')
                    
                    if code != 0:
                        print('❌ 搜索失败')
                        return False
                    break
                
            except asyncio.TimeoutError:
                print('❌ 超时')
                return False
        
        if not search_position_data:
            print('❌ 未获取到玩具位置')
            return False
        
        # 等待一下再执行抓取
        await asyncio.sleep(2)
        
        # ========== 步骤 2: 使用 search 返回的位置数据抓取 ==========
        print('\n【步骤 2】抓取玩具')
        print('-' * 70)
        
        # 直接使用 search 返回的位置数据
        grab_data = {
            'object': {
                'rag_id': '',  # search 没有返回 rag_id，使用空字符串
                'item': '玩具',
                'color': '',
                'shape': '',
                'person': ''
            },
            # 直接使用 search 返回的位置数据
            'position': search_position_data.get('position', {'x': 0, 'y': 0, 'z': 0}),
            'orientation': search_position_data.get('orientation', {'x': 0, 'y': 0, 'z': 0, 'w': 1}),
            'box_length': search_position_data.get('box_length', {'x': 0.15, 'y': 0.15, 'z': 0.15}),
            'frame_id': search_position_data.get('frame_id', 'map')
        }
        
        print(f'抓取位置数据:')
        print(f'  position: {grab_data["position"]}')
        print(f'  orientation: {grab_data["orientation"]}')
        print(f'  box_length: {grab_data["box_length"]}')
        print(f'  frame_id: {grab_data["frame_id"]}')
        
        grab_task_id = f'grab_{uuid.uuid4().hex[:8]}'
        grab_request = {
            'header': {
                'mode': 'mission',
                'type': 'request',
                'cmd': 'start',
                'ts': int(time.time()),
                'uuid': str(uuid.uuid4())
            },
            'body': {
                'name': 'accurate_grab',
                'task_id': grab_task_id,
                'data': grab_data
            }
        }
        
        print(f'\nTask ID: {grab_task_id}')
        await ws.send(json.dumps(grab_request))
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=180.0)
                response = json.loads(msg)
                header = response.get('header', {})
                body = response.get('body', {})
                msg_type = header.get('type')
                cmd = header.get('cmd')
                
                if msg_type == 'response':
                    error_code = body.get('data', {}).get('error_code', {})
                    code = error_code.get('code', 0)
                    if code == 0:
                        print('✓ 抓取任务启动成功')
                        print('⏳ 等待执行完成...')
                    else:
                        print(f'❌ 启动失败：0x{code:08X} - {error_code.get("msg")}')
                        return False
                
                elif msg_type == 'notify' and cmd == 'finish':
                    error_code = body.get('data', {}).get('error_code', {})
                    code = error_code.get('code', 0)
                    msg_text = error_code.get('msg', '')
                    
                    print(f'\n📊 抓取完成')
                    print(f'   错误码：0x{code:08X}')
                    print(f'   错误信息：{msg_text}')
                    
                    if code == 0:
                        print('\n✅ 成功！玩具已抓起')
                        return True
                    else:
                        print('\n❌ 抓取失败')
                        return False
                
            except asyncio.TimeoutError:
                print('❌ 超时')
                return False
        
        print('\n' + '=' * 70)

async def main():
    success = await search_and_grab()
    
    print('\n' + '=' * 70)
    print('📊 任务总结')
    print('=' * 70)
    status = "✅ 成功" if success else "❌ 失败"
    print(f'搜索 + 抓取：{status}')
    print('=' * 70)

if __name__ == "__main__":
    asyncio.run(main())
