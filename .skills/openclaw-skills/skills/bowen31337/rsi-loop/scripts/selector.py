#!/usr/bin/env python3
"""
Gene Selector — Pattern-to-Gene matching with scored selection.
Part of RSI Loop v2.0 Gene Registry (Phase 1).
"""

from datetime import datetime, timezone, timedelta


def was_applied_recently(gene: dict, days: int = 3) -> bool:
    """
    Return True if the gene was last applied within `days` days.
    If last_applied is not set, treat as never applied (returns False).
    """
    last_applied = gene.get("meta", {}).get("last_applied")
    if not last_applied:
        return False
    try:
        applied_at = datetime.fromisoformat(last_applied.replace("Z", "+00:00"))
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return applied_at >= cutoff
    except (ValueError, TypeError):
        return False


def select_gene(pattern: dict, genes: list) -> dict | None:
    """
    Select the best-matching Gene for a given pattern dict.

    Scoring (see GENE_REGISTRY_SPEC.md §Selector Algorithm):
      - category match: REQUIRED (skip gene if no match)
      - issue_type match: +3
      - task_type match: +2
      - success_rate weight: +2 × success_rate
      - recency penalty: -1 if applied within last 3 days

    Returns the best gene if its score >= 3, else None.

    Pattern dict expected keys:
      - category (str): e.g. "model_routing"
      - issue (str): e.g. "rate_limit"
      - task_type (str): e.g. "message_routing"
    """
    candidates = []

    for gene in genes:
        trigger = gene.get("trigger", {})

        # Category match is required
        if trigger.get("pattern_category") != pattern.get("category"):
            continue

        score = 0.0

        # Issue type match
        if pattern.get("issue") in trigger.get("issue_types", []):
            score += 3

        # Task type match
        if pattern.get("task_type") in trigger.get("task_types", []):
            score += 2

        # Success rate weight (prefer proven genes)
        success_rate = gene.get("meta", {}).get("success_rate", 0.0)
        score += success_rate * 2

        # Recency penalty (don't reuse same gene too soon)
        if was_applied_recently(gene, days=3):
            score -= 1

        candidates.append((score, gene))

    if not candidates:
        return None

    # Sort descending by score
    candidates.sort(key=lambda x: -x[0])
    best_score, best_gene = candidates[0]

    # Minimum score threshold — don't force a bad match
    return best_gene if best_score >= 3 else None
