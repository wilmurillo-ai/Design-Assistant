#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 检查家具地图和收纳筐位置 (oneshot 方式)
"""

import asyncio
import json
import time
import uuid
import websockets

WEBSOCKET_URL = 'ws://10.10.10.12:9900'

async def check_furniture():
    """检查家具地图"""
    print('=' * 70)
    print('🤖 八界机器人 - 检查家具地图')
    print('=' * 70)
    
    async with websockets.connect(WEBSOCKET_URL) as ws:
        # 使用 oneshot 获取机器状态
        oneshot_task_id = f'oneshot_{uuid.uuid4().hex[:8]}'
        oneshot_request = {
            'header': {
                'mode': 'event',
                'type': 'request',
                'cmd': 'oneshot',
                'ts': int(time.time()),
                'uuid': str(uuid.uuid4())
            },
            'body': {
                'name': 'robot_info',
                'task_id': oneshot_task_id,
                'data': {
                    'topics': ['furniture', 'pos', 'battery']
                }
            }
        }
        
        print('获取机器状态...')
        await ws.send(json.dumps(oneshot_request))
        
        # 等待接收数据
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
            response = json.loads(msg)
            print(f'\n响应类型：{response.get("header", {}).get("cmd")}')
            
            data = response.get('body', {}).get('data', {})
            furniture = data.get('furniture', {})
            info = furniture.get('info', [])
            
            if info:
                print('\n📍 家具地图:')
                print('-' * 70)
                for item in info:
                    fid = item.get('fid', '')
                    fname = item.get('fname', '')
                    mssid = item.get('mssid', '')
                    print(f'  ID: {fid} | 名称：{fname} | 父区域：{mssid}')
                
                # 检查是否有收纳筐
                basket_names = [item.get('fname') for item in info if '收纳' in item.get('fname', '') or '筐' in item.get('fname', '') or '篮' in item.get('fname', '')]
                if basket_names:
                    print(f'\n✅ 找到收纳筐：{basket_names}')
                else:
                    print('\n⚠️  未在家具地图中找到"收纳筐"')
                    print('   可用区域名称:', [item.get('fname') for item in info])
            else:
                print('\n⚠️  未获取到家具信息')
                print(f'完整数据：{json.dumps(data, indent=2, ensure_ascii=False)}')
                
        except asyncio.TimeoutError:
            print('❌ 超时')
        
        print('\n' + '=' * 70)

async def main():
    await check_furniture()

if __name__ == "__main__":
    asyncio.run(main())
