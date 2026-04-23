#!/usr/bin/env python3
"""
RSI Loop v2 — Knowledge Base Manager
Maintains structured markdown files of failure patterns, success patterns,
and anti-patterns. Provides query and update APIs.
"""

import math
import re
import json
from collections import defaultdict
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
    lineage_refs: list = field(default_factory=list)  # proposal IDs that contributed
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
            "failure-patterns.md": (
                "# Failure Patterns\n\n"
                "Structured catalog of known failure patterns with proven fixes.\n"
                "Auto-updated by RSI Loop v2 from lineage history.\n\n"
                "---\n\n"
            ),
            "success-patterns.md": (
                "# Success Patterns\n\n"
                "What has worked, with lineage references.\n"
                "Auto-updated by RSI Loop v2 from lineage history.\n\n"
                "---\n\n"
            ),
            "anti-patterns.md": (
                "# Anti-Patterns\n\n"
                "Approaches that have been tried and failed repeatedly.\n"
                "Auto-updated by RSI Loop v2 from lineage history.\n\n"
                "---\n\n"
            ),
        }
        for filename, header in templates.items():
            fpath = self.kb_dir / filename
            if not fpath.exists():
                fpath.write_text(header)

    def _get_filepath(self, kind: str) -> Path:
        """Return the KB file path for a given entry kind."""
        mapping = {
            "failure": self.kb_dir / "failure-patterns.md",
            "success": self.kb_dir / "success-patterns.md",
            "anti": self.kb_dir / "anti-patterns.md",
        }
        return mapping[kind]

    def _parse_entries(self, filepath: Path) -> list:
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

    def _parse_section(self, section_text: str):
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
        for line in lines[1:]:
            if line.startswith("- **"):
                # Extract field
                field_match = re.match(r'^- \*\*(.+?):\*\*\s*(.+)', line)
                if field_match:
                    key = field_match.group(1).lower().replace(" ", "_")
                    val = field_match.group(2).strip()
                    fields[key] = val
            elif line.strip() and not line.startswith("---"):
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

        occurrences = 0
        try:
            occurrences = int(fields.get("occurrences", "0"))
        except (ValueError, TypeError):
            pass

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
            occurrences=occurrences,
        )

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

    def _rewrite_file(self, filepath: Path, entries: list) -> None:
        """Rewrite a KB markdown file from entries list."""
        content = filepath.read_text()
        # Get header up to and including ---
        parts = content.split("---")
        if len(parts) >= 2:
            header = parts[0] + "---\n\n"
        else:
            header = content + "\n---\n\n"
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
    ) -> list:
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
        nodes = lineage_store.load_all()
        stats = {"added": 0, "updated": 0}

        # Group by (issue, task_type, action_type) for anti-pattern detection
        rejection_groups: dict = defaultdict(list)
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
            if not n.issue:
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


def kb_query_cli(issue: str = "", task_type: str = "", category: str = "", top_k: int = 3) -> list:
    """CLI-friendly wrapper for KBManager.query(). Returns dicts without KBEntry objects."""
    kb = KBManager()
    results = kb.query(issue=issue, task_type=task_type, category=category, top_k=top_k)
    return [{"reference": r["reference"], "score": r["score"]} for r in results]


def kb_update_cli() -> dict:
    """CLI-friendly wrapper for update_from_lineage. Returns stats dict."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from lineage import LineageStore
    kb = KBManager()
    store = LineageStore()
    return kb.update_from_lineage(store)
