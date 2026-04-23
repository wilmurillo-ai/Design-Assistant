#!/usr/bin/env python3
"""
每日信号复盘 - 自我进化机制
"""
import json
import os
from datetime import datetime, timedelta
import requests

SIGNAL_LOG = "~/.openclaw/skills/crypto-monitor-team/signals_log.json"

def load_signals():
    """加载信号记录"""
    try:
        with open(os.path.expanduser(SIGNAL_LOG), 'r') as f:
            return json.load(f)
    except:
        return {"signals": [], "daily_stats": {}}

def save_signals(data):
    with open(os.path.expanduser(SIGNAL_LOG), 'w') as f:
        json.dump(data, f, indent=2)

def log_signal(asset, signal, confidence, cycle, structure, result="pending"):
    """记录信号"""
    data = load_signals()
    data["signals"].append({
        "timestamp": datetime.now().isoformat(),
        "asset": asset,
        "signal": signal,
        "confidence": confidence,
        "cycle": cycle,
        "structure": structure,
        "result": result
    })
    save_signals(data)

def get_binance_price(symbol, days_ago=0):
    """获取历史价格"""
    try:
        # 简化：使用当前价格对比
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}", timeout=5)
        return json.loads(r.text).get('lastPrice', 0)
    except:
        return 0

def daily_review():
    """每日复盘"""
    data = load_signals()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 当天信号
    today_signals = [s for s in data["signals"] if today in s.get("timestamp", "")]
    
    if not today_signals:
        return "今日无信号记录"
    
    # 统计
    total = len(today_signals)
    strong = len([s for s in today_signals if s.get("confidence", 0) >= 82])
    medium = len([s for s in today_signals if 55 <= s.get("confidence", 0) < 82])
    filtered = len([s for s in today_signals if "过滤" in s.get("signal", "")])
    
    # 分析问题
    issues = []
    if filtered > total * 0.5:
        issues.append("过滤信号过多，需调整结构判断逻辑")
    if strong == 0:
        issues.append("今日无强信号，市场可能处于震荡期")
    
    # 生成报告
    report = f"""
🦞 每日信号复盘报告 - {today}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 信号统计:
  总信号数: {total}
  强信号(≥82%): {strong}
  中信号(55-81%): {medium}
  过滤信号: {filtered}

📋 信号列表:
"""
    for s in today_signals:
        report += f"  - {s['asset']}: {s['signal']} (置信度{s['confidence']}%)\n"
    
    report += f"""
⚠️ 问题分析:
"""
    for issue in issues:
        report += f"  • {issue}\n"
    
    report += f"""
📝 优化建议:
  • 保持当前V7规则
  • 关注Neutral周期处理
  • 考虑增加ADX辅助判断

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 复盘时间: {datetime.now().strftime('%H:%M:%S')}
"""
    return report

if __name__ == "__main__":
    print(daily_review())
