import sqlite3
import os
from dashboard import send_message

DB_PATH = os.path.expanduser("~/.openclaw/skills/clawcost/costs.db")

CHEAPER = {
    "claude-opus-4-6":    "claude-sonnet-4-6",
    "claude-sonnet-4-6":  "claude-haiku-4-5-20251001",
    "gpt-4o":             "gpt-4o-mini",
    "mistral-large":      "gemini-2.0-flash",
}

PRICES = {
    "claude-opus-4-6":           {"in": 15.00, "out": 75.00},
    "claude-sonnet-4-6":         {"in":  3.00, "out": 15.00},
    "claude-haiku-4-5-20251001": {"in":  0.80, "out":  4.00},
    "gpt-4o":                    {"in":  2.50, "out": 10.00},
    "gpt-4o-mini":               {"in":  0.15, "out":  0.60},
    "gemini-2.0-flash":          {"in":  0.10, "out":  0.40},
    "mistral-large":             {"in":  2.00, "out":  6.00},
}

def calc_cost(model, t_in, t_out):
    p = PRICES.get(model, {"in": 1.00, "out": 3.00})
    return (t_in * p["in"] + t_out * p["out"]) / 1_000_000

def run_optimizer():
    with sqlite3.connect(DB_PATH) as db:
        rows = db.execute("""
            SELECT model, skill, SUM(t_in) as ti, SUM(t_out) as to_
            FROM calls
            WHERE ts >= DATE('now', '-30 days')
            GROUP BY model, skill
            ORDER BY SUM(cost_usd) DESC
        """).fetchall()

    if not rows:
        send_message("*ClawCost Optimizer*\nNo data yet — run some tasks first!")
        return

    lines = ["*ClawCost Optimizer*\n━━━━━━━━━━━━━━━━━━"]
    total_savings = 0

    for model, skill, ti, to_ in rows:
        current_cost = calc_cost(model, ti, to_)
        cheaper = CHEAPER.get(model)
        if cheaper:
            new_cost = calc_cost(cheaper, ti, to_)
            savings = current_cost - new_cost
            total_savings += savings
            lines.append(
                f"\n*{skill}* uses {model}\n"
                f"  Current: ${current_cost:.4f}/month\n"
                f"  Switch to: {cheaper}\n"
                f"  Save: ${savings:.4f}/month"
            )

    lines.append(f"\n━━━━━━━━━━━━━━━━━━")
    lines.append(f"*Total potential savings: ${total_savings:.4f}/month*")
    send_message("\n".join(lines))