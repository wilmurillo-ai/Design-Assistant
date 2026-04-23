#!/usr/bin/env python3
# FILE_META
# INPUT:  JSON array of review verdicts (stdin or --auto-approve with candidates.json)
# OUTPUT: stats file updates + manifest updates + trajectory deletions
# POS:    skill scripts — Step 3 post-processing, depends on reject.py and lib/paths.py
# MISSION: Batch-process agent review results: update stats for PASS, reject for FAIL.
"""Process review verdicts for trajectory candidates.

Usage (stdin):
    python review.py <<'EOF'
    [
      {"session_id": "abc", "verdict": "pass", "domain": "development", "title": "..."},
      {"session_id": "def", "verdict": "fail", "reason": "闲聊"}
    ]
    EOF

Usage (auto-approve all candidates):
    python review.py --auto-approve
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from reject import reject_sessions
from lib.paths import get_default_output_dir

DEFAULT_OUTPUT_DIR = get_default_output_dir()

VALID_DOMAINS = {
    "development", "system_admin", "data_analysis", "research",
    "content_creation", "communication", "media_processing",
    "automation", "monitoring", "scheduling", "knowledge_mgmt",
    "finance", "crm",
}


def process_reviews(output_dir: str, reviews: list[dict]) -> dict:
    """Process a list of review verdicts.

    Each review dict must have:
      - session_id: str
      - verdict: "pass" or "fail"
      - domain: str (required for pass)
      - title: str (required for pass)
      - reason: str (optional, for fail)

    Returns:
        {"passed": N, "rejected": M, "errors": [...]}
    """
    passed = 0
    errors = []
    rejections: list[tuple[str, str]] = []

    for review in reviews:
        sid = review.get("session_id", "")
        verdict = review.get("verdict", "").lower()

        if not sid:
            errors.append("missing session_id in review entry")
            continue

        if verdict == "pass":
            stats_path = os.path.join(output_dir, f"{sid}.stats.json")
            if not os.path.isfile(stats_path):
                errors.append(f"{sid}: stats file not found")
                continue

            try:
                try:
                    with open(stats_path, "r", encoding="utf-8") as f:
                        stats = json.load(f)
                except UnicodeDecodeError:
                    with open(stats_path, "r", encoding="gbk") as f:
                        stats = json.load(f)

                domain = review.get("domain", stats.get("domain", ""))
                title = review.get("title", stats.get("title", ""))

                if domain and domain not in VALID_DOMAINS:
                    errors.append(f"{sid}: invalid domain '{domain}'")
                    continue

                stats["domain"] = domain
                stats["title"] = title
                stats["review_status"] = "reviewed"

                # Atomic write
                tmp_path = stats_path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, stats_path)

                passed += 1
            except (json.JSONDecodeError, OSError) as e:
                errors.append(f"{sid}: {e}")

        elif verdict == "fail":
            reason = review.get("reason", "")
            rejections.append((sid, reason))

        else:
            errors.append(f"{sid}: invalid verdict '{verdict}' (must be 'pass' or 'fail')")

    # Batch reject all FAIL entries
    rejected = 0
    if rejections:
        rejected = reject_sessions(output_dir, rejections)

    return {"passed": passed, "rejected": rejected, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description="Process review verdicts for trajectory candidates")
    parser.add_argument("--output-dir", "-o", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument("--auto-approve", action="store_true",
                        help="Auto-approve all candidates in candidates.json (keep heuristic domain/title)")
    args = parser.parse_args()

    if args.auto_approve:
        candidates_path = os.path.join(args.output_dir, "candidates.json")
        if not os.path.isfile(candidates_path):
            print(json.dumps({"error": f"candidates.json not found in {args.output_dir}"}))
            sys.exit(1)

        with open(candidates_path, "r", encoding="utf-8") as f:
            candidates = json.load(f)

        reviews = [{"session_id": c["session_id"], "verdict": "pass"} for c in candidates]
    else:
        try:
            raw = sys.stdin.read()
            reviews = json.loads(raw)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"invalid JSON input: {e}"}))
            sys.exit(1)

    if not isinstance(reviews, list):
        print(json.dumps({"error": "input must be a JSON array"}))
        sys.exit(1)

    result = process_reviews(args.output_dir, reviews)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
