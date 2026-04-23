#!/usr/bin/env python3
"""
workflow.py — Oblio Workflow & Task Queue Management
=====================================================

Enhanced task queue with:
  - Priority levels (free/medium/high)
  - Task dependencies
  - Trigger events (auto-kickoff when dependencies resolved)
  - Status tracking (pending → processing → complete/failed/blocked)
  - Unified TODO view (database-backed, not file-based)

Usage:
    from workflow import WorkflowManager
    wf = WorkflowManager('local')
    
    # Create a task
    task_id = wf.create_task(
        agent='research_agent',
        task_type='market_research',
        priority='high',
        payload={'proposal': 'tripatourium-seo'},
        depends_on=[12, 34]  # Wait for task 12 & 34 first
    )
    
    # Check what's ready to run
    ready = wf.get_ready_tasks('research_agent')
    
    # Update status + trigger dependents
    wf.complete_task(task_id, result='found 5 competitors')
    
    # Get unified TODO view
    todos = wf.get_todos(priority='high')
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.dirname(__file__))
from sql_memory import get_memory


class WorkflowManager:
    """
    Database-backed workflow manager.
    Coordinates tasks across agents with priority + dependencies.
    """

    def __init__(self, backend: str = 'cloud'):
        self.mem = get_memory(backend)
        self._ensure_tables()

    def _ensure_tables(self):
        """Ensure workflow tables exist (on top of sql_memory schema)."""
        schema_sql = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'WorkflowTasks')
        BEGIN
            CREATE TABLE memory.WorkflowTasks (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(255) NOT NULL,
                agent NVARCHAR(100),
                task_type NVARCHAR(100),
                priority NVARCHAR(20) DEFAULT 'medium',  -- free, medium, high
                status NVARCHAR(50) DEFAULT 'pending',   -- pending, ready, processing, complete, failed, blocked
                payload NVARCHAR(MAX),
                result NVARCHAR(MAX),
                error_log NVARCHAR(MAX),
                created_at DATETIME2 DEFAULT GETDATE(),
                started_at DATETIME2,
                completed_at DATETIME2,
                retry_count TINYINT DEFAULT 0,
                max_retries TINYINT DEFAULT 3
            );
            CREATE INDEX IX_WorkflowTasks_Priority ON memory.WorkflowTasks(priority, status);
            CREATE INDEX IX_WorkflowTasks_Agent ON memory.WorkflowTasks(agent, status);
        END

        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'TaskDependencies')
        BEGIN
            CREATE TABLE memory.TaskDependencies (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                task_id BIGINT NOT NULL,
                depends_on_task_id BIGINT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES memory.WorkflowTasks(id),
                FOREIGN KEY (depends_on_task_id) REFERENCES memory.WorkflowTasks(id)
            );
            CREATE INDEX IX_TaskDependencies_Task ON memory.TaskDependencies(task_id);
            CREATE INDEX IX_TaskDependencies_DependsOn ON memory.TaskDependencies(depends_on_task_id);
        END

        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'WorkflowTriggers')
        BEGIN
            CREATE TABLE memory.WorkflowTriggers (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(255) NOT NULL,
                trigger_on_event NVARCHAR(100),  -- task_complete, task_failed, new_proposal, etc.
                action NVARCHAR(100),            -- create_task, notify, run_analysis
                action_params NVARCHAR(MAX),     -- JSON with what to do
                enabled BIT DEFAULT 1,
                created_at DATETIME2 DEFAULT GETDATE()
            );
        END
        """
        try:
            self.mem.execute(schema_sql, timeout=30)
        except Exception as e:
            print(f"Schema creation warning (may already exist): {e}")

    def create_task(
        self,
        name: str,
        priority: str = 'medium',
        agent: str = None,
        task_type: str = None,
        payload: Dict = None,
        depends_on: List[int] = None,
    ) -> int:
        """Create a new task."""
        payload_json = json.dumps(payload or {})
        
        insert_sql = f"""
        INSERT INTO memory.WorkflowTasks (name, priority, agent, task_type, payload, status)
        VALUES ('{self._esc(name)}', '{priority}', '{self._esc(agent or "")}', '{self._esc(task_type or "")}', '{self._esc(payload_json)}', 'pending')
        SELECT SCOPE_IDENTITY()
        """
        
        result = self.mem.execute(insert_sql, timeout=10)
        task_id = None
        if result:
            lines = result.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('(') and line.strip().isdigit():
                    try:
                        task_id = int(line.strip())
                        break
                    except:
                        pass
        
        if task_id and depends_on:
            for dep_id in depends_on:
                dep_sql = f"""
                INSERT INTO memory.TaskDependencies (task_id, depends_on_task_id)
                VALUES ({task_id}, {dep_id})
                """
                self.mem.execute(dep_sql, timeout=10)
        
        return task_id

    def get_ready_tasks(self, agent: str = None, priority: str = None) -> List[Dict]:
        """
        Get tasks that are ready to run (all dependencies complete).
        """
        where_clauses = ["wt.status = 'pending'"]
        if agent:
            where_clauses.append(f"wt.agent = '{self._esc(agent)}'")
        if priority:
            where_clauses.append(f"wt.priority = '{priority}'")
        
        # Tasks with no unfinished dependencies
        where_clauses.append("""
        NOT EXISTS (
            SELECT 1 FROM memory.TaskDependencies td
            INNER JOIN memory.WorkflowTasks dep ON td.depends_on_task_id = dep.id
            WHERE td.task_id = wt.id
            AND dep.status NOT IN ('complete')
        )
        """)
        
        where = " AND ".join(where_clauses)
        
        sql = f"""
        SELECT id, name, agent, task_type, priority, payload
        FROM memory.WorkflowTasks wt
        WHERE {where}
        ORDER BY 
            CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
            created_at
        """
        
        result = self.mem.execute(sql, timeout=30)
        return self._parse_results(result)

    def claim_task(self, task_id: int):
        """Mark task as being processed."""
        sql = f"""
        UPDATE memory.WorkflowTasks
        SET status = 'processing', started_at = GETDATE()
        WHERE id = {task_id}
        """
        self.mem.execute(sql, timeout=10)

    def complete_task(self, task_id: int, result: str = ""):
        """Mark task complete and trigger dependents."""
        sql = f"""
        UPDATE memory.WorkflowTasks
        SET status = 'complete', completed_at = GETDATE(), result = '{self._esc(result)}'
        WHERE id = {task_id}
        """
        self.mem.execute(sql, timeout=10)
        
        # Trigger any workflows that depend on this
        self._trigger_workflows('task_complete', {'task_id': task_id, 'result': result})

    def fail_task(self, task_id: int, error: str = ""):
        """Mark task failed (may retry)."""
        sql = f"""
        UPDATE memory.WorkflowTasks
        SET status = 'failed', error_log = '{self._esc(error)}', completed_at = GETDATE()
        WHERE id = {task_id}
        """
        self.mem.execute(sql, timeout=10)
        
        self._trigger_workflows('task_failed', {'task_id': task_id, 'error': error})

    def block_task(self, task_id: int, reason: str = ""):
        """Mark task blocked (waiting for external event)."""
        sql = f"""
        UPDATE memory.WorkflowTasks
        SET status = 'blocked', error_log = '{self._esc(reason)}'
        WHERE id = {task_id}
        """
        self.mem.execute(sql, timeout=10)

    def get_todos(self, priority: str = None, agent: str = None, status: str = None) -> List[Dict]:
        """
        Get unified TODO view (all pending + ready tasks).
        Organized by priority.
        """
        where_clauses = ["status IN ('pending', 'ready', 'blocked')"]
        if priority:
            where_clauses.append(f"priority = '{priority}'")
        if agent:
            where_clauses.append(f"agent = '{self._esc(agent)}'")
        
        where = " AND ".join(where_clauses)
        
        sql = f"""
        SELECT id, name, agent, priority, status, created_at, 
               (SELECT COUNT(*) FROM memory.TaskDependencies WHERE task_id = WorkflowTasks.id) as dependencies
        FROM memory.WorkflowTasks
        WHERE {where}
        ORDER BY 
            CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
            status,
            created_at
        """
        
        result = self.mem.execute(sql, timeout=30)
        todos = self._parse_results(result)
        
        # Organize by priority
        organized = {'high': [], 'medium': [], 'free': []}
        for todo in todos:
            p = todo.get('priority', 'medium')
            organized[p].append(todo)
        
        return organized

    def create_trigger(self, name: str, trigger_on: str, action: str, params: Dict):
        """
        Create an automatic workflow trigger.
        
        Example:
            wf.create_trigger(
                'auto_research_on_proposal',
                trigger_on='new_proposal',
                action='create_task',
                params={'agent': 'research_agent', 'task_type': 'market_analysis'}
            )
        """
        params_json = json.dumps(params)
        sql = f"""
        INSERT INTO memory.WorkflowTriggers (name, trigger_on_event, action, action_params, enabled)
        VALUES ('{self._esc(name)}', '{trigger_on}', '{action}', '{self._esc(params_json)}', 1)
        """
        self.mem.execute(sql, timeout=10)

    def _trigger_workflows(self, event: str, context: Dict):
        """Fire any triggers matching this event."""
        sql = f"""
        SELECT id, action, action_params FROM memory.WorkflowTriggers
        WHERE trigger_on_event = '{event}' AND enabled = 1
        """
        result = self.mem.execute(sql, timeout=30)
        triggers = self._parse_results(result)
        
        for trigger in triggers:
            action = trigger.get('action')
            params = json.loads(trigger.get('action_params', '{}'))
            
            if action == 'create_task':
                self.create_task(
                    name=params.get('name', 'Auto-triggered task'),
                    agent=params.get('agent'),
                    task_type=params.get('task_type'),
                    priority=params.get('priority', 'medium'),
                    payload=params.get('payload')
                )
            elif action == 'notify':
                # Could hook to message system
                print(f"[TRIGGER] {params.get('message')}")

    def _parse_results(self, result_text: str) -> List[Dict]:
        """Parse sqlcmd output into list of dicts."""
        if not result_text:
            return []
        
        lines = result_text.strip().split('\n')
        if len(lines) < 3:
            return []
        
        # Skip header and control lines
        items = []
        for line in lines[2:]:  # Skip header rows
            line = line.strip()
            if line and not line.startswith('('):
                items.append({'raw': line})
        
        return items

    def _esc(self, s: str) -> str:
        """Escape for SQL."""
        if s is None:
            return ''
        return str(s).replace("'", "''")

    def print_todo_report(self):
        """Pretty-print unified TODO view."""
        todos = self.get_todos()
        
        print("\n" + "=" * 80)
        print("UNIFIED TODO REPORT")
        print("=" * 80)
        
        for priority in ['high', 'medium', 'free']:
            items = todos.get(priority, [])
            if not items:
                continue
            
            print(f"\n{priority.upper()} PRIORITY ({len(items)} items)")
            print("-" * 80)
            for item in items:
                deps = item.get('dependencies', 0)
                deps_str = f" [+{deps} deps]" if deps else ""
                print(f"  #{item.get('id', '?')} {item.get('name', '?')}{deps_str}")
                print(f"     Agent: {item.get('agent', 'N/A')} | Status: {item.get('status', '?')}")


if __name__ == "__main__":
    # Test workflow
    wf = WorkflowManager('local')
    
    # Create sample tasks
    print("Creating sample tasks...")
    t1 = wf.create_task(
        name="Research market size",
        priority="high",
        agent="research_agent",
        task_type="market_research",
        payload={"domain": "blotter_art"}
    )
    print(f"✅ Task {t1} created")
    
    t2 = wf.create_task(
        name="Analyze competitors",
        priority="high",
        agent="research_agent",
        task_type="competitive_analysis",
        depends_on=[t1]
    )
    print(f"✅ Task {t2} created (depends on {t1})")
    
    t3 = wf.create_task(
        name="Write business plan",
        priority="medium",
        depends_on=[t1, t2]
    )
    print(f"✅ Task {t3} created (depends on {t1}, {t2})")
    
    # Check what's ready
    print("\nReady tasks (no unmet dependencies):")
    ready = wf.get_ready_tasks()
    for task in ready:
        print(f"  - {task}")
    
    # Print TODO report
    wf.print_todo_report()
