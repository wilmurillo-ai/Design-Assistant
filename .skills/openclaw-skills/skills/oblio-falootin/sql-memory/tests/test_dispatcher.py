#!/usr/bin/env python3
"""
test_dispatcher.py — Unit tests for TaskDispatcher
"""

import unittest
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "infrastructure"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))

from agent_dispatcher import TaskDispatcher


class TestGitHubSetup(unittest.TestCase):
    """Test GitHub setup operations."""
    
    def setUp(self):
        with patch.object(TaskDispatcher, '__init__', lambda x: None):
            self.dispatcher = TaskDispatcher()
            self.dispatcher.mem = MagicMock()
            self.dispatcher.log = MagicMock()
        self.test_task_id = 1
    
    @patch('subprocess.run')
    def test_github_setup_success(self, mock_run):
        """Test successful GitHub auth verification."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="Oblio-Falootin\n", stderr=""),
            Mock(returncode=0, stdout="AI-UI\nsequel-memory-skill\n", stderr="")
        ]
        
        result = self.dispatcher._handle_github_setup(self.test_task_id, {})
        
        self.assertEqual(result, "SUCCESS")
        self.dispatcher.mem.complete_task.assert_called_once()


class TestGitHubClone(unittest.TestCase):
    """Test GitHub clone operations."""
    
    def setUp(self):
        with patch.object(TaskDispatcher, '__init__', lambda x: None):
            self.dispatcher = TaskDispatcher()
            self.dispatcher.mem = MagicMock()
            self.dispatcher.log = MagicMock()
        self.test_task_id = 2
    
    def test_clone_missing_repo_param(self):
        """Test clone with missing repo parameter."""
        result = self.dispatcher._handle_github_clone(self.test_task_id, {})
        
        self.assertEqual(result, "FAIL")
        self.dispatcher.mem.fail_task.assert_called_once()


class TestGitHubCheckin(unittest.TestCase):
    """Test GitHub checkin operations."""
    
    def setUp(self):
        with patch.object(TaskDispatcher, '__init__', lambda x: None):
            self.dispatcher = TaskDispatcher()
            self.dispatcher.mem = MagicMock()
            self.dispatcher.log = MagicMock()
        self.test_task_id = 3
    
    def test_checkin_missing_repo_param(self):
        """Test checkin with missing repo parameter."""
        result = self.dispatcher._handle_github_checkin(self.test_task_id, {})
        
        self.assertEqual(result, "FAIL")
        self.dispatcher.mem.fail_task.assert_called_once()


class TestUIFix(unittest.TestCase):
    """Test UI endpoint fixes."""
    
    def setUp(self):
        with patch.object(TaskDispatcher, '__init__', lambda x: None):
            self.dispatcher = TaskDispatcher()
            self.dispatcher.mem = MagicMock()
            self.dispatcher.log = MagicMock()
        self.test_task_id = 4
    
    def test_ui_fix_unknown_component(self):
        """Test UI fix with unknown component."""
        result = self.dispatcher._handle_ui_fix(self.test_task_id, {"component": "unknown"})
        
        self.assertEqual(result, "FAIL")
        self.dispatcher.mem.fail_task.assert_called_once()


class TestSecurityTest(unittest.TestCase):
    """Test security operations."""
    
    def setUp(self):
        with patch.object(TaskDispatcher, '__init__', lambda x: None):
            self.dispatcher = TaskDispatcher()
            self.dispatcher.mem = MagicMock()
            self.dispatcher.log = MagicMock()
        self.test_task_id = 5
    
    def test_security_test_unknown_component(self):
        """Test security test with unknown component."""
        result = self.dispatcher._handle_security_test(self.test_task_id, {"component": "unknown"})
        
        self.assertEqual(result, "FAIL")
        self.dispatcher.mem.fail_task.assert_called_once()


class TestTaskRouting(unittest.TestCase):
    """Test task type routing."""
    
    def setUp(self):
        with patch.object(TaskDispatcher, '__init__', lambda x: None):
            self.dispatcher = TaskDispatcher()
            self.dispatcher.mem = MagicMock()
            self.dispatcher.log = MagicMock()
    
    @patch('agent_dispatcher.TaskDispatcher._handle_github_setup')
    def test_route_github_setup(self, mock_handler):
        """Test routing to github_setup handler."""
        mock_handler.return_value = "SUCCESS"
        
        task = {
            "id": 1,
            "task_type": "github_setup",
            "payload": "{}"
        }
        
        result = self.dispatcher.run_task(task)
        
        self.assertEqual(result, "SUCCESS")
    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON payload."""
        task = {
            "id": 2,
            "task_type": "github_setup",
            "payload": "invalid json"
        }
        
        result = self.dispatcher.run_task(task)
        
        self.assertEqual(result, "FAIL")
    
    def test_unknown_task_type(self):
        """Test handling of unknown task type."""
        task = {
            "id": 3,
            "task_type": "unknown_type",
            "payload": "{}"
        }
        
        result = self.dispatcher.run_task(task)
        
        self.assertEqual(result, "FAIL")


if __name__ == '__main__':
    unittest.main()


