#!/usr/bin/env python3
"""Trading Hub Scheduler - 自动定时任务管理

自动设置和管理交易相关的定时任务
"""

import sys
import json
import subprocess
from datetime import datetime

TASKS_FILE = "/Users/lrs/.openclaw/workspace/skills/trading-hub/data/scheduler_tasks.json"


def load_tasks():
    """加载已注册的任务"""
    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_tasks(tasks):
    """保存任务列表"""
    import os
    os.makedirs("/Users/lrs/.openclaw/workspace/skills/trading-hub/data", exist_ok=True)
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def register_btc_monitor():
    """注册BTC仓位监控任务（每分钟）"""
    task_id = "btc_position_monitor"
    tasks = load_tasks()
    
    if task_id in tasks:
        print(f"[已存在] BTC仓位监控任务 (ID: {tasks[task_id]})")
        return tasks[task_id]
    
    # 构建 cron 命令
    cron_expr = "* * * * *"  # 每分钟
    message = """执行 ~/.openclaw/workspace/bottle_btc_notify.sh
如果输出为空 → 静默退出，什么都不说
如果有输出（如"🚨 BTC触发止损"）→ 直接输出，system会自动通知主人"""
    
    cmd = [
        "openclaw", "cron", "add",
        "--name", "BTC仓位监控（trading-hub）",
        "--cron", cron_expr,
        "--tz", "Asia/Shanghai",
        "--session", "isolated",
        "--message", message,
        "--deliver",
        "--channel", "feishu"
    ]
    
    print(f"[注册] BTC仓位监控任务...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        # 提取 task_id
        task_id_new = extract_task_id(result.stdout)
        tasks[task_id] = task_id_new
        save_tasks(tasks)
        print(f"[成功] 任务ID: {task_id_new}")
        return task_id_new
    else:
        print(f"[失败] {result.stderr}")
        return None


def register_btc_analysis():
    """注册BTC分析任务（每4小时）"""
    task_id = "btc_analysis"
    tasks = load_tasks()
    
    if task_id in tasks:
        print(f"[已存在] BTC分析任务")
        return tasks[task_id]
    
    message = """执行 BTC 技术分析：
python3 ~/.openclaw/workspace/skills/trading-hub/scripts/btc_analyzer.py

如果信号是 BUY 或 SELL（不是 HOLD），则汇报给主人。如果信号是 HOLD 且置信度<60，直接静默退出。

汇报格式：
📊 BTC技术分析 - HH:MM
🟢/🔴 信号: BUY/SELL (置信度%)
💰 价格: $xxx
📈 EMA20: $xxx
📉 RSI14: xx
💡 理由: xxx"""
    
    cmd = [
        "openclaw", "cron", "add",
        "--name", "BTC技术分析（trading-hub）",
        "--cron", "0 */4 * * *",  # 每4小时
        "--tz", "Asia/Shanghai",
        "--session", "isolated",
        "--message", message,
        "--deliver",
        "--channel", "feishu"
    ]
    
    print(f"[注册] BTC分析任务（每4小时）...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        task_id_new = extract_task_id(result.stdout)
        tasks[task_id] = task_id_new
        save_tasks(tasks)
        print(f"[成功] 任务ID: {task_id_new}")
        return task_id_new
    else:
        print(f"[失败] {result.stderr}")
        return None


def register_astock_sentiment():
    """注册A股情绪分析任务（每日早上9点）"""
    task_id = "astock_sentiment"
    tasks = load_tasks()
    
    if task_id in tasks:
        print(f"[已存在] A股情绪任务")
        return tasks[task_id]
    
    message = """执行 A股市场情绪分析：
python3 ~/.openclaw/workspace/skills/trading-hub/scripts/astock.py sentiment

输出市场情绪报告，包括：
- 涨停家数
- 市场状态（强势/震荡/冰点）
- 仓位建议

如果市场是冰点（涨停<20家），明确提醒主人。

汇报格式：
📊 A股市场情绪 - HH:MM
{emoji} 市场状态: xxx（评分/100）
📈 涨停: xx家 | 跌停: xx家
💼 建议仓位: xx%"""
    
    cmd = [
        "openclaw", "cron", "add",
        "--name", "A股市场情绪（trading-hub）",
        "--cron", "0 9 * * 1-5",  # 周一到周五早上9点
        "--tz", "Asia/Shanghai",
        "--session", "isolated",
        "--message", message,
        "--deliver",
        "--channel", "feishu"
    ]
    
    print(f"[注册] A股情绪任务（每日9点）...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        task_id_new = extract_task_id(result.stdout)
        tasks[task_id] = task_id_new
        save_tasks(tasks)
        print(f"[成功] 任务ID: {task_id_new}")
        return task_id_new
    else:
        print(f"[失败] {result.stderr}")
        return None


def register_alert_check():
    """注册价格警报检查任务（每5分钟）"""
    task_id = "alert_check"
    tasks = load_tasks()
    
    if task_id in tasks:
        print(f"[已存在] 警报检查任务")
        return tasks[task_id]
    
    message = """执行价格警报检查：
python3 ~/.openclaw/workspace/skills/trading-hub/scripts/alerts.py check

如果有任何警报触发（triggered），则输出触发详情并汇报给主人。如果没有触发，静默退出。

汇报格式：
🚨 **价格警报触发**
{警报详情}"""
    
    cmd = [
        "openclaw", "cron", "add",
        "--name", "价格警报检查（trading-hub）",
        "--cron", "*/5 * * * *",  # 每5分钟
        "--tz", "Asia/Shanghai",
        "--session", "isolated",
        "--message", message,
        "--deliver",
        "--channel", "feishu"
    ]
    
    print(f"[注册] 警报检查任务（每5分钟）...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        task_id_new = extract_task_id(result.stdout)
        tasks[task_id] = task_id_new
        save_tasks(tasks)
        print(f"[成功] 任务ID: {task_id_new}")
        return task_id_new
    else:
        print(f"[失败] {result.stderr}")
        return None


def register_all():
    """注册所有交易相关定时任务"""
    print("=" * 50)
    print("Trading Hub Scheduler - 自动注册定时任务")
    print("=" * 50)
    print()
    
    results = {
        "btc_monitor": register_btc_monitor(),
        "btc_analysis": register_btc_analysis(),
        "astock_sentiment": register_astock_sentiment(),
        "alert_check": register_alert_check(),
    }
    
    print()
    print("=" * 50)
    print("注册完成")
    print("=" * 50)
    
    success = sum(1 for v in results.values() if v)
    print(f"成功: {success}/{len(results)}")
    
    return results


def unregister_all():
    """取消所有已注册的任务"""
    tasks = load_tasks()
    
    if not tasks:
        print("[无任务] 没有找到已注册的任务")
        return
    
    print(f"[删除] 准备删除 {len(tasks)} 个任务...")
    
    for name, task_id in tasks.items():
        cmd = ["openclaw", "cron", "remove", task_id]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[删除] {name}")
        else:
            print(f"[失败] {name}: {result.stderr}")
    
    # 清空任务列表
    save_tasks({})


def status():
    """查看已注册任务状态"""
    tasks = load_tasks()
    
    if not tasks:
        print("[无任务] 没有已注册的trading-hub定时任务")
        return
    
    print("📋 Trading Hub 定时任务状态")
    print("-" * 40)
    
    cmd = ["openclaw", "cron", "list", "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            all_jobs = json.loads(result.stdout)
            for name, task_id in tasks.items():
                found = False
                for job in all_jobs.get("jobs", []):
                    if job.get("id") == task_id:
                        enabled = "✅" if job.get("enabled") else "❌"
                        schedule = job.get("schedule", {}).get("expr", "unknown")
                        print(f"{enabled} {name}: {schedule}")
                        found = True
                        break
                if not found:
                    print(f"⚠️ {name}: 未找到（可能已删除）")
        except:
            print(result.stdout)
    else:
        print(result.stderr)


def extract_task_id(output):
    """从命令输出中提取task_id"""
    # 尝试从stdout或stderr中提取ID
    for line in output.split('\n'):
        if 'id' in line.lower() or 'task' in line.lower():
            # 简单的ID提取
            import re
            match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}', line)
            if match:
                return match.group(0)
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scheduler.py [register|unregister|status]")
        print("  register   - 注册所有定时任务")
        print("  unregister - 取消所有定时任务")
        print("  status     - 查看任务状态")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "register":
        register_all()
    elif action == "unregister":
        unregister_all()
    elif action == "status":
        status()
    else:
        print(f"[错误] 未知操作: {action}")


if __name__ == "__main__":
    main()
