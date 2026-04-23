#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 检查当前状态（夹爪、电量、位置）
"""

import asyncio
import json
import time
import uuid
import websockets

WEBSOCKET_URL = 'ws://10.10.10.12:9900'

async def check_status():
    """检查机器人状态"""
    print('=' * 70)
    print('🤖 八界机器人 - 检查当前状态')
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
                    'topics': ['pos', 'battery', 'gripper']
                }
            }
        }
        
        print('获取机器状态...')
        await ws.send(json.dumps(oneshot_request))
        
        # 等待接收数据
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
            response = json.loads(msg)
            data = response.get('body', {}).get('data', {})
            
            # 位置
            pos = data.get('pos', {})
            print(f'\n📍 位置:')
            print(f'   房间：{pos.get("room", "未知")}')
            print(f'   坐标：({pos.get("x", 0):.2f}, {pos.get("y", 0):.2f})')
            print(f'   朝向：{pos.get("yaw", 0):.1f}°')
            
            # 电量
            battery = data.get('battery', {})
            print(f'\n🔋 电量:')
            print(f'   电量：{battery.get("value", 0)}%')
            print(f'   充电状态：{"充电中" if battery.get("isCharge") else "未充电"}')
            print(f'   模式：{battery.get("mode", 0)}')
            
            # 夹爪
            gripper = data.get('gripper', {})
            usage = data.get('gripper_usage_percent', 0)
            print(f'\n🤏 夹爪:')
            print(f'   使用率：{usage}%')
            if usage > 50:
                print(f'   状态：✅ 夹爪中有物品')
            else:
                print(f'   状态：⚠️  夹爪可能为空')
            
            # 当前任务
            workState = data.get('workState', {})
            print(f'\n📋 当前任务:')
            print(f'   名称：{workState.get("name", "无")}')
            print(f'   摘要：{workState.get("summary", "无")}')
            
        except asyncio.TimeoutError:
            print('❌ 超时')
        
        print('\n' + '=' * 70)

async def main():
    await check_status()

if __name__ == "__main__":
    asyncio.run(main())
