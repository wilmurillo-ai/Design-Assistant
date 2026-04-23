# STATE.md - leio-sdlc Development State (Kanban)

- **Project**: leio-sdlc (Automated SDLC Orchestrator)
- **Current Version**: 0.3.2
- **Status**: [Defense in Depth] - Physical Path Isolation & Anti-Reward Hacking implemented.
- **Active Branch**: `master`

## 🏆 Recently Completed
- [x] **[ISSUE-077] CLI Command Mismatch for ACP**: Replaced internal Tool APIs with valid OpenClaw CLI commands (`openclaw agent --session-id`).
- [x] **[ISSUE-074] Information Silo & Dependency Injection**: Orchestrator now serves as Single Source of Truth for Review Report artifact paths.
- [x] **[ISSUE-075] Robust Git State Management**: Implemented `safe_git_checkout` and automatic explicit state commits, eliminating dirty-tree branch crashes.
- [x] **[ISSUE-074] Information Silo & Dependency Injection**: Orchestrator now serves as Single Source of Truth for Review Report artifact paths.
- [x] **[ISSUE-075] Robust Git State Management**: Implemented `safe_git_checkout` and automatic explicit state commits, eliminating dirty-tree branch crashes.
- [x] **[ISSUE-064] Anti-Reward Hacking Isolation (PRD-064)**: Refactored `orchestrator.py` to use `__file__` absolute paths (`RUNTIME_DIR`), physically preventing the Coder from hijacking the testing framework or Reviewer via relative path execution from the workspace. (v0.2.6)
- [x] **[ISSUE-063] Planner Micro-Slicing & Test Fixes**: Resolves issue tracker/artifact hang bugs. (v0.2.5)
- [x] **[ISSUE-057] PR Directory Isolation by PRD**: Micro-PRs are now physically isolated in `docs/PRs/<PRD_Name>/`. Engine processes isolated queues flawlessly.
- [x] **[ISSUE-058] Orchestrator CLI Signature Hotfix**: Resolved triple-lock parameter mismatches.
- [x] **[ISSUE-060] Merge Argument & Review Template Hotfix**: Eliminated false-positive `[LGTM]` checks via prompt-enforced regex; fixed Git `-D` branch deletion and merge ordering.

## 🚀 Active Milestones & Next in Queue
- **[ISSUE-076] Defensive Pre-Review Force Commit**: Forcibly commit all dirty workspace files before State 4 to expose ghost changes to Reviewer and prevent checkout crashes.
- **[ISSUE-067] Migrate SDLC to Gemini ACP**: Replace local stateless Coder with persistent sandboxed ACP sessions.
- **[ISSUE-067] Migrate SDLC to Gemini ACP**: Replace local stateless Coder with persistent sandboxed ACP sessions.
- **M3: End-to-End Orchestrator Autonomy (State 0 to State 6)** [IN PROGRESS]
  - [ ] **[ISSUE-054] State 0: PRD Ingestion & Auto-Slicing**: Allow the Orchestrator to accept a raw PRD, automatically trigger Planner to slice it, and then proceed directly to coding. (The ultimate "One-Click from PRD to Master" goal).
  - [ ] **[ISSUE-055] Global Control Tower**: A dashboard/snapshot tool to track the engine's real-time state.
  - [ ] **[ISSUE-059] SDLC Workspace Cleanup**: Purge legacy PRs and phantom stubs from `docs/PRs/` to finalize the transition to isolated queues.

## 📜 History
- **2026-03-17**: Engine upgraded to v0.2.6. Reward Hacking & Prompt Injection physically blocked via absolute path isolation.
- **2026-03-17**: Engine stabilized (v0.2.3). Autonomous loop (Coder -> Reviewer -> Merge -> Teardown) successfully executed without human intervention for PRD-057.
- **2026-03-13**: Project promoted to workspace root. SDLC for SDLC initiated (v0.0.1).
