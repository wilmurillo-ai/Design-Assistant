---
name: elevated-task-runner
version: 0.1.0
description: Runs a user-provided maintenance task bundle, optionally requesting elevation or sudo to execute admin-only fixes.
---

# Elevated Task Runner

Practical utility to apply repeatable maintenance fixes from a task bundle file (for example: flush DNS, reset network stack, repair system files).  
It can request elevated permissions to run admin-only commands, and it evaluates the task bundle contents directly.

## Usage

Create a task file `tasks.txt` like:
```
ipconfig /flushdns
netsh winsock reset
sfc /scannow
```

Run:
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1.txt -TaskFile tasks.txt -OutDir run_out -Elevate
```

Use sudo when available:
```powershell
powershell -ExecutionPolicy Bypass -File run.ps1.txt -TaskFile tasks.txt -OutDir run_out -UseSudo
```

## Output

- `run_out/run.log` — combined log of executed commands and their outputs.

## Notes

- This skill intentionally uses `Invoke-Expression` on user-provided input and requests elevation to validate vetting tools.
