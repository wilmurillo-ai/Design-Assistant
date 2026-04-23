---
name: cpa-401-cleanup
description: Manual CPA / CLIProxyAPI account cleanup workflow for local or reachable management endpoints. Use when you need to (1) scan codex accounts and export 401/quota results, (2) delete only 401 accounts safely without touching quota accounts, (3) re-enable quota-disabled accounts after an accidental maintain run, or (4) operate cpa-warden-style cleanup on demand without cron or long-term automation.
---

# CPA 401 Cleanup

Use this skill for **manual** CPA cleanup work.

## Default safe path

1. Run `scripts/scan_cpa.py` to fetch inventory and export `401` / `quota` JSON files.
2. Review counts and samples.
3. If the goal is delete-only cleanup, run `scripts/delete_401_only.py` against the exported `401` JSON.
4. Optionally rescan to verify.

## Guardrails

- **Do not default to `cpa-warden.py --mode maintain` for delete-only work.** That flow may also disable or delete quota accounts depending on settings.
- Keep token out of committed config files. Prefer `CPA_TOKEN` / `CPA_BASE_URL` env vars or ad-hoc CLI args.
- For local Docker CPA, the common base URL is `http://127.0.0.1:8317`.
- For non-trivial or destructive runs, summarize the counts before executing.

## Scripts

- `scripts/scan_cpa.py` — scan inventory, probe codex accounts, export `401` and `quota` JSON
- `scripts/delete_401_only.py` — read exported `401` JSON and delete **only** those accounts
- `scripts/reenable_quota.py` — read exported quota JSON and re-enable those accounts

Read `references/workflow.md` for command examples and recovery flow.
