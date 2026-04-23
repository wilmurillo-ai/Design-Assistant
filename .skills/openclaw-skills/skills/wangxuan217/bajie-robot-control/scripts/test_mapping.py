#!/usr/bin/env python3
"""测试：回充 + 建图任务"""

import asyncio
import sys
sys.path.insert(0, '/home/Agi/.openclaw/workspace/skills/bajie-robot-control')

from bajie_robot import BajieRobot

async def main():
    async with BajieRobot() as robot:
        print("\n🤖 八界机器人 - 回充 + 建图任务")
        print("=" * 50)
        
        # 1. 查询当前状态
        print("\n📊 当前状态:")
        state_info = await robot.oneshot_robot_info()
        battery = state_info.get("battery", {})
        print(f"  🔋 电量：{battery.get('value', 'N/A')}%")
        print(f"  🔌 充电：{'是' if battery.get('isCharge') == 1 else '否'}")
        
        # 2. 执行回充任务
        print("\n" + "=" * 50)
        print("\n🔌 任务 1: 回充")
        result = await robot.recharge()
        
        if result.success:
            print("✓ 回充成功（已在充电桩上）")
        else:
            print(f"⚠ 回充失败：{result.error_code.msg}")
            print("  继续尝试建图...")
        
        await asyncio.sleep(2)
        
        # 3. 执行建图任务
        print("\n" + "=" * 50)
        print("\n🗺️  任务 2: 建图")
        print("（建图过程中机器人会自动探索环境）\n")
        
        # 建图任务通常耗时较长，设置 10 分钟超时
        result = await robot.map_create()
        
        if result.success:
            print("✅ 建图完成！")
            print(f"  任务 ID: {result.task_id}")
        else:
            print(f"❌ 建图失败：{result.error_code.msg}")
            print(f"  错误码：0x{result.error_code.code:08X}")
            print(f"  错误等级：{result.error_code.level}")
            print(f"  处理策略：{result.error_code.get_handler_strategy()}")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
