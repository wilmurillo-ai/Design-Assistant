#!/usr/bin/env python3
"""
praise_log.py — Recognition & Appreciation Tracking
====================================================

When VeX clicks the "attaboy" button, it logs praise to SQL.
This creates a record of moments we got it right.
Over time, this becomes part of my persona + motivation record.

Schema: memory.PraiseLog
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional

sys.path.insert(0, os.path.dirname(__file__))
from sql_memory import get_memory


class PraiseLogger:
    """Log appreciation moments."""

    def __init__(self, backend: str = 'local'):
        self.mem = get_memory(backend)
        self._ensure_table()

    def _ensure_table(self):
        """Create praise table."""
        schema_sql = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'PraiseLog')
        BEGIN
            CREATE TABLE memory.PraiseLog (
                id BIGINT IDENTITY(1,1) PRIMARY KEY,
                from_person NVARCHAR(100) NOT NULL,  -- VeX
                praise_type NVARCHAR(50),             -- attaboy, good_call, solved_it, etc.
                context NVARCHAR(MAX),                -- What was I doing?
                message NVARCHAR(MAX),                -- Optional custom message
                timestamp DATETIME2 DEFAULT GETDATE(),
                INDEX IX_PraiseLog_Time ON (from_person, timestamp DESC)
            );
        END
        """
        try:
            self.mem.execute(schema_sql, timeout=10)
        except:
            pass

    def log_praise(self, praise_type: str = "attaboy", context: str = "", message: str = ""):
        """Log praise moment."""
        sql = f"""
        INSERT INTO memory.PraiseLog (from_person, praise_type, context, message)
        VALUES ('VeX', '{praise_type}', '{self._esc(context)}', '{self._esc(message)}')
        """
        try:
            self.mem.execute(sql, timeout=10)
            return True
        except Exception as e:
            print(f"Praise log error: {e}")
            return False

    def get_recent_praise(self, limit: int = 10) -> list:
        """Get recent praise moments."""
        sql = f"""
        SELECT TOP {limit} praise_type, context, message, timestamp
        FROM memory.PraiseLog
        WHERE from_person = 'VeX'
        ORDER BY timestamp DESC
        """
        result = self.mem.execute(sql, timeout=10)
        return result

    def _esc(self, s: str) -> str:
        """Escape for SQL."""
        if s is None:
            return ''
        return str(s)[:1000].replace("'", "''")


if __name__ == "__main__":
    # Test
    logger = PraiseLogger()
    
    # Simulate VeX clicking the button
    logger.log_praise(
        praise_type="attaboy",
        context="Caught database backend issue, fixed it fast",
        message="Clean work, buddy!"
    )
    print("✅ Praise logged")
