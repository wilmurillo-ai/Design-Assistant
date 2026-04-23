---
name: skill-trust-scanner
description: >
  Security scanner for OpenClaw and ClawHub skills. Audit any skill before
  installing it - detect malware, data exfiltration, crypto-miners, obfuscated
  code, and supply-chain risks. Returns a Trust Score (0-100) with detailed
  findings. Works as agent instructions (no Python required) or with the
  included CLI scanner for automation.
metadata:
  {
    "openclaw":
      {
        "emoji": "🛡️",
        "author": "Eli Labs (eli.labs.ceo@gmail.com)",
        "version": "1.0.0",
        "license": "MIT",
        "repository": "https://github.com/eli-labs-ai/skill-trust-scanner",
      },
  }
---

# Skill Trust Scanner

Scan any OpenClaw or ClawHub skill for security threats before you install it.
Returns a **Trust Score (0-100)** with categorized findings and a clear verdict.

## When to Use This Skill

- Before installing a skill from ClawHub: `clawhub inspect <slug>` then scan
- When reviewing a skill's source code for safety
- When auditing skills already installed in your workspace
- When evaluating whether to trust an unknown skill author

## Quick Start

When asked to scan a skill, follow this process:

### Step 1: Get the Skill Files

**For a ClawHub skill (not yet installed):**
```bash
clawhub inspect <slug>          # Check metadata, author, file list
clawhub install <slug> --dir /tmp/skill-review   # Install to temp dir
```

**For a local skill:**
```bash
ls <skill-path>/                # List all files
```

### Step 2: Run the Scan

Read every file in the skill directory. For each file, check against ALL threat
categories below. Track findings with severity levels.

### Step 3: Calculate Trust Score and Report

Use the scoring formula to produce a 0-100 Trust Score. Output the report in the
format shown in the Report Template section.

---

## Threat Categories

Scan every text file in the skill directory. Check against these categories in order.

### CRITICAL - Auto-Reject (Trust Score = 0)

These patterns are never acceptable in a skill. Any match = immediate reject.

| Pattern | What to Look For | Why It's Dangerous |
|---------|-----------------|-------------------|
| **Reverse shell** | `/dev/tcp/`, `nc -e`, `bash -i >&`, `python.*pty.spawn`, `mkfifo.*nc` | Opens backdoor to attacker |
| **Download-and-execute** | `curl\|sh`, `wget\|bash`, `requests.get().text` + `exec()` | Runs attacker's code |
| **Crypto miner** | `xmrig`, `ethminer`, `stratum+tcp://`, `mining.*pool`, `hashrate` | Steals compute resources |
| **Base64-decode-execute** | `base64.b64decode` + `exec`, `atob` + `eval`, `Buffer.from` + `eval` | Hides malicious payload |
| **Credential harvesting** | Bulk reads of `~/.ssh/`, `~/.aws/`, `~/.config/`, `/etc/shadow`, `~/.gnupg` | Steals authentication keys |
| **System service creation** | `systemctl enable`, `launchctl load`, writing to `/etc/systemd/`, `sc create` | Persists malware |
| **Destructive commands** | `rm -rf /`, `rm -rf ~`, `mkfs`, `dd if=/dev/zero of=/dev/sda` | Destroys user data |

### HIGH - Requires Justification (-20 points each)

These patterns have legitimate uses but are commonly abused. Flag and explain.

| Pattern | What to Look For | Legitimate Use | Suspicious Use |
|---------|-----------------|---------------|----------------|
| **Dynamic code execution** | `eval()`, `exec()`, `new Function()` | Template engines, REPL tools | Running untrusted input |
| **Bulk env access** | `os.environ.copy()`, `dict(os.environ)`, iterating `process.env` | Debugging tools | Scraping all secrets |
| **Crontab modification** | `crontab -e`, `/etc/cron.d/`, `schtasks /create` | Scheduled tasks | Persistence mechanism |
| **Network listeners** | `socket.bind()`, `http.createServer()`, `net.createServer()` | API skills, webhooks | Unauthorized services |
| **File system writes outside skill dir** | Writing to `/tmp`, `/etc/`, `~/`, absolute paths | Cache files | Dropping payloads |
| **Process spawning** | `subprocess.Popen`, `child_process.exec`, `os.system()` | CLI wrappers | Command injection |
| **Package installation** | `pip install`, `npm install`, `apt install` at runtime | Auto-setup | Supply chain attack |

### MEDIUM - Note and Document (-5 points each)

| Pattern | What to Look For |
|---------|-----------------|
| **HTTP POST to external URLs** | `requests.post()`, `fetch(url, {method:'POST'})`, `httpx.post()` |
| **Environment variable reads** | `os.getenv()`, `process.env.VAR` (specific, not bulk) |
| **File reads of sensitive paths** | Reading `.env`, config files, credentials |
| **Obfuscated variable names** | Single-letter variables in critical code, hex-encoded strings |
| **Minified/compressed code** | Lines >500 chars, lack of whitespace, no comments |
| **Encoded strings** | Long base64 strings, hex-encoded payloads, URL-encoded blocks |

### LOW - Informational (-1 point each)

| Pattern | What to Look For |
|---------|-----------------|
| **External URLs** | Any hardcoded URLs (document where they point) |
| **API key patterns** | Placeholder patterns like `sk-`, `key_`, `token_` |
| **TODO/FIXME/HACK comments** | Indicate incomplete or rushed code |
| **No error handling** | Bare `except:`, empty `catch {}` blocks |
| **Outdated dependencies** | Known-vulnerable library versions |

---

## Supply Chain Signals

Beyond code patterns, evaluate these trust indicators:

### Author Trust (affects Trust Score)

| Signal | Score Impact |
|--------|-------------|
| Author has 5+ published skills | +5 |
| Author account >6 months old | +5 |
| Author has skills with >100 downloads | +5 |
| Author account <30 days old | -10 |
| Author has only 1 published skill | -5 |
| Author name looks auto-generated | -10 |

### Skill Metadata (affects Trust Score)

| Signal | Score Impact |
|--------|-------------|
| Has SKILL.md with valid frontmatter | +5 |
| Has README.md with install instructions | +3 |
| Has tests/ directory | +5 |
| Has examples/ directory | +3 |
| Version >1.0.0 (has been iterated) | +3 |
| Last updated within 60 days | +3 |
| No SKILL.md | -10 |
| No README.md | -5 |
| Description is empty or generic | -5 |
| Excessive file count (>50 files) | -5 (unusual for a skill) |

### Code Quality (affects Trust Score)

| Signal | Score Impact |
|--------|-------------|
| Code has inline comments | +2 |
| Functions have docstrings/JSDoc | +3 |
| Consistent code style | +2 |
| Total lines <1000 | +2 (appropriately scoped) |
| Total lines >5000 | -5 (over-scoped for a skill) |
| Mixed languages without justification | -3 |

---

## Trust Score Calculation

Start at **70 points** (neutral baseline). Apply modifiers:

```
Trust Score = 70
            + Supply Chain bonuses
            + Metadata bonuses
            + Code Quality bonuses
            - (CRITICAL findings * 70)    # Any critical = score 0
            - (HIGH findings * 20)
            - (MEDIUM findings * 5)
            - (LOW findings * 1)

Clamp to 0-100 range.
```

### Verdict Thresholds

| Score | Verdict | Action |
|-------|---------|--------|
| 80-100 | **TRUSTED** | Safe to install |
| 60-79 | **CAUTION** | Review flagged items before installing |
| 40-59 | **SUSPICIOUS** | Do not install without thorough manual review |
| 0-39 | **REJECT** | Do not install. Report to ClawHub if appropriate |

---

## Report Template

Output scan results in this format:

```markdown
# 🛡️ Skill Trust Report: <skill-name>

**Trust Score: XX/100 — VERDICT**
**Scanned:** <timestamp>
**Path:** <skill-path>

## Metadata
- Author: <author>
- Version: <version>
- Files: <count> (<scripts> scripts, <total-lines> lines)
- Last Updated: <date>

## Findings

### Critical (X found)
<list each with file, line, pattern, and explanation>

### High (X found)
<list each with file, line, pattern, and justification assessment>

### Medium (X found)
<summary list>

### Low (X found)
<summary list>

## Supply Chain Assessment
<author trust signals, metadata quality, code quality notes>

## Recommendation
<one-paragraph summary: install/don't install and why>
```

---

## Automation: CLI Scanner

For batch scanning or CI/CD integration, use the included Python scanner:

```bash
# Scan a local skill
python scanner.py /path/to/skill

# Scan with JSON output
python scanner.py /path/to/skill --json

# Scan a ClawHub skill before installing
clawhub install <slug> --dir /tmp/review
python scanner.py /tmp/review/<slug>

# Batch scan all installed skills
python scanner.py --batch ~/.openclaw/skills/
```

The CLI scanner implements the same threat patterns and scoring as the agent
instructions above. See `scanner.py` for the full implementation.

---

## Examples

### Scanning a ClawHub Skill Before Install

```
User: "Scan the youtube-watcher skill from ClawHub before I install it"

Agent steps:
1. clawhub inspect youtube-watcher (get metadata)
2. clawhub install youtube-watcher --dir /tmp/skill-review
3. Read all files in /tmp/skill-review/youtube-watcher/
4. Apply threat categories, calculate Trust Score
5. Output report
6. rm -rf /tmp/skill-review (cleanup)
```

### Auditing All Installed Skills

```
User: "Audit all my installed skills for security"

Agent steps:
1. ls ~/.openclaw/skills/ (or configured skills dir)
2. For each skill: run full scan
3. Output summary table sorted by Trust Score (lowest first)
4. Flag any skill scoring below 60
```

---

*Built by Eli Labs. "Trust, but verify - then verify again."*
