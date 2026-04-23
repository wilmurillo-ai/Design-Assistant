#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八界机器人 - 托盘抓取玩具
"""

import asyncio
import sys
sys.path.insert(0, '/home/Agi/.openclaw/workspace/skills/bajie-robot-control/scripts')

from bajie_robot import BajieRobot


async def main():
    print("🤖 八界机器人 - 托盘抓取玩具")
    print("=" * 50)
    
    async with BajieRobot() as robot:
        # 托盘抓取玩具
        print("\n📍 开始抓取：玩具...")
        result = await robot.tray_grab(item="玩具")
        
        if result.success:
            print("✅ 抓取完成！")
            print(f"   任务 ID: {result.task_id}")
            print(f"   物品：玩具")
        else:
            print(f"❌ 抓取失败：{result.error_code.msg}")
            print(f"   错误码：0x{result.error_code.code:08X}")
            return False
        
        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
