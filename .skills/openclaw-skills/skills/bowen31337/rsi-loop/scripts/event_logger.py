#!/usr/bin/env python3
"""
RSI Loop - EvolutionEvent Logger
Appends structured EvolutionEvent records to data/events.jsonl.
Part of RSI Loop v2.0 Gene Registry (Phase 2).
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
EVENTS_FILE = DATA_DIR / "events.jsonl"


def _compute_asset_id(event: dict) -> str:
    """SHA-256 of canonical event JSON (excluding asset_id), first 16 chars."""
    clean = {k: v for k, v in event.items() if k != "asset_id"}
    canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def _make_event_id() -> str:
    now = datetime.now(timezone.utc)
    return f"evt_{now.strftime('%Y%m%d_%H%M%S')}"


def log_event(
    mutation_type: str,
    gene_id: str = None,
    capsule_id: str = None,
    signals: dict = None,
    outcome: dict = None,
    files_changed: list = None,
) -> dict:
    """
    Append one EvolutionEvent to data/events.jsonl.

    Args:
        mutation_type:  "repair" | "optimize" | "innovate"
        gene_id:        Gene ID used (or None)
        capsule_id:     Capsule ID used (or None)
        signals:        dict with top_pattern, repair_ratio_last8, forced_innovate
        outcome:        dict with status, validation_passed, quality, notes
        files_changed:  list of file paths actually modified

    Returns:
        The event dict that was written.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    strategy = os.environ.get("EVOLVE_STRATEGY", "balanced")

    _signals = {
        "top_pattern": "",
        "repair_ratio_last8": 0.0,
        "forced_innovate": False,
    }
    if signals:
        _signals.update(signals)

    _outcome = {
        "status": "skipped",
        "validation_passed": True,
        "quality": None,
        "notes": "",
    }
    if outcome:
        _outcome.update(outcome)

    paths = list(files_changed) if files_changed else []

    event = {
        "event_id": _make_event_id(),
        "schema_version": "1.0",
        "timestamp": now.isoformat(),
        "mutation_type": mutation_type,
        "strategy": strategy,
        "gene_id": gene_id,
        "capsule_id": capsule_id,
        "signals": _signals,
        "blast_radius_actual": {
            "files_changed": len(paths),
            "paths": paths,
        },
        "outcome": _outcome,
        "personality_delta": {},
    }

    # Compute asset_id before writing
    event["asset_id"] = _compute_asset_id(event)

    # Update personality state after each completed event
    try:
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).parent))
        from personality import update_personality
        success = (_outcome.get("status") == "success")
        p_result = update_personality(mutation_type, success)
        event["personality_delta"] = {
            "current_bias": p_result.get("current_bias", "balanced"),
        }
    except Exception:
        pass

    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

    return event


def load_events(last_n: int = None) -> list:
    """Load EvolutionEvents from events.jsonl. Returns list of event dicts."""
    if not EVENTS_FILE.exists():
        return []
    events = []
    with open(EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                pass
    if last_n is not None:
        events = events[-last_n:]
    return events


def get_recent_innovation_targets(events: list, last_n: int = 10) -> dict:
    """
    Return {path: count} of paths innovated in the last N events.
    Used by synthesizer to apply innovation cooldown.
    """
    recent = events[-last_n:] if len(events) > last_n else events
    counts: dict = {}
    for event in recent:
        if event.get("mutation_type") != "innovate":
            continue
        paths = event.get("blast_radius_actual", {}).get("paths", [])
        for path in paths:
            counts[path] = counts.get(path, 0) + 1
    return counts


if __name__ == "__main__":
    # Quick smoke test
    import argparse

    parser = argparse.ArgumentParser(description="EvolutionEvent Logger")
    parser.add_argument("--test", action="store_true", help="Log a test event")
    args = parser.parse_args()

    if args.test:
        evt = log_event(
            mutation_type="optimize",
            signals={"top_pattern": "test/smoke", "repair_ratio_last8": 0.0, "forced_innovate": False},
            outcome={"status": "success", "validation_passed": True, "quality": 4, "notes": "Smoke test"},
            files_changed=["skills/rsi-loop/scripts/event_logger.py"],
        )
        print(f"Logged event: {evt['event_id']}")
        print(json.dumps(evt, indent=2))
