import requests
import os
from tracker import get_today_total, get_top_spenders, get_monthly_total

# Paste your Telegram bot token and chat ID here
TELEGRAM_TOKEN = "8180846166:AAGH8CAva9qA-HTO4ziAWRnGbBDdbdyE0_8"
TELEGRAM_CHAT_ID = "6243624505"

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

def send_daily_report():
    today   = get_today_total()
    monthly = get_monthly_total()
    top     = get_top_spenders(7)

    top_lines = "\n".join(
        [f"  {i+1}. {row[0]} — ${row[1]:.6f}" for i, row in enumerate(top)]
    ) or "  No data yet"

    msg = f"""
*ClawCost Daily Report*
━━━━━━━━━━━━━━━━━━
*Today*
  Spend: ${today['total']:.6f}
  API calls: {today['calls']}

*This Month*
  Spend: ${monthly['total']:.6f}
  API calls: {monthly['calls']}

*Top spenders (7 days)*
{top_lines}
━━━━━━━━━━━━━━━━━━
_ClawCost is watching your wallet_
"""
    send_message(msg.strip())

def send_alert(current, budget):
    pct = int((current / budget) * 100)
    msg = f"""
*ClawCost Budget Alert*
━━━━━━━━━━━━━━━━━━
You have used *{pct}%* of your monthly budget.
Spent: ${current:.4f} / ${budget:.2f}
━━━━━━━━━━━━━━━━━━
_Consider optimizing your top skills_
"""
    send_message(msg.strip())