#!/usr/bin/env python3
"""Tests for openclaw_shim.py — pattern detection, dedup, aggregation."""

import json
import tempfile
from pathlib import Path

import pytest

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent))
from openclaw_shim import (
    detect_tool_validation_error,
    detect_is_error_tool_result,
    detect_context_reset,
    detect_model_fallback,
    detect_rate_limit,
    detect_timeout,
    scan_session_file,
    aggregate_hits,
    DETECTORS,
    MAX_SAMPLES,
)


# ── Helper to build JSONL entries ───────────────────────────────────────────────

def make_tool_result(tool_name: str, content_text: str, is_error: bool = False,
                     details: dict | None = None) -> dict:
    """Build a realistic OpenClaw toolResult entry."""
    return {
        "type": "message",
        "id": "test123",
        "timestamp": "2026-02-20T10:00:00.000Z",
        "message": {
            "role": "toolResult",
            "toolCallId": "call_abc",
            "toolName": tool_name,
            "content": [{"type": "text", "text": content_text}],
            "details": details or {},
            "isError": is_error,
            "timestamp": 1771548731404,
        },
    }


def make_system_entry(entry_type: str, **kwargs) -> dict:
    return {"type": entry_type, "timestamp": "2026-02-20T10:00:00.000Z", **kwargs}


# ── Test: No false positives on normal tool output ──────────────────────────────

class TestNoFalsePositives:
    """Ensure normal tool output containing 'error' words is NOT flagged."""

    def test_tool_output_with_error_word(self):
        """Tool output mentioning 'error' in content should not trigger."""
        entry = make_tool_result("exec", '{"status":"completed","output":"Error: file not found"}')
        for detector in DETECTORS:
            assert detector(entry) is None

    def test_tool_output_with_error_in_details_content(self):
        """Tool with error in details but isError=false."""
        entry = make_tool_result(
            "web_search",
            '{"error": "missing_brave_api_key", "message": "web_search needs a key"}',
            is_error=False,
            details={"error": "missing_brave_api_key", "message": "needs key"},
        )
        for detector in DETECTORS:
            assert detector(entry) is None

    def test_tool_output_with_timeout_word(self):
        """Content mentioning timeout should not trigger if isError=false."""
        entry = make_tool_result("exec", "Connection timeout error in logs")
        for detector in DETECTORS:
            assert detector(entry) is None

    def test_assistant_message_with_error_word(self):
        """Assistant messages are never flagged."""
        entry = {
            "type": "message",
            "timestamp": "2026-02-20T10:00:00.000Z",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "I got an error when trying the tool"}],
            },
        }
        for detector in DETECTORS:
            assert detector(entry) is None

    def test_user_message_with_error_word(self):
        """User messages are never flagged."""
        entry = {
            "type": "message",
            "timestamp": "2026-02-20T10:00:00.000Z",
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "Fix this error please"}],
            },
        }
        for detector in DETECTORS:
            assert detector(entry) is None

    def test_normal_model_change(self):
        """Normal model changes are not flagged."""
        entry = {
            "type": "model_change",
            "timestamp": "2026-02-20T10:00:00.000Z",
            "provider": "anthropic-proxy-4",
            "modelId": "glm-4.7",
        }
        for detector in DETECTORS:
            assert detector(entry) is None

    def test_session_header(self):
        """Session header lines are not flagged."""
        entry = {"type": "session", "version": 3, "id": "abc-123", "timestamp": "2026-02-20T10:00:00.000Z"}
        for detector in DETECTORS:
            assert detector(entry) is None


# ── Test: True positives (real errors ARE detected) ─────────────────────────────

class TestTruePositives:
    def test_validation_error_detected(self):
        entry = make_tool_result(
            "message",
            'Validation failed for tool "message":\n  - action: must have required property \'action\'',
            is_error=True,
        )
        result = detect_tool_validation_error(entry)
        assert result is not None
        assert result[0] == "tool_validation_error"

    def test_tool_not_found_detected(self):
        entry = make_tool_result(
            "<tool_call>exec",
            "Tool <tool_call>exec not found",
            is_error=True,
        )
        result = detect_tool_validation_error(entry)
        assert result is not None
        assert result[0] == "tool_not_found"

    def test_generic_tool_error_with_is_error(self):
        entry = make_tool_result(
            "exec",
            "Command failed with signal SIGKILL",
            is_error=True,
        )
        result = detect_is_error_tool_result(entry)
        assert result is not None
        assert result[0] == "tool_error"

    def test_context_reset_detected(self):
        entry = make_system_entry("context_reset")
        result = detect_context_reset(entry)
        assert result is not None
        assert result[0] == "session_reset"

    def test_compaction_detected(self):
        entry = make_system_entry("compaction")
        result = detect_compaction_entry(entry)
        assert result is not None
        assert result[0] == "context_loss"

    def test_rate_limit_429_in_details(self):
        entry = make_tool_result(
            "web_fetch", "Rate limited",
            is_error=False,
            details={"status": 429, "message": "Too many requests"},
        )
        result = detect_rate_limit(entry)
        assert result is not None
        assert result[0] == "rate_limit"

    def test_rate_limit_system_error(self):
        entry = {"type": "error", "timestamp": "2026-02-20T10:00:00.000Z",
                 "error": "429 Too Many Requests"}
        result = detect_rate_limit(entry)
        assert result is not None

    def test_timeout_system_error(self):
        entry = {"type": "error", "timestamp": "2026-02-20T10:00:00.000Z",
                 "error": "Request timed out after 30s"}
        result = detect_timeout(entry)
        assert result is not None
        assert result[0] == "timeout"

    def test_timeout_in_tool_details(self):
        entry = make_tool_result(
            "exec", "output text",
            is_error=False,
            details={"error": "Command timed out", "status": "timeout"},
        )
        result = detect_timeout(entry)
        assert result is not None
        assert result[0] == "timeout"


# Fix reference to compaction detector
def detect_compaction_entry(entry):
    return detect_context_reset(entry)


# ── Test: scan_session_file ─────────────────────────────────────────────────────

class TestScanSessionFile:
    def _write_jsonl(self, lines: list[dict]) -> Path:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        for line in lines:
            f.write(json.dumps(line) + "\n")
        f.close()
        return Path(f.name)

    def test_no_false_positives_on_normal_session(self):
        """A session with normal tool output should produce zero hits."""
        lines = [
            {"type": "session", "version": 3, "id": "test", "timestamp": "2026-02-20T10:00:00Z"},
            {"type": "model_change", "timestamp": "2026-02-20T10:00:00Z", "provider": "x", "modelId": "y"},
            make_tool_result("exec", "Error: file not found", is_error=False),
            make_tool_result("web_search",
                             '{"error":"missing_brave_api_key","message":"needs key"}',
                             is_error=False,
                             details={"error": "missing_brave_api_key"}),
            make_tool_result("exec", "timeout connecting to server", is_error=False),
            {
                "type": "message", "timestamp": "2026-02-20T10:00:00Z",
                "message": {"role": "assistant", "content": [{"type": "text", "text": "I see the tool error"}]},
            },
        ]
        path = self._write_jsonl(lines)
        try:
            hits = scan_session_file(path)
            assert len(hits) == 0, f"Expected 0 hits but got {len(hits)}: {hits}"
        finally:
            path.unlink()

    def test_detects_real_errors(self):
        """Real isError=true entries should be detected."""
        lines = [
            {"type": "session", "version": 3, "id": "test", "timestamp": "2026-02-20T10:00:00Z"},
            make_tool_result("message", 'Validation failed for tool "message"', is_error=True),
            make_tool_result("<tool_call>exec", "Tool <tool_call>exec not found", is_error=True),
        ]
        path = self._write_jsonl(lines)
        try:
            hits = scan_session_file(path)
            assert len(hits) == 2
            issue_types = {h[0] for h in hits}
            assert "tool_validation_error" in issue_types
            assert "tool_not_found" in issue_types
        finally:
            path.unlink()

    def test_handles_malformed_json(self):
        """Non-JSON lines should be skipped, not crash."""
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
        f.write("not json\n")
        f.write('{"type":"session"}\n')
        f.write("{bad json\n")
        f.close()
        path = Path(f.name)
        try:
            hits = scan_session_file(path)
            assert len(hits) == 0
        finally:
            path.unlink()


# ── Test: Aggregation ───────────────────────────────────────────────────────────

class TestAggregation:
    def test_groups_by_session_and_issue(self):
        """Same issue in same session should be grouped into one event."""
        all_hits = {
            "session-abc.jsonl": [
                ("tool_error", "Tool 'exec' error: fail1", "ts1"),
                ("tool_error", "Tool 'exec' error: fail2", "ts2"),
                ("tool_error", "Tool 'exec' error: fail3", "ts3"),
            ],
        }
        events = aggregate_hits(all_hits)
        assert len(events) == 1
        assert events[0]["count"] == 3
        assert "seen 3 times" in events[0]["error_message"]

    def test_different_issues_same_session(self):
        """Different issue types in same session -> separate events."""
        all_hits = {
            "session-abc.jsonl": [
                ("tool_error", "fail", "ts1"),
                ("rate_limit", "429", "ts2"),
            ],
        }
        events = aggregate_hits(all_hits)
        assert len(events) == 2

    def test_same_issue_different_sessions(self):
        """Same issue in different sessions -> separate events."""
        all_hits = {
            "session-1.jsonl": [("tool_error", "fail", "ts1")],
            "session-2.jsonl": [("tool_error", "fail", "ts2")],
        }
        events = aggregate_hits(all_hits)
        assert len(events) == 2

    def test_samples_capped(self):
        """Samples should be capped at MAX_SAMPLES."""
        all_hits = {
            "s.jsonl": [("tool_error", f"error {i}", f"ts{i}") for i in range(20)],
        }
        events = aggregate_hits(all_hits)
        assert len(events) == 1
        assert len(events[0]["samples"]) == MAX_SAMPLES
        assert events[0]["count"] == 20

    def test_sorted_by_count_descending(self):
        """Events should be sorted most-frequent first."""
        all_hits = {
            "s.jsonl": [
                ("rate_limit", "429", "ts1"),
                *[("tool_error", f"e{i}", f"ts{i}") for i in range(5)],
            ],
        }
        events = aggregate_hits(all_hits)
        assert events[0]["issues"][0] == "tool_error"
        assert events[0]["count"] == 5

    def test_single_occurrence_no_count_suffix(self):
        """Single occurrence should not have 'seen X times' suffix."""
        all_hits = {"s.jsonl": [("tool_error", "one error", "ts1")]}
        events = aggregate_hits(all_hits)
        assert "seen" not in events[0]["error_message"]

    def test_empty_hits(self):
        """Empty input produces empty output."""
        assert aggregate_hits({}) == []


# ── Test: parse_since ───────────────────────────────────────────────────────────

class TestParseSince:
    def test_hours(self):
        from openclaw_shim import parse_since
        import time
        ts = parse_since("2h")
        assert abs(ts - (time.time() - 7200)) < 2

    def test_days(self):
        from openclaw_shim import parse_since
        import time
        ts = parse_since("1d")
        assert abs(ts - (time.time() - 86400)) < 2

    def test_invalid_defaults_1h(self):
        from openclaw_shim import parse_since
        import time
        ts = parse_since("invalid")
        assert abs(ts - (time.time() - 3600)) < 2


# ── Test: dropped request detection (incomplete_task) ──────────────────────────

def _make_user_msg(text: str, ts: str = "2026-02-20T10:00:00.000Z") -> dict:
    return {
        "type": "message",
        "timestamp": ts,
        "message": {
            "role": "user",
            "content": [{"type": "text", "text": text}],
        },
    }


def _make_assistant_msg(text: str = "OK", ts: str = "2026-02-20T10:01:00.000Z") -> dict:
    return {
        "type": "message",
        "timestamp": ts,
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": text}],
        },
    }


def _make_context_reset(ts: str = "2026-02-20T10:00:30.000Z") -> dict:
    return {"type": "context_reset", "timestamp": ts}


def _write_jsonl(lines: list[dict]) -> Path:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for line in lines:
        f.write(json.dumps(line) + "\n")
    f.close()
    return Path(f.name)


class TestDroppedRequests:
    """Tests for incomplete_task detection (dropped user requests at session reset)."""

    def test_request_dropped_at_context_reset(self):
        """User message followed by context_reset with no assistant response = dropped."""
        f = _write_jsonl([
            _make_assistant_msg("Previous answer"),          # prior response exists
            _make_user_msg("Read https://docs.openclaw.ai/tools/lobster"),
            _make_context_reset(),
        ])
        hits = scan_session_file(f, is_active=False)
        dropped = [h for h in hits if h[0] == "incomplete_task"]
        assert len(dropped) == 1
        assert "lobster" in dropped[0][1].lower() or "dropped" in dropped[0][1].lower()

    def test_request_answered_not_flagged(self):
        """User message followed by assistant response = NOT dropped."""
        f = _write_jsonl([
            _make_user_msg("What is lobster?"),
            _make_assistant_msg("Lobster is a workflow tool."),
            _make_context_reset(),
        ])
        hits = scan_session_file(f, is_active=False)
        dropped = [h for h in hits if h[0] == "incomplete_task"]
        assert len(dropped) == 0

    def test_request_at_eof_closed_session(self):
        """User message at end of closed (non-active) session with prior responses = dropped."""
        f = _write_jsonl([
            _make_assistant_msg("Earlier response"),
            _make_user_msg("Address it"),
        ])
        hits = scan_session_file(f, is_active=False)
        dropped = [h for h in hits if h[0] == "incomplete_task"]
        assert len(dropped) == 1
        assert "address it" in dropped[0][1].lower() or "no response" in dropped[0][1].lower()

    def test_request_at_eof_active_session_not_flagged(self):
        """User message at end of active session = NOT flagged (in-flight)."""
        f = _write_jsonl([
            _make_assistant_msg("Earlier response"),
            _make_user_msg("Address it"),
        ])
        hits = scan_session_file(f, is_active=True)
        dropped = [h for h in hits if h[0] == "incomplete_task"]
        assert len(dropped) == 0

    def test_no_prior_responses_eof_not_flagged(self):
        """Brand-new session with only user message at EOF = NOT flagged."""
        f = _write_jsonl([
            _make_user_msg("Hello"),
        ])
        hits = scan_session_file(f, is_active=False)
        dropped = [h for h in hits if h[0] == "incomplete_task"]
        assert len(dropped) == 0

    def test_compaction_resets_pending(self):
        """context_loss (compaction) after unanswered user message is also flagged."""
        f = _write_jsonl([
            _make_assistant_msg("Previous answer"),
            _make_user_msg("Summarize this"),
            {"type": "compaction", "timestamp": "2026-02-20T10:00:30.000Z"},
        ])
        hits = scan_session_file(f, is_active=False)
        dropped = [h for h in hits if h[0] == "incomplete_task"]
        assert len(dropped) == 1
