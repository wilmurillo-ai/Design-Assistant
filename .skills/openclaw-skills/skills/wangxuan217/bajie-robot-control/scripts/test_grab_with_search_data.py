#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 使用 search 完整数据抓取

直接使用 search 返回的完整数据，不做任何修改
"""

import asyncio
import json
import time
import uuid
import websockets

async def main():
    uri = 'ws://10.10.10.12:9900'
    
    print('=' * 70)
    print('🤖 八界机器人 - 使用 search 完整数据抓取')
    print('=' * 70)
    
    async with websockets.connect(uri) as ws:
        # 步骤 1: 搜索
        print('\n【步骤 1】搜索玩具')
        print('-' * 70)
        
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
                'task_id': f'search_{uuid.uuid4().hex[:8]}',
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
        
        await ws.send(json.dumps(search_request))
        
        search_data = None
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
                response = json.loads(msg)
                header = response.get('header', {})
                body = response.get('body', {})
                
                if header.get('type') == 'notify' and header.get('cmd') == 'notify':
                    search_data = body.get('data', {})
                    print(f'📍 搜索到物体:')
                    print(json.dumps(search_data, indent=2, ensure_ascii=False))
                
                elif header.get('type') == 'notify' and header.get('cmd') == 'finish':
                    error_code = body.get('data', {}).get('error_code', {})
                    if error_code.get('code', 0) == 0:
                        print('✅ 搜索完成')
                    else:
                        print(f'❌ 搜索失败')
                        return
                    break
            except asyncio.TimeoutError:
                print('❌ 超时')
                return
        
        if not search_data:
            print('❌ 未获取到数据')
            return
        
        await asyncio.sleep(2)
        
        # 步骤 2: 直接使用 search 返回的完整数据抓取
        print('\n【步骤 2】抓取玩具（使用 search 完整数据）')
        print('-' * 70)
        
        # 构建抓取数据 - 完全使用 search 返回的数据
        grab_data = {
            'object': {
                'rag_id': '',
                'item': '玩具',
                'color': '',
                'shape': '',
                'person': ''
            },
            'position': search_data['position'],
            'orientation': search_data['orientation'],
            'box_length': search_data['box_length'],
            'frame_id': search_data['frame_id']
        }
        
        print('抓取数据:')
        print(json.dumps(grab_data, indent=2, ensure_ascii=False))
        
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
                'task_id': f'grab_{uuid.uuid4().hex[:8]}',
                'data': grab_data
            }
        }
        
        await ws.send(json.dumps(grab_request))
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=180.0)
                response = json.loads(msg)
                header = response.get('header', {})
                body = response.get('body', {})
                
                if header.get('type') == 'response':
                    error_code = body.get('data', {}).get('error_code', {})
                    code = error_code.get('code', 0)
                    if code == 0:
                        print('✓ 抓取启动成功')
                    else:
                        print(f'❌ 启动失败：0x{code:08X}')
                        break
                
                elif header.get('type') == 'notify' and header.get('cmd') == 'finish':
                    error_code = body.get('data', {}).get('error_code', {})
                    code = error_code.get('code', 0)
                    msg_text = error_code.get('msg', '')
                    
                    print(f'📊 完成：0x{code:08X} - {msg_text}')
                    
                    if code == 0:
                        print('✅ 成功！')
                    else:
                        print('❌ 失败')
                    break
            except asyncio.TimeoutError:
                print('❌ 超时')
                break
        
        print('\n' + '=' * 70)

if __name__ == "__main__":
    asyncio.run(main())
