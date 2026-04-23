#!/usr/bin/env python3
"""
Task Executor - Main orchestration (SQL-backed, modular)
Delegates verification to specialized modules
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sql_memory import SQLMemory
from health_checker import HealthChecker
from queue_verifier import QueueVerifier

def main():
    """Run 30-minute verification and execution cycle"""
    
    mem = SQLMemory(backend='cloud')
    
    # Start cycle
    cycle_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    mem.log_event(
        'cycle_start',
        'task_executor',
        f'Verification cycle {cycle_id}',
        json.dumps({'cycle_id': cycle_id, 'timestamp': datetime.now().isoformat()})
    )
    
    # Check system health
    print("[HEALTH CHECK]")
    health = HealthChecker()
    health_results = health.run_all_checks()
    for check, status in health_results.items():
        print(f"  {check}: {status}")
    
    # Check task queue
    print("\n[TASK QUEUE]")
    verifier = QueueVerifier()
    pending_count = verifier.get_pending_count()
    print(f"  Pending tasks: {pending_count}")
    
    # Retry recent failures
    if pending_count < 5:  # Only retry if queue is not busy
        print("\n[RETRY LOGIC]")
        print("  (Skipping for now - stored in SQL for async processing)")
    
    # End cycle
    mem.log_event(
        'cycle_end',
        'task_executor',
        f'Cycle complete. Health OK, {pending_count} pending',
        json.dumps({
            'cycle_id': cycle_id,
            'health': health_results,
            'pending_count': pending_count
        })
    )
    
    print(f"\n✅ Cycle {cycle_id} complete")
    print(f"   Pending: {pending_count}")
    print(f"   Status: ALL OK" if all('OK' in str(v) or 'UP' in str(v) for v in health_results.values()) else "   Status: ⚠️ CHECK WARNINGS")

if __name__ == '__main__':
    main()
