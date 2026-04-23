#!/usr/bin/env python3
"""
migrate_md_to_sql.py — Migrate daily .md memory files to SQL
=============================================================
Reads memory/YYYY-MM-DD.md files, inserts into memory.Memories table,
then deletes the .md files after confirming successful storage.

Usage:
    python3 migrate_md_to_sql.py [--dry-run]
"""

import os
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE / 'infrastructure'))
from sql_memory import get_memory

def migrate_file(md_path: Path, mem, dry_run: bool = False) -> bool:
    """Migrate a single .md file to SQL. Returns True on success."""
    try:
        content = md_path.read_text(encoding='utf-8')
        if not content.strip():
            print(f"  SKIP (empty): {md_path.name}")
            md_path.unlink()
            return True

        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', md_path.name)
        date_str = date_match.group(1) if date_match else md_path.stem
        title = f"Daily memory: {date_str}"
        key = f"daily_{date_str.replace('-', '_')}"

        if dry_run:
            print(f"  DRY-RUN: would insert {key} ({len(content)} chars)")
            return True

        ok = mem.remember(
            category='daily_log',
            key=key,
            content=content[:4000],  # SQL max
            importance=3,
            tags=f'daily,migration,{date_str[:7]}'
        )
        if ok:
            # Verify it was stored
            stored = mem.recall('daily_log', key)
            if stored:
                md_path.unlink()
                print(f"  ✅ Migrated + deleted: {md_path.name}")
                return True
            else:
                print(f"  ⚠️  Insert claimed ok but recall failed: {md_path.name}")
                return False
        else:
            print(f"  ❌ Failed to insert: {md_path.name}")
            return False
    except Exception as e:
        print(f"  ❌ Error migrating {md_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Migrate daily .md files to SQL')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without making changes')
    args = parser.parse_args()

    mem_dir = WORKSPACE / 'memory'
    if not mem_dir.exists():
        print("No memory/ directory found. Nothing to migrate.")
        return

    md_files = sorted(mem_dir.glob('????-??-??.md'))
    if not md_files:
        print("No daily .md files found. All clean!")
        return

    print(f"Found {len(md_files)} daily .md files to migrate")
    mem = get_memory('local')

    success = fail = 0
    for f in md_files:
        result = migrate_file(f, mem, dry_run=args.dry_run)
        if result:
            success += 1
        else:
            fail += 1

    print(f"\nDone: {success} migrated, {fail} failed")

    if not args.dry_run:
        # Log migration event
        mem.log_event(
            'migration',
            'migrate_md_to_sql',
            f'Migrated {success} daily .md files to SQL ({fail} failed)',
            f'{{"success":{success},"failed":{fail}}}'
        )


if __name__ == '__main__':
    main()
