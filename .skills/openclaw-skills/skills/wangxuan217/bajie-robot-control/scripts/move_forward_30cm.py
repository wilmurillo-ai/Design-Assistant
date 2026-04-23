#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人前进 30cm
"""

import asyncio
import sys
sys.path.insert(0, '/home/Agi/.openclaw/workspace/skills/bajie-robot-control/scripts')

from bajie_robot import BajieRobot


async def main():
    print("🤖 八界机器人 - 前进 30cm")
    print("=" * 40)
    
    async with BajieRobot() as robot:
        # 执行底盘移动：前进 0.3 米（30cm），不旋转
        print("\n📍 开始移动：前进 30cm...")
        result = await robot.chassis_move(
            move_distance=0.3,  # 30cm = 0.3 米
            move_angle=0.0      # 不旋转
        )
        
        if result.success:
            print("✅ 移动完成！")
            print(f"   任务 ID: {result.task_id}")
        else:
            print(f"❌ 移动失败：{result.error_code.msg}")
            print(f"   错误码：0x{result.error_code.code:08X}")
        
        return result.success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
