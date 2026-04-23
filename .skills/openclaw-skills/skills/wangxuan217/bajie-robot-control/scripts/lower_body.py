#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 机身降到最低
"""

import asyncio
import sys
sys.path.insert(0, '/home/Agi/.openclaw/workspace/skills/bajie-robot-control/scripts')

from bajie_robot import BajieRobot


async def main():
    print("🤖 八界机器人 - 机身降到最低")
    print("=" * 40)
    
    async with BajieRobot() as robot:
        print("\n📍 正在降到最低...")
        result = await robot.robot_height_ctrl(mode=2)
        
        if result.success:
            print("✅ 降到最低完成！")
            print(f"   任务 ID: {result.task_id}")
        else:
            print(f"❌ 降低失败：{result.error_code.msg}")
            print(f"   错误码：0x{result.error_code.code:08X}")
            return False
        
        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
