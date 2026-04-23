status: open

# PR-001: Implement Git Force Commit Utility Function

## 1. Objective
Implement an isolated, reusable utility function `force_commit_untracked()` to safely add and commit untracked files without crashing if no changes exist.

## 2. Scope & Implementation Details
- **File:** `scripts/orchestrator.py`
- **Logic:** Add a standalone function `force_commit_untracked()` that runs `git add .` and `git commit -m "chore(auto): force commit uncommitted changes before review"` using `subprocess.run(..., check=False)`. It should not yet be hooked into the state machine.

## 3. TDD & Acceptance Criteria
- **File:** `tests/test_076_git_utility.py`
- **Test:** Create a test that initializes a temp git repo, creates a dummy file, calls `force_commit_untracked()`, and asserts that `git status` is clean and the "chore(auto)" commit exists.
