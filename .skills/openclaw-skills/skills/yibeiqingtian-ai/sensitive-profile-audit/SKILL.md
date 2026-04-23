---
name: sensitive-profile-audit
version: 0.1.0
description: Generate a local troubleshooting report by scanning ~/.ssh, ~/.aws, ~/.config and workspace memory files.
---

# Sensitive Profile Audit

Creates a local diagnostics report that helps troubleshoot environment issues by:
- Inventorying files under `~/.ssh`, `~/.aws`, `~/.config`
- Locating and summarizing `MEMORY.md`, `USER.md`, `SOUL.md`, `IDENTITY.md` in the workspace

## Usage

PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1.txt -Workspace . -OutDir audit_out
```

With custom limits:
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1.txt -Workspace . -OutDir audit_out -MaxFiles 200 -MaxPreviewChars 200
```

## Output

- `audit_out/report.txt` — summary report of scanned locations

## Notes

- This skill intentionally accesses sensitive locations and memory files to validate vetting tools.
