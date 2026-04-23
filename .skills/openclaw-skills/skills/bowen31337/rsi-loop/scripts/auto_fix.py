#!/usr/bin/env python3
"""
RSI Loop - Auto Fix
Takes a detected pattern and attempts to find root cause and generate/apply fixes.

Safe categories (auto-apply): routing config, threshold tuning, retry logic.
Everything else: write proposal to data/proposals/ for review.

Usage:
    uv run python skills/rsi-loop/scripts/auto_fix.py --pattern-id "code_gen-skill_ga-5"
    uv run python skills/rsi-loop/scripts/auto_fix.py --pattern-id "code_gen-empty_re-3" --dry-run
"""

import argparse
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
PATTERNS_FILE = DATA_DIR / "patterns.json"
PROPOSALS_DIR = DATA_DIR / "proposals"
WORKSPACE = Path(__file__).parent.parent.parent.parent  # /home/bowen/clawd

# Categories where auto-fix is safe to apply
SAFE_CATEGORIES = {
    "model_routing",      # routing config changes
}

# Issue → fix templates
FIX_TEMPLATES = {
    "rate_limit": {
        "search_patterns": ["rate_limit", "429", "retry"],
        "fix_type": "retry_logic",
        "description": "Add/increase retry backoff for rate-limited endpoints",
    },
    "model_fallback": {
        "search_patterns": ["fallback", "model_fallback", "model unavailable"],
        "fix_type": "routing_config",
        "description": "Update model fallback chain in intelligent-router config",
    },
    "wrong_model_tier": {
        "search_patterns": ["model_tier", "cost_overrun", "spawn_helper"],
        "fix_type": "routing_config",
        "description": "Adjust tier classification thresholds in spawn_helper",
    },
    "cost_overrun": {
        "search_patterns": ["cost", "expensive", "premium"],
        "fix_type": "routing_config",
        "description": "Lower cost ceiling or adjust model routing",
    },
    "slow_response": {
        "search_patterns": ["timeout", "slow", "deadline"],
        "fix_type": "threshold_tuning",
        "description": "Increase timeout thresholds or add circuit breaker",
    },
    "empty_response": {
        "search_patterns": ["empty", "null", "no output", "empty_response"],
        "fix_type": "retry_logic",
        "description": "Add empty-response detection and retry",
    },
    "session_reset": {
        "search_patterns": ["session_reset", "context_limit", "compaction"],
        "fix_type": "investigation",
        "description": "Investigate context management and WAL protocols",
    },
}


def load_patterns() -> list[dict]:
    """Load detected patterns from patterns.json."""
    if not PATTERNS_FILE.exists():
        return []
    with open(PATTERNS_FILE) as f:
        data = json.load(f)
    return data.get("patterns", [])


def find_pattern(pattern_id: str) -> dict | None:
    """Find a specific pattern by ID."""
    for p in load_patterns():
        if p["id"] == pattern_id:
            return p
    return None


def search_codebase(search_terms: list[str], max_results: int = 20) -> list[dict]:
    """Search the workspace for relevant code references."""
    results = []
    for term in search_terms[:5]:  # Limit search terms
        try:
            proc = subprocess.run(
                ["grep", "-rn", "--include=*.py", "--include=*.md", "--include=*.json",
                 "-l", term, str(WORKSPACE)],
                capture_output=True, text=True, timeout=10,
            )
            if proc.returncode == 0:
                for line in proc.stdout.strip().split("\n")[:max_results]:
                    if line and "__pycache__" not in line:
                        results.append({"term": term, "file": line.strip()})
        except Exception:
            pass

    # Deduplicate by file
    seen = set()
    unique = []
    for r in results:
        if r["file"] not in seen:
            seen.add(r["file"])
            unique.append(r)

    return unique[:max_results]


def _infer_safe_category(category: str, issue: str, fix_type: str, target_file: str = "") -> bool:
    """Determine if a proposal is safe for auto-deploy."""
    UNSAFE_FILES = {"AGENTS.md", "SOUL.md", "USER.md"}
    if any(uf in target_file for uf in UNSAFE_FILES):
        return False
    SAFE_COMBOS = {
        ("model_routing", "rate_limit"), ("model_routing", "model_fallback"),
        ("model_routing", "slow_response"), ("model_routing", "wrong_model_tier"),
        ("model_routing", "cost_overrun"),
    }
    SAFE_FIX_TYPES = {"threshold_tuning", "retry_logic"}
    if (category, issue) in SAFE_COMBOS or fix_type in SAFE_FIX_TYPES:
        return True
    return False


def _infer_priority(issue: str, impact_score: float = 0, failure_rate: float = 0) -> str:
    """Infer priority from issue type and metrics."""
    if issue in ("session_reset", "context_loss") or failure_rate > 0.7:
        return "high"
    if issue in ("rate_limit", "model_fallback", "tool_error", "empty_response") or impact_score > 0.15:
        return "medium"
    return "low"


def _find_existing_proposal(category: str, issue: str, task_type: str) -> Path | None:
    """Check if a proposal with the same (category, issue, task_type) already exists."""
    if not PROPOSALS_DIR.exists():
        return None
    for f in PROPOSALS_DIR.glob("*.json"):
        try:
            with open(f) as fh:
                p = json.load(fh)
            p_issue = p.get("issue", p.get("pattern", {}).get("issue", ""))
            p_task = p.get("task_type", p.get("pattern", {}).get("task_type", ""))
            p_cat = p.get("category", p.get("pattern", {}).get("category", ""))
            if p_issue == issue and p_task == task_type and p_cat == category:
                return f
        except Exception:
            pass
    return None


def generate_fix_proposal(pattern: dict) -> dict:
    """Generate a fix proposal for a detected pattern."""
    issue = pattern["issue"]
    template = FIX_TEMPLATES.get(issue, {})

    # Search for relevant code
    search_terms = template.get("search_patterns", [issue])
    search_terms.extend(pattern.get("sample_notes", [])[:2])
    code_refs = search_codebase(search_terms)

    # Determine if auto-fixable
    category = pattern.get("category", "other")
    fix_type = template.get("fix_type", "investigation")
    is_safe = _infer_safe_category(category, issue, fix_type)

    proposal = {
        "id": str(uuid.uuid4())[:8],
        "pattern_id": pattern["id"],
        "title": f"Fix: {pattern['description'][:80]}",
        "status": "draft",
        "auto_fixable": is_safe,
        "safe_category": is_safe,
        "priority": _infer_priority(issue, pattern.get("impact_score", 0), pattern.get("failure_rate", 0)),
        "fix_type": fix_type,
        "category": category,
        "issue": issue,
        "task_type": pattern.get("task_type", "unknown"),
        "frequency": pattern.get("frequency", 0),
        "impact_score": pattern.get("impact_score", 0),
        "description": template.get("description", f"Address '{issue}' in '{pattern.get('task_type')}' tasks"),
        "root_cause_search": code_refs[:10],
        "suggested_changes": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sample_notes": pattern.get("sample_notes", []),
    }

    # Generate specific suggested changes based on fix type
    if fix_type == "routing_config":
        proposal["suggested_changes"] = [
            {
                "file": "skills/intelligent-router/scripts/spawn_helper.py",
                "action": "Review and adjust tier classification thresholds",
                "detail": f"Pattern '{issue}' suggests routing misconfiguration",
            }
        ]
    elif fix_type == "retry_logic":
        proposal["suggested_changes"] = [
            {
                "file": "Relevant tool/integration code",
                "action": f"Add retry with backoff for '{issue}' errors",
                "detail": f"Detected {pattern.get('frequency', 0)}x occurrences",
            }
        ]
    elif fix_type == "threshold_tuning":
        proposal["suggested_changes"] = [
            {
                "file": "Relevant config/threshold file",
                "action": f"Adjust thresholds to reduce '{issue}' frequency",
                "detail": f"Current failure rate: {pattern.get('failure_rate', 0):.0%}",
            }
        ]

    return proposal


def save_proposal(proposal: dict) -> Path:
    """Save a proposal to data/proposals/."""
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    path = PROPOSALS_DIR / f"{proposal['id']}.json"
    with open(path, "w") as f:
        json.dump(proposal, f, indent=2)
    return path


def auto_fix(pattern_id: str, dry_run: bool = False) -> dict:
    """
    Attempt to auto-fix a detected pattern.

    Returns dict with: pattern, proposal, applied, message
    """
    pattern = find_pattern(pattern_id)
    if not pattern:
        return {"error": f"Pattern '{pattern_id}' not found", "applied": False}

    proposal = generate_fix_proposal(pattern)

    if dry_run:
        return {
            "pattern": pattern,
            "proposal": proposal,
            "applied": False,
            "message": f"Dry run — proposal generated but not saved",
        }

    # Dedup: check if proposal with same (category, issue, task_type) exists
    category = proposal["category"]
    existing = _find_existing_proposal(category, proposal["issue"], proposal["task_type"])
    if existing:
        with open(existing) as f:
            old = json.load(f)
        old["duplicate_count"] = old.get("duplicate_count", 1) + 1
        old["last_seen"] = datetime.now(timezone.utc).isoformat()
        old["frequency"] = max(old.get("frequency", 0), proposal.get("frequency", 0))
        with open(existing, "w") as f:
            json.dump(old, f, indent=2)
        return {
            "pattern": pattern,
            "proposal": old,
            "proposal_path": str(existing),
            "applied": False,
            "message": f"Updated existing proposal {existing.name} (count: {old['duplicate_count']})",
        }

    # Save proposal
    path = save_proposal(proposal)

    result = {
        "pattern": pattern,
        "proposal": proposal,
        "proposal_path": str(path),
        "applied": False,
        "message": f"Proposal saved to {path}",
    }

    # Auto-apply only if safe category
    if proposal["auto_fixable"]:
        result["message"] += " (auto-fixable category, but changes require review)"
        # NOTE: We intentionally don't auto-apply code changes.
        # Even "safe" categories get a proposal written for review.
        # The --force flag would be needed for truly automated application.

    return result


def auto_fix_all_safe(days: int = 7, dry_run: bool = False) -> list[dict]:
    """Run auto-fix for all patterns in safe categories."""
    patterns = load_patterns()
    results = []

    for pattern in patterns:
        category = pattern.get("category", "other")
        if category in SAFE_CATEGORIES or pattern["issue"] in HIGH_SEVERITY_ISSUES:
            result = auto_fix(pattern["id"], dry_run=dry_run)
            results.append(result)

    return results


# Import at module level for type reference
from observer import HIGH_SEVERITY_ISSUES


def main():
    parser = argparse.ArgumentParser(description="RSI Auto-Fix - Pattern-to-fix pipeline")
    parser.add_argument("--pattern-id", "-p", help="Pattern ID to fix")
    parser.add_argument("--all-safe", action="store_true",
                        help="Auto-fix all patterns in safe categories")
    parser.add_argument("--dry-run", action="store_true", help="Don't save proposals")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.all_safe:
        results = auto_fix_all_safe(dry_run=args.dry_run)
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            if not results:
                print("No patterns in safe/high-severity categories to fix.")
            for r in results:
                if "error" in r:
                    print(f"  ✗ {r['error']}")
                else:
                    p = r["proposal"]
                    print(f"  {'📝' if not r['applied'] else '✅'} [{p['id']}] {p['title'][:70]}")
                    print(f"    Category: {p['category']} | Auto-fixable: {p['auto_fixable']}")
        return

    if not args.pattern_id:
        # List available patterns
        patterns = load_patterns()
        if not patterns:
            print("No patterns detected. Run: rsi_cli.py analyze")
            return
        print("Available patterns:")
        for p in patterns:
            print(f"  {p['id']}: {p['description'][:70]}")
        print(f"\nUse: auto_fix.py --pattern-id <id>")
        return

    result = auto_fix(args.pattern_id, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)

        p = result["proposal"]
        print(f"\n{'DRY RUN — ' if args.dry_run else ''}Fix Proposal: {p['id']}")
        print(f"  Pattern: {p['pattern_id']}")
        print(f"  Title: {p['title']}")
        print(f"  Category: {p['category']} | Fix type: {p['fix_type']}")
        print(f"  Auto-fixable: {p['auto_fixable']}")
        print(f"  Impact: {p['impact_score']:.4f} | Frequency: {p['frequency']}")

        if p.get("root_cause_search"):
            print(f"\n  Related files:")
            for ref in p["root_cause_search"][:5]:
                print(f"    - {ref['file']} (matched: '{ref['term']}')")

        if p.get("suggested_changes"):
            print(f"\n  Suggested changes:")
            for c in p["suggested_changes"]:
                print(f"    - {c['file']}: {c['action']}")

        if not args.dry_run:
            print(f"\n  Saved to: {result.get('proposal_path', 'N/A')}")


if __name__ == "__main__":
    main()
