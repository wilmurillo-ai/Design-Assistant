#!/usr/bin/env python3
"""
RSI Loop v2 — Test Suite
Tests for lineage tracking, critique phase, and knowledge base.
Run with: uv run pytest skills/rsi-loop/tests/test_rsi_v2.py -v
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts dir to path
SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# 4.1 Lineage Tests
# ---------------------------------------------------------------------------

def test_proposal_node_creation():
    """Test 1: ProposalNode with defaults has auto-set timestamp."""
    from lineage import ProposalNode
    node = ProposalNode(id="abc123")
    assert node.id == "abc123"
    assert node.timestamp != ""
    assert node.outcome == "pending"
    assert node.parent_id is None


def test_proposal_node_roundtrip():
    """Test 2: to_dict() → from_dict() preserves all fields."""
    from lineage import ProposalNode
    node = ProposalNode(
        id="abc123",
        parent_id="parent01",
        task_type="code_generation",
        issue="timeout",
        category="skill_gap",
        proposal_text="Fix timeout in code gen",
        action_type="create_skill",
        mutation_type="repair",
        outcome="deployed",
        outcome_notes="Deployed successfully",
        tags=["tag1", "tag2"],
    )
    d = node.to_dict()
    restored = ProposalNode.from_dict(d)
    assert restored.id == node.id
    assert restored.parent_id == node.parent_id
    assert restored.task_type == node.task_type
    assert restored.issue == node.issue
    assert restored.category == node.category
    assert restored.proposal_text == node.proposal_text
    assert restored.action_type == node.action_type
    assert restored.mutation_type == node.mutation_type
    assert restored.outcome == node.outcome
    assert restored.outcome_notes == node.outcome_notes
    assert restored.tags == node.tags


def test_proposal_node_from_dict_extra_fields():
    """Test 3: Extra fields in dict are silently ignored."""
    from lineage import ProposalNode
    d = {
        "id": "xyz789",
        "unknown_field": "should_be_ignored",
        "another_extra": 42,
        "outcome": "pending",
    }
    node = ProposalNode.from_dict(d)
    assert node.id == "xyz789"
    assert node.outcome == "pending"
    # Extra fields should not be present
    assert not hasattr(node, "unknown_field")


def test_lineage_store_append_and_load(lineage_store):
    """Test 4: Append 3 nodes, load_all returns all 3 in order."""
    from lineage import ProposalNode
    nodes = [
        ProposalNode(id="n1", issue="timeout"),
        ProposalNode(id="n2", issue="context_loss"),
        ProposalNode(id="n3", issue="tool_error"),
    ]
    for n in nodes:
        lineage_store.append(n)

    loaded = lineage_store.load_all()
    assert len(loaded) == 3
    assert loaded[0].id == "n1"
    assert loaded[1].id == "n2"
    assert loaded[2].id == "n3"


def test_lineage_store_empty(tmp_path):
    """Test 5: load_all on non-existent file returns []."""
    from lineage import LineageStore
    store = LineageStore(path=tmp_path / "nonexistent.jsonl")
    assert store.load_all() == []


def test_lineage_store_get_node(lineage_store):
    """Test 6: get_node returns correct node or None."""
    from lineage import ProposalNode
    lineage_store.append(ProposalNode(id="found_node", issue="rate_limit"))
    lineage_store.append(ProposalNode(id="other_node", issue="timeout"))

    result = lineage_store.get_node("found_node")
    assert result is not None
    assert result.id == "found_node"
    assert result.issue == "rate_limit"

    missing = lineage_store.get_node("nonexistent")
    assert missing is None


def test_lineage_store_get_ancestors(lineage_store):
    """Test 7: Chain of 4 nodes, get_ancestors returns [parent, grandparent, great-grandparent]."""
    from lineage import ProposalNode
    # root → child → grandchild → great_grandchild
    lineage_store.append(ProposalNode(id="root", issue="timeout"))
    lineage_store.append(ProposalNode(id="child", parent_id="root", issue="timeout"))
    lineage_store.append(ProposalNode(id="grandchild", parent_id="child", issue="timeout"))
    lineage_store.append(ProposalNode(id="great_grandchild", parent_id="grandchild", issue="timeout"))

    ancestors = lineage_store.get_ancestors("great_grandchild")
    assert len(ancestors) == 3
    assert ancestors[0].id == "grandchild"
    assert ancestors[1].id == "child"
    assert ancestors[2].id == "root"


def test_lineage_store_get_ancestors_cycle_protection(lineage_store):
    """Test 8: Circular parent chain doesn't infinite loop."""
    from lineage import ProposalNode
    # Create a cycle: a → b → a
    lineage_store.append(ProposalNode(id="a", parent_id="b", issue="cycle"))
    lineage_store.append(ProposalNode(id="b", parent_id="a", issue="cycle"))

    # Should not raise or loop forever
    ancestors = lineage_store.get_ancestors("a")
    # Should be finite
    assert len(ancestors) <= 2


def test_lineage_store_get_descendants(lineage_store):
    """Test 9: Tree with branches, get_descendants returns all children in BFS order."""
    from lineage import ProposalNode
    # root → child1, child2
    # child1 → grandchild1
    lineage_store.append(ProposalNode(id="root", issue="timeout"))
    lineage_store.append(ProposalNode(id="child1", parent_id="root", issue="timeout"))
    lineage_store.append(ProposalNode(id="child2", parent_id="root", issue="timeout"))
    lineage_store.append(ProposalNode(id="grandchild1", parent_id="child1", issue="timeout"))

    descendants = lineage_store.get_descendants("root")
    desc_ids = [d.id for d in descendants]
    # BFS: child1 and child2 come before grandchild1
    assert set(desc_ids) == {"child1", "child2", "grandchild1"}
    # grandchild1 should come after both children
    gc1_idx = desc_ids.index("grandchild1")
    c1_idx = desc_ids.index("child1")
    assert gc1_idx > c1_idx


def test_lineage_store_get_lineage_tree(lineage_store):
    """Test 10: Returns correct adjacency list with __roots__."""
    from lineage import ProposalNode
    lineage_store.append(ProposalNode(id="root1", issue="timeout"))
    lineage_store.append(ProposalNode(id="root2", issue="context_loss"))
    lineage_store.append(ProposalNode(id="child1", parent_id="root1", issue="timeout"))

    tree = lineage_store.get_lineage_tree()
    assert "root1" in tree["__roots__"]
    assert "root2" in tree["__roots__"]
    assert "child1" in tree["root1"]


def test_lineage_store_update_outcome(lineage_store):
    """Test 11: Update outcome from pending to deployed, verify file rewritten."""
    from lineage import ProposalNode
    lineage_store.append(ProposalNode(id="target", issue="timeout", outcome="pending"))
    lineage_store.append(ProposalNode(id="other", issue="context_loss", outcome="pending"))

    found = lineage_store.update_outcome("target", "deployed", "Deployed successfully")
    assert found is True

    # Reload and verify
    nodes = lineage_store.load_all()
    target = next(n for n in nodes if n.id == "target")
    assert target.outcome == "deployed"
    assert target.outcome_notes == "Deployed successfully"
    assert target.outcome_timestamp is not None

    # Other node unchanged
    other = next(n for n in nodes if n.id == "other")
    assert other.outcome == "pending"


def test_lineage_store_update_outcome_not_found(lineage_store):
    """Test 12: Returns False for nonexistent node."""
    result = lineage_store.update_outcome("nonexistent_id", "deployed")
    assert result is False


def test_lineage_store_find_similar(lineage_store):
    """Test 13: Finds proposals matching issue, respects filters."""
    from lineage import ProposalNode
    lineage_store.append(ProposalNode(id="n1", issue="timeout", task_type="code_gen", category="skill_gap"))
    lineage_store.append(ProposalNode(id="n2", issue="timeout", task_type="code_gen", category="model_routing"))
    lineage_store.append(ProposalNode(id="n3", issue="timeout", task_type="message_routing", category="skill_gap"))
    lineage_store.append(ProposalNode(id="n4", issue="context_loss", task_type="code_gen", category="memory_continuity"))

    # By issue only
    result = lineage_store.find_similar(issue="timeout")
    assert len(result) == 3
    assert all(n.issue == "timeout" for n in result)

    # By issue + task_type
    result = lineage_store.find_similar(issue="timeout", task_type="code_gen")
    assert len(result) == 2
    ids = {n.id for n in result}
    assert ids == {"n1", "n2"}

    # By issue + task_type + category
    result = lineage_store.find_similar(issue="timeout", task_type="code_gen", category="skill_gap")
    assert len(result) == 1
    assert result[0].id == "n1"

    # No match
    result = lineage_store.find_similar(issue="nonexistent")
    assert result == []


# ---------------------------------------------------------------------------
# 4.2 Critique Tests
# ---------------------------------------------------------------------------

def test_critique_approve_no_history(critique_agent):
    """Test 14: New proposal with no prior history → approve."""
    proposal = {
        "id": "new_proposal",
        "pattern": {"issue": "brand_new_issue", "task_type": "new_task", "category": "skill_gap"},
        "action_type": "create_skill",
    }
    result = critique_agent.critique(proposal)
    assert result.verdict == "approve"
    assert result.similar_count == 0


def test_critique_reject_repeated_failures(critique_agent, lineage_store):
    """Test 15: 3+ rejected proposals with same action_type → reject."""
    from lineage import ProposalNode
    # Add 3 rejected proposals with same issue + action_type
    for i in range(3):
        lineage_store.append(ProposalNode(
            id=f"old_{i}",
            issue="rate_limit",
            task_type="api_call",
            category="model_routing",
            action_type="fix_routing",
            outcome="rejected",
        ))

    proposal = {
        "id": "new_proposal",
        "pattern": {"issue": "rate_limit", "task_type": "api_call", "category": "model_routing"},
        "action_type": "fix_routing",
    }
    result = critique_agent.critique(proposal)
    assert result.verdict == "reject"
    assert "fix_routing" in result.reason
    assert "3" in result.reason


def test_critique_reject_redundant_deployed(critique_agent, lineage_store):
    """Test 16: Proposal redundant with deployed fix → reject."""
    from lineage import ProposalNode
    lineage_store.append(ProposalNode(
        id="already_deployed",
        issue="context_loss",
        task_type="memory_task",
        category="memory_continuity",
        action_type="update_memory",
        outcome="deployed",
    ))

    proposal = {
        "id": "new_proposal",
        "pattern": {"issue": "context_loss", "task_type": "memory_task", "category": "memory_continuity"},
        "action_type": "update_memory",
    }
    result = critique_agent.critique(proposal)
    assert result.verdict == "reject"
    assert result.redundant_with == "already_deployed"
    assert "Redundant" in result.reason


def test_critique_defer_anti_pattern(critique_agent, kb_manager, lineage_store):
    """Test 17: KB has anti-pattern for this approach → defer."""
    from kb_manager import KBEntry
    # Add an anti-pattern entry to KB
    entry = KBEntry(
        id="",
        kind="anti",
        issue="tool_error",
        task_type="tool_call",
        category="behavior_pattern",
        title="Repeated failure: retry_logic for tool_error",
        description="This approach keeps failing.",
        fix="N/A",
        occurrences=3,
    )
    kb_manager.add_entry(entry)

    proposal = {
        "id": "new_proposal",
        "pattern": {"issue": "tool_error", "task_type": "tool_call", "category": "behavior_pattern"},
        "action_type": "retry_logic",
    }
    result = critique_agent.critique(proposal)
    assert result.verdict == "defer"
    assert "[ANTI]" in result.reason


def test_critique_defer_low_ancestor_success(critique_agent, lineage_store):
    """Test 18: Parent chain with <30% success rate → defer."""
    from lineage import ProposalNode
    # Create parent with poor track record (rejected ancestors)
    lineage_store.append(ProposalNode(id="grandparent", issue="skill_gap", outcome="rejected"))
    lineage_store.append(ProposalNode(id="parent", parent_id="grandparent", issue="skill_gap", outcome="rejected"))

    proposal = {
        "id": "new_proposal",
        "parent_id": "parent",
        "pattern": {"issue": "new_issue", "task_type": "new_task", "category": "skill_gap"},
        "action_type": "create_skill",
    }
    result = critique_agent.critique(proposal)
    assert result.verdict == "defer"
    assert "success rate" in result.reason.lower() or "ancestor" in result.reason.lower()


def test_critique_approve_with_enrichment(critique_agent, lineage_store):
    """Test 19: Approve with note about prior similar proposals."""
    from lineage import ProposalNode
    # Add one similar deployed proposal (different action_type, so no redundancy)
    lineage_store.append(ProposalNode(
        id="prior",
        issue="slow_response",
        task_type="code_gen",
        category="model_routing",
        action_type="fix_routing",
        outcome="deployed",
    ))

    # New proposal with different action_type
    proposal = {
        "id": "new_proposal",
        "pattern": {"issue": "slow_response", "task_type": "code_gen", "category": "model_routing"},
        "action_type": "threshold_tuning",  # different action_type, not redundant
    }
    result = critique_agent.critique(proposal)
    assert result.verdict == "approve"
    assert result.similar_count >= 1
    # Should mention prior proposals
    assert "similar" in result.reason.lower() or "prior" in result.reason.lower()


def test_critique_excludes_self(critique_agent, lineage_store):
    """Test 20: Proposal's own ID in lineage is excluded from similar check."""
    from lineage import ProposalNode
    # Simulate the proposal being already in lineage (pending)
    lineage_store.append(ProposalNode(
        id="self_proposal",
        issue="timeout",
        task_type="task",
        category="cat",
        action_type="create_skill",
        outcome="pending",
    ))

    proposal = {
        "id": "self_proposal",
        "pattern": {"issue": "timeout", "task_type": "task", "category": "cat"},
        "action_type": "create_skill",
    }
    result = critique_agent.critique(proposal)
    # Should not count itself as a similar proposal
    assert result.similar_count == 0


# ---------------------------------------------------------------------------
# 4.3 Knowledge Base Tests
# ---------------------------------------------------------------------------

def test_kb_manager_creates_files(tmp_path):
    """Test 21: Instantiation creates all 3 KB files with headers."""
    from kb_manager import KBManager
    kb = KBManager(kb_dir=tmp_path / "kb")
    assert (tmp_path / "kb" / "failure-patterns.md").exists()
    assert (tmp_path / "kb" / "success-patterns.md").exists()
    assert (tmp_path / "kb" / "anti-patterns.md").exists()

    # Verify headers
    content = (tmp_path / "kb" / "failure-patterns.md").read_text()
    assert "# Failure Patterns" in content


def test_kb_add_and_parse_entry(kb_manager):
    """Test 22: Add entry, parse it back, verify fields match."""
    from kb_manager import KBEntry
    entry = KBEntry(
        id="",
        kind="failure",
        issue="rate_limit",
        task_type="api_call",
        category="model_routing",
        title="Rate limit in API calls",
        description="API calls hit rate limits frequently.",
        fix="Use exponential backoff",
        lineage_refs=["p001", "p002"],
        occurrences=5,
    )
    assigned_id = kb_manager.add_entry(entry)
    assert assigned_id.startswith("FP-")

    # Parse back
    entries = kb_manager._parse_entries(kb_manager._get_filepath("failure"))
    assert len(entries) == 1
    e = entries[0]
    assert e.id == assigned_id
    assert e.issue == "rate_limit"
    assert e.task_type == "api_call"
    assert e.occurrences == 5
    assert "p001" in e.lineage_refs


def test_kb_query_by_issue(kb_manager):
    """Test 23: Query returns entries matching issue, sorted by score."""
    from kb_manager import KBEntry
    # Add entries
    kb_manager.add_entry(KBEntry(
        id="", kind="failure", issue="rate_limit", task_type="api_call",
        category="model_routing", title="Rate limit issue",
        description="", occurrences=5,
    ))
    kb_manager.add_entry(KBEntry(
        id="", kind="success", issue="timeout", task_type="code_gen",
        category="skill_gap", title="Timeout fix",
        description="", occurrences=2,
    ))

    results = kb_manager.query(issue="rate_limit")
    assert len(results) > 0
    assert results[0]["reference"].startswith("[FAIL]")
    assert "Rate limit issue" in results[0]["reference"]


def test_kb_query_empty(kb_manager):
    """Test 24: Query with no matches returns []."""
    results = kb_manager.query(issue="completely_nonexistent_issue")
    assert results == []


def test_kb_update_entry(kb_manager):
    """Test 25: Update occurrences and lineage_refs, verify persistence."""
    from kb_manager import KBEntry
    entry = KBEntry(
        id="", kind="success", issue="context_loss",
        task_type="*", category="memory_continuity",
        title="Fix context loss", description="", occurrences=1,
        lineage_refs=["old_ref"],
    )
    entry_id = kb_manager.add_entry(entry)

    # Update
    updated = kb_manager.update_entry(entry_id, {
        "occurrences": 5,
        "lineage_refs": ["new_ref1", "new_ref2"],
    })
    assert updated is True

    # Verify
    entries = kb_manager._parse_entries(kb_manager._get_filepath("success"))
    e = next((e for e in entries if e.id == entry_id), None)
    assert e is not None
    assert e.occurrences == 5
    assert "old_ref" in e.lineage_refs
    assert "new_ref1" in e.lineage_refs
    assert "new_ref2" in e.lineage_refs


def test_kb_update_from_lineage_success_pattern(kb_manager, lineage_store):
    """Test 26: Deployed proposal creates success pattern entry."""
    from lineage import ProposalNode
    lineage_store.append(ProposalNode(
        id="deployed_prop",
        issue="tool_error",
        task_type="tool_call",
        category="behavior_pattern",
        action_type="update_soul",
        outcome="deployed",
        outcome_notes="Fixed by updating SOUL.md",
        proposal_text="Fix tool_error in tool_call",
    ))

    stats = kb_manager.update_from_lineage(lineage_store)
    assert stats["added"] == 1
    assert stats["updated"] == 0

    entries = kb_manager._parse_entries(kb_manager._get_filepath("success"))
    assert len(entries) == 1
    e = entries[0]
    assert e.issue == "tool_error"
    assert "deployed_prop" in e.lineage_refs


def test_kb_update_from_lineage_anti_pattern(kb_manager, lineage_store):
    """Test 27: 3+ rejected proposals creates anti-pattern entry."""
    from lineage import ProposalNode
    for i in range(3):
        lineage_store.append(ProposalNode(
            id=f"rejected_{i}",
            issue="rate_limit",
            task_type="api_call",
            category="model_routing",
            action_type="fix_routing",
            outcome="rejected",
            outcome_notes="Did not work",
        ))

    stats = kb_manager.update_from_lineage(lineage_store)
    assert stats["added"] == 1  # anti-pattern added

    entries = kb_manager._parse_entries(kb_manager._get_filepath("anti"))
    assert len(entries) == 1
    e = entries[0]
    assert e.issue == "rate_limit"
    assert e.occurrences == 3


def test_kb_update_from_lineage_idempotent(kb_manager, lineage_store):
    """Test 28: Running update twice doesn't create duplicate entries."""
    from lineage import ProposalNode
    lineage_store.append(ProposalNode(
        id="deployed_prop",
        issue="context_loss",
        task_type="*",
        category="memory_continuity",
        action_type="update_memory",
        outcome="deployed",
        proposal_text="Fix context loss",
    ))

    stats1 = kb_manager.update_from_lineage(lineage_store)
    assert stats1["added"] == 1

    stats2 = kb_manager.update_from_lineage(lineage_store)
    # Second run should update, not add
    assert stats2["added"] == 0
    assert stats2["updated"] == 1

    # Only 1 entry in total
    entries = kb_manager._parse_entries(kb_manager._get_filepath("success"))
    assert len(entries) == 1


def test_kb_next_id_sequential(kb_manager):
    """Test 29: IDs are assigned sequentially (FP-001, FP-002, ...)."""
    from kb_manager import KBEntry
    for i in range(3):
        entry = KBEntry(
            id="", kind="failure",
            issue=f"issue_{i}", task_type="*", category="",
            title=f"Entry {i}", description="",
        )
        assigned_id = kb_manager.add_entry(entry)
        expected = f"FP-{i + 1:03d}"
        assert assigned_id == expected, f"Expected {expected}, got {assigned_id}"


def test_kb_query_cli_returns_clean_dicts(kb_manager, monkeypatch):
    """Test 30: CLI wrapper returns dicts without KBEntry objects."""
    from kb_manager import KBEntry
    import kb_manager as kbm

    # Ensure KB has an entry
    kb_manager.add_entry(KBEntry(
        id="", kind="failure", issue="test_issue",
        task_type="test_task", category="test_cat",
        title="Test entry", description="", occurrences=1,
    ))

    # Patch default KBManager to use our test instance
    monkeypatch.setattr(kbm, "KBManager", lambda: kb_manager)

    results = kbm.kb_query_cli(issue="test_issue")
    assert len(results) > 0
    for r in results:
        assert "reference" in r
        assert "score" in r
        assert "entry" not in r  # KBEntry objects should be stripped


# ---------------------------------------------------------------------------
# 4.4 Integration Tests
# ---------------------------------------------------------------------------

def test_full_cycle_with_critique(lineage_store, kb_manager):
    """Test 31: Simulate critique gate — only approved proposals are deployed."""
    from critique import CritiqueAgent
    from lineage import ProposalNode

    # Pre-populate: 3 rejections for fix_routing on rate_limit
    for i in range(3):
        lineage_store.append(ProposalNode(
            id=f"old_{i}",
            issue="rate_limit",
            task_type="api_call",
            category="model_routing",
            action_type="fix_routing",
            outcome="rejected",
        ))

    agent = CritiqueAgent(lineage_store=lineage_store, kb_path=kb_manager.kb_dir)

    proposals = [
        {
            "id": "good_proposal",
            "pattern": {"issue": "context_loss", "task_type": "memory", "category": "memory_continuity"},
            "action_type": "update_memory",
        },
        {
            "id": "bad_proposal",
            "pattern": {"issue": "rate_limit", "task_type": "api_call", "category": "model_routing"},
            "action_type": "fix_routing",  # rejected 3x before
        },
    ]

    approved = []
    for p in proposals:
        result = agent.critique(p)
        if result.verdict == "approve":
            approved.append(p)

    # Only good_proposal should be approved
    assert len(approved) == 1
    assert approved[0]["id"] == "good_proposal"


def test_lineage_parent_assignment(tmp_path):
    """Test 32: Parent_id is set when prior deployed proposal exists for same issue."""
    from lineage import LineageStore, ProposalNode

    store = LineageStore(path=tmp_path / "lineage.jsonl")

    # Simulate a prior deployed proposal for "timeout" in "code_gen"
    prior = ProposalNode(
        id="prior_proposal",
        issue="timeout",
        task_type="code_gen",
        category="skill_gap",
        action_type="create_skill",
        outcome="deployed",
    )
    store.append(prior)

    # Now simulate synthesizer logic for new proposal targeting same issue
    issue = "timeout"
    task_type = "code_gen"
    similar = store.find_similar(issue=issue, task_type=task_type)
    parent_id = None
    for s in reversed(similar):
        if s.outcome == "deployed":
            parent_id = s.id
            break

    assert parent_id == "prior_proposal"


def test_deploy_updates_lineage(tmp_path):
    """Test 33: Deploying a proposal updates lineage node outcome to 'deployed'."""
    from lineage import LineageStore, ProposalNode

    store = LineageStore(path=tmp_path / "lineage.jsonl")

    # Add a pending node
    store.append(ProposalNode(id="test_prop", issue="tool_error", outcome="pending"))

    # Simulate deploy outcome update
    found = store.update_outcome("test_prop", "deployed", "Deployed via create_skill")
    assert found is True

    # Verify
    node = store.get_node("test_prop")
    assert node is not None
    assert node.outcome == "deployed"
    assert node.outcome_notes == "Deployed via create_skill"
