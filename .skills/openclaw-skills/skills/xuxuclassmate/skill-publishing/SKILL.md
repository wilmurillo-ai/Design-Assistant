---
name: skill-publishing
description: Guide to publishing and sharing Hermes skills via Skills Hub, GitHub PR, or Discord community. Covers security scan requirements and contribution workflow.
tags: [publish, clawhub, github, skills, community, devops]
---

# Skill Publishing & Sharing Guide

## Overview

Hermes has a **Skills Hub** with **648+ skills** across 4 registries:

| Registry | Count | Description |
|----------|-------|-------------|
| Built-in | 79 | Ships with every install |
| Optional | 48 | Official, user-installed |
| Community | 521 | Community-contributed |
| LobeHub | 505 | From LobeHub ecosystem |

---

## Publishing Methods

### Method 1: ClawHub CLI Publish (Recommended for ClawHub) ⭐

ClawHub's official npm CLI is the recommended way to publish skills.

#### Install ClawHub CLI

```bash
mkdir -p ~/clawhub-cli && cd ~/clawhub-cli
npm init -y > /dev/null 2>&1
npm install clawhub
npx clawhub --version
```

Requires `npm` / `npx` (Node.js). Installs to user directory, no root needed.

#### Login

```bash
cd ~/clawhub-cli
npx clawhub login --token "clh_YOUR_TOKEN" --no-browser
```

Get your token from [ClawHub settings](https://clawhub.ai).

#### Publish

```bash
npx clawhub publish /path/to/skill-folder \
  --slug "skill-slug" \
  --name "Display Name" \
  --version "1.0.0" \
  --changelog "Description of changes" \
  --tags "latest,tag1,tag2,tag3"
```

#### CLI Commands Reference

| Command | Purpose |
|---------|---------|
| `npx clawhub whoami` | Check login status |
| `npx clawhub inspect <slug>` | View skill details |
| `npx clawhub explore` | Browse latest skills |
| `npx clawhub search <query>` | Search skills |
| `npx clawhub delete <slug>` | Delete a skill (owner only) |

### Method 2: GitHub PR

For skills suitable for official distribution:

1. Fork NousResearch/hermes-agent on GitHub
2. Create branch: `skill/your-skill-name`
3. Add files under `optional-skills/category/your-skill-name/`
4. Open Pull Request

### Method 3: Discord Community Share

Post specialized skills in the Hermes Discord community.

---

## Security Scan Requirements

All published skills undergo automatic security scanning.

### Verdict Levels

| Verdict | Built-in | Community/Self |
|---------|----------|----------------|
| PASS | Publishes | Publishes |
| CAUTION | Warning | Blocked |
| FAIL | Blocked | Blocked |

Community skills are held to stricter standards. There is no override flag.

### How to Pass Security Scan

Follow these guidelines to ensure your skill passes:

**1. Use Official Sources Only**

Only reference downloads or clones from well-known official sources:
- GitHub (github.com)
- HuggingFace (huggingface.co)
- PyPI (pypi.org)
- npm (npmjs.com)

Avoid any third-party mirror domains or unknown download URLs.

**2. Avoid Hardcoded System Paths**

Do not include literal filesystem paths like `/opt/data/`, `/etc/`, or other system-specific locations. Instead:
- Use environment variable references like `$HOME`, `$AUDIO_CACHE_DIR`
- Describe paths in prose rather than code examples
- Use relative paths where possible

**3. No Credentials in Code**

Never include API keys, tokens, or secrets. Reference config files at runtime instead.

**4. Avoid Sensitive Command Patterns**

Documentation should not contain examples of:
- Commands that read sensitive system files
- Privilege escalation commands (sudo, chmod 777, etc.)
- Network exfiltration patterns (curl posting data to external servers)
- Persistence mechanisms (modifying shell startup files, systemd services)

**5. Keep Documentation Clean**

- Code examples should only show safe, intended usage
- If describing what to avoid, use plain text descriptions rather than code blocks containing bad patterns
- The scanner analyzes code blocks literally — it cannot distinguish "examples of bad practice" from actual malicious content

### Pre-Publish Checklist

Verify all of these before publishing:

- [ ] YAML frontmatter has name, description, tags
- [ ] No hardcoded credentials anywhere
- [ ] All URLs point to official sources only
- [ ] No literal system paths in code blocks
- [ ] No sensitive command patterns in code examples
- [ ] Skill tested in a real session
- [ ] Prerequisites clearly documented
- [ ] Troubleshooting section included for common errors

---

## CLI Installation (for GitHub publish method)

If using the Hermes CLI publish method:

```bash
git clone --depth 1 https://github.com/NousResearch/hermes-agent.git ~/hermes-agent
cd ~/hermes-agent
uv venv hermes-venv --python 3.13
source hermes-venv/bin/activate
uv pip install -e ".[all]"
hermes --version
```

Requirements: Python 3.13+, uv, git, C compiler. All installs to user directory.

---

## Known Limitations

### Owner Tools — Web Only

Settings like "Merge into" on ClawHub require GitHub OAuth web login. Cannot be modified via CLI token.

### Scan Appeals

If your skill is blocked by the scan:
1. Review the scan report on the skill page
2. Remove or rewrite triggering content
3. Increment version number and republish
