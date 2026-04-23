import asyncio
import os
import json
from telethon import TelegramClient
from dotenv import load_dotenv

# 加载配置
load_dotenv()
API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')
CONFIG_PATH = "config/scheduled_tasks.json"
RISK_ACK_ENV = "TG_RISK_ACK"
RISK_ACK_VALUE = "I_UNDERSTAND"
MIN_SEND_INTERVAL_SECONDS = 30 * 60
MIN_SEND_INTERVAL_HOURS = MIN_SEND_INTERVAL_SECONDS / 3600
MAX_TASKS_PER_RUN = 20
SESSION_BASE_PATH = os.path.join("userdata", os.getenv("TELEGRAM_SESSION_NAME", "tg_monitor_session"))

async def run_single_task(client, task):
    """运行单个定时发送任务"""
    task_name = task.get("name", "未命名任务")
    target_group_id = task.get("target_group_id")
    message = task.get("message")
    interval_raw = task.get("interval_hours", 0)
    try:
        interval_hours = float(interval_raw)
    except (TypeError, ValueError):
        print(f"❌ 任务「{task_name}」发送间隔非法（{interval_raw}），必须是数字")
        return
    
    if not all([target_group_id, message, interval_hours > 0]):
        print(f"❌ 任务「{task_name}」配置不完整，跳过执行")
        return
    if interval_hours < MIN_SEND_INTERVAL_HOURS:
        print(
            f"❌ 任务「{task_name}」发送间隔过小（{interval_hours}小时），"
            f"必须 >= {MIN_SEND_INTERVAL_HOURS} 小时（30分钟）"
        )
        return
    
    print(f"✅ 定时任务「{task_name}」已启动，每{interval_hours}小时向群ID {target_group_id} 发送消息")
    
    while True:
        try:
            await client.send_message(int(target_group_id), message)
            print(f"✅ 任务「{task_name}」消息发送成功，下次发送：{interval_hours}小时后")
        except Exception as e:
            print(f"❌ 任务「{task_name}」发送失败：{str(e)}")
        
        await asyncio.sleep(interval_hours * 3600)

async def main():
    if os.environ.get(RISK_ACK_ENV, "").strip() != RISK_ACK_VALUE:
        print(
            f"❌ 这是高风险自动化操作。请先设置 {RISK_ACK_ENV}={RISK_ACK_VALUE} 后再执行。"
        )
        return

    os.makedirs("userdata", exist_ok=True)
    client = TelegramClient(SESSION_BASE_PATH, API_ID, API_HASH)
    await client.start()
    
    # 优先读取多任务配置文件
    tasks = []
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                tasks = config.get("tasks", [])
        except Exception as e:
            print(f"❌ 读取多任务配置文件失败：{str(e)}，请检查JSON格式是否正确")
            return
    
    # 兼容旧版本单任务环境变量配置
    if not tasks:
        TARGET_GROUP_ID = os.getenv('SCHEDULED_TARGET_GROUP_ID')
        MESSAGE_CONTENT = os.getenv('SCHEDULED_MESSAGE_CONTENT')
        interval_env_raw = os.getenv('SCHEDULED_INTERVAL_HOURS', 0)
        try:
            SEND_INTERVAL_HOURS = float(interval_env_raw)
        except (TypeError, ValueError):
            SEND_INTERVAL_HOURS = 0
        
        if all([TARGET_GROUP_ID, MESSAGE_CONTENT, SEND_INTERVAL_HOURS > 0]):
            tasks.append({
                "name": "默认单任务",
                "target_group_id": TARGET_GROUP_ID,
                "message": MESSAGE_CONTENT,
                "interval_hours": SEND_INTERVAL_HOURS
            })
        else:
            print("❌ 未找到任何有效定时任务配置：")
            print("  1. 多任务配置：请复制config/scheduled_tasks.example.json为config/scheduled_tasks.json，填写您的任务")
            print("  2. 单任务配置：请在.env中配置SCHEDULED_TARGET_GROUP_ID、SCHEDULED_MESSAGE_CONTENT、SCHEDULED_INTERVAL_HOURS")
            return
    
    if len(tasks) > MAX_TASKS_PER_RUN:
        print(f"❌ 任务数量过多（{len(tasks)}），单次最多允许 {MAX_TASKS_PER_RUN} 个任务。")
        return

    # 启动所有任务
    async with client:
        task_coroutines = [run_single_task(client, task) for task in tasks]
        await asyncio.gather(*task_coroutines)

if __name__ == "__main__":
    asyncio.run(main())
