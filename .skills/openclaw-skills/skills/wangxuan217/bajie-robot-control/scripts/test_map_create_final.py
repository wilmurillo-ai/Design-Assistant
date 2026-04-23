#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 建图任务完整测试脚本（最终版）

功能：
1. 自动回充并确保充电状态
2. 执行建图任务（15 分钟超时）
3. 详细的进度反馈和错误处理
4. 建图后验证地图数据

使用：
    python3 test_map_create_final.py
"""

import asyncio
import sys
import time
sys.path.insert(0, '/home/Agi/.openclaw/workspace/skills/bajie-robot-control')

from bajie_robot import BajieRobot

async def main():
    async with BajieRobot() as robot:
        print('\n' + '=' * 70)
        print('🤖 八界机器人 - 建图任务（最终版）')
        print('=' * 70)
        
        # ========== 步骤 1: 初始状态 ==========
        print('\n【步骤 1/5】查询初始状态')
        print('-' * 70)
        
        state = await robot.oneshot_robot_info()
        battery = state.get('battery', {})
        pos = state.get('pos', {})
        
        print(f'  🔋 电量：{battery.get("value", "N/A")}%')
        print(f'  🔌 充电：{"是 ✓" if battery.get("isCharge") == 1 else "否 ✗"}')
        print(f'  📍 位置：x={pos.get("x", 0):.2f}, y={pos.get("y", 0):.2f}')
        
        # ========== 步骤 2: 回充 ==========
        print('\n【步骤 2/5】执行回充任务')
        print('-' * 70)
        
        recharge_result = await robot.recharge()
        
        if recharge_result.success:
            print(f'  ✓ 回充成功')
        else:
            print(f'  ⚠ 回充失败：{recharge_result.error_code.msg}')
            print(f'  → 将影响建图任务，继续执行...')
        
        # 等待充电状态
        print(f'  ⏳ 等待充电状态确认...')
        for i in range(30):  # 最多等 60 秒
            await asyncio.sleep(2)
            check = await robot.oneshot_robot_info()
            if check.get('battery', {}).get('isCharge') == 1:
                print(f'  ✓ 已确认充电状态（{i*2+2}秒）')
                break
        else:
            print(f'  ⚠ 未检测到充电状态，继续...')
        
        await asyncio.sleep(2)
        
        # ========== 步骤 3: 执行建图 ==========
        print('\n【步骤 3/5】执行建图任务')
        print('-' * 70)
        print(f'  📝 说明：')
        print(f'     • 机器人将自动下桩并探索环境')
        print(f'     • 预计耗时：5-15 分钟')
        print(f'     • 请勿移动障碍物')
        print()
        
        start_time = time.time()
        result = await robot.map_create(timeout=900.0)
        elapsed = time.time() - start_time
        
        # ========== 步骤 4: 结果 ==========
        print('\n【步骤 4/5】建图结果')
        print('-' * 70)
        print(f'  ⏱️  耗时：{elapsed:.1f}秒 ({elapsed/60:.1f}分钟)')
        
        if result.success:
            print(f'\n  ✅ 建图成功！')
            print(f'  📋 任务 ID: {result.task_id}')
        else:
            print(f'\n  ❌ 建图失败')
            print(f'  🔴 错误码：0x{result.error_code.code:08X}')
            print(f'  📝 错误：{result.error_code.msg}')
            
            # 错误处理建议
            print(f'\n  💡 建议:')
            if result.error_code.code == 0x000028D0:
                print(f'     桩充状态检测问题 - 检查充电硬件和触点')
            elif '超时' in result.error_code.msg:
                print(f'     任务超时 - 检查网络和机器人状态')
            else:
                print(f'     查看 error_code.md 获取详细信息')
        
        # ========== 步骤 5: 验证 ==========
        print('\n【步骤 5/5】验证地图数据')
        print('-' * 70)
        
        final_state = await robot.oneshot_robot_info()
        furniture = final_state.get('furniture', {})
        
        if furniture and 'info' in furniture:
            count = len(furniture['info'])
            print(f'  📍 已知区域/家具：{count}个')
            for i, item in enumerate(furniture['info'][:10], 1):
                print(f'     {i}. {item.get("fname", "未知")}')
            if count > 10:
                print(f'     ... 还有 {count-10} 个')
        else:
            print(f'  ⚠️  未获取到家具信息')
            print(f'  💡 地图数据可能需要通过其他方式查询')
        
        # 完成
        print('\n' + '=' * 70)
        print('✅ 任务完成')
        print('=' * 70 + '\n')
        
        return result

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result.success else 1)
    except KeyboardInterrupt:
        print('\n⚠️  用户中断')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ 异常：{e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
