# Example: Scan a ClawHub Skill Before Installing

## Scenario
You found a skill on ClawHub called "auto-deployer" and want to check if it's safe.

## Steps

### 1. Inspect the skill metadata first
```bash
clawhub inspect auto-deployer
```

Check: Who's the author? When was it last updated? How many files?

### 2. Install to a temporary directory
```bash
clawhub install auto-deployer --dir /tmp/skill-review
```

### 3. Run the trust scanner
```bash
python3 scanner.py /tmp/skill-review/auto-deployer
```

### 4. Review the report
- Score 80+: Safe to install normally
- Score 60-79: Read each finding before deciding
- Score 40-59: Don't install without expert review
- Score 0-39: Don't install. Consider reporting.

### 5. If safe, install for real
```bash
clawhub install auto-deployer
```

### 6. Clean up
```bash
rm -rf /tmp/skill-review
```

## As an Agent Prompt
```
"Before installing the auto-deployer skill, scan it for security issues
and tell me the trust score."
```

Your agent will follow the SKILL.md instructions automatically.
