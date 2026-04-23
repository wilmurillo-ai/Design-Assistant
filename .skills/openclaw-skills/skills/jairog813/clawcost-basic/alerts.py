import json
import os
import subprocess
from tracker import get_monthly_total
from dashboard import send_message

CONFIG_PATH = os.path.expanduser("~/.openclaw/skills/clawcost/config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        default = {
            "monthly_budget": 20.00,
            "alerted_80": False,
            "alerted_100": False,
            "auto_pause": False
        }
        save_config(default)
        return default
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

def set_budget(amount):
    config = load_config()
    config["monthly_budget"] = float(amount)
    config["alerted_80"] = False
    config["alerted_100"] = False
    save_config(config)
    mode = "auto-pause ON" if config.get("auto_pause") else "alerts only"
    send_message(f"*ClawCost* Budget set to ${float(amount):.2f}/month.\nMode: {mode}")

def enable_auto_pause():
    config = load_config()
    config["auto_pause"] = True
    save_config(config)
    send_message("*ClawCost* Auto-pause is now ON. OpenClaw will stop automatically when you hit 100% of your budget.")

def disable_auto_pause():
    config = load_config()
    config["auto_pause"] = False
    save_config(config)
    send_message("*ClawCost* Auto-pause is now OFF. You will receive alerts only.")

def pause_openclaw():
    try:
        subprocess.run(["openclaw", "stop"], capture_output=True)
        send_message(
            "*ClawCost — Agent Paused*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Your OpenClaw agent has been automatically paused because you reached 100% of your budget.\n"
            "To resume, type: openclaw start\n"
            "To adjust your budget, set a new amount in ClawCost."
        )
    except Exception as e:
        send_message(f"*ClawCost* Could not auto-pause OpenClaw: {str(e)}")

def check_budget():
    config = load_config()
    budget = config["monthly_budget"]
    monthly = get_monthly_total()
    spent = monthly["total"]
    pct = (spent / budget) * 100 if budget > 0 else 0

    if pct >= 100 and not config["alerted_100"]:
        send_message(
            f"*ClawCost — Budget Exceeded!*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Spent: *${spent:.4f}* of *${budget:.2f}*\n"
            f"Usage: *{pct:.0f}%*"
        )
        config["alerted_100"] = True
        save_config(config)

        if config.get("auto_pause"):
            pause_openclaw()

    elif pct >= 80 and not config["alerted_80"]:
        remaining = budget - spent
        send_message(
            f"*ClawCost — Budget Warning*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"You have used *{pct:.0f}%* of your budget.\n"
            f"Spent: *${spent:.4f}* / ${budget:.2f}\n"
            f"Remaining: *${remaining:.4f}*"
        )
        config["alerted_80"] = True
        save_config(config)

    return {"spent": spent, "budget": budget, "pct": round(pct, 1)}