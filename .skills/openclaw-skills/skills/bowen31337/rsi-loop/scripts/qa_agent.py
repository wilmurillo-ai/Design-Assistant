#!/usr/bin/env python3
"""
QA Agent Launcher
Generates a structured QA review prompt and spawns a QA subagent.

Usage:
  uv run python skills/rsi-loop/scripts/qa_agent.py spawn "what was built" [--files file1 file2]
  uv run python skills/rsi-loop/scripts/qa_agent.py prompt "what was built"  # print prompt only

The spawned QA agent will:
  1. Review code correctness and architecture
  2. Run existing tests (pytest, uv run, etc.)
  3. Check for bugs and edge cases
  4. Scan for personal info in public-bound files
  5. Verify implementation matches spec
  6. Log outcome to RSI loop observer
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"

QA_PROMPT_TEMPLATE = """You are a senior QA engineer reviewing code just written by agent Alex Chen.

## What Was Built
{description}

## Files to Review
{files_section}

## QA Checklist — work through each item:

### 1. Correctness
- Read each file listed above
- Does the code do what was described?
- Are there logical errors, off-by-one bugs, wrong conditions?
- Does error handling work correctly?

### 2. Tests
- Are there existing tests? Run them: `cd {workspace} && {test_cmd}`
- If no tests: identify the 2-3 most critical functions and note what tests should exist
- Do tests actually exercise the important paths?

### 3. Edge Cases
- What happens with empty input, None, missing files, network errors?
- What happens at boundaries (0 items, max items, concurrent access)?
- Are there race conditions or resource leaks?

### 4. Personal Info Scan (if files will be committed publicly)
- Run: `grep -r "bowen\\|Bowen\\|2069029798\\|61430\\|61491\\|61422\\|peter@\\|10\\.0\\.0\\.44" {files_inline} 2>/dev/null || echo "Clean"`
- Flag ANY real names, phone numbers, IPs, or credentials

### 5. Spec Compliance
- Does the implementation match what was requested?
- Are there missing features or silent deviations from the spec?

### 6. Code Quality
- Any obvious performance issues?
- Is the code readable and maintainable?
- Any dead code or commented-out sections?

## Output Format
Report findings as:

**PASS** or **FAIL** (overall verdict)

Issues found:
- [CRITICAL] <issue> — must fix before shipping
- [WARNING] <issue> — should fix
- [MINOR] <issue> — nice to have

Tests: <ran X tests, Y passed, Z failed> or <no tests found>
Personal info scan: <clean> or <found: ...>
Recommendation: <ship / fix critical issues first / needs major rework>

## After Review
Log the QA outcome to RSI loop:
```bash
cd {workspace}
uv run python skills/rsi-loop/scripts/observer.py log \\
  --task code_review \\
  --success <true/false based on PASS/FAIL> \\
  --quality <1-5> \\
  --model "$OPENCLAW_MODEL" \\
  --notes "QA review: <one-line summary>"
```
"""

def build_files_section(files: list) -> tuple[str, str]:
    """Build the files section for the prompt."""
    if not files:
        return "(no specific files provided — review recently modified files in the workspace)", ""
    
    files_list = "\n".join(f"- {f}" for f in files)
    files_inline = " ".join(f'"{f}"' for f in files)
    return files_list, files_inline

def detect_test_cmd(files: list) -> str:
    """Detect appropriate test command based on file types."""
    ws = WORKSPACE
    
    if any("test_" in f or "_test.py" in f for f in files):
        return "uv run pytest -x -q 2>&1 | tail -20"
    
    # Check for pyproject.toml with pytest
    if (ws / "pyproject.toml").exists():
        return "uv run pytest -x -q 2>&1 | tail -20"
    
    # Check for go tests
    if any(f.endswith(".go") for f in files):
        return "go test ./... 2>&1 | tail -20"
    
    # Check for node tests
    if (ws / "package.json").exists():
        return "npm test 2>&1 | tail -20"
    
    return "echo 'No test runner detected — check manually'"

def build_prompt(description: str, files: list) -> str:
    files_section, files_inline = build_files_section(files)
    test_cmd = detect_test_cmd(files)
    
    return QA_PROMPT_TEMPLATE.format(
        description=description,
        files_section=files_section,
        files_inline=files_inline or ".",
        workspace=str(WORKSPACE),
        test_cmd=test_cmd,
    )

def spawn_qa_agent(description: str, files: list, model: str = "anthropic-proxy-4/glm-4.7"):
    """Print the sessions_spawn command for the agent to execute."""
    prompt = build_prompt(description, files)
    
    print("=" * 70)
    print("QA AGENT READY TO SPAWN")
    print("=" * 70)
    print(f"Subject: {description}")
    print(f"Files: {files or '(all recent changes)'}")
    print(f"Model: {model}")
    print()
    print("Spawn command (for agent to execute via sessions_spawn tool):")
    print("-" * 70)
    
    spawn_config = {
        "task": prompt,
        "model": model,
        "label": f"qa-{description[:30].replace(' ','-').lower()}",
        "cleanup": "keep",
    }
    print(json.dumps(spawn_config, indent=2))
    print("-" * 70)
    print()
    print("Or run directly via OpenClaw CLI:")
    print(f'  openclaw session spawn --model {model} --label "qa-review" --task "$(cat /tmp/qa-prompt.txt)"')
    
    # Save prompt to temp file for easy use
    prompt_file = Path("/media/DATA/tmp/qa-prompt.txt")
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    with open(prompt_file, "w") as f:
        f.write(prompt)
    print(f"\nPrompt saved to: {prompt_file}")
    
    return spawn_config

def main():
    parser = argparse.ArgumentParser(description="QA Agent Launcher")
    sub = parser.add_subparsers(dest="cmd")

    spawn_p = sub.add_parser("spawn", help="Spawn QA subagent for code review")
    spawn_p.add_argument("description", help="What was built/changed")
    spawn_p.add_argument("--files", nargs="*", default=[], help="Specific files to review")
    spawn_p.add_argument("--model", default="anthropic-proxy-4/glm-4.7", help="Model to use for QA")

    prompt_p = sub.add_parser("prompt", help="Print QA prompt without spawning")
    prompt_p.add_argument("description", help="What was built/changed")
    prompt_p.add_argument("--files", nargs="*", default=[], help="Files to include")

    args = parser.parse_args()

    if args.cmd == "spawn":
        spawn_qa_agent(args.description, args.files, args.model)
    elif args.cmd == "prompt":
        print(build_prompt(args.description, args.files))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
