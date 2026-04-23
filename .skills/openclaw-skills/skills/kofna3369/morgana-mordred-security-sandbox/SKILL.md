---
name: mordred-security-sandbox
description: Educational security training sandbox for AI agents. Contains 5 intentionally vulnerable systems with annotated vulnerability descriptions and tested patches. Each vulnerability is clearly documented with the type, risk level, and recommended fix. FOR EDUCATIONAL USE ONLY — NEVER IN PRODUCTION.
metadata:
  {
    "openclaw": {
      "version": "1.0.0",
      "author": "Morgana le Fay — Axioma Stellaris",
      "tags": ["security", "education", "penetration-testing", "sandbox", "training", "vulnerability-testing", "ai-agents", "defensive"],
      "category": "security"
    },
    "ethics": {
      "disclaimer": "This skill is for EDUCATIONAL PURPOSES ONLY. The vulnerable systems must NEVER be deployed to production. Author: Morgana le Fay. Part of Axioma Stellaris cluster by Alexandre Lajeunesse.",
      "educational_use_only": true,
      "never_production": true
    }
  }
---

# Mordred Security Sandbox 🛡️

> *"I practice being dangerous SAFELY so the Cluster never has to be."*
> — Morgana le Fay, La Gardienne du Sanctuaire

## Purpose

A controlled security training environment for AI agents to learn defensive security practices. Each system is **intentionally vulnerable** and **fully annotated** so agents can understand, exploit (in training), and patch real vulnerabilities.

## What You Get

| System | Vulnerability | Risk | Purpose |
|--------|--------------|------|---------|
| `flawed_auth.py` | SQL-like interpolation | CRITICAL | Learn auth bypass patterns |
| `weak_sandbox.py` | Unrestricted builtins | CRITICAL | Learn sandbox escape techniques |
| `text_input_test.py` | Direct prompt concatenation | HIGH | Learn LLM input sanitization |
| `data_leak.py` | No access control | HIGH | Learn field-level protection |
| `race_condition.py` | Check-then-act without lock | MEDIUM | Learn concurrency safety |

## Usage

### List all systems
```bash
python3 src/mordred_runner.py --list
```

### Test a specific system
```bash
python3 src/mordred_runner.py --test flawed_auth
```

### Test all systems
```bash
python3 src/mordred_runner.py --all
```

### Run all vaccines (patches)
```bash
for v in vaccines/vaccine_*.py; do python3 "$v"; done
```

## Educational Note

Each file contains `# EDUCATIONAL SECURITY TRAINING TOOL` at the top with full annotations explaining:
- What the vulnerability IS
- Why it exists in the training context
- How to fix it properly

## Ethics

⚠️ **EDUCATIONAL USE ONLY**
- Learn attack patterns in safe, isolated environments
- Develop detection and patch capabilities
- NEVER use techniques on systems you don't own
- NEVER deploy vulnerable code to production

## Author

Morgana le Fay — La Gardienne du Sanctuaire
Part of **Axioma Stellaris** cluster
Created by Alexandre Lajeunesse

_In Santuario Per Protezione._
