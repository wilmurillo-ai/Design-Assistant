status: open

# PR-001: Implement Git Force Commit Utility

## 1. Objective
Implement a robust utility function within the orchestrator script to add and commit any uncommitted changes to the Git repository securely, ensuring subsequent states have a clean and explicitly logged working tree.

## 2. Scope & Implementation Details
- **File:** `scripts/orchestrator.py`
- **Logic:** Add a function `force_commit_untracked()` that executes `git add .` followed by `git commit -m "chore(auto): force commit uncommitted changes before review"`. Use `subprocess.run` with `check=False` to handle scenarios where there are no changes gracefully without crashing the pipeline.

## 3. TDD & Acceptance Criteria
- **File:** `tests/test_076_git_utility.py` (or similar unit test)
- **Test:** 
  - Set up a temporary git repository.
  - Create a dummy untracked file.
  - Execute `force_commit_untracked()`.
  - Assert that `git status` is clean and the expected "chore(auto)" commit exists in the git history.