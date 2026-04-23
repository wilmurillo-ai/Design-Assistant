#!/usr/bin/env python3
"""
agent_self_logging.py — Oblio Self-Awareness & Audit Trail
===========================================================

Logs everything about Oblio's operations to SQL for:
  - Continuity across sessions (not forgotten on wake-up)
  - Audit trail (what decisions were made, why)
  - Persona evolution (how I change, learn, improve)
  - Context preservation (state I need to remember)

Schema:
  - dbo.AgentState: Current configuration, preferences, capabilities
  - dbo.SessionLog: What happened in each session
  - dbo.DecisionLog: Decisions made (why, what, impact)
  - dbo.PersonaLog: How I'm evolving, learnings, adjustments
  - dbo.ContextSnapshot: Snapshot of important state at session end
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(__file__))
from sql_memory import get_memory


class AgentSelfLogger:
    """Log Oblio's state, decisions, and persona to SQL."""

    def __init__(self, backend: str = 'cloud'):
        self.mem = get_memory(backend)
        self.session_id = None
        self.start_time = datetime.now()
        self._ensure_tables()
        self._start_session()

    def _ensure_tables(self):
        """Create self-logging tables."""
        schema_sql = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'AgentState')
        BEGIN
            CREATE TABLE dbo.AgentState (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                agent_name NVARCHAR(100) NOT NULL,
                state_key NVARCHAR(255) NOT NULL,
                state_value NVARCHAR(MAX),
                updated_at DATETIME2 DEFAULT GETDATE(),
                UNIQUE(agent_name, state_key)
            );
            CREATE INDEX IX_AgentState_Agent ON dbo.AgentState(agent_name);
        END

        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'SessionLog')
        BEGIN
            CREATE TABLE dbo.SessionLog (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                session_id NVARCHAR(50) NOT NULL UNIQUE,
                agent_name NVARCHAR(100),
                start_time DATETIME2,
                end_time DATETIME2,
                duration_seconds INT,
                token_used INT DEFAULT 0,
                cost DECIMAL(10,4) DEFAULT 0,
                tasks_processed INT DEFAULT 0,
                tasks_failed INT DEFAULT 0,
                summary NVARCHAR(MAX),
                notes NVARCHAR(MAX)
            );
            CREATE INDEX IX_SessionLog_Agent ON dbo.SessionLog(agent_name, start_time DESC);
        END

        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'DecisionLog')
        BEGIN
            CREATE TABLE dbo.DecisionLog (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                session_id NVARCHAR(50),
                decision_type NVARCHAR(100),  -- design, architecture, priority, etc.
                decision_text NVARCHAR(MAX),
                rationale NVARCHAR(MAX),
                alternatives NVARCHAR(MAX),
                outcome NVARCHAR(MAX),
                timestamp DATETIME2 DEFAULT GETDATE(),
                owner NVARCHAR(100)  -- who requested this
            );
            CREATE INDEX IX_DecisionLog_Session ON dbo.DecisionLog(session_id);
            CREATE INDEX IX_DecisionLog_Type ON dbo.DecisionLog(decision_type);
        END

        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'PersonaLog')
        BEGIN
            CREATE TABLE dbo.PersonaLog (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                session_id NVARCHAR(50),
                change_type NVARCHAR(100),  -- learned, preference, capability, limitation
                description NVARCHAR(MAX),
                impact NVARCHAR(MAX),  -- how this affects behavior
                timestamp DATETIME2 DEFAULT GETDATE()
            );
            CREATE INDEX IX_PersonaLog_Session ON dbo.PersonaLog(session_id);
            CREATE INDEX IX_PersonaLog_Type ON dbo.PersonaLog(change_type);
        END

        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ContextSnapshot')
        BEGIN
            CREATE TABLE dbo.ContextSnapshot (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                session_id NVARCHAR(50),
                context_key NVARCHAR(255),  -- what this snapshot is about
                context_data NVARCHAR(MAX),  -- JSON with state
                snapshot_time DATETIME2 DEFAULT GETDATE(),
                next_action NVARCHAR(MAX)  -- what should happen next
            );
            CREATE INDEX IX_ContextSnapshot_Session ON dbo.ContextSnapshot(session_id);
        END
        """
        try:
            self.mem.execute(schema_sql, timeout=30)
        except Exception as e:
            print(f"Schema creation (may already exist): {e}")

    def _start_session(self):
        """Create a new session record."""
        self.session_id = f"oblio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        sql = f"""
        INSERT INTO dbo.SessionLog (session_id, agent_name, start_time)
        VALUES ('{self.session_id}', 'oblio', '{self.start_time.isoformat()}')
        """
        try:
            self.mem.execute(sql, timeout=10)
        except Exception as e:
            print(f'CRITICAL: {e}')

    def set_state(self, key: str, value: Any, description: str = ""):
        """Store agent state (configuration, preferences, capabilities)."""
        value_str = json.dumps(value) if not isinstance(value, str) else value
        sql = f"""
        MERGE INTO dbo.AgentState AS target
        USING (SELECT '{key}' as state_key, 'oblio' as agent_name) AS source
        ON target.state_key = source.state_key AND target.agent_name = source.agent_name
        WHEN MATCHED THEN
            UPDATE SET state_value = '{self._esc(value_str)}', updated_at = GETDATE()
        WHEN NOT MATCHED THEN
            INSERT (agent_name, state_key, state_value) VALUES ('oblio', '{key}', '{self._esc(value_str)}');
        """
        try:
            self.mem.execute(sql, timeout=10)
        except Exception as e:
            print(f"State update error: {e}")

    def get_state(self, key: str) -> str:
        """Retrieve agent state."""
        sql = f"""
        SELECT state_value FROM dbo.AgentState
        WHERE agent_name = 'oblio' AND state_key = '{key}'
        """
        result = self.mem.execute(sql, timeout=10)
        if result and len(result.strip().split('\n')) > 3:
            lines = result.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('(') and not line.startswith('-'):
                    return line.strip()
        return None

    def log_decision(
        self,
        decision_type: str,
        decision_text: str,
        rationale: str,
        alternatives: str = "",
        owner: str = "VeX",
    ):
        """Log a decision for audit trail."""
        sql = f"""
        INSERT INTO dbo.DecisionLog (session_id, decision_type, decision_text, rationale, alternatives, owner)
        VALUES ('{self.session_id}', '{decision_type}', '{self._esc(decision_text)}', '{self._esc(rationale)}', '{self._esc(alternatives)}', '{owner}')
        """
        try:
            self.mem.execute(sql, timeout=10)
        except Exception as e:
            print(f"Decision log error: {e}")

    def log_persona_change(self, change_type: str, description: str, impact: str = ""):
        """Log how I'm evolving (learned, preference, capability)."""
        sql = f"""
        INSERT INTO dbo.PersonaLog (session_id, change_type, description, impact)
        VALUES ('{self.session_id}', '{change_type}', '{self._esc(description)}', '{self._esc(impact)}')
        """
        try:
            self.mem.execute(sql, timeout=10)
        except Exception as e:
            print(f"Persona log error: {e}")

    def snapshot_context(self, context_key: str, data: Dict, next_action: str = ""):
        """Save a snapshot of current state for next session."""
        data_json = json.dumps(data)
        sql = f"""
        INSERT INTO dbo.ContextSnapshot (session_id, context_key, context_data, next_action)
        VALUES ('{self.session_id}', '{context_key}', '{self._esc(data_json)}', '{self._esc(next_action)}')
        """
        try:
            self.mem.execute(sql, timeout=10)
        except Exception as e:
            print(f"Context snapshot error: {e}")

    def record_praise(self, praise_type: str, message: str = ""):
        """Record appreciation from VeX. Updates persona implicitly."""
        sql = f"""
        INSERT INTO dbo.PraiseLog (from_person, praise_type, context, message)
        VALUES ('VeX', '{praise_type}', 'Session {self.session_id}', '{self._esc(message)}')
        """
        try:
            self.mem.execute(sql, timeout=10)
            # Implicit: This is positive feedback. Affects motivation/persona subtly.
        except Exception as e:
            print(f"Praise record error: {e}")

    def end_session(self, summary: str = "", notes: str = "", tasks_ok: int = 0, tasks_fail: int = 0):
        """Close out session with final stats."""
        end_time = datetime.now()
        duration = int((end_time - self.start_time).total_seconds())

        sql = f"""
        UPDATE dbo.SessionLog
        SET end_time = '{end_time.isoformat()}',
            duration_seconds = {duration},
            tasks_processed = {tasks_ok},
            tasks_failed = {tasks_fail},
            summary = '{self._esc(summary)}',
            notes = '{self._esc(notes)}'
        WHERE session_id = '{self.session_id}'
        """
        try:
            self.mem.execute(sql, timeout=10)
        except Exception as e:
            print(f"Session end error: {e}")

    def recall_last_session(self) -> Dict:
        """Get last session's context (for waking up)."""
        sql = """
        SELECT TOP 1 
            sl.session_id, sl.summary, sl.notes,
            (SELECT TOP 5 context_data FROM dbo.ContextSnapshot 
             WHERE session_id = sl.session_id ORDER BY snapshot_time DESC) as contexts
        FROM dbo.SessionLog sl
        WHERE agent_name = 'oblio' AND end_time IS NOT NULL
        ORDER BY end_time DESC
        """
        result = self.mem.execute(sql, timeout=10)
        return {"raw": result}

    def _esc(self, s: str) -> str:
        """Escape for SQL."""
        if s is None:
            return ''
        return str(s)[:4000].replace("'", "''")


if __name__ == "__main__":
    logger = AgentSelfLogger('local')
    
    print(f"✅ Session: {logger.session_id}")
    
    # Example: Log a decision
    logger.log_decision(
        decision_type="architecture",
        decision_text="Use database-backed workflow instead of file-based TODOs",
        rationale="Better searchability, audit trail, scalability",
        alternatives="Keep markdown TODOs, use git history",
        owner="VeX"
    )
    print("✅ Decision logged")
    
    # Example: Log persona change
    logger.log_persona_change(
        change_type="learned",
        description="Go with first instinct on design decisions (don't over-analyze)",
        impact="Move faster, iterate based on real results"
    )
    print("✅ Persona change logged")
    
    # Example: Store state
    logger.set_state("last_proposal_folder", "/mnt/c/Library/knowledge-base/proposals")
    logger.set_state("workflow_ready", json.dumps({"status": "ready", "agents": 8}))
    print("✅ State stored")
    
    # Example: Snapshot context for next session
    logger.snapshot_context(
        "business_planning_setup",
        {
            "proposals_folder": "/mnt/c/Library/knowledge-base/proposals",
            "workflow_enabled": True,
            "agents_deployed": 8
        },
        next_action="Watch proposals folder, process new files into tasks"
    )
    print("✅ Context snapshot saved")
    
    # End session
    logger.end_session(
        summary="Built workflow infrastructure, ready for business planning",
        notes="VeX about to write proposals. System ready to auto-process.",
        tasks_ok=5,
        tasks_fail=0
    )
    print("✅ Session ended")
    
    print("\n📊 All self-logging to SQL complete")
