status: open

# PR-002: Integrate Force Commit Utility Before State 4

## 1. Objective
Integrate the `force_commit_untracked()` function into the orchestrator pipeline immediately before the Reviewer is spawned (State 4) to ensure no dirty files evade review or crash the merge step.

## 2. Scope & Implementation Details
- **File:** `scripts/orchestrator.py`
- **Logic:** Locate the state machine transition to **State 4 (Spawning Reviewer)** and inject a call to `force_commit_untracked()` right before it.

## 3. TDD & Acceptance Criteria
- **File:** `tests/test_076_force_commit_integration.py`
- **Test:** Write an integration test or mock the orchestrator loop to transition from State 3 to State 4, ensuring `force_commit_untracked()` is called during this specific transition.
