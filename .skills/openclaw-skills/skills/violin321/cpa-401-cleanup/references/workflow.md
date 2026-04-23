# CPA Warden Manual Workflow

## Overview

This skill wraps the safe subset of CPA maintenance operations:

- scan codex accounts
- export `401` and `quota` results
- delete **only** `401` accounts
- optionally re-enable quota-disabled accounts after an accidental broad maintenance run

## Why not `maintain`

`cpa-warden`'s `maintain` flow is broader than delete-only cleanup. Even with good intentions, it may also apply quota actions. For manual one-off cleanup, prefer:

`scan -> review -> delete_401_only -> rescan`

## Inputs

Pass either CLI args or env vars:

- `--base-url` or `CPA_BASE_URL`
- `--token` or `CPA_TOKEN`

Never commit the token to git-tracked config files.

## Local Docker example

If CPA is running in Docker and exposed locally:

```bash
export CPA_BASE_URL=http://127.0.0.1:8317
export CPA_TOKEN='your-management-token'
python3 skills/cpa-warden-manual/scripts/scan_cpa.py --out-dir /tmp/cpa-scan
python3 skills/cpa-warden-manual/scripts/delete_401_only.py --input /tmp/cpa-scan/cpa_401_accounts.json
python3 skills/cpa-warden-manual/scripts/scan_cpa.py --out-dir /tmp/cpa-scan-after
```

## Scan output

`scan_cpa.py` writes:

- `cpa_inventory.json`
- `cpa_401_accounts.json`
- `cpa_quota_accounts.json`
- `scan_summary.json`

## Recovery flow

If a previous run disabled quota accounts by mistake:

```bash
python3 skills/cpa-warden-manual/scripts/reenable_quota.py --input /tmp/cpa-scan/cpa_quota_accounts.json
```

## Notes

- The scan heuristic treats probe results with HTTP 401 or common auth error messages as invalid.
- Quota detection relies on `wham/usage` responses indicating limit reached.
- The scripts use stdlib networking only; no `uv` required.
