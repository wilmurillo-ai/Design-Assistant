#!/usr/bin/env python3
"""
RSI Loop v2 — Critique Phase
Reviews proposals before deployment by checking lineage history and
knowledge base for prior art, redundancy, and failure patterns.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class CritiqueResult:
    """Result of the critique phase for a single proposal."""
    verdict: str                             # "approve" | "reject" | "defer"
    reason: str                              # human-readable explanation
    similar_count: int = 0                   # how many similar proposals exist in lineage
    ancestor_success_rate: float = 0.0       # success rate of ancestor proposals
    redundant_with: Optional[str] = None     # ID of already-deployed proposal this is redundant with
    kb_references: list = field(default_factory=list)  # relevant KB entries (from kb_manager)


class CritiqueAgent:
    """
    Reviews proposals before deployment by checking lineage history
    and knowledge base for prior art, redundancy, and failure patterns.
    """

    def __init__(self, lineage_store=None, kb_path: Path = None):
        from lineage import LineageStore
        self.lineage = lineage_store or LineageStore()
        self.kb_path = kb_path or Path(__file__).parent.parent / "kb"

    def critique(self, proposal: dict) -> CritiqueResult:
        """
        Run all critique checks on a proposal dict.
        Returns CritiqueResult with verdict.
        """
        issue = proposal.get("pattern", {}).get("issue", proposal.get("issue", ""))
        task_type = proposal.get("pattern", {}).get("task_type", proposal.get("task_type", ""))
        category = proposal.get("pattern", {}).get("category", proposal.get("category", ""))
        action_type = proposal.get("action_type", proposal.get("fix_type", ""))
        proposal_id = proposal.get("id", "")

        # 1. Check for similar prior proposals
        similar = self.lineage.find_similar(
            issue=issue, task_type=task_type, category=category
        )
        # Exclude self if already in lineage
        similar = [s for s in similar if s.id != proposal_id]

        # 2. Check ancestor outcomes (if proposal has parent_id)
        parent_id = proposal.get("parent_id")
        ancestor_success_rate, ancestor_resolved_count = self._compute_ancestor_success_rate(parent_id)

        # 3. Check for redundancy with deployed proposals
        redundant_with = self._check_redundancy(similar, action_type)

        # 4. Check KB for anti-patterns
        kb_refs = self._query_kb(issue, task_type, category)

        # 5. Check for repeated failures with same approach
        failed_similar = [s for s in similar if s.outcome == "rejected"]
        deployed_similar = [s for s in similar if s.outcome == "deployed"]

        # --- Decision logic ---

        # REJECT: If 3+ similar proposals with same action_type were rejected
        same_action_rejected = [
            s for s in failed_similar
            if s.action_type == action_type
        ]
        if len(same_action_rejected) >= 3:
            return CritiqueResult(
                verdict="reject",
                reason=(
                    f"Same fix approach ({action_type}) has been rejected "
                    f"{len(same_action_rejected)} times for issue '{issue}'. "
                    f"Try a different approach."
                ),
                similar_count=len(similar),
                ancestor_success_rate=ancestor_success_rate,
                kb_references=kb_refs,
            )

        # REJECT: Redundant with already-deployed fix
        if redundant_with:
            return CritiqueResult(
                verdict="reject",
                reason=(
                    f"Redundant with already-deployed proposal '{redundant_with}' "
                    f"targeting the same issue with the same approach."
                ),
                similar_count=len(similar),
                ancestor_success_rate=ancestor_success_rate,
                redundant_with=redundant_with,
                kb_references=kb_refs,
            )

        # DEFER: If KB has anti-pattern match for this approach
        anti_pattern_refs = [r for r in kb_refs if r.startswith("[ANTI]")]
        if anti_pattern_refs:
            return CritiqueResult(
                verdict="defer",
                reason=(
                    f"KB anti-pattern match: {anti_pattern_refs[0]}. "
                    f"Review before deploying."
                ),
                similar_count=len(similar),
                ancestor_success_rate=ancestor_success_rate,
                kb_references=kb_refs,
            )

        # DEFER: Low ancestor success rate with enough data (at least 1 resolved ancestor)
        if parent_id and ancestor_resolved_count > 0 and ancestor_success_rate < 0.3:
            return CritiqueResult(
                verdict="defer",
                reason=(
                    f"Ancestor proposals have low success rate "
                    f"({ancestor_success_rate:.0%}). Review lineage before deploying."
                ),
                similar_count=len(similar),
                ancestor_success_rate=ancestor_success_rate,
                kb_references=kb_refs,
            )

        # APPROVE: Default — no objections found
        enrichment = ""
        if deployed_similar:
            enrichment = (
                f" Note: {len(deployed_similar)} similar proposals were previously "
                f"deployed for this issue."
            )
        if kb_refs:
            enrichment += f" KB refs: {', '.join(kb_refs[:3])}"

        return CritiqueResult(
            verdict="approve",
            reason=f"No objections. {len(similar)} prior proposals found.{enrichment}",
            similar_count=len(similar),
            ancestor_success_rate=ancestor_success_rate,
            kb_references=kb_refs,
        )

    def _compute_ancestor_success_rate(self, parent_id) -> tuple:
        """
        Walk ancestor chain (including parent_id itself), compute deployed/(deployed+rejected) ratio.
        Returns (rate: float, resolved_count: int).
        Returns (0.0, 0) if no resolved ancestors or parent not found.
        """
        if not parent_id:
            return 0.0, 0
        # Include the parent node itself
        parent_node = self.lineage.get_node(parent_id)
        ancestors = self.lineage.get_ancestors(parent_id)
        chain = ([parent_node] if parent_node else []) + ancestors
        if not chain:
            return 0.0, 0
        resolved = [a for a in chain if a.outcome in ("deployed", "rejected")]
        if not resolved:
            return 0.0, 0
        deployed = sum(1 for a in resolved if a.outcome == "deployed")
        return deployed / len(resolved), len(resolved)

    def _check_redundancy(self, similar: list, action_type: str) -> Optional[str]:
        """
        Check if any similar proposal with same action_type is already deployed.
        Returns the ID of the redundant proposal, or None.
        """
        for s in similar:
            if s.outcome == "deployed" and s.action_type == action_type:
                return s.id
        return None

    def _query_kb(self, issue: str, task_type: str, category: str) -> list:
        """
        Query KB markdown files for relevant entries.
        Returns list of reference strings, prefixed with [ANTI], [FAIL], or [SUCCESS].
        """
        try:
            from kb_manager import KBManager
            kb = KBManager(self.kb_path)
            results = kb.query(issue=issue, task_type=task_type, category=category, top_k=3)
            return [r["reference"] for r in results]
        except Exception:
            return []
