#!/usr/bin/env python3
"""Tests for auto_fix.py"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

import auto_fix


class TestFindPattern(unittest.TestCase):
    def test_find_existing(self):
        patterns = [{"id": "test-123", "issue": "tool_error"}]
        with patch.object(auto_fix, "load_patterns", return_value=patterns):
            result = auto_fix.find_pattern("test-123")
            self.assertIsNotNone(result)
            self.assertEqual(result["id"], "test-123")

    def test_find_missing(self):
        with patch.object(auto_fix, "load_patterns", return_value=[]):
            result = auto_fix.find_pattern("nonexistent")
            self.assertIsNone(result)


class TestGenerateFixProposal(unittest.TestCase):
    def test_basic_proposal(self):
        pattern = {
            "id": "code_gen-rate_lim-5",
            "category": "model_routing",
            "task_type": "code_generation",
            "issue": "rate_limit",
            "frequency": 5,
            "impact_score": 0.42,
            "failure_rate": 0.8,
            "avg_quality": 2.0,
            "description": "rate_limit in code_generation 5x",
            "sample_notes": ["hit rate limit on openai"],
            "suggested_action": "Update routing",
        }
        with patch.object(auto_fix, "search_codebase", return_value=[]):
            proposal = auto_fix.generate_fix_proposal(pattern)

        self.assertEqual(proposal["pattern_id"], "code_gen-rate_lim-5")
        self.assertEqual(proposal["status"], "draft")
        self.assertEqual(proposal["issue"], "rate_limit")
        self.assertTrue(proposal["auto_fixable"])  # model_routing is safe
        self.assertEqual(proposal["fix_type"], "retry_logic")

    def test_unsafe_category(self):
        pattern = {
            "id": "code_gen-skill_ga-3",
            "category": "skill_gap",
            "task_type": "code_generation",
            "issue": "skill_gap",
            "frequency": 3,
            "impact_score": 0.3,
            "failure_rate": 0.6,
            "avg_quality": 2.5,
            "description": "skill_gap in code_generation",
            "sample_notes": [],
            "suggested_action": "Create skill",
        }
        with patch.object(auto_fix, "search_codebase", return_value=[]):
            proposal = auto_fix.generate_fix_proposal(pattern)

        self.assertFalse(proposal["auto_fixable"])

    def test_empty_response_fix_type(self):
        pattern = {
            "id": "web_sea-empty_re-4",
            "category": "tool_reliability",
            "task_type": "web_search",
            "issue": "empty_response",
            "frequency": 4,
            "impact_score": 0.5,
            "failure_rate": 1.0,
            "avg_quality": 1.0,
            "description": "empty_response in web_search",
            "sample_notes": [],
            "suggested_action": "Add retry",
        }
        with patch.object(auto_fix, "search_codebase", return_value=[]):
            proposal = auto_fix.generate_fix_proposal(pattern)

        self.assertEqual(proposal["fix_type"], "retry_logic")


class TestAutoFix(unittest.TestCase):
    def test_pattern_not_found(self):
        with patch.object(auto_fix, "find_pattern", return_value=None):
            result = auto_fix.auto_fix("nonexistent")
            self.assertIn("error", result)
            self.assertFalse(result["applied"])

    def test_dry_run(self):
        pattern = {
            "id": "test-pat-1",
            "category": "other",
            "task_type": "unknown",
            "issue": "other",
            "frequency": 2,
            "impact_score": 0.1,
            "failure_rate": 0.5,
            "avg_quality": 3.0,
            "description": "test pattern",
            "sample_notes": [],
            "suggested_action": "Investigate",
        }
        with patch.object(auto_fix, "find_pattern", return_value=pattern), \
             patch.object(auto_fix, "search_codebase", return_value=[]):
            result = auto_fix.auto_fix("test-pat-1", dry_run=True)
            self.assertFalse(result["applied"])
            self.assertIn("Dry run", result["message"])

    def test_saves_proposal(self):
        pattern = {
            "id": "test-pat-2",
            "category": "model_routing",
            "task_type": "code_generation",
            "issue": "rate_limit",
            "frequency": 5,
            "impact_score": 0.4,
            "failure_rate": 0.8,
            "avg_quality": 2.0,
            "description": "test",
            "sample_notes": [],
            "suggested_action": "Fix routing",
        }
        tmpdir = tempfile.mkdtemp()
        with patch.object(auto_fix, "find_pattern", return_value=pattern), \
             patch.object(auto_fix, "search_codebase", return_value=[]), \
             patch.object(auto_fix, "PROPOSALS_DIR", Path(tmpdir) / "proposals"):
            result = auto_fix.auto_fix("test-pat-2", dry_run=False)
            self.assertIn("proposal_path", result)
            self.assertTrue(Path(result["proposal_path"]).exists())


class TestSearchCodebase(unittest.TestCase):
    def test_returns_list(self):
        results = auto_fix.search_codebase(["import json"])
        self.assertIsInstance(results, list)

    def test_filters_pycache(self):
        results = auto_fix.search_codebase(["import"])
        for r in results:
            self.assertNotIn("__pycache__", r["file"])


class TestAutoFixAllSafe(unittest.TestCase):
    def test_empty_patterns(self):
        with patch.object(auto_fix, "load_patterns", return_value=[]):
            results = auto_fix.auto_fix_all_safe(dry_run=True)
            self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
