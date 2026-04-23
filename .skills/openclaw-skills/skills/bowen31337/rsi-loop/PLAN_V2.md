# PLAN_V2.md — RSI Loop v2: Lineage, Critique, Knowledge Base

**Author:** Planner (Opus)  
**Date:** 2026-03-26  
**Status:** PLAN COMPLETE — Ready for Builder  
**Scope:** Additive upgrade. No existing files are rewritten. Only integration hooks are added to existing scripts.

---

## 1. File Structure (New Files Only)

```
skills/rsi-loop/
├── scripts/
│   ├── lineage.py          # NEW — Proposal lineage tracking
│   ├── critique.py          # NEW — Critique phase (gate before deploy)
│   ├── kb_manager.py        # NEW — Knowledge base manager
│   └── test_rsi_v2.py       # NEW — All v2 tests (20+ cases)
├── kb/                      # NEW directory
│   ├── failure-patterns.md  # NEW — Catalog of known failures + proven fixes
│   ├── success-patterns.md  # NEW — What worked, with lineage refs
│   └── anti-patterns.md     # NEW — Repeatedly failed approaches
└── memory/
    └── rsi-lineage.jsonl    # NEW — Append-only lineage store (auto-created)
```

**Existing files with integration hooks added (minimal changes):**
- `scripts/rsi_cli.py` — 2 new subcommands (`lineage`, `kb`) + critique gate in cycle
- `scripts/synthesizer.py` — write `parent_id` when generating proposals
- `scripts/deployer.py` — run critique before deploy in `full-cycle`
- `scripts/observer.py` — update lineage node when logging outcome

---

## 2. Data Structures

### 2.1 ProposalNode (lineage.py)

```python
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timezone

@dataclass
class ProposalNode:
    """A node in the proposal lineage tree."""
    id: str                                    # proposal ID (matches proposal JSON id)
    parent_id: Optional[str] = None            # ID of the proposal this descended from (None = root)
    timestamp: str = ""                        # ISO 8601 UTC
    task_type: str = ""                        # from pattern.task_type
    issue: str = ""                            # from pattern.issue
    category: str = ""                         # from pattern.category
    proposal_text: str = ""                    # title or description of the proposal
    action_type: str = ""                      # create_skill, fix_routing, apply_gene, etc.
    mutation_type: str = ""                    # repair, optimize, innovate
    outcome: str = "pending"                   # pending | deployed | rejected | superseded
    outcome_notes: str = ""                    # reason for rejection / deploy result
    outcome_timestamp: Optional[str] = None    # when outcome was recorded
    tags: list[str] = field(default_factory=list)  # freeform tags for KB queries

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ProposalNode":
        # Handle extra/missing fields gracefully
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**filtered)
```

### 2.2 LineageStore (lineage.py)

```python
import json
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).parent.parent
MEMORY_DIR = SKILL_DIR / "memory"
LINEAGE_FILE = MEMORY_DIR / "rsi-lineage.jsonl"

class LineageStore:
    """Append-only store for proposal lineage nodes."""

    def __init__(self, path: Path = LINEAGE_FILE):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, node: ProposalNode) -> None:
        """Append a ProposalNode to the lineage store."""
        with open(self.path, "a") as f:
            f.write(json.dumps(node.to_dict()) + "\n")

    def load_all(self) -> list[ProposalNode]:
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

    def get_ancestors(self, node_id: str) -> list[ProposalNode]:
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

    def get_descendants(self, node_id: str) -> list[ProposalNode]:
        """
        Get all descendant nodes (children, grandchildren, ...).
        Returns list in BFS order.
        """
        all_nodes = self.load_all()
        # Build children index
        children_of: dict[str, list[ProposalNode]] = {}
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

    def get_lineage_tree(self) -> dict[str, list[str]]:
        """
        Return adjacency list: {parent_id: [child_id, child_id, ...], ...}.
        Roots (parent_id=None) are listed under key "__roots__".
        """
        all_nodes = self.load_all()
        tree: dict[str, list[str]] = {"__roots__": []}
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
    ) -> list[ProposalNode]:
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
```

### 2.3 CritiqueResult (critique.py)

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CritiqueResult:
    """Result of the critique phase for a single proposal."""
    verdict: str                # "approve" | "reject" | "defer"
    reason: str                 # human-readable explanation
    similar_count: int = 0      # how many similar proposals exist in lineage
    ancestor_success_rate: float = 0.0  # success rate of ancestor proposals
    redundant_with: Optional[str] = None  # ID of already-deployed proposal this is redundant with
    kb_references: list[str] = None  # relevant KB entries (from kb_manager)

    def __post_init__(self):
        if self.kb_references is None:
            self.kb_references = []
```

### 2.4 CritiqueAgent (critique.py)

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from lineage import LineageStore, ProposalNode

class CritiqueAgent:
    """
    Reviews proposals before deployment by checking lineage history
    and knowledge base for prior art, redundancy, and failure patterns.
    """

    def __init__(self, lineage_store: LineageStore = None, kb_path: Path = None):
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
        ancestor_success_rate = self._compute_ancestor_success_rate(parent_id)

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

        # DEFER: Low ancestor success rate with enough data
        if parent_id and ancestor_success_rate < 0.3 and ancestor_success_rate > 0:
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

    def _compute_ancestor_success_rate(self, parent_id: str | None) -> float:
        """Walk ancestor chain, compute deployed/(deployed+rejected) ratio."""
        if not parent_id:
            return 0.0
        ancestors = self.lineage.get_ancestors(parent_id)
        if not ancestors:
            return 0.0
        resolved = [a for a in ancestors if a.outcome in ("deployed", "rejected")]
        if not resolved:
            return 0.0
        deployed = sum(1 for a in resolved if a.outcome == "deployed")
        return deployed / len(resolved)

    def _check_redundancy(
        self, similar: list[ProposalNode], action_type: str
    ) -> str | None:
        """
        Check if any similar proposal with same action_type is already deployed.
        Returns the ID of the redundant proposal, or None.
        """
        for s in similar:
            if s.outcome == "deployed" and s.action_type == action_type:
                return s.id
        return None

    def _query_kb(self, issue: str, task_type: str, category: str) -> list[str]:
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
```

### 2.5 KBManager (kb_manager.py)

```python
#!/usr/bin/env python3
"""
RSI Loop v2 — Knowledge Base Manager
Maintains structured markdown files of failure patterns, success patterns,
and anti-patterns. Provides query and update APIs.
"""

import re
import json
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field

SKILL_DIR = Path(__file__).parent.parent
KB_DIR = SKILL_DIR / "kb"

# File paths
FAILURE_PATTERNS_FILE = KB_DIR / "failure-patterns.md"
SUCCESS_PATTERNS_FILE = KB_DIR / "success-patterns.md"
ANTI_PATTERNS_FILE = KB_DIR / "anti-patterns.md"


@dataclass
class KBEntry:
    """A single knowledge base entry."""
    id: str                         # e.g. "FP-001", "SP-001", "AP-001"
    kind: str                       # "failure" | "success" | "anti"
    issue: str                      # issue type (rate_limit, tool_error, etc.)
    task_type: str                  # task type or "*" for any
    category: str                   # pattern category
    title: str                      # one-line summary
    description: str                # detailed description
    fix: str = ""                   # proven fix (for failure/success) or "N/A" (for anti)
    lineage_refs: list[str] = field(default_factory=list)  # proposal IDs that contributed
    created_at: str = ""
    updated_at: str = ""
    occurrences: int = 0            # how many times this pattern was seen

    def to_markdown_section(self) -> str:
        """Render as a markdown section for the KB file."""
        refs = ", ".join(self.lineage_refs) if self.lineage_refs else "none"
        return (
            f"### {self.id}: {self.title}\n"
            f"- **Issue:** `{self.issue}`\n"
            f"- **Task type:** `{self.task_type}`\n"
            f"- **Category:** `{self.category}`\n"
            f"- **Occurrences:** {self.occurrences}\n"
            f"- **Fix:** {self.fix}\n"
            f"- **Lineage refs:** {refs}\n"
            f"- **Updated:** {self.updated_at}\n"
            f"\n{self.description}\n"
        )


class KBManager:
    """Manage the RSI knowledge base."""

    def __init__(self, kb_dir: Path = KB_DIR):
        self.kb_dir = kb_dir
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_files()

    def _ensure_files(self):
        """Create KB files with headers if they don't exist."""
        templates = {
            FAILURE_PATTERNS_FILE: (
                "# Failure Patterns\n\n"
                "Structured catalog of known failure patterns with proven fixes.\n"
                "Auto-updated by RSI Loop v2 from lineage history.\n\n"
                "---\n\n"
            ),
            SUCCESS_PATTERNS_FILE: (
                "# Success Patterns\n\n"
                "What has worked, with lineage references.\n"
                "Auto-updated by RSI Loop v2 from lineage history.\n\n"
                "---\n\n"
            ),
            ANTI_PATTERNS_FILE: (
                "# Anti-Patterns\n\n"
                "Approaches that have been tried and failed repeatedly.\n"
                "Auto-updated by RSI Loop v2 from lineage history.\n\n"
                "---\n\n"
            ),
        }
        for filepath, header in templates.items():
            fpath = self.kb_dir / filepath.name if not filepath.is_absolute() else filepath
            if not fpath.exists():
                fpath.write_text(header)

    def _parse_entries(self, filepath: Path) -> list[KBEntry]:
        """Parse a KB markdown file into KBEntry objects."""
        if not filepath.exists():
            return []
        text = filepath.read_text()
        entries = []
        # Split on ### headers
        sections = re.split(r'^### ', text, flags=re.MULTILINE)
        for section in sections[1:]:  # skip header
            entry = self._parse_section(section)
            if entry:
                entries.append(entry)
        return entries

    def _parse_section(self, section_text: str) -> KBEntry | None:
        """Parse a single ### section into a KBEntry."""
        lines = section_text.strip().split("\n")
        if not lines:
            return None

        # First line: "ID: Title"
        header = lines[0]
        match = re.match(r'^([A-Z]+-\d+):\s*(.+)', header)
        if not match:
            return None
        entry_id = match.group(1)
        title = match.group(2).strip()

        # Parse metadata fields
        fields: dict = {}
        description_lines = []
        in_description = False
        for line in lines[1:]:
            if line.startswith("- **"):
                in_description = False
                # Extract field
                field_match = re.match(r'^- \*\*(.+?):\*\*\s*(.+)', line)
                if field_match:
                    key = field_match.group(1).lower().replace(" ", "_")
                    val = field_match.group(2).strip()
                    fields[key] = val
            elif line.strip() and not line.startswith("---"):
                in_description = True
                description_lines.append(line)

        # Determine kind from ID prefix
        kind = "failure"
        if entry_id.startswith("SP"):
            kind = "success"
        elif entry_id.startswith("AP"):
            kind = "anti"

        lineage_refs = []
        if fields.get("lineage_refs") and fields["lineage_refs"] != "none":
            lineage_refs = [r.strip() for r in fields["lineage_refs"].split(",")]

        return KBEntry(
            id=entry_id,
            kind=kind,
            issue=fields.get("issue", "").strip("`"),
            task_type=fields.get("task_type", "*").strip("`"),
            category=fields.get("category", "").strip("`"),
            title=title,
            description="\n".join(description_lines).strip(),
            fix=fields.get("fix", ""),
            lineage_refs=lineage_refs,
            created_at=fields.get("created", ""),
            updated_at=fields.get("updated", ""),
            occurrences=int(fields.get("occurrences", "0")),
        )

    def _get_filepath(self, kind: str) -> Path:
        """Return the KB file path for a given entry kind."""
        mapping = {
            "failure": self.kb_dir / "failure-patterns.md",
            "success": self.kb_dir / "success-patterns.md",
            "anti": self.kb_dir / "anti-patterns.md",
        }
        return mapping[kind]

    def _next_id(self, kind: str) -> str:
        """Generate the next sequential ID for a kind."""
        prefix = {"failure": "FP", "success": "SP", "anti": "AP"}[kind]
        existing = self._parse_entries(self._get_filepath(kind))
        max_num = 0
        for e in existing:
            match = re.match(rf'{prefix}-(\d+)', e.id)
            if match:
                max_num = max(max_num, int(match.group(1)))
        return f"{prefix}-{max_num + 1:03d}"

    def add_entry(self, entry: KBEntry) -> str:
        """
        Add a new entry to the appropriate KB file. Auto-assigns ID if empty.
        Returns the assigned ID.
        """
        if not entry.id:
            entry.id = self._next_id(entry.kind)
        now = datetime.now(timezone.utc).isoformat()
        if not entry.created_at:
            entry.created_at = now
        entry.updated_at = now

        filepath = self._get_filepath(entry.kind)
        with open(filepath, "a") as f:
            f.write("\n" + entry.to_markdown_section())
        return entry.id

    def update_entry(self, entry_id: str, updates: dict) -> bool:
        """
        Update an existing entry in-place. Rewrites the file.
        updates dict can contain: occurrences, fix, description, lineage_refs (appended).
        Returns True if found and updated.
        """
        for kind in ("failure", "success", "anti"):
            filepath = self._get_filepath(kind)
            entries = self._parse_entries(filepath)
            found_idx = None
            for i, e in enumerate(entries):
                if e.id == entry_id:
                    found_idx = i
                    break
            if found_idx is not None:
                entry = entries[found_idx]
                if "occurrences" in updates:
                    entry.occurrences = updates["occurrences"]
                if "fix" in updates:
                    entry.fix = updates["fix"]
                if "description" in updates:
                    entry.description = updates["description"]
                if "lineage_refs" in updates:
                    for ref in updates["lineage_refs"]:
                        if ref not in entry.lineage_refs:
                            entry.lineage_refs.append(ref)
                entry.updated_at = datetime.now(timezone.utc).isoformat()
                # Rewrite file
                self._rewrite_file(filepath, entries)
                return True
        return False

    def _rewrite_file(self, filepath: Path, entries: list[KBEntry]) -> None:
        """Rewrite a KB markdown file from entries list."""
        header = filepath.read_text().split("---")[0] + "---\n\n"
        with open(filepath, "w") as f:
            f.write(header)
            for entry in entries:
                f.write(entry.to_markdown_section() + "\n")

    def query(
        self,
        issue: str = "",
        task_type: str = "",
        category: str = "",
        top_k: int = 3,
    ) -> list[dict]:
        """
        Query all KB files for entries matching the given criteria.
        Returns top_k results sorted by relevance score, each as:
        {"reference": "[PREFIX] ID: title", "entry": KBEntry, "score": float}
        """
        all_entries = []
        for kind in ("failure", "success", "anti"):
            filepath = self._get_filepath(kind)
            for entry in self._parse_entries(filepath):
                score = 0.0
                if issue and entry.issue == issue:
                    score += 3.0
                if task_type and entry.task_type == task_type:
                    score += 2.0
                elif entry.task_type == "*":
                    score += 0.5
                if category and entry.category == category:
                    score += 1.0
                # Boost by occurrences (log scale)
                import math
                score += min(1.0, math.log1p(entry.occurrences) / 5.0)

                if score > 0:
                    prefix = {"failure": "[FAIL]", "success": "[SUCCESS]", "anti": "[ANTI]"}[kind]
                    all_entries.append({
                        "reference": f"{prefix} {entry.id}: {entry.title}",
                        "entry": entry,
                        "score": score,
                    })

        all_entries.sort(key=lambda x: -x["score"])
        return all_entries[:top_k]

    def update_from_lineage(self, lineage_store) -> dict:
        """
        Scan lineage for deployed/rejected proposals and update KB accordingly.
        - Deployed proposals → success-patterns (or update existing)
        - Rejected proposals with 3+ rejections for same issue+action → anti-patterns
        - Deployed proposals that fixed recurring issues → failure-patterns with fix

        Returns {"added": int, "updated": int}
        """
        from collections import defaultdict

        nodes = lineage_store.load_all()
        stats = {"added": 0, "updated": 0}

        # Group by (issue, task_type, action_type) for anti-pattern detection
        rejection_groups: dict[tuple, list] = defaultdict(list)
        for n in nodes:
            if n.outcome == "rejected":
                key = (n.issue, n.task_type, n.action_type)
                rejection_groups[key].append(n)

        # Check existing KB entries to avoid duplicates
        existing_success = {e.issue: e for e in self._parse_entries(self._get_filepath("success"))}
        existing_anti = {(e.issue, e.category): e for e in self._parse_entries(self._get_filepath("anti"))}
        existing_failure = {e.issue: e for e in self._parse_entries(self._get_filepath("failure"))}

        # Process deployed nodes → success patterns
        for n in nodes:
            if n.outcome != "deployed":
                continue
            if n.issue in existing_success:
                # Update occurrences and add lineage ref
                self.update_entry(
                    existing_success[n.issue].id,
                    {"occurrences": existing_success[n.issue].occurrences + 1,
                     "lineage_refs": [n.id]},
                )
                stats["updated"] += 1
            else:
                entry = KBEntry(
                    id="",  # auto-assigned
                    kind="success",
                    issue=n.issue,
                    task_type=n.task_type,
                    category=n.category,
                    title=f"Deployed fix for '{n.issue}' via {n.action_type}",
                    description=n.proposal_text or f"Fix deployed for {n.issue} in {n.task_type} tasks.",
                    fix=f"Action: {n.action_type}. {n.outcome_notes or ''}".strip(),
                    lineage_refs=[n.id],
                    occurrences=1,
                )
                self.add_entry(entry)
                existing_success[n.issue] = entry
                stats["added"] += 1

        # Process rejection groups → anti-patterns (threshold: 3+ rejections)
        for (issue, task_type, action_type), rejected_nodes in rejection_groups.items():
            if len(rejected_nodes) < 3:
                continue
            key = (issue, action_type)
            if key in existing_anti:
                self.update_entry(
                    existing_anti[key].id,
                    {"occurrences": len(rejected_nodes),
                     "lineage_refs": [n.id for n in rejected_nodes[-3:]]},
                )
                stats["updated"] += 1
            else:
                entry = KBEntry(
                    id="",
                    kind="anti",
                    issue=issue,
                    task_type=task_type,
                    category="",  # mixed
                    title=f"Repeated failure: {action_type} for '{issue}'",
                    description=(
                        f"The approach '{action_type}' has been rejected "
                        f"{len(rejected_nodes)} times for issue '{issue}'. "
                        f"Reasons: {'; '.join(n.outcome_notes for n in rejected_nodes[-3:] if n.outcome_notes)}"
                    ),
                    fix="N/A — try a different approach",
                    lineage_refs=[n.id for n in rejected_nodes[-3:]],
                    occurrences=len(rejected_nodes),
                )
                self.add_entry(entry)
                existing_anti[key] = entry
                stats["added"] += 1

        # Process deployed nodes that fixed known failure patterns
        for n in nodes:
            if n.outcome != "deployed" or not n.issue:
                continue
            if n.issue in existing_failure:
                if not existing_failure[n.issue].fix:
                    self.update_entry(
                        existing_failure[n.issue].id,
                        {"fix": f"Fixed via {n.action_type}: {n.outcome_notes or 'see lineage'}",
                         "lineage_refs": [n.id]},
                    )
                    stats["updated"] += 1

        return stats
```

### 2.6 Standalone Functions (kb_manager.py)

```python
def kb_query_cli(issue: str = "", task_type: str = "", category: str = "", top_k: int = 3) -> list[dict]:
    """CLI-friendly wrapper for KBManager.query(). Returns dicts without KBEntry objects."""
    kb = KBManager()
    results = kb.query(issue=issue, task_type=task_type, category=category, top_k=top_k)
    return [{"reference": r["reference"], "score": r["score"]} for r in results]


def kb_update_cli() -> dict:
    """CLI-friendly wrapper for update_from_lineage. Returns stats dict."""
    from lineage import LineageStore
    kb = KBManager()
    store = LineageStore()
    return kb.update_from_lineage(store)
```

---

## 3. Integration Hooks

### 3.1 synthesizer.py — Add parent_id to proposals

**Location:** `generate_proposals_heuristic()`, after the `for p in patterns[:max_proposals]:` loop body, before `proposals.append(proposal)`.

**What to add:** For each proposal generated, check if a previously deployed proposal for the same issue exists in lineage. If so, set `parent_id` on the new proposal and record it in lineage.

```python
# === INTEGRATION HOOK: RSI v2 lineage ===
# Insert this at the END of generate_proposals_heuristic(), AFTER the proposals list
# is fully built but BEFORE the return statement.
# Add at the top of the file:
try:
    from lineage import LineageStore, ProposalNode
    _LINEAGE_AVAILABLE = True
except ImportError:
    _LINEAGE_AVAILABLE = False

# Insert BEFORE `return proposals` (around line ~260, after the for loop closes):
if _LINEAGE_AVAILABLE:
    try:
        store = LineageStore()
        for p in proposals:
            issue = p.get("pattern", {}).get("issue", "")
            task_type = p.get("pattern", {}).get("task_type", "")
            category = p.get("pattern", {}).get("category", "")
            action_type = p.get("action_type", "")

            # Find most recent deployed ancestor for this issue
            similar = store.find_similar(issue=issue, task_type=task_type)
            parent_id = None
            for s in reversed(similar):  # most recent first
                if s.outcome == "deployed":
                    parent_id = s.id
                    break

            p["parent_id"] = parent_id

            # Record in lineage
            node = ProposalNode(
                id=p["id"],
                parent_id=parent_id,
                task_type=task_type,
                issue=issue,
                category=category,
                proposal_text=p.get("title", ""),
                action_type=action_type,
                mutation_type=p.get("mutation_type", mutation_type),
                outcome="pending",
            )
            store.append(node)
    except Exception as e:
        print(f"[LINEAGE] Warning: could not record lineage: {e}")
```

### 3.2 deployer.py — Run critique before deploy in full-cycle

**Location:** In `full-cycle` handler (the `main()` function, `args.cmd == "full-cycle"` branch), after Step 3 (auto-approve) and before Step 4 (deploy).

```python
# === INTEGRATION HOOK: RSI v2 critique ===
# Add at the top of the file:
try:
    from critique import CritiqueAgent
    _CRITIQUE_AVAILABLE = True
except ImportError:
    _CRITIQUE_AVAILABLE = False

# Insert as new Step 3.5 in full-cycle, BETWEEN existing Step 3 and Step 4:
#
# (After the auto_approved list is built, before the deploy loop)

        # Step 3.5: Critique phase (RSI v2)
        if _CRITIQUE_AVAILABLE:
            print(f"\nStep 3.5: Running critique on {len(auto_approved)} proposals...")
            critic = CritiqueAgent()
            critique_passed = []
            for p in auto_approved:
                result = critic.critique(p)
                if result.verdict == "approve":
                    critique_passed.append(p)
                    print(f"  ✓ {p['id']}: approved — {result.reason[:80]}")
                elif result.verdict == "reject":
                    # Update proposal status to rejected
                    p["status"] = "rejected"
                    synthesizer.save_proposals([p])
                    # Update lineage
                    try:
                        from lineage import LineageStore
                        LineageStore().update_outcome(p["id"], "rejected", result.reason[:200])
                    except Exception:
                        pass
                    print(f"  ✗ {p['id']}: REJECTED — {result.reason[:80]}")
                else:  # defer
                    p["status"] = "draft"  # back to draft for manual review
                    synthesizer.save_proposals([p])
                    print(f"  ⏸ {p['id']}: DEFERRED — {result.reason[:80]}")
            auto_approved = critique_passed
        else:
            print("\n(Critique module not available — skipping critique phase)")
```

### 3.3 deployer.py — Update lineage on deploy

**Location:** In `deploy_proposal()`, after `mark_deployed(p, notes=result[:200])` (the existing success path, around line ~280).

```python
# === INTEGRATION HOOK: RSI v2 lineage outcome update ===
# Add after mark_deployed(p, notes=result[:200]):
        try:
            from lineage import LineageStore
            LineageStore().update_outcome(p["id"], "deployed", result[:200])
        except Exception:
            pass
```

### 3.4 observer.py — Update lineage on outcome logging

**No change needed.** The lineage is updated via deployer.py when proposals are deployed/rejected. Observer logs task outcomes to outcomes.jsonl — these are separate from proposal outcomes. The lineage tracks proposal lifecycle, not individual task observations.

**Rationale:** Proposals are the unit of lineage tracking. Observer logs raw task outcomes which feed the analyzer. Conflating the two would add complexity without value.

### 3.5 rsi_cli.py — New subcommands

**Add these to `main()` after the existing subcommand parsers:**

```python
    # === RSI v2 subcommands ===

    # lineage
    lineage_p = sub.add_parser("lineage", help="Show proposal lineage tree")
    lineage_p.add_argument("--node", help="Show lineage for specific proposal ID")
    lineage_p.add_argument("--format", choices=["tree", "json", "flat"], default="tree")

    # kb
    kb_p = sub.add_parser("kb", help="Query or update knowledge base")
    kb_sub = kb_p.add_subparsers(dest="kb_cmd")
    kb_query_p = kb_sub.add_parser("query", help="Query KB for relevant entries")
    kb_query_p.add_argument("--issue", default="")
    kb_query_p.add_argument("--task-type", default="")
    kb_query_p.add_argument("--category", default="")
    kb_query_p.add_argument("--top", type=int, default=3)
    kb_sub.add_parser("update", help="Update KB from lineage history")
    kb_sub.add_parser("stats", help="Show KB statistics")
```

**Add handlers in the dispatch section:**

```python
    elif args.cmd == "lineage":
        sys.path.insert(0, str(SCRIPTS_DIR))
        from lineage import LineageStore
        store = LineageStore()

        if args.node:
            node = store.get_node(args.node)
            if not node:
                print(f"Node '{args.node}' not found in lineage.")
                sys.exit(1)
            ancestors = store.get_ancestors(args.node)
            descendants = store.get_descendants(args.node)

            print(f"\n=== Lineage for {args.node} ===\n")
            print(f"Node: {node.id} | {node.issue} | {node.outcome}")
            print(f"  Proposal: {node.proposal_text[:80]}")
            print(f"  Parent: {node.parent_id or '(root)'}")
            print(f"  Timestamp: {node.timestamp[:19]}")

            if ancestors:
                print(f"\nAncestors ({len(ancestors)}):")
                for a in ancestors:
                    print(f"  ← {a.id}: {a.proposal_text[:60]} [{a.outcome}]")

            if descendants:
                print(f"\nDescendants ({len(descendants)}):")
                for d in descendants:
                    print(f"  → {d.id}: {d.proposal_text[:60]} [{d.outcome}]")
        else:
            # Show full tree
            tree = store.get_lineage_tree()
            all_nodes = {n.id: n for n in store.load_all()}
            roots = tree.get("__roots__", [])

            if not all_nodes:
                print("No lineage data yet. Run a cycle to generate proposals.")
                sys.exit(0)

            if args.format == "json":
                print(json.dumps(tree, indent=2))
            elif args.format == "flat":
                print(f"\n{'ID':<12} {'PARENT':<12} {'ISSUE':<20} {'OUTCOME':<12} {'TITLE'}")
                print("─" * 90)
                for n in all_nodes.values():
                    print(f"{n.id:<12} {(n.parent_id or '-'):<12} "
                          f"{n.issue:<20} {n.outcome:<12} {n.proposal_text[:40]}")
            else:  # tree format
                print(f"\n=== Proposal Lineage Tree ({len(all_nodes)} nodes) ===\n")

                def print_tree(node_id: str, indent: int = 0):
                    node = all_nodes.get(node_id)
                    if not node:
                        return
                    prefix = "  " * indent + ("├─ " if indent > 0 else "")
                    outcome_icon = {"deployed": "✓", "rejected": "✗", "pending": "…", "superseded": "→"}.get(node.outcome, "?")
                    print(f"{prefix}[{outcome_icon}] {node.id}: {node.proposal_text[:50]} ({node.issue})")
                    children = tree.get(node_id, [])
                    for child_id in children:
                        print_tree(child_id, indent + 1)

                for root_id in roots:
                    print_tree(root_id)

                # Show orphaned nodes (parent_id set but parent not in lineage)
                orphans = [n for n in all_nodes.values()
                           if n.parent_id and n.parent_id not in all_nodes and n.id not in roots]
                if orphans:
                    print(f"\nOrphaned nodes ({len(orphans)}):")
                    for o in orphans:
                        print(f"  [?] {o.id}: {o.proposal_text[:50]} (parent {o.parent_id} missing)")

    elif args.cmd == "kb":
        sys.path.insert(0, str(SCRIPTS_DIR))
        if not args.kb_cmd:
            kb_p.print_help()
        elif args.kb_cmd == "query":
            from kb_manager import kb_query_cli
            results = kb_query_cli(
                issue=args.issue,
                task_type=args.task_type,
                category=args.category,
                top_k=args.top,
            )
            if not results:
                print("No matching KB entries found.")
            else:
                print(f"\nTop {len(results)} KB results:\n")
                for r in results:
                    print(f"  [{r['score']:.1f}] {r['reference']}")
        elif args.kb_cmd == "update":
            from kb_manager import kb_update_cli
            stats = kb_update_cli()
            print(f"KB updated: {stats['added']} added, {stats['updated']} updated")
        elif args.kb_cmd == "stats":
            from kb_manager import KBManager
            kb = KBManager()
            for kind, label in [("failure", "Failure"), ("success", "Success"), ("anti", "Anti")]:
                entries = kb._parse_entries(kb._get_filepath(kind))
                print(f"  {label} patterns: {len(entries)}")
                for e in entries[:3]:
                    print(f"    - {e.id}: {e.title[:60]} ({e.occurrences} occurrences)")
```

---

## 4. Test Plan (test_rsi_v2.py)

All tests use `pytest` and `tmp_path` fixture. No external dependencies. Tests are in `scripts/test_rsi_v2.py`.

### 4.1 Lineage Tests

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_proposal_node_creation` | Create ProposalNode with defaults, verify timestamp auto-set |
| 2 | `test_proposal_node_roundtrip` | `to_dict()` → `from_dict()` preserves all fields |
| 3 | `test_proposal_node_from_dict_extra_fields` | Extra fields in dict are silently ignored |
| 4 | `test_lineage_store_append_and_load` | Append 3 nodes, load_all returns all 3 in order |
| 5 | `test_lineage_store_empty` | load_all on non-existent file returns [] |
| 6 | `test_lineage_store_get_node` | get_node returns correct node or None |
| 7 | `test_lineage_store_get_ancestors` | Chain of 4 nodes, get_ancestors returns [parent, grandparent, great-grandparent] |
| 8 | `test_lineage_store_get_ancestors_cycle_protection` | Circular parent chain doesn't infinite loop |
| 9 | `test_lineage_store_get_descendants` | Tree with branches, get_descendants returns all children in BFS order |
| 10 | `test_lineage_store_get_lineage_tree` | Returns correct adjacency list with __roots__ |
| 11 | `test_lineage_store_update_outcome` | Update outcome from pending to deployed, verify file rewritten |
| 12 | `test_lineage_store_update_outcome_not_found` | Returns False for nonexistent node |
| 13 | `test_lineage_store_find_similar` | Finds proposals matching issue, respects task_type/category filters |

### 4.2 Critique Tests

| # | Test Name | Description |
|---|-----------|-------------|
| 14 | `test_critique_approve_no_history` | New proposal with no prior history → approve |
| 15 | `test_critique_reject_repeated_failures` | 3+ rejected proposals with same action_type → reject |
| 16 | `test_critique_reject_redundant_deployed` | Proposal redundant with deployed fix → reject |
| 17 | `test_critique_defer_anti_pattern` | KB has anti-pattern for this approach → defer |
| 18 | `test_critique_defer_low_ancestor_success` | Parent chain with <30% success rate → defer |
| 19 | `test_critique_approve_with_enrichment` | Approve with note about prior similar proposals |
| 20 | `test_critique_excludes_self` | Proposal's own ID in lineage is excluded from similar check |

### 4.3 Knowledge Base Tests

| # | Test Name | Description |
|---|-----------|-------------|
| 21 | `test_kb_manager_creates_files` | Instantiation creates all 3 KB files with headers |
| 22 | `test_kb_add_and_parse_entry` | Add entry, parse it back, verify fields match |
| 23 | `test_kb_query_by_issue` | Query returns entries matching issue, sorted by score |
| 24 | `test_kb_query_empty` | Query with no matches returns [] |
| 25 | `test_kb_update_entry` | Update occurrences and lineage_refs, verify persistence |
| 26 | `test_kb_update_from_lineage_success_pattern` | Deployed proposal creates success pattern entry |
| 27 | `test_kb_update_from_lineage_anti_pattern` | 3+ rejected proposals creates anti-pattern entry |
| 28 | `test_kb_update_from_lineage_idempotent` | Running update twice doesn't create duplicate entries |
| 29 | `test_kb_next_id_sequential` | IDs are assigned sequentially (FP-001, FP-002, ...) |
| 30 | `test_kb_query_cli_returns_clean_dicts` | CLI wrapper returns dicts without KBEntry objects |

### 4.4 Integration Tests

| # | Test Name | Description |
|---|-----------|-------------|
| 31 | `test_full_cycle_with_critique` | Simulate: generate proposals → critique → only approved are deployed |
| 32 | `test_lineage_parent_assignment` | Synthesizer sets parent_id when prior deployed proposal exists |
| 33 | `test_deploy_updates_lineage` | Deploying a proposal updates lineage node outcome to "deployed" |

### Test Fixture Patterns

```python
import pytest
from pathlib import Path

@pytest.fixture
def lineage_store(tmp_path):
    """Create a LineageStore with a temp file."""
    from lineage import LineageStore
    return LineageStore(path=tmp_path / "test-lineage.jsonl")

@pytest.fixture
def kb_manager(tmp_path):
    """Create a KBManager with a temp directory."""
    from kb_manager import KBManager
    return KBManager(kb_dir=tmp_path / "kb")

@pytest.fixture
def critique_agent(lineage_store, kb_manager):
    """Create a CritiqueAgent with test stores."""
    from critique import CritiqueAgent
    return CritiqueAgent(lineage_store=lineage_store, kb_path=kb_manager.kb_dir)
```

---

## 5. Migration Notes

### 5.1 Existing Proposals (No Lineage)

The 28 existing proposals in `data/proposals/` have no `parent_id` field and no lineage entries. **Migration is passive:**

1. **No data migration required.** The LineageStore starts empty. Existing proposals are not retroactively added to lineage.
2. **First cycle after v2:** New proposals generated by `synthesizer.py` will be the first lineage entries. They will have `parent_id=None` (roots) since no prior lineage exists for matching.
3. **Subsequent cycles:** New proposals that address the same issues as previously deployed proposals will automatically get `parent_id` pointing to the deployed ancestor.
4. **Existing deployed proposals:** The critique agent's `find_similar()` checks lineage only — it won't find old proposals that aren't in lineage. This means the first v2 cycle won't reject proposals as "redundant" even if an identical one was deployed in v1. This is intentional — we want a clean start for lineage tracking.

### 5.2 One-Time KB Seeding (Optional)

After the first few cycles populate lineage, run:
```bash
uv run python skills/rsi-loop/scripts/rsi_cli.py kb update
```
This scans lineage and auto-populates failure/success/anti patterns.

**Manual seeding:** Operators can manually add entries to `kb/failure-patterns.md` etc. using the markdown format documented in KBEntry.to_markdown_section(). The parser is tolerant of extra whitespace/content.

### 5.3 Backward Compatibility

- All new features are behind `try/except ImportError` guards in existing scripts
- If `lineage.py` or `critique.py` are missing/broken, the existing flow runs unchanged
- The `parent_id` field on proposals is optional — existing JSON files without it are handled
- New CLI subcommands (`lineage`, `kb`) are additive — no existing commands change behavior
- The `memory/` directory is created automatically by LineageStore

### 5.4 Feature Flags (Implicit)

The system uses import availability as implicit feature flags:
- `_LINEAGE_AVAILABLE` → enables parent_id tracking in synthesizer
- `_CRITIQUE_AVAILABLE` → enables critique gate in deployer full-cycle
- KB query in critique falls back to empty list if kb_manager import fails

---

## 6. Sequencing for Builder

1. **Create `kb/` directory** with the 3 empty template files (failure-patterns.md, success-patterns.md, anti-patterns.md)
2. **Create `memory/` directory** (will be populated by LineageStore on first write)
3. **Write `scripts/lineage.py`** — ProposalNode dataclass + LineageStore class (self-contained, no deps on other new files)
4. **Write `scripts/kb_manager.py`** — KBEntry + KBManager + CLI wrappers (depends only on lineage.py for update_from_lineage)
5. **Write `scripts/critique.py`** — CritiqueResult + CritiqueAgent (depends on lineage.py and kb_manager.py)
6. **Add integration hooks to `scripts/synthesizer.py`** — import guard + lineage recording
7. **Add integration hooks to `scripts/deployer.py`** — import guard + critique gate + lineage outcome update
8. **Add subcommands to `scripts/rsi_cli.py`** — `lineage` and `kb` subcommands
9. **Write `scripts/test_rsi_v2.py`** — all 33 tests
10. **Run tests:** `cd skills/rsi-loop && uv run pytest scripts/test_rsi_v2.py -v`

---

## 7. CLI Usage After v2

```bash
# Existing commands (unchanged)
uv run python skills/rsi-loop/scripts/rsi_cli.py cycle
uv run python skills/rsi-loop/scripts/rsi_cli.py status
uv run python skills/rsi-loop/scripts/rsi_cli.py log --task code_generation --success true --quality 4

# NEW: Show proposal lineage tree
uv run python skills/rsi-loop/scripts/rsi_cli.py lineage
uv run python skills/rsi-loop/scripts/rsi_cli.py lineage --node abc12345
uv run python skills/rsi-loop/scripts/rsi_cli.py lineage --format flat
uv run python skills/rsi-loop/scripts/rsi_cli.py lineage --format json

# NEW: Knowledge base operations
uv run python skills/rsi-loop/scripts/rsi_cli.py kb query --issue rate_limit --task-type message_routing
uv run python skills/rsi-loop/scripts/rsi_cli.py kb update
uv run python skills/rsi-loop/scripts/rsi_cli.py kb stats
```

---

## 8. Cycle Flow After v2

```
Observe → Analyze → Synthesize → [NEW: Record Lineage] → [NEW: Critique] → Deploy → [NEW: Update Lineage Outcome]
                                        │                       │
                                        │                       ├─ approve → deploy
                                        │                       ├─ reject → log rejected in lineage
                                        │                       └─ defer → back to draft for review
                                        │
                                        └─ Find parent_id from prior deployed proposals
                                           Record ProposalNode in lineage store
```

**Critique Decision Matrix:**

| Condition | Verdict | Rationale |
|-----------|---------|-----------|
| 3+ rejected with same action_type | REJECT | Proven failure pattern |
| Redundant with deployed fix | REJECT | Already addressed |
| KB anti-pattern match | DEFER | Known bad approach |
| Ancestor success rate < 30% | DEFER | Low-confidence lineage |
| No objections | APPROVE | Proceed with deployment |
