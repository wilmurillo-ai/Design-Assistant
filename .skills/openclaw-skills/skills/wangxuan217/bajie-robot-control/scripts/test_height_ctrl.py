#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 机身高度控制测试
测试流程：升到最高 → 降到最低
"""

import asyncio
import sys
sys.path.insert(0, '/home/Agi/.openclaw/workspace/skills/bajie-robot-control/scripts')

from bajie_robot import BajieRobot


async def main():
    print("🤖 八界机器人 - 机身高度控制测试")
    print("=" * 50)
    
    async with BajieRobot() as robot:
        # 步骤 1: 升到最高
        print("\n📍 步骤 1/2: 升到最高 (mode=1)...")
        result = await robot.robot_height_ctrl(mode=1)
        
        if result.success:
            print("✅ 升到最高完成！")
            print(f"   任务 ID: {result.task_id}")
        else:
            print(f"❌ 升到最高失败：{result.error_code.msg}")
            print(f"   错误码：0x{result.error_code.code:08X}")
            return False
        
        # 等待用户确认
        print("\n⏸️  等待 2 秒...")
        await asyncio.sleep(2)
        
        # 步骤 2: 降到最低
        print("\n📍 步骤 2/2: 降到最低 (mode=2)...")
        result = await robot.robot_height_ctrl(mode=2)
        
        if result.success:
            print("✅ 降到最低完成！")
            print(f"   任务 ID: {result.task_id}")
        else:
            print(f"❌ 降到最低失败：{result.error_code.msg}")
            print(f"   错误码：0x{result.error_code.code:08X}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 机身高度控制测试完成！")
        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
