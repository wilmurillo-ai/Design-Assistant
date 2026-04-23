#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 优化版建图任务脚本

优化点：
1. 建图前不强制检查充电状态（避免误判）
2. 增加详细的进度反馈
3. 建图失败后提供清晰的错误信息和建议
4. 支持手动跳过充电桩检查
"""

import asyncio
import sys
import time
sys.path.insert(0, '/home/Agi/.openclaw/workspace/skills/bajie-robot-control')

from bajie_robot import BajieRobot, ErrorCode

async def map_create_optimized(force_charge: bool = True, max_wait_charge_sec: int = 120):
    """
    优化的建图任务
    
    Args:
        force_charge: 是否强制要求充电状态（默认 True，服务端要求）
        max_wait_charge_sec: 等待充电状态的最大秒数（默认 120 秒）
    
    Returns:
        TaskResult: 建图结果
    """
    async with BajieRobot() as robot:
        print('🤖 八界机器人 - 建图任务（优化版 v2）')
        print('=' * 60)
        
        # ========== 步骤 1: 查询初始状态 ==========
        print('\n📊 步骤 1: 查询机器人状态')
        print('-' * 60)
        
        state = await robot.oneshot_robot_info()
        battery = state.get('battery', {})
        pos = state.get('pos', {})
        
        print(f'  🔋 电量：{battery.get("value", "N/A")}%')
        print(f'  🔌 充电状态：{"是" if battery.get("isCharge") == 1 else "否"}')
        print(f'  📍 当前位置：{pos.get("room", "未知")} (x={pos.get("x", 0):.2f}, y={pos.get("y", 0):.2f})')
        
        # ========== 步骤 2: 确保充电状态（服务端要求） ==========
        print('\n📋 步骤 2: 确保充电状态')
        print('-' * 60)
        
        if force_charge:
            if battery.get('isCharge') != 1:
                print(f'  ⚠️  机器人未在充电状态，开始回充...')
                recharge_result = await robot.recharge()
                
                if recharge_result.success:
                    print(f'  ✓ 回充成功')
                    
                    # 等待充电状态确认
                    print(f'  ⏳ 等待充电状态确认（最多 {max_wait_charge_sec} 秒）...')
                    wait_start = time.time()
                    charged = False
                    
                    while time.time() - wait_start < max_wait_charge_sec:
                        await asyncio.sleep(2)
                        check_state = await robot.oneshot_robot_info()
                        if check_state.get('battery', {}).get('isCharge') == 1:
                            charged = True
                            print(f'  ✓ 已确认充电状态')
                            break
                        else:
                            elapsed = int(time.time() - wait_start)
                            print(f'  ⏳ 等待中... ({elapsed}/{max_wait_charge_sec}秒)')
                    
                    if not charged:
                        print(f'  ⚠️  超时：未检测到充电状态，但继续尝试建图')
                else:
                    print(f'  ⚠️  回充失败：{recharge_result.error_code.msg}')
                    print(f'  ⏭️  继续尝试建图...')
            else:
                print(f'  ✓ 已在充电状态')
        else:
            print(f'  ⏭️  跳过充电状态检查')
        
        # ========== 步骤 3: 执行建图 ==========
        print('\n🗺️  步骤 3: 执行建图任务')
        print('-' * 60)
        print(f'  📝 说明:')
        print(f'     - 机器人将自动下桩并探索周围环境')
        print(f'     - 建图过程约需 5-15 分钟')
        print(f'     - 请勿移动环境中的障碍物')
        print(f'     - 保持网络畅通')
        print()
        
        start_time = time.time()
        
        # 执行建图（失败后不重试）
        result = await robot.map_create(timeout=900.0)  # 15 分钟超时
        
        elapsed = time.time() - start_time
        
        # ========== 步骤 4: 结果汇报 ==========
        print('\n📊 步骤 4: 建图结果')
        print('-' * 60)
        print(f'  ⏱️  耗时：{elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)')
        
        if result.success:
            print(f'\n  ✅ 建图成功！')
            print(f'  📋 任务 ID: {result.task_id}')
            
            # 查询建图后的状态
            print(f'\n📊 建图后状态:')
            new_state = await robot.oneshot_robot_info()
            new_furniture = new_state.get('furniture', {})
            if new_furniture and 'info' in new_furniture:
                print(f'  📍 已知区域/家具：{len(new_furniture["info"])} 个')
                for item in new_furniture['info']:
                    print(f'     - {item.get("fname", "未知")}')
            else:
                print(f'  ⚠️  未获取到家具信息，可能需要查询状态订阅')
        else:
            print(f'\n  ❌ 建图失败')
            print(f'  📋 任务 ID: {result.task_id}')
            print(f'  🔴 错误码：0x{result.error_code.code:08X} ({result.error_code.code})')
            print(f'  📝 错误信息：{result.error_code.msg}')
            print(f'  📊 错误等级：{result.error_code.level}')
            
            # 提供针对性建议
            print(f'\n  💡 处理建议:')
            
            error_code = result.error_code.code
            
            if error_code == 0x000028D0:  # 桩充状态检测问题
                print(f'     问题：桩充状态检测未在充电')
                print(f'     原因：服务端建图任务要求机器人必须在充电状态')
                print(f'     建议：')
                print(f'       1. 检查充电桩是否通电')
                print(f'       2. 检查充电触点是否接触良好')
                print(f'       3. 查看机器人屏幕上的充电图标')
                print(f'       4. 确认硬件正常后，手动重试')
            
            elif error_code == 0x00007002:  # 全局规划失败
                print(f'     问题：全局规划失败')
                print(f'     建议:')
                print(f'       1. 检查机器人周围是否有障碍物')
                print(f'       2. 确保机器人有足够的移动空间')
                print(f'       3. 清理 LDS 激光雷达上的灰尘')
            
            elif error_code == 0x00007004:  # 路径被阻挡
                print(f'     问题：路径被阻挡')
                print(f'     建议:')
                print(f'       1. 清除机器人前方的可移动障碍物')
                print(f'       2. 确保地面平整无障碍')
                print(f'       3. 检查是否有细小物体卡住底盘')
            
            elif error_code == -1 or '超时' in result.error_code.msg:  # 超时
                print(f'     问题：任务超时')
                print(f'     建议:')
                print(f'       1. 检查网络连接是否稳定')
                print(f'       2. 确认 WebSocket 服务正常运行')
                print(f'       3. 增加超时时间后重试')
            
            else:
                print(f'     建议:')
                print(f'       1. 记录错误码并查看 error_code.md')
                print(f'       2. 检查机器人硬件状态')
                print(f'       3. 联系技术支持')
        
        print('\n' + '=' * 60)
        
        return result

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='八界机器人建图任务（优化版）')
    parser.add_argument('--no-force-charge', action='store_true',
                       help='不强制要求充电状态')
    parser.add_argument('--max-wait', type=int, default=120,
                       help='等待充电状态的最大秒数（默认 120）')
    
    args = parser.parse_args()
    
    result = await map_create_optimized(
        force_charge=not args.no_force_charge,
        max_wait_charge_sec=args.max_wait
    )
    
    # 返回状态码
    sys.exit(0 if result.success else 1)

if __name__ == "__main__":
    asyncio.run(main())
