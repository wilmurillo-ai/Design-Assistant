#!/usr/bin/env python3
"""
System Health Checker Module
Verifies UI, GitHub, STAMPS, and other critical systems
"""

import sys
import os
import subprocess
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sql_memory import SQLMemory

class HealthChecker:
    """Verify system components are operational"""
    
    def __init__(self, backend='cloud'):
        self.mem = SQLMemory(backend=backend)
        self.checks = {}
    
    def check_ui(self):
        """Verify UI server responds"""
        try:
            result = subprocess.run(
                ['curl', '-s', '-I', 'http://localhost:3000'],
                capture_output=True,
                timeout=3
            )
            status = 'UP' if b'200' in result.stdout else 'DOWN'
            self.checks['ui'] = status
            
            # If down, try restart
            if status == 'DOWN':
                self._restart_ui()
                self.checks['ui_restart'] = 'ATTEMPTED'
            
            return status
        except Exception as e:
            self.checks['ui'] = f'ERROR: {str(e)[:50]}'
            return 'ERROR'
    
    def check_github(self):
        """Verify GitHub authentication"""
        try:
            result = subprocess.run(
                ['gh', 'auth', 'status'],
                capture_output=True,
                timeout=3,
                text=True
            )
            status = 'OK' if result.returncode == 0 else 'FAIL'
            self.checks['github'] = status
            return status
        except Exception as e:
            self.checks['github'] = 'ERROR'
            return 'ERROR'
    
    def check_stamps_agent(self):
        """Verify STAMPS agent is syntactically valid"""
        try:
            result = subprocess.run(
                ['python3', '-m', 'py_compile', 
                 '/home/oblio/.openclaw/workspace/agents/agent_stamps.py'],
                capture_output=True,
                timeout=3
            )
            status = 'OK' if result.returncode == 0 else 'SYNTAX_ERROR'
            self.checks['stamps_agent'] = status
            return status
        except Exception as e:
            self.checks['stamps_agent'] = 'ERROR'
            return 'ERROR'
    
    def check_cron_jobs(self):
        """Count active cron jobs"""
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                timeout=3,
                text=True
            )
            count = len([l for l in result.stdout.split('\n') 
                        if l.strip() and not l.startswith('#')])
            status = f"{count} jobs"
            self.checks['cron'] = status
            return status
        except Exception as e:
            self.checks['cron'] = 'ERROR'
            return 'ERROR'
    
    def check_database(self):
        """Verify database connectivity"""
        try:
            result = self.mem.ping()
            status = 'OK' if result else 'FAIL'
            self.checks['database'] = status
            return status
        except Exception as e:
            self.checks['database'] = 'ERROR'
            return 'ERROR'
    
    def run_all_checks(self):
        """Run all health checks"""
        self.check_ui()
        self.check_github()
        self.check_stamps_agent()
        self.check_cron_jobs()
        self.check_database()
        
        # Log results to SQL
        self.mem.log_event(
            'health_check_cycle',
            'health_checker',
            f"All checks: {json.dumps(self.checks, indent=2)}",
            json.dumps(self.checks)
        )
        
        return self.checks
    
    def _restart_ui(self):
        """Attempt to restart UI server"""
        try:
            subprocess.run(['pkill', '-f', 'node server.js'], capture_output=True)
            subprocess.Popen(
                ['node', 'server.js'],
                cwd='/home/oblio/.openclaw/workspace/ui',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except:
            return False

if __name__ == '__main__':
    checker = HealthChecker()
    results = checker.run_all_checks()
    
    print("System Health Check Results:")
    for check, status in results.items():
        print(f"  {check}: {status}")
