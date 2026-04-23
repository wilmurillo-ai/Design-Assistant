#!/usr/bin/env python3
"""测试：连续移动任务序列"""

import asyncio
import sys
sys.path.insert(0, '/home/Agi/.openclaw/workspace/skills/bajie-robot-control')

from bajie_robot import BajieRobot

async def main():
    async with BajieRobot() as robot:
        print("\n🤖 八界机器人 - 连续移动任务")
        print("=" * 50)
        
        # 1. 前进 30cm
        print("\n📍 任务 1: 前进 30cm")
        result = await robot.chassis_move(move_distance=0.3)
        if result.success:
            print("✓ 前进 30cm 完成")
        else:
            print(f"✗ 前进失败：{result.error_code.msg}")
            return  # 如果失败就停止
        
        await asyncio.sleep(1)
        
        # 2. 原地转一圈（360 度顺时针）
        print("\n🔄 任务 2: 原地转一圈（360°）")
        result = await robot.chassis_move(move_distance=0, move_angle=6.28)
        if result.success:
            print("✓ 转圈完成")
        else:
            print(f"✗ 转圈失败：{result.error_code.msg}")
        
        await asyncio.sleep(1)
        
        # 3. 后退 50cm
        print("\n📍 任务 3: 后退 50cm")
        result = await robot.chassis_move(move_distance=-0.5)
        if result.success:
            print("✓ 后退 50cm 完成")
        else:
            print(f"✗ 后退失败：{result.error_code.msg}")
        
        await asyncio.sleep(1)
        
        # 4. 左转 90 度
        print("\n🔄 任务 4: 左转 90°")
        result = await robot.chassis_move(move_distance=0, move_angle=-1.57)
        if result.success:
            print("✓ 左转完成")
        else:
            print(f"✗ 左转失败：{result.error_code.msg}")
        
        print("\n" + "=" * 50)
        print("✅ 所有任务完成！")

if __name__ == "__main__":
    asyncio.run(main())
