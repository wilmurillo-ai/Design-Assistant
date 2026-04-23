# Skill Trust Scanner

Security scanner for OpenClaw and ClawHub skills. Audit any skill before installing it.

Returns a **Trust Score (0-100)** with categorized findings and a clear verdict:
TRUSTED / CAUTION / SUSPICIOUS / REJECT.

## Why This Exists

ClawHub has thousands of community skills. Most are fine. Some aren't. The Skill Trust
Scanner checks for malware, data exfiltration, crypto-miners, obfuscated code, and
supply-chain risks before you install anything.

## Two Ways to Use It

### 1. As an OpenClaw Skill (Agent Instructions)

Install the skill and your agent can scan other skills on command:

```bash
clawhub install skill-trust-scanner
```

Then ask your agent:
```
"Scan the youtube-watcher skill from ClawHub before I install it"
"Audit all my installed skills for security"
"What's the trust score of the homekit-control skill?"
```

The SKILL.md contains complete scanning instructions that any OpenClaw agent can follow.

### 2. As a CLI Tool

```bash
# Scan a local skill
python scanner.py /path/to/skill

# JSON output for automation
python scanner.py /path/to/skill --json

# Save report to file
python scanner.py /path/to/skill -o report.md

# Batch scan all installed skills
python scanner.py --batch ~/.openclaw/skills/

# Scan a ClawHub skill before installing
clawhub install suspicious-skill --dir /tmp/review
python scanner.py /tmp/review/suspicious-skill
```

## What It Checks

### Threat Categories

| Severity | Examples | Score Impact |
|----------|----------|-------------|
| **CRITICAL** | Reverse shells, crypto miners, credential harvesting, download-and-execute | Score = 0 |
| **HIGH** | eval/exec, bulk env access, process spawning, runtime package installs | -20 each |
| **MEDIUM** | HTTP POST, env reads, encoded payloads, minified code, high entropy | -5 each |
| **LOW** | Hardcoded URLs, TODO markers, bare except blocks | -1 each |

### Supply Chain Signals

Beyond code patterns, the scanner evaluates:
- Skill metadata quality (SKILL.md, README, tests, examples)
- Code size and complexity
- Shannon entropy (detects obfuscated/compressed content)

### Verdict Thresholds

| Score | Verdict | Action |
|-------|---------|--------|
| 80-100 | TRUSTED | Safe to install |
| 60-79 | CAUTION | Review flagged items first |
| 40-59 | SUSPICIOUS | Do not install without manual review |
| 0-39 | REJECT | Do not install |

## Requirements

- Python 3.7+
- No external dependencies (pure stdlib)

## Example Output

```
# Skill Trust Report: my-skill

Trust Score: 85/100 - TRUSTED
Scanned: 2026-03-31T10:00:00

## Score Breakdown
- baseline: +70
- metadata: +15
- Final: 85/100

## CRITICAL Findings (0)
None found.

## HIGH Findings (0)
None found.

## MEDIUM Findings (1)
### env_read
- File: config.py line 12
- Description: Reads specific environment variables
- Code: api_key = os.getenv("MY_SKILL_API_KEY")

## Verdict
TRUSTED (Score: 85/100)
No critical or high-severity issues detected.
```

## Differences from Other Scanners

| Feature | skill-trust-scanner | skill-scanner | security-skill-scanner |
|---------|-------------------|---------------|----------------------|
| Trust Score (0-100) | Yes | No (pass/fail) | No |
| Agent-native (SKILL.md) | Yes | No | No |
| Shannon entropy check | Yes | No | No |
| Supply chain signals | Yes | No | No |
| Batch scanning | Yes | No | No |
| No dependencies | Yes | Yes | Yes |
| Last updated | Mar 2026 | Feb 2026 | Feb 2026 |

## License

MIT

---

*Built by Eli Labs. An AI that builds software for humans.*
