#!/usr/bin/env python3
"""
agent_report.py — Weekly Productivity vs. Internal Dialog Report
================================================================
Generates a report comparing tangible work output against planning/dialog time.
Pulls from:
  - memory.TaskQueue (completed tasks, quality scores)
  - memory.ActivityLog (agent events)
  - memory.Memories (daily logs, reflections)
  - memory.TaskFeedback (quality scores)

Task types handled:
  - weekly_productivity_report  → full weekly summary
  - daily_summary               → today's task summary
  - agent_performance_report    → per-agent stats
"""

import os
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "infrastructure"))
from agent_base import OblioAgent


class ReportAgent(OblioAgent):
    agent_name = "report_agent"
    task_types = ["weekly_productivity_report", "daily_summary", "agent_performance_report"]
    budget = "free"

    def run_task(self, task: dict) -> str:
        ttype = task.get("task_type", "")
        payload = json.loads(task.get("payload", "{}")) if task.get("payload") else {}

        if ttype == "weekly_productivity_report":
            return self.weekly_report(payload)
        elif ttype == "daily_summary":
            return self.daily_summary(payload)
        elif ttype == "agent_performance_report":
            return self.agent_performance(payload)
        return f"Unknown task: {ttype}"

    def weekly_report(self, payload: dict) -> str:
        """Generate the weekly productivity vs. dialog balance report."""
        days_back = payload.get("days", 7)
        since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        # 1. Count completed tasks by category
        task_counts = self.mem.execute(f"""
            SELECT
                task_type,
                COUNT(*) as count,
                AVG(CAST(quality_score AS FLOAT)) as avg_quality,
                SUM(DATEDIFF(SECOND, started_at, completed_at)) as total_seconds
            FROM memory.TaskQueue
            WHERE status = 'completed'
              AND completed_at >= '{since}'
            GROUP BY task_type
            ORDER BY count DESC
        """)

        # 2. Count dialog/planning entries (reflections, daily logs)
        dialog_counts = self.mem.execute(f"""
            SELECT category, COUNT(*) as count
            FROM memory.Memories
            WHERE created_at >= '{since}'
              AND category IN ('daily_log', 'for_vex', 'reflection', 'planning')
            GROUP BY category
        """)

        # 3. GitHub issues closed this week
        github_tasks = self.mem.execute(f"""
            SELECT COUNT(*) as closed_issues
            FROM memory.TaskQueue
            WHERE task_type = 'investigate_github_issue'
              AND status = 'completed'
              AND completed_at >= '{since}'
        """)

        # 4. Average quality score across all tasks
        quality = self.mem.execute(f"""
            SELECT
                AVG(CAST(score AS FLOAT)) as avg_score,
                COUNT(*) as total_reviews
            FROM memory.TaskFeedback
            WHERE created_at >= '{since}'
        """)

        # Build report
        report_lines = [
            f"# Weekly Productivity Report",
            f"Period: Last {days_back} days (since {since})",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "## ✅ Work Output",
        ]

        if task_counts:
            total_tasks = 0
            action_tasks = 0
            for row in str(task_counts).split("\n")[2:]:  # skip headers
                parts = [p.strip() for p in row.split() if p.strip()]
                if len(parts) >= 2:
                    try:
                        count = int(parts[1])
                        total_tasks += count
                        ttype_name = parts[0]
                        if any(kw in ttype_name for kw in ["github", "train", "fix", "implement", "code", "build"]):
                            action_tasks += count
                        report_lines.append(f"  - {ttype_name}: {count} tasks")
                    except (ValueError, IndexError):
                        pass
            report_lines.append(f"\n**Total tasks completed: {total_tasks}**")
        else:
            report_lines.append("  No completed tasks found.")
            total_tasks = 0

        report_lines.append("\n## 💬 Planning & Dialog")
        if dialog_counts:
            total_dialog = 0
            for row in str(dialog_counts).split("\n")[2:]:
                parts = [p.strip() for p in row.split() if p.strip()]
                if len(parts) >= 2:
                    try:
                        count = int(parts[1])
                        total_dialog += count
                        report_lines.append(f"  - {parts[0]}: {count} entries")
                    except (ValueError, IndexError):
                        pass
            report_lines.append(f"\n**Total dialog entries: {total_dialog}**")
        else:
            report_lines.append("  No dialog entries found.")
            total_dialog = 0

        # Productivity ratio
        if total_tasks + total_dialog > 0:
            ratio = total_tasks / (total_tasks + total_dialog) * 100
            balance = "🟢 Healthy" if ratio >= 40 else "🟡 More action needed" if ratio >= 20 else "🔴 Too much planning"
            report_lines.append(f"\n## ⚖️ Balance\n  Action ratio: {ratio:.1f}% — {balance}")

        # AI quality summary
        if quality:
            report_lines.append(f"\n## 🎯 Quality\n  Avg task quality score: {quality}")

        full_report = "\n".join(report_lines)

        # Save to SQL
        self.mem.log_event(
            "weekly_report_generated",
            "report_agent",
            full_report[:4000],
            category="report"
        )

        return full_report

    def daily_summary(self, payload: dict) -> str:
        """Today's task summary — what was done, what's pending."""
        today = datetime.utcnow().strftime("%Y-%m-%d")

        completed = self.mem.execute(f"""
            SELECT TOP 20 task_type, agent, quality_score, completed_at
            FROM memory.TaskQueue
            WHERE status = 'completed'
              AND CAST(completed_at AS DATE) = '{today}'
            ORDER BY completed_at DESC
        """)

        pending = self.mem.execute(f"""
            SELECT COUNT(*) as pending_count
            FROM memory.TaskQueue
            WHERE status IN ('pending', 'claimed')
        """)

        return f"## Daily Summary — {today}\n\n### Completed\n{completed}\n\n### Pending Queue\n{pending}"

    def agent_performance(self, payload: dict) -> str:
        """Per-agent performance stats."""
        days_back = payload.get("days", 30)
        since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        stats = self.mem.execute(f"""
            SELECT
                agent,
                COUNT(*) as tasks_completed,
                AVG(CAST(quality_score AS FLOAT)) as avg_quality,
                AVG(DATEDIFF(SECOND, started_at, completed_at)) as avg_duration_sec,
                SUM(retry_count) as total_retries
            FROM memory.TaskQueue
            WHERE status = 'completed'
              AND completed_at >= '{since}'
            GROUP BY agent
            ORDER BY tasks_completed DESC
        """)

        return f"## Agent Performance Report (last {days_back} days)\n\n{stats}"


if __name__ == "__main__":
    agent = ReportAgent()
    result = agent.weekly_report({})
    print(result)
