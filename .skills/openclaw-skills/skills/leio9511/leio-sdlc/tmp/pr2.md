status: open

# PR-002: Integrate Force Commit Before Reviewer State

## 1. Objective
Integrate the previously built `force_commit_untracked` utility into the orchestrator's state machine, executing it immediately before spawning the Reviewer (transitioning to State 4), thereby preventing pipeline crashes on `git checkout` due to dirty working trees.

## 2. Scope & Implementation Details
- **File:** `scripts/orchestrator.py`
- **Logic:** Locate the transition logic from State 3 (Coder) to State 4 (Reviewer). Inject a call to `force_commit_untracked()` immediately before the Reviewer agent is spawned.

## 3. TDD & Acceptance Criteria
- **File:** `tests/test_076_force_commit.sh`
- **Test:** 
  - Write an integration test that runs the orchestrator.
  - Simulate the Coder state leaving behind an untracked dirty file (e.g., a dummy comment or leftover artifact).
  - Assert that the orchestrator successfully commits this file with the message "chore(auto): force commit uncommitted changes before review" *before* entering State 4.
  - Verify the pipeline reaches State 4 without raising a git checkout error.