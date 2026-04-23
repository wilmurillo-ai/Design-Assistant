#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 复合动作测试
流程：前进 30cm → 转 180 度 → 升到最高
"""

import asyncio
import sys
import math
sys.path.insert(0, '/home/Agi/.openclaw/workspace/skills/bajie-robot-control/scripts')

from bajie_robot import BajieRobot


async def main():
    print("🤖 八界机器人 - 复合动作测试")
    print("=" * 50)
    
    async with BajieRobot() as robot:
        # 步骤 1: 前进 30cm
        print("\n📍 步骤 1/3: 前进 30cm...")
        result = await robot.chassis_move(
            move_distance=0.3,  # 30cm = 0.3 米
            move_angle=0.0
        )
        
        if result.success:
            print("✅ 前进完成！")
            print(f"   任务 ID: {result.task_id}")
        else:
            print(f"❌ 前进失败：{result.error_code.msg}")
            print(f"   错误码：0x{result.error_code.code:08X}")
            return False
        
        # 步骤 2: 转 180 度（π 弧度）
        print("\n📍 步骤 2/3: 旋转 180 度...")
        result = await robot.chassis_move(
            move_distance=0.0,
            move_angle=math.pi  # 180 度 = π 弧度 ≈ 3.14159
        )
        
        if result.success:
            print("✅ 旋转完成！")
            print(f"   任务 ID: {result.task_id}")
        else:
            print(f"❌ 旋转失败：{result.error_code.msg}")
            print(f"   错误码：0x{result.error_code.code:08X}")
            return False
        
        # 步骤 3: 升到最高
        print("\n📍 步骤 3/3: 机身升到最高...")
        result = await robot.robot_height_ctrl(mode=1)
        
        if result.success:
            print("✅ 升到最高完成！")
            print(f"   任务 ID: {result.task_id}")
        else:
            print(f"❌ 升到最高失败：{result.error_code.msg}")
            print(f"   错误码：0x{result.error_code.code:08X}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 复合动作执行完成！")
        print("   ✓ 前进 30cm")
        print("   ✓ 旋转 180 度")
        print("   ✓ 升到最高")
        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
