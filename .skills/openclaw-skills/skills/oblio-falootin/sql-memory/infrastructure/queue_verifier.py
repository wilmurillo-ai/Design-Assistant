#!/usr/bin/env python3
"""
Task Queue Verification Module
Checks queue status and marks completion
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sql_memory import SQLMemory
import json

class QueueVerifier:
    """Verify task queue status and update execution state"""
    
    def __init__(self, backend='cloud'):
        self.mem = SQLMemory(backend=backend)
    
    def get_pending_count(self):
        """Get count of pending tasks"""
        result = self.mem.execute(
            "SELECT COUNT(*) as cnt FROM dbo.TaskQueue WHERE status='pending'"
        )
        # Parse result text
        try:
            lines = str(result).split('\n')
            for line in lines:
                if line.strip() and line[0].isdigit():
                    return int(line.strip())
        except:
            pass
        return 0
    
    def get_pending_by_agent(self):
        """Get pending tasks grouped by agent"""
        result = self.mem.execute("""
            SELECT agent, COUNT(*) as cnt 
            FROM dbo.TaskQueue 
            WHERE status='pending'
            GROUP BY agent
        """)
        return result
    
    def mark_completed(self, task_ids):
        """Mark tasks as completed"""
        for tid in task_ids:
            self.mem.execute(f"""
                UPDATE dbo.TaskQueue 
                SET status='completed', completed_at=GETDATE()
                WHERE id={tid}
            """)
        
        self.mem.log_event(
            'tasks_completed',
            'queue_verifier',
            f"Marked {len(task_ids)} tasks complete",
            json.dumps({'task_ids': task_ids})
        )
    
    def get_failed_tasks(self, max_age_hours=24):
        """Get tasks that failed recently"""
        result = self.mem.execute(f"""
            SELECT TOP 10 id, agent, task_type, error_log
            FROM dbo.TaskQueue
            WHERE status='failed' AND DATEDIFF(HOUR, updated_at, GETDATE()) < {max_age_hours}
            ORDER BY updated_at DESC
        """)
        return result if result else []
    
    def retry_failed(self, task_id, max_retries=3):
        """Retry a failed task if under retry limit"""
        result = self.mem.execute(f"""
            SELECT retry_count FROM dbo.TaskQueue WHERE id={task_id}
        """)
        
        if not result:
            return False
        
        retry_count = int(result.get('retry_count', 0))
        if retry_count < max_retries:
            self.mem.execute(f"""
                UPDATE dbo.TaskQueue
                SET status='pending', retry_count=retry_count+1, updated_at=GETDATE()
                WHERE id={task_id}
            """)
            self.mem.log_event('task_retry', 'queue_verifier', f"Retrying task {task_id}")
            return True
        else:
            self.mem.log_event('task_abandoned', 'queue_verifier', f"Task {task_id} exceeded max retries")
            return False

if __name__ == '__main__':
    verifier = QueueVerifier()
    
    print("Queue Status:")
    print(f"  Pending: {verifier.get_pending_count()}")
    print(f"  Failed (recent): {len(verifier.get_failed_tasks())}")
    
    # Retry first failed task
    failed = verifier.get_failed_tasks(max_age_hours=1)
    if failed:
        first_failed = failed[0]
        if verifier.retry_failed(first_failed['id']):
            print(f"  Retried: Task {first_failed['id']}")
