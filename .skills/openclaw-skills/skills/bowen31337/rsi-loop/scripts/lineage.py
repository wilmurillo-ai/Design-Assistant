#!/usr/bin/env python3
"""
RSI Loop v2 — Proposal Lineage Tracking
Append-only JSONL store for proposal nodes forming a lineage tree.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).parent.parent
MEMORY_DIR = SKILL_DIR / "memory"
LINEAGE_FILE = MEMORY_DIR / "rsi-lineage.jsonl"


@dataclass
class ProposalNode:
    """A node in the proposal lineage tree."""
    id: str                                     # proposal ID (matches proposal JSON id)
    parent_id: Optional[str] = None             # ID of the proposal this descended from (None = root)
    timestamp: str = ""                         # ISO 8601 UTC
    task_type: str = ""                         # from pattern.task_type
    issue: str = ""                             # from pattern.issue
    category: str = ""                          # from pattern.category
    proposal_text: str = ""                     # title or description of the proposal
    action_type: str = ""                       # create_skill, fix_routing, apply_gene, etc.
    mutation_type: str = ""                     # repair, optimize, innovate
    outcome: str = "pending"                    # pending | deployed | rejected | superseded
    outcome_notes: str = ""                     # reason for rejection / deploy result
    outcome_timestamp: Optional[str] = None     # when outcome was recorded
    tags: list = field(default_factory=list)    # freeform tags for KB queries

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ProposalNode":
        # Handle extra/missing fields gracefully
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**filtered)


class LineageStore:
    """Append-only store for proposal lineage nodes."""

    def __init__(self, path: Path = LINEAGE_FILE):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, node: ProposalNode) -> None:
        """Append a ProposalNode to the lineage store."""
        with open(self.path, "a") as f:
            f.write(json.dumps(node.to_dict()) + "\n")

    def load_all(self) -> list:
        """Load all nodes from the lineage file."""
        if not self.path.exists():
            return []
        nodes = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    nodes.append(ProposalNode.from_dict(json.loads(line)))
                except (json.JSONDecodeError, TypeError):
                    pass
        return nodes

    def get_node(self, node_id: str) -> Optional[ProposalNode]:
        """Get a single node by ID. Returns None if not found."""
        for node in self.load_all():
            if node.id == node_id:
                return node
        return None

    def get_ancestors(self, node_id: str) -> list:
        """
        Walk up the parent chain from node_id.
        Returns list ordered [parent, grandparent, ...] (closest ancestor first).
        """
        all_nodes = {n.id: n for n in self.load_all()}
        ancestors = []
        current = all_nodes.get(node_id)
        visited = set()  # cycle protection
        while current and current.parent_id and current.parent_id not in visited:
            visited.add(current.id)
            parent = all_nodes.get(current.parent_id)
            if parent:
                ancestors.append(parent)
                current = parent
            else:
                break
        return ancestors

    def get_descendants(self, node_id: str) -> list:
        """
        Get all descendant nodes (children, grandchildren, ...).
        Returns list in BFS order.
        """
        all_nodes = self.load_all()
        # Build children index
        children_of: dict = {}
        for n in all_nodes:
            if n.parent_id:
                children_of.setdefault(n.parent_id, []).append(n)

        descendants = []
        queue = [node_id]
        visited = set()
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            for child in children_of.get(current_id, []):
                descendants.append(child)
                queue.append(child.id)
        return descendants

    def get_lineage_tree(self) -> dict:
        """
        Return adjacency list: {parent_id: [child_id, child_id, ...], ...}.
        Roots (parent_id=None) are listed under key "__roots__".
        """
        all_nodes = self.load_all()
        tree: dict = {"__roots__": []}
        for n in all_nodes:
            if n.parent_id is None:
                tree["__roots__"].append(n.id)
            else:
                tree.setdefault(n.parent_id, []).append(n.id)
        return tree

    def update_outcome(self, node_id: str, outcome: str, notes: str = "") -> bool:
        """
        Update the outcome of a node. Rewrites the file (append-only violated
        only for outcome updates — acceptable because it's idempotent).
        Returns True if node was found and updated.
        """
        nodes = self.load_all()
        found = False
        for n in nodes:
            if n.id == node_id:
                n.outcome = outcome
                n.outcome_notes = notes
                n.outcome_timestamp = datetime.now(timezone.utc).isoformat()
                found = True
                break
        if found:
            # Rewrite file
            with open(self.path, "w") as f:
                for n in nodes:
                    f.write(json.dumps(n.to_dict()) + "\n")
        return found

    def find_similar(
        self,
        issue: str,
        task_type: str = "",
        category: str = "",
        action_type: str = "",
    ) -> list:
        """
        Find proposals that targeted the same issue (and optionally same
        task_type, category, action_type). Used by critique to detect
        prior attempts.
        """
        results = []
        for n in self.load_all():
            if n.issue != issue:
                continue
            if task_type and n.task_type != task_type:
                continue
            if category and n.category != category:
                continue
            if action_type and n.action_type != action_type:
                continue
            results.append(n)
        return results
