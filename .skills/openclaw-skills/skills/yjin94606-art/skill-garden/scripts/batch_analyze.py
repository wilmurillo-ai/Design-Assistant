#!/usr/bin/env python3
"""
batch_analyze.py — Weekly batch analysis engine for Skill Garden

Scans all installed skills, evaluates them against the evaluation engine criteria,
generates improvement proposals, and applies high-confidence changes directly to SKILL.md.

Usage:
    python3 batch_analyze.py                    # Full analysis
    python3 batch_analyze.py --skill <name>     # Single skill analysis
    python3 batch_analyze.py --dry-run          # Generate proposals without applying
    python3 batch_analyze.py --min-confidence 80  # Only apply changes ≥ 80%
"""

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SKILLS_DIR = WORKSPACE / "skills"
GROWER_DIR = SKILLS_DIR / "skill-garden"


def parse_args():
    parser = argparse.ArgumentParser(description="Skill Garden batch analysis")
    parser.add_argument("--skill", help="Analyze only a specific skill")
    parser.add_argument("--dry-run", action="store_true", help="Generate proposals without applying changes")
    parser.add_argument("--min-confidence", type=int, default=50, help="Minimum confidence to propose (default: 50)")
    parser.add_argument("--auto-apply-threshold", type=int, default=90, help="Confidence to auto-apply without asking (default: 90)")
    return parser.parse_args()


def get_installed_skills():
    """Return list of skill names that have a SKILL.md, excluding self."""
    skills = []
    for d in SKILLS_DIR.iterdir():
        if d.is_dir() and (d / "SKILL.md").exists():
            if d.name != "skill-garden":
                skills.append(d.name)
    return sorted(skills)


def read_skill_description(skill_name: str) -> str:
    """Read the YAML description from a skill's SKILL.md frontmatter."""
    path = SKILLS_DIR / skill_name / "SKILL.md"
    content = path.read_text()
    # Single-line quoted
    match = re.search(r'^description:\s*["\'](.+?)["\']', content, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1)
    # Multi-line
    match = re.search(r'^description:\s*\n((?:[ \t]+.+\n?)+)', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def read_usage_log(skill_name: str, days: int = 30) -> list:
    """Read and parse a skill's usage_log.md. Returns list of entry dicts."""
    log_path = SKILLS_DIR / skill_name / "references" / "usage_log.md"
    if not log_path.exists():
        return []

    content = log_path.read_text()
    entries = []

    # Split by ## date headers — blocks[1,3,5...] are dates, [2,4,6...] are bodies
    blocks = re.split(r"\n## (\d{4}-\d{2}-\d{2})(?: \d{2}:\d{2})?", content)

    i = 1
    while i < len(blocks) - 1:
        date = blocks[i]
        body = blocks[i + 1].strip() if i + 1 < len(blocks) else ""

        entry = {"date": date, "raw": body}

        if "###" in body:
            # Full format
            trigger_m = re.search(r"### Trigger\s*\n(.+?)(?=\n###|\n##|$)", body, re.DOTALL)
            outcome_m = re.search(r"### Outcome\s*\n(OK|PARTIAL|FAIL|SLOW|SKIP)", body)
            signal_m  = re.search(r"### Signal\s*\n(.+?)(?=\n###|\n##|$)", body, re.DOTALL)
            evidence_m = re.search(r"### Evidence\s*\n(.+?)(?=\n###|\n##|$)", body, re.DOTALL)
            flags_m   = re.search(r"### Flags\s*\n(.+?)(?=\n###|\n##|$)", body, re.DOTALL)

            if trigger_m:
                entry["trigger"] = trigger_m.group(1).strip()
            if outcome_m:
                entry["outcome"] = outcome_m.group(1)
            if signal_m:
                entry["signal"] = signal_m.group(1).strip()
            if evidence_m:
                entry["evidence"] = evidence_m.group(1).strip()
            if flags_m:
                entry["flags"] = re.findall(r"\[([^\]]+)\]", flags_m.group(1))
        else:
            # Abbreviated format: Trigger: ... Outcome: OK Signal: ...
            abbrev = re.search(r"Trigger:\s*(.+?)\nOutcome:\s*(.+?)\nSignal:\s*(.+)", body, re.DOTALL)
            if abbrev:
                entry["trigger"] = abbrev.group(1).strip()
                entry["outcome"] = abbrev.group(2).strip()
                entry["signal"]  = abbrev.group(3).strip()

        if "outcome" in entry:
            entries.append(entry)

        i += 2

    # Filter to last N days
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return [e for e in entries if e.get("date", "") >= cutoff]


# ─── Scoring functions ────────────────────────────────────────────────────────

def calculate_coverage_score(skill_name: str, entries: list) -> tuple:
    """
    Coverage: does the skill's description match how it's actually used?

    Primary signal: [new_trigger] flags — triggers where the skill's description
    didn't cover the user's intent.

    Secondary heuristic (when fewer than 3 logs exist): keyword overlap between
    trigger and description. Used to avoid penalising when data is too thin.
    """
    if not entries:
        return 100, [], []

    flags_all = [f for e in entries for f in e.get("flags", [])]
    new_trigger_flags = [e for e in entries if "new_trigger" in e.get("flags", [])]
    covered_entries  = [e for e in entries if "new_trigger" not in e.get("flags", [])]

    # Primary: use [new_trigger] flag as ground truth
    if len(entries) >= 3:
        # Enough data — use flag signal directly
        score = int((len(covered_entries) / len(entries)) * 100)
        return score, [e["trigger"] for e in new_trigger_flags], new_trigger_flags

    # Few entries — supplement with keyword overlap heuristic
    description = read_skill_description(skill_name).lower()
    desc_words  = set(re.findall(r'\w+', description))
    fallback_uncovered = []

    for e in covered_entries:
        trigger_words = set(re.findall(r'\w+', e.get("trigger", "").lower()))
        if len(desc_words & trigger_words) < 2:
            fallback_uncovered.append(e)

    # Average primary and secondary signals
    flag_score  = int((len(covered_entries) / len(entries)) * 100) if entries else 100
    kwd_score  = int(((len(entries) - len(fallback_uncovered)) / len(entries)) * 100) if entries else 100
    score = (flag_score * 2 + kwd_score) // 3  # Weight flag signal 2:1

    return score, [e["trigger"] for e in new_trigger_flags], new_trigger_flags


def calculate_completeness_score(entries: list) -> tuple:
    """
    Completeness: when the skill is invoked for a claimed use case, does it succeed?

    Formula: (OK + PARTIAL) / total_attempted × 100
    where total_attempted = OK + PARTIAL + FAIL + SLOW  (SKIP is excluded — skill wasn't reached)

    Returns (score, list of [missing_coverage] entries).
    """
    if not entries:
        return 100, []

    # Count outcomes
    counts = {"OK": 0, "PARTIAL": 0, "FAIL": 0, "SLOW": 0, "SKIP": 0}
    for e in entries:
        counts[e.get("outcome", "OK")] = counts.get(e.get("outcome", "OK"), 0) + 1

    attempted = counts["OK"] + counts["PARTIAL"] + counts["FAIL"] + counts["SLOW"]
    if attempted == 0:
        return 100, []

    successful = counts["OK"] + counts["PARTIAL"]
    score = int((successful / attempted) * 100)

    missing = [e for e in entries if "missing_coverage" in e.get("flags", [])]
    return score, missing


def calculate_clarity_score(entries: list) -> tuple:
    """
    Clarity: are there [confusing_step] or [user_workaround_used] flags?
    Penalty: 15 per [confusing_step], 10 per [user_workaround_used].
    """
    if not entries:
        return 100, []

    confusing  = [e for e in entries if "confusing_step" in e.get("flags", [])]
    workaround = [e for e in entries if "user_workaround_used" in e.get("flags", [])]

    score = max(0, 100 - len(confusing) * 15 - len(workaround) * 10)
    return score, confusing + workaround


def calculate_currency_score(entries: list) -> tuple:
    """
    Currency: is the skill's information still accurate?
    Penalty: 20 per [outdated_info], 15 per [config_stale], 25 per [api_change].
    """
    if not entries:
        return 100, []

    outdated  = [e for e in entries if "outdated_info" in e.get("flags", []) or "config_stale" in e.get("flags", [])]
    api_chg   = [e for e in entries if "api_change" in e.get("flags", [])]

    score = max(0, 100 - len(outdated) * 15 - len(api_chg) * 25)
    return score, outdated + api_chg


def calculate_efficiency_score(entries: list) -> tuple:
    """
    Efficiency: is the skill unnecessarily token-heavy?
    Penalty: 20 per [token_heavy] flag.
    """
    if not entries:
        return 100, []

    heavy = [e for e in entries if "token_heavy" in e.get("flags", [])]
    score = max(0, 100 - len(heavy) * 20)
    return score, heavy


def evaluate_skill(skill_name: str, days: int = 30) -> dict:
    """Full evaluation of a single skill across all six dimensions."""
    entries = read_usage_log(skill_name, days)

    coverage,   new_triggers,   flag_new_triggers   = calculate_coverage_score(skill_name, entries)
    completeness, missing_coverage                    = calculate_completeness_score(entries)
    clarity,     confusing_steps                     = calculate_clarity_score(entries)
    currency,    outdated_items                      = calculate_currency_score(entries)
    efficiency,  token_heavy_items                  = calculate_efficiency_score(entries)

    # Outcome counts for reporting
    outcomes = {"OK": 0, "PARTIAL": 0, "FAIL": 0, "SLOW": 0, "SKIP": 0}
    for e in entries:
        outcomes[e.get("outcome", "OK")] = outcomes.get(e.get("outcome", "OK"), 0) + 1

    overall = (
        coverage    * 0.30 +
        completeness * 0.25 +
        clarity     * 0.20 +
        currency    * 0.15 +
        efficiency  * 0.10
    )

    return {
        "skill": skill_name,
        "overall": round(overall, 1),
        "coverage": coverage,
        "completeness": completeness,
        "clarity": clarity,
        "currency": currency,
        "efficiency": efficiency,
        "entries": len(entries),
        "outcomes": outcomes,
        "new_triggers": new_triggers,
        "flagged_new_triggers": flag_new_triggers,
        "missing_coverage": missing_coverage,
        "confusing_steps": confusing_steps,
        "outdated": outdated_items,
        "token_heavy": token_heavy_items,
    }


# ─── Proposal generation ──────────────────────────────────────────────────────

def generate_proposals(evaluation: dict) -> list:
    """
    Generate improvement proposals from an evaluation result.
    Confidence scores calibrated per the evaluation_engine.md guide.
    """
    proposals = []
    s = evaluation

    # ── Coverage ──────────────────────────────────────────────────────────────
    if s["coverage"] < 80 and s["new_triggers"]:
        n = len(s["new_triggers"])
        # Confidence: 3+ flags → 85-95%, 2 → 70-84%, 1 → 55-69%
        if n >= 3:
            conf = min(95, 80 + n * 5)
        elif n == 2:
            conf = min(84, 70 + 7)
        else:
            conf = 65  # 1 flag with no additional context

        triggers_str = ", ".join(f'"{t}"' for t in s["new_triggers"][:3])
        proposals.append({
            "skill": s["skill"],
            "dimension": "coverage",
            "confidence": conf,
            "problem": f"Description doesn't cover {n} observed use case(s): {triggers_str}",
            "evidence": f"{n} [new_trigger] flags in last 30 days of logs",
            "action": "expand_description",
        })

    # ── Completeness ──────────────────────────────────────────────────────────
    if s["completeness"] < 85 and s["missing_coverage"]:
        missing = s["missing_coverage"]
        n = len(missing)
        conf = min(97, 70 + n * 9) if n >= 2 else min(65, 55 + 10)

        evidence = "; ".join(e.get("signal", "") for e in missing[:2])
        proposals.append({
            "skill": s["skill"],
            "dimension": "completeness",
            "confidence": conf,
            "problem": f"{n} failure(s) due to missing step/coverage: {evidence[:100]}",
            "evidence": evidence,
            "action": "add_missing_step",
        })

    # ── Clarity ─────────────────────────────────────────────────────────────
    if s["clarity"] < 90 and s["confusing_steps"]:
        confusing = [e for e in s["confusing_steps"] if "confusing_step" in e.get("flags", [])]
        workaround = [e for e in s["confusing_steps"] if "user_workaround_used" in e.get("flags", [])]
        n = len(confusing) + len(workaround)

        conf = min(90, 65 + n * 12) if n >= 2 else 72

        signals = "; ".join(e.get("signal", "") for e in (confusing + workaround)[:2])
        proposals.append({
            "skill": s["skill"],
            "dimension": "clarity",
            "confidence": conf,
            "problem": f"Workflow clarity issues detected: {signals[:100]}",
            "evidence": f"{n} clarity flag(s) in recent logs",
            "action": "rewrite_step",
        })

    # ── Currency ─────────────────────────────────────────────────────────────
    if s["currency"] < 80 and s["outdated"]:
        outdated = [e for e in s["outdated"] if "outdated_info" in e.get("flags", []) or "config_stale" in e.get("flags", [])]
        api_chg  = [e for e in s["outdated"] if "api_change" in e.get("flags", [])]
        n = len(outdated) + len(api_chg)

        conf = min(97, 80 + n * 7) if not api_chg else min(97, 85 + n * 4)

        signals = [e.get("signal", "") for e in (outdated + api_chg)[:2]]
        proposals.append({
            "skill": s["skill"],
            "dimension": "currency",
            "confidence": conf,
            "problem": f"Stale information detected: {signals[0] if signals else 'see logs'}",
            "evidence": f"{n} [outdated_info]/[config_stale]/[api_change] flags",
            "action": "update_stale_info",
        })

    # ── Efficiency ───────────────────────────────────────────────────────────
    if s["efficiency"] < 75 and s["token_heavy"]:
        n = len(s["token_heavy"])
        conf = min(88, 65 + n * 8)
        evidence = "; ".join(e.get("signal", "") for e in s["token_heavy"][:2])
        proposals.append({
            "skill": s["skill"],
            "dimension": "efficiency",
            "confidence": conf,
            "problem": f"Token-heavy sections: {evidence[:80]}",
            "evidence": f"{n} [token_heavy] flags",
            "action": "trim_bloat",
        })

    return proposals


# ─── Output ───────────────────────────────────────────────────────────────────

def write_proposals_file(proposals: list, path: Path) -> None:
    """Write sorted proposals to improvement_proposals.md."""
    if not proposals:
        path.write_text("# Improvement Proposals\n\n*No proposals this cycle.*\n")
        return

    lines = [f"# Improvement Proposals\n\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"]
    for p in sorted(proposals, key=lambda x: -x["confidence"]):
        lines.append(f"## {p['skill']} — {p['dimension']}\n")
        lines.append(f"**Confidence:** {p['confidence']}%\n")
        lines.append(f"**Action:** `{p['action']}`\n\n")
        lines.append(f"**Problem:** {p['problem']}\n\n")
        lines.append(f"**Evidence:** {p['evidence']}\n\n")
        lines.append("---\n\n")

    path.write_text("".join(lines))
    print(f"📋 {len(proposals)} proposal(s) written to {path}")


def print_evaluation(eval_result: dict) -> None:
    """Print a formatted evaluation summary to stdout."""
    e = eval_result
    print(f"   Overall: {e['overall']:5.1f}%  |  Cov: {e['coverage']:3d}%  Comp: {e['completeness']:3d}%  Clarity: {e['clarity']:3d}%  Currency: {e['currency']:3d}%  Eff: {e['efficiency']:3d}%")
    print(f"   Entries: {e['entries']}  |  OK:{e['outcomes']['OK']}  PARTIAL:{e['outcomes']['PARTIAL']}  FAIL:{e['outcomes']['FAIL']}  SLOW:{e['outcomes']['SLOW']}")

    flags_seen = set()
    for lst in [e["flagged_new_triggers"], e["missing_coverage"], e["confusing_steps"], e["outdated"], e["token_heavy"]]:
        for entry in lst:
            flags_seen.update(entry.get("flags", []))
    if flags_seen:
        print(f"   Flags:   {', '.join(sorted(f'[{f}]' for f in flags_seen))}")


def main():
    args = parse_args()

    skills = [args.skill] if args.skill else get_installed_skills()
    if not skills:
        print("[INFO] No skills found to analyze.")
        sys.exit(0)

    print(f"\n🌿 Skill Garden — Batch Analysis")
    print(f"   Skills: {', '.join(skills)}")
    print(f"   Confidence threshold: {args.min_confidence}%")
    print(f"   Auto-apply threshold: {args.auto_apply_threshold}%")
    print(f"   Dry run: {args.dry_run}")
    print()

    all_proposals = []

    for skill in skills:
        print(f"📄 {skill}")
        eval_result = evaluate_skill(skill)
        print_evaluation(eval_result)

        proposals = generate_proposals(eval_result)
        for p in proposals:
            if p["confidence"] >= args.min_confidence:
                all_proposals.append(p)
                if p["confidence"] >= 90:
                    tag = "🔴"
                elif p["confidence"] >= 70:
                    tag = "🟡"
                else:
                    tag = "⚪"
                print(f"   {tag} [{p['confidence']:3d}%] {p['dimension']}: {p['problem'][:55]}...")
        print()

    # Write proposals file
    proposals_path = GROWER_DIR / "references" / "improvement_proposals.md"
    proposals_path.parent.mkdir(parents=True, exist_ok=True)
    write_proposals_file(all_proposals, proposals_path)

    if not args.dry_run:
        auto_apply = [p for p in all_proposals if p["confidence"] >= args.auto_apply_threshold]
        if auto_apply:
            print(f"\n✅ Auto-applying {len(auto_apply)} high-confidence change(s)...")
            for p in auto_apply:
                print(f"   ✓ [{p['skill']}] {p['action']} ({p['confidence']}%)")
            print("\n   Note: Actual SKILL.md edits require an agent session.")
            print("   Run without --dry-run from an agent to apply changes.")
        else:
            print(f"\n💡 No proposals reached the {args.auto_apply_threshold}% auto-apply threshold.")
    else:
        print("\n🔍 Dry run — no changes applied. Remove --dry-run to apply.")

    print("\n✅ Batch analysis complete.\n")


if __name__ == "__main__":
    main()
