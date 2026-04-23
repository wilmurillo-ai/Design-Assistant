#!/usr/bin/env python3
"""
Decay Sweep — Weekly fact lifecycle processor for autonomous memory management.

Inspired by GAM-RAG (arXiv:2603.01783): Kalman-inspired updates apply rapid changes
to uncertain memories (new facts) and conservative refinement to stable ones (old facts).

This maps to memory decay: new facts (uncertain, frequently accessed) update easily;
established facts (stable, rarely accessed) resist change via access-count resistance.

Algorithm:
  1. Scan all items.json files under base_path
  2. For each fact, classify based on days since lastAccessed:
     - Hot: < 7 days (prominent in summaries)
     - Warm: 7-30 days (included, lower priority)
     - Cold: > 30 days (archived, removed from summaries)
  3. Apply access-count resistance: facts with accessCount > 5 get +14 day resistance
  4. Update status field: active → warm → cold (never delete, never set to "superseded")
  5. Rewrite summary.md for each entity: hot facts prominent, cold facts removed
  6. Output summary of changes

No external dependencies beyond stdlib (json, pathlib, datetime, argparse).
"""

import json
import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def classify_age(days_since_access, access_count):
    """
    Classify fact age based on lastAccessed and accessCount.
    
    Base classification:
      - Hot: < 7 days
      - Warm: 7-30 days
      - Cold: > 30 days
    
    Resistance bonus: facts with accessCount > 5 get +14 days before cooling.
    Rationale (GAM-RAG): Frequently-accessed facts are "stable" and resist change.
    """
    resistance_bonus = 14 if access_count > 5 else 0
    effective_age = days_since_access - resistance_bonus
    
    if effective_age < 7:
        return "hot"
    elif effective_age < 30:
        return "warm"
    else:
        return "cold"


def update_fact_status(fact, classification):
    """
    Update fact status based on classification.
    Progression: active → warm → cold (never delete, never set "superseded").
    """
    current_status = fact.get("status", "active")
    
    if classification == "hot":
        # Reactivate hot facts
        fact["status"] = "active"
    elif classification == "warm":
        # Warm facts stay warm
        fact["status"] = "warm"
    elif classification == "cold":
        # Cold facts move to cold
        fact["status"] = "cold"
    
    return fact


def process_items_file(items_path, dry_run=False):
    """
    Process single items.json file.
    Returns: (facts_cooled, facts_activated, summary_updated)
    """
    try:
        with open(items_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return (0, 0, False)
    
    facts = data.get("facts", [])
    if not facts:
        return (0, 0, False)
    
    now = datetime.now()
    facts_cooled = 0
    facts_activated = 0
    
    # Classify and update each fact
    for fact in facts:
        try:
            last_accessed_str = fact.get("lastAccessed", "")
            last_accessed = datetime.fromisoformat(last_accessed_str.replace('Z', '+00:00'))
            days_since = (now - last_accessed).days
        except (ValueError, TypeError):
            days_since = 999  # If unparseable, treat as very old
        
        access_count = fact.get("accessCount", 0)
        classification = classify_age(days_since, access_count)
        
        old_status = fact.get("status", "active")
        update_fact_status(fact, classification)
        new_status = fact.get("status", "active")
        
        if old_status != new_status:
            if new_status == "cold":
                facts_cooled += 1
            elif new_status == "active":
                facts_activated += 1
    
    # Write updated items.json (unless dry-run)
    if not dry_run:
        with open(items_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    # Rewrite summary.md if changed
    summary_path = items_path.parent / "summary.md"
    summary_updated = rewrite_summary(items_path.parent, facts, dry_run=dry_run)
    
    return (facts_cooled, facts_activated, summary_updated)


def rewrite_summary(entity_dir, facts, dry_run=False):
    """
    Rewrite summary.md: hot facts prominent, cold facts removed.
    Returns: True if summary was rewritten.
    """
    summary_path = entity_dir / "summary.md"
    
    # Separate facts by status
    hot_facts = [f for f in facts if f.get("status") == "active"]
    warm_facts = [f for f in facts if f.get("status") == "warm"]
    cold_facts = [f for f in facts if f.get("status") == "cold"]
    
    # Build new summary
    lines = ["# Summary\n"]
    
    if hot_facts:
        lines.append("## Active (Hot)\n")
        for fact in hot_facts:
            lines.append(f"- {fact.get('fact', 'N/A')}\n")
        lines.append("\n")
    
    if warm_facts:
        lines.append("## Warm (Older)\n")
        for fact in warm_facts:
            lines.append(f"- {fact.get('fact', 'N/A')}\n")
        lines.append("\n")
    
    # Note: cold facts are NOT included in summary (kept in items.json)
    if cold_facts:
        lines.append(f"## Archived ({len(cold_facts)} cold facts in items.json)\n")
    
    new_summary = "".join(lines)
    
    # Only write if changed
    existing_summary = ""
    if summary_path.exists():
        try:
            with open(summary_path, 'r') as f:
                existing_summary = f.read()
        except IOError:
            pass
    
    if new_summary != existing_summary and not dry_run:
        with open(summary_path, 'w') as f:
            f.write(new_summary)
        return True
    
    return new_summary != existing_summary


def scan_base_path(base_path):
    """
    Recursively find all items.json files under base_path.
    Expected structure: base_path/*/items.json or base_path/*/*/items.json (PARA)
    """
    base = Path(base_path)
    if not base.exists():
        return []
    
    items_files = list(base.rglob("items.json"))
    return items_files


def run_decay_sweep(base_path, dry_run=False):
    """Main decay sweep loop."""
    items_files = scan_base_path(base_path)
    
    if not items_files:
        print(f"No items.json files found under {base_path}")
        return
    
    total_cooled = 0
    total_activated = 0
    total_summaries = 0
    
    for items_path in items_files:
        cooled, activated, summary_updated = process_items_file(items_path, dry_run=dry_run)
        total_cooled += cooled
        total_activated += activated
        if summary_updated:
            total_summaries += 1
    
    # Output summary
    mode = "(dry-run)" if dry_run else "(committed)"
    print(f"{total_cooled} facts cooled, {total_activated} facts reactivated, {total_summaries} summaries updated {mode}")


def main():
    parser = argparse.ArgumentParser(
        description="Weekly decay sweep: age facts based on access patterns, update summaries"
    )
    parser.add_argument(
        '--base-path',
        type=str,
        default='life',
        help='Base path containing items.json files (default: life)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing'
    )
    
    args = parser.parse_args()
    run_decay_sweep(args.base_path, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
