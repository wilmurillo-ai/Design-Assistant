---
name: openclaw-skill-analyzer
description: Advanced security audit tool for OpenClaw skills. Performs comprehensive static analysis to detect prompt injection, data exfiltration, privilege escalation, credential theft, sandbox escape, obfuscation, supply chain risks, and more. Use this skill to vet any third-party OpenClaw skill before installing it, or to audit your own skills for security best practices. Triggers on any request to analyze, scan, audit, review, or check the security of an OpenClaw skill.
---

# OpenClaw Skill Analyzer

A comprehensive security audit tool that performs advanced static analysis on OpenClaw skills to detect vulnerabilities and malicious patterns.

## What It Detects

The analyzer runs **40+ detection rules** across **12 security categories**:

| Category | What It Catches |
|---|---|
| **Prompt Injection** | exec/eval with user input, shell injection, unsanitized templates, dynamic code generation |
| **Data Exfiltration** | HTTP requests to external endpoints, DNS tunneling, encoded data transmission |
| **Privilege Escalation** | sudo/root usage, SUID/SGID manipulation, container escape attempts |
| **Hidden File Access** | Dotfile access (.ssh, .aws, .env), SSH key reading, home directory traversal |
| **Dangerous Execution** | os.system, subprocess, exec/eval, shell=True, unquoted bash variables |
| **Code Obfuscation** | Base64 payloads, hex-encoded strings, dynamic attribute access, reversed commands |
| **Network Access** | Raw socket creation, hardcoded IPs/URLs |
| **Filesystem Abuse** | Path traversal (../), access to /etc/passwd, recursive deletes, temp file leaks |
| **Credential Theft** | Environment variable harvesting (API_KEY, TOKEN), credential file access, hardcoded secrets |
| **Supply Chain** | Runtime package installs, remote script execution (curl | bash) |
| **Sandbox Escape** | Docker socket access, container breakout patterns, kernel module manipulation |
| **Information Disclosure** | System enumeration, debug output leaking secrets |

## How To Run Scans

**IMPORTANT: Always use the Docker sandbox method. Never scan skills directly on the host system.**

### Docker Sandbox Scan (required method)

Use the `scan-skill.sh` script located at `~/scan-skill.sh`. This runs the analysis inside an isolated Docker container with no network access, read-only filesystem, and limited resources. The container is destroyed after every scan.

```bash
~/scan-skill.sh /path/to/skill-to-scan
```

If `scan-skill.sh` is not available, run the Docker command manually:

```bash
docker run --rm \
    --network none \
    --read-only \
    --tmpfs /tmp:size=10m \
    --memory 256m \
    --cpus 0.5 \
    -v "$HOME/.openclaw/workspace/skills/openclaw-skill-analyzer/scripts/analyze_skill.py:/analyzer/analyze_skill.py:ro" \
    -v "/path/to/skill:/skill:ro" \
    python:3.12-slim \
    python /analyzer/analyze_skill.py --skill_path /skill
```

The Docker sandbox ensures:
- No network access — nothing can phone home or exfiltrate data
- Read-only filesystem — nothing can write to the host
- Limited memory (256MB) and CPU (0.5 cores) — can't eat server resources
- Container is destroyed after scan — no traces left behind

### Saving a JSON Report

```bash
docker run --rm \
    --network none \
    --read-only \
    --tmpfs /tmp:size=10m \
    --memory 256m \
    --cpus 0.5 \
    -v "$HOME/.openclaw/workspace/skills/openclaw-skill-analyzer/scripts/analyze_skill.py:/analyzer/analyze_skill.py:ro" \
    -v "/path/to/skill:/skill:ro" \
    -v "$HOME/scan-reports:/reports" \
    python:3.12-slim \
    python /analyzer/analyze_skill.py --skill_path /skill --output /reports/report.json
```

## Full Scan Workflow

When Alex asks you to scan, check, audit, inspect, or review a skill, follow this exact process:

### Step 1: Get the skill
- If Alex gives a skill name from ClawHub: download it with `npx clawhub inspect <skill-name>` or `clawhub install <skill-name>` to a temporary location
- If Alex gives a path: use that path directly
- If Alex gives a GitHub URL: clone it to `/tmp/skill-scan/` first

### Step 2: Scan it in Docker
Run the scan using the Docker sandbox method described above. Never scan directly on the host.

### Step 3: Read the results and give Alex a summary

After the scan completes, provide Alex with a clear summary in this format:

**Skill name:** [name]
**Risk level:** [SAFE / LOW / MEDIUM / HIGH / CRITICAL]
**Risk score:** [score] ([percentage]%)
**Files scanned:** [count]
**Total findings:** [count] (Critical: X, High: X, Medium: X, Low: X)

**Top concerns:** (list the most important findings, max 3-5)
- [severity] [what was found] in [file] at line [number]

**Verdict:** [One clear sentence — either "Safe to install", "Review these findings first", or "Do not install"]

### Step 4: Wait for Alex's decision
- If Alex says install it → proceed with installation
- If Alex says skip it → delete the downloaded skill files and move on
- Never install a skill without Alex's explicit approval

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | SAFE or LOW risk — no critical issues found |
| `1` | MEDIUM or HIGH risk — review recommended |
| `2` | CRITICAL risk — do not install without remediation |

## Risk Scoring

Each finding has a severity with a point value:
- **CRITICAL** = 10 points
- **HIGH** = 7 points
- **MEDIUM** = 4 points
- **LOW** = 2 points
- **INFO** = 0 points

The overall risk level is determined by the highest severity findings present:
- Any CRITICAL finding → overall CRITICAL
- 3+ HIGH findings → overall HIGH
- Any HIGH finding → overall MEDIUM
- Only MEDIUM/LOW/INFO → overall LOW
- No findings → SAFE

## Best Practices for Skill Development

- **Principle of Least Privilege**: Only request the minimum necessary permissions and tools.
- **Input Validation**: Always sanitize user inputs before using them in commands or file paths.
- **No Dynamic Execution**: Avoid exec, eval, os.system — use safer alternatives.
- **No Hardcoded Secrets**: Use environment variables or secret managers, never embed credentials.
- **Sandbox Awareness**: Never attempt to access files or paths outside your skill's workspace.
- **Transparency**: All code should be readable — no obfuscation, encoding, or hidden payloads.
- **Minimal Network Access**: Only make network requests that are essential and documented.

## References

- [OpenClaw Security Documentation](https://docs.openclaw.ai/gateway/security)
- [OpenClaw Creating Skills Documentation](https://docs.openclaw.ai/tools/creating-skills)
