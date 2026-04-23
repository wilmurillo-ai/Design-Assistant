#!/usr/bin/env python3
"""Tests for auto_observe.py"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

import auto_observe
import observer


class TestClassifyIssues(unittest.TestCase):
    def test_empty_error(self):
        self.assertEqual(auto_observe.classify_issues(""), [])

    def test_rate_limit(self):
        issues = auto_observe.classify_issues("Got 429 too many requests")
        self.assertIn("rate_limit", issues)

    def test_empty_response(self):
        issues = auto_observe.classify_issues("LLM returned empty response")
        self.assertIn("empty_response", issues)

    def test_session_reset(self):
        issues = auto_observe.classify_issues("context_length exceeded, session reset")
        self.assertIn("session_reset", issues)

    def test_multiple_issues(self):
        issues = auto_observe.classify_issues("tool error with empty response after timeout")
        self.assertIn("tool_error", issues)
        self.assertIn("empty_response", issues)

    def test_existing_issues_preserved(self):
        issues = auto_observe.classify_issues("rate limit hit", ["skill_gap"])
        self.assertIn("skill_gap", issues)
        self.assertIn("rate_limit", issues)

    def test_no_duplicates(self):
        issues = auto_observe.classify_issues("rate limit 429", ["rate_limit"])
        self.assertEqual(issues.count("rate_limit"), 1)

    def test_wal_miss(self):
        issues = auto_observe.classify_issues("forgot wal before session end")
        self.assertIn("wal_miss", issues)

    def test_hydration_fail(self):
        issues = auto_observe.classify_issues("hydration failed, missed wake detection")
        self.assertIn("hydration_fail", issues)


class TestClassifyTask(unittest.TestCase):
    def test_explicit_task(self):
        self.assertEqual(auto_observe.classify_task("anything", "code_generation"), "code_generation")

    def test_from_description(self):
        self.assertEqual(auto_observe.classify_task("debug the login bug"), "code_debug")

    def test_unknown_fallback(self):
        self.assertEqual(auto_observe.classify_task("xyzzy foobar"), "unknown")

    def test_existing_unknown_overridden(self):
        self.assertEqual(auto_observe.classify_task("write code for parser", "unknown"), "code_generation")


class TestAutoObserve(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_data_dir = observer.DATA_DIR
        self.orig_outcomes = observer.OUTCOMES_FILE
        observer.DATA_DIR = Path(self.tmpdir)
        observer.OUTCOMES_FILE = Path(self.tmpdir) / "outcomes.jsonl"
        auto_observe.DATA_DIR = Path(self.tmpdir)

    def tearDown(self):
        observer.DATA_DIR = self.orig_data_dir
        observer.OUTCOMES_FILE = self.orig_outcomes

    def test_basic_success(self):
        result = auto_observe.auto_observe({
            "task": "code_generation",
            "success": True,
            "source": "openclaw",
        })
        self.assertTrue(result["record"]["success"])
        self.assertEqual(result["record"]["source"], "openclaw")
        self.assertEqual(result["record"]["task_type"], "code_generation")

    def test_failure_with_error(self):
        result = auto_observe.auto_observe({
            "task": "web_search",
            "success": False,
            "error_msg": "returned empty response",
            "source": "subagent",
        })
        self.assertFalse(result["record"]["success"])
        self.assertIn("empty_response", result["record"]["issues"])
        self.assertEqual(result["record"]["quality"], 1)  # high-severity auto-quality

    def test_auto_classify_task(self):
        result = auto_observe.auto_observe({
            "description": "debugging the login flow",
            "success": True,
            "source": "evoclaw",
        })
        self.assertEqual(result["record"]["task_type"], "code_debug")

    def test_quality_auto_infer(self):
        # Success with no issues → quality 4
        r1 = auto_observe.auto_observe({"task": "file_ops", "success": True, "source": "cron"})
        self.assertEqual(r1["record"]["quality"], 4)

        # Failure with non-high-severity → quality 2
        r2 = auto_observe.auto_observe({
            "task": "file_ops", "success": False,
            "error_msg": "something weird happened", "source": "cron"
        })
        self.assertEqual(r2["record"]["quality"], 2)

    def test_recurrence_detection(self):
        # Log 3 outcomes with same issue
        for _ in range(3):
            auto_observe.auto_observe({
                "task": "code_generation",
                "success": False,
                "error_msg": "returned empty response",
                "source": "openclaw",
            })
        # 4th should flag recurrence (3 existing + 1 new = 4 >= 3)
        result = auto_observe.auto_observe({
            "task": "code_generation",
            "success": False,
            "error_msg": "returned empty response",
            "source": "openclaw",
        })
        self.assertTrue(len(result["recurrence_flags"]) > 0)
        flag = result["recurrence_flags"][0]
        self.assertEqual(flag["issue"], "empty_response")
        self.assertGreaterEqual(flag["count"], 3)

    def test_outcomes_file_written(self):
        auto_observe.auto_observe({
            "task": "monitoring",
            "success": True,
            "source": "cron",
        })
        outcomes_path = Path(self.tmpdir) / "outcomes.jsonl"
        self.assertTrue(outcomes_path.exists())
        with open(outcomes_path) as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["task_type"], "monitoring")


class TestDetectRecurrence(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.orig_outcomes = observer.OUTCOMES_FILE
        observer.OUTCOMES_FILE = Path(self.tmpdir) / "outcomes.jsonl"

    def tearDown(self):
        observer.OUTCOMES_FILE = self.orig_outcomes

    def test_no_recurrence_when_empty(self):
        flags = auto_observe.detect_recurrence(["tool_error"], "openclaw")
        self.assertEqual(flags, [])

    def test_no_recurrence_below_threshold(self):
        # Log 1 outcome
        observer.log_outcome("code_generation", False, 2, issues=["tool_error"])
        flags = auto_observe.detect_recurrence(["tool_error"], "openclaw", threshold=3)
        # 1 existing + 1 new = 2, below threshold of 3
        self.assertEqual(len(flags), 0)


if __name__ == "__main__":
    unittest.main()
