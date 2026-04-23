import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.openclaw/skills/clawcost/costs.db")

def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
          CREATE TABLE IF NOT EXISTS calls (
            id        INTEGER PRIMARY KEY,
            ts        TEXT,
            model     TEXT,
            skill     TEXT,
            t_in      INTEGER,
            t_out     INTEGER,
            cost_usd  REAL,
            latency   REAL
          )
        """)
        db.commit()

def log_call(data):
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            "INSERT INTO calls VALUES (NULL,?,?,?,?,?,?,?)",
            (
                datetime.utcnow().isoformat(),
                data["model"],
                data["skill"],
                data["t_in"],
                data["t_out"],
                data["cost_usd"],
                data["latency"],
            )
        )
        db.commit()

def get_today_total():
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("""
            SELECT SUM(cost_usd), COUNT(*)
            FROM calls
            WHERE DATE(ts) = DATE('now')
        """).fetchone()
    return {"total": round(row[0] or 0, 6), "calls": row[1]}

def get_top_spenders(days=7):
    with sqlite3.connect(DB_PATH) as db:
        return db.execute("""
            SELECT skill, ROUND(SUM(cost_usd), 6) as total
            FROM calls
            WHERE ts >= DATE('now', ?)
            GROUP BY skill
            ORDER BY total DESC
            LIMIT 5
        """, (f"-{days} days",)).fetchall()

def get_monthly_total():
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("""
            SELECT SUM(cost_usd), COUNT(*)
            FROM calls
            WHERE strftime('%Y-%m', ts) = strftime('%Y-%m', 'now')
        """).fetchone()
    return {"total": round(row[0] or 0, 6), "calls": row[1]}

init_db()
print("[ClawCost] Database ready.")