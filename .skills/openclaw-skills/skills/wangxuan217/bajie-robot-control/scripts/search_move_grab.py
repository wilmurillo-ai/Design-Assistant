#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 搜索、移动、抓取玩具

流程：
1. 使用 search 搜索地上玩具
2. 计算移动距离和角度
3. 使用 chassis_move 移动到玩具附近
4. 使用 accurate_grab 抓取（使用 base_link 坐标系）
"""

import asyncio
import json
import time
import uuid
import websockets
import math

async def execute_task(ws, task_name, task_data, timeout=120.0):
    """执行任务并返回结果"""
    task_id = f'{task_name}_{uuid.uuid4().hex[:8]}'
    
    request = {
        'header': {
            'mode': 'mission',
            'type': 'request',
            'cmd': 'start',
            'ts': int(time.time()),
            'uuid': str(uuid.uuid4())
        },
        'body': {
            'name': task_name,
            'task_id': task_id,
            'data': task_data
        }
    }
    
    print(f'Task ID: {task_id}')
    await ws.send(json.dumps(request))
    
    start_time = time.time()
    
    while True:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
            response = json.loads(msg)
            header = response.get('header', {})
            body = response.get('body', {})
            msg_type = header.get('type')
            cmd = header.get('cmd')
            
            if msg_type == 'response':
                error_code = body.get('data', {}).get('error_code', {})
                code = error_code.get('code', 0)
                if code == 0:
                    print('✓ 启动成功')
                else:
                    print(f'❌ 启动失败：0x{code:08X} - {error_code.get("msg")}')
                    return False
            
            elif msg_type == 'notify' and cmd == 'finish':
                error_code = body.get('data', {}).get('error_code', {})
                code = error_code.get('code', 0)
                msg_text = error_code.get('msg', '')
                elapsed = time.time() - start_time
                
                if code == 0:
                    print(f'✅ 成功 ({elapsed:.1f}秒)')
                    return True
                else:
                    print(f'❌ 失败 ({elapsed:.1f}秒): 0x{code:08X} - {msg_text}')
                    return False
                
        except asyncio.TimeoutError:
            print('❌ 超时')
            return False

async def main():
    uri = 'ws://10.10.10.12:9900'
    
    print('=' * 70)
    print('🤖 八界机器人 - 搜索、移动、抓取玩具')
    print('=' * 70)
    
    async with websockets.connect(uri) as ws:
        # ========== 步骤 1: 搜索玩具 ==========
        print('\n【步骤 1】搜索地上玩具')
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
        
        toy_position = None
        
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=60.0)
                response = json.loads(msg)
                header = response.get('header', {})
                body = response.get('body', {})
                
                if header.get('type') == 'notify' and header.get('cmd') == 'notify':
                    data = body.get('data', {})
                    if 'position' in data:
                        toy_position = data
                        print(f'\n📍 找到玩具！')
                        print(f'   位置：x={data["position"]["x"]:.2f}, y={data["position"]["y"]:.2f}, z={data["position"]["z"]:.2f}')
                
                elif header.get('type') == 'notify' and header.get('cmd') == 'finish':
                    error_code = body.get('data', {}).get('error_code', {})
                    if error_code.get('code', 0) == 0:
                        print('✅ 搜索完成')
                    else:
                        print(f'❌ 搜索失败')
                        return False
                    break
            except asyncio.TimeoutError:
                print('❌ 超时')
                return False
        
        if not toy_position:
            print('❌ 未找到玩具')
            return False
        
        # 获取机器人当前位置
        print('\n【步骤 1.5】获取机器人位置')
        print('-' * 70)
        
        robot_info_request = {
            'header': {
                'mode': 'event',
                'type': 'request',
                'cmd': 'oneshot',
                'ts': int(time.time()),
                'uuid': str(uuid.uuid4())
            },
            'body': {
                'name': 'robot_info',
                'task_id': f'robot_info_{uuid.uuid4().hex[:8]}',
                'data': {
                    'topics': ['pos']
                }
            }
        }
        
        await ws.send(json.dumps(robot_info_request))
        
        robot_pos = None
        
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
            response = json.loads(msg)
            data = response.get('body', {}).get('data', {})
            robot_pos = data.get('pos', {})
            print(f'📍 机器人位置：x={robot_pos.get("x", 0):.2f}, y={robot_pos.get("y", 0):.2f}')
        except asyncio.TimeoutError:
            print('⚠️ 获取机器人位置超时，使用默认值')
            robot_pos = {'x': 0, 'y': 0}
        
        # 计算移动参数
        toy_x = toy_position['position']['x']
        toy_y = toy_position['position']['y']
        
        # 计算机器人到玩具的距离和角度
        dx = toy_x - robot_pos.get('x', 0)
        dy = toy_y - robot_pos.get('y', 0)
        distance = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)
        
        print(f'\n📏 计算移动参数:')
        print(f'   距离：{distance:.2f}m')
        print(f'   角度：{math.degrees(angle):.1f}°')
        
        # 留 35cm 给机械臂操作
        move_distance = max(0, distance - 0.35)
        
        await asyncio.sleep(2)
        
        # ========== 步骤 2: 旋转朝向玩具 ==========
        print('\n【步骤 2】旋转朝向玩具')
        print('-' * 70)
        
        rotate_success = await execute_task(ws, 'chassis_move', {
            'move_distance': 0.0,
            'move_angle': angle
        }, timeout=60.0)
        
        if not rotate_success:
            print('⚠️ 旋转失败，继续尝试移动')
        
        await asyncio.sleep(1)
        
        # ========== 步骤 3: 前进到玩具附近 ==========
        print('\n【步骤 3】前进到玩具附近')
        print('-' * 70)
        
        move_success = await execute_task(ws, 'chassis_move', {
            'move_distance': move_distance,
            'move_angle': 0.0
        }, timeout=60.0)
        
        if not move_success:
            print('⚠️ 移动失败，继续尝试抓取')
        
        await asyncio.sleep(2)
        
        # ========== 步骤 4: 抓取玩具 ==========
        print('\n【步骤 4】抓取玩具（base_link 坐标系）')
        print('-' * 70)
        
        # 使用 base_link 坐标系，机器人前方 35cm
        grab_data = {
            'object': {
                'rag_id': '',
                'item': '玩具',
                'color': '',
                'shape': '',
                'person': ''
            },
            'position': {'x': 0.35, 'y': 0.0, 'z': 0.05},
            'orientation': {'x': 0, 'y': 0, 'z': 0, 'w': 1},
            'box_length': {'x': 0.15, 'y': 0.15, 'z': 0.15},
            'frame_id': 'base_link'
        }
        
        print(f'抓取位置：前方 35cm')
        
        grab_success = await execute_task(ws, 'accurate_grab', grab_data, timeout=180.0)
        
        # ========== 总结 ==========
        print('\n' + '=' * 70)
        print('📊 任务总结')
        print('=' * 70)
        search_status = "✅" if toy_position else "❌"
        rotate_status = "✅" if rotate_success else "❌"
        move_status = "✅" if move_success else "❌"
        grab_status = "✅" if grab_success else "❌"
        print(f'搜索：{search_status}')
        print(f'旋转：{rotate_status}')
        print(f'移动：{move_status}')
        print(f'抓取：{grab_status}')
        print('=' * 70)
        
        return grab_success

if __name__ == "__main__":
    success = asyncio.run(main())
    result = "✅ 成功" if success else "❌ 失败"
    print(f'\n最终结果：{result}')
