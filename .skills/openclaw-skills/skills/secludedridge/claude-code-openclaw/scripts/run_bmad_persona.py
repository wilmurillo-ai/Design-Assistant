#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
CLAUDE_CODE_RUN = SCRIPT_DIR / "claude_code_run.py"

AGENT_COMMANDS = {
    "analyst": "/bmad-agent-bmm-analyst",
    "pm": "/bmad-agent-bmm-pm",
    "architect": "/bmad-agent-bmm-architect",
    "sm": "/bmad-agent-bmm-sm",
    "dev": "/bmad-agent-bmm-dev",
    "qa": "/bmad-agent-bmm-qa",
    "quick-flow-solo-dev": "/bmad-agent-bmm-quick-flow-solo-dev",
    "ux-designer": "/bmad-agent-bmm-ux-designer",
    "tech-writer": "/bmad-agent-bmm-tech-writer",
    "tea": "/bmad-agent-tea-tea",
    "agent-builder": "/bmad-agent-bmb-agent-builder",
    "module-builder": "/bmad-agent-bmb-module-builder",
    "workflow-builder": "/bmad-agent-bmb-workflow-builder",
    "bmad-master": "/bmad-agent-bmad-master",
}

PERSONA_ALIASES = {
    "analyst": "analyst",
    "mary": "analyst",
    "pm": "pm",
    "product-manager": "pm",
    "product manager": "pm",
    "john": "pm",
    "architect": "architect",
    "winston": "architect",
    "sm": "sm",
    "scrum-master": "sm",
    "scrum master": "sm",
    "bob": "sm",
    "dev": "dev",
    "developer": "dev",
    "developer-agent": "dev",
    "developer agent": "dev",
    "amelia": "dev",
    "qa": "qa",
    "quinn": "qa",
    "quick": "quick-flow-solo-dev",
    "quick-flow": "quick-flow-solo-dev",
    "quick-flow-solo-dev": "quick-flow-solo-dev",
    "barry": "quick-flow-solo-dev",
    "ux": "ux-designer",
    "ux-designer": "ux-designer",
    "ux designer": "ux-designer",
    "sally": "ux-designer",
    "tech-writer": "tech-writer",
    "tech writer": "tech-writer",
    "writer": "tech-writer",
    "paige": "tech-writer",
    "tea": "tea",
    "murat": "tea",
    "agent-builder": "agent-builder",
    "agent builder": "agent-builder",
    "bond": "agent-builder",
    "module-builder": "module-builder",
    "module builder": "module-builder",
    "morgan": "module-builder",
    "workflow-builder": "workflow-builder",
    "workflow builder": "workflow-builder",
    "wendy": "workflow-builder",
    "master": "bmad-master",
    "bmad-master": "bmad-master",
    "bmad master": "bmad-master",
}

ARTIFACT_STOP_WORKFLOWS = {
    "bmad-bmm-create-product-brief",
    "bmad-bmm-create-prd",
    "bmad-bmm-create-ux-design",
    "bmad-bmm-create-architecture",
    "bmad-bmm-create-epics-and-stories",
    "bmad-bmm-check-implementation-readiness",
    "bmad-bmm-sprint-planning",
    "bmad-bmm-create-story",
    "bmad-bmm-dev-story",
    "bmad-bmm-code-review",
    "bmad-bmm-generate-project-context",
    "bmad-bmm-quick-spec",
}


def normalize_persona(value: str | None) -> str | None:
    if not value:
        return None
    key = value.strip().lower()
    return PERSONA_ALIASES.get(key, key)


def load_catalog(cwd: str) -> list[dict[str, str]]:
    path = Path(cwd) / "_bmad" / "_config" / "bmad-help.csv"
    if not path.exists():
        raise SystemExit(f"BMad help catalog not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def list_catalog(catalog: list[dict[str, str]]) -> str:
    lines: list[str] = []
    current = None
    for row in catalog:
        section = f"{row.get('module','').strip()} / {row.get('phase','').strip()}"
        if section != current:
            current = section
            lines.append(f"\n[{section}]")
        lines.append(
            f"- code={row.get('code','').strip() or '-':<4} "
            f"agent={row.get('agent-name','').strip() or '-':<18} "
            f"command={row.get('command','').strip() or '-':<34} "
            f"name={row.get('name','').strip()}"
        )
    return "\n".join(lines).strip()


def resolve_entry(catalog: list[dict[str, str]], persona: str | None, trigger: str) -> dict[str, str]:
    raw = trigger.strip()
    normalized = raw.lstrip("/")
    trig_code = normalized.upper()
    trig_command = normalized.lower()

    candidates = [row for row in catalog if row.get("code", "").strip().upper() == trig_code]
    match_kind = "code"

    if not candidates:
        candidates = [row for row in catalog if row.get("command", "").strip().lower() == trig_command]
        match_kind = "command"

    if not candidates:
        candidates = [row for row in catalog if row.get("name", "").strip().lower() == trig_command]
        match_kind = "name"

    if not candidates:
        raise SystemExit(
            f"No BMad workflow/trigger found for: {raw} "
            f"(expected code like CS, command like bmad-bmm-create-story, or workflow name)"
        )

    if persona:
        candidates = [row for row in candidates if row.get("agent-name", "").strip() == persona]
        if not candidates:
            raise SystemExit(f"No BMad entry found for persona={persona} trigger={raw} ({match_kind})")

    if len(candidates) > 1:
        distinct_agents = sorted({row.get('agent-name', '').strip() or '?' for row in candidates})
        if len(distinct_agents) == 1:
            return candidates[0]
        agent_names = ", ".join(distinct_agents)
        raise SystemExit(f"Trigger {raw} is ambiguous. Provide --persona. Candidates: {agent_names}")

    return candidates[0]


def command_for_persona(persona: str) -> str:
    slash = AGENT_COMMANDS.get(persona)
    if not slash:
        raise SystemExit(f"No installed agent command mapping for persona: {persona}")
    return slash


def slash_for_entry(entry: dict[str, str], persona: str | None) -> str:
    command = entry.get("command", "").strip()
    if persona:
        return command_for_persona(persona)
    if command:
        return f"/{command}"
    raise SystemExit("Could not determine slash command for entry; provide --persona or use a row with an installed command")


def workflow_for_entry(entry: dict[str, str], persona: str | None) -> str:
    command = entry.get("command", "").strip()
    if command:
        return command
    if persona:
        code = entry.get("code", "").strip().lower() or "chat"
        return f"bmad-agent-{persona}-{code}"
    raise SystemExit("Could not determine workflow for entry")


def build_prompt(args: argparse.Namespace, entry: dict[str, str], persona: str | None) -> str:
    slash = slash_for_entry(entry, persona)
    trigger_value = (entry.get("code", "").strip() or args.trigger or "").upper()
    lines = [slash]
    if persona and trigger_value:
        lines.append(trigger_value)

    name = entry.get("name", "").strip()
    description = entry.get("description", "").strip()
    outputs = entry.get("outputs", "").strip()
    workflow_command = entry.get("command", "").strip()

    if name:
        lines.append(f"Target BMad action: {name}")
    if workflow_command:
        lines.append(f"Workflow command: {workflow_command}")
    if args.story_id:
        lines.append(f"Target story: {args.story_id}")
    if args.story_path:
        lines.append(f"Target story file: {args.story_path}")
    if args.epic:
        lines.append(f"Target epic: {args.epic}")
    if args.target_file:
        lines.append(f"Primary expected artifact: {args.target_file}")
    if outputs:
        lines.append(f"Expected outputs: {outputs}")
    if description:
        lines.append(f"Intent: {description}")

    if args.instruction:
        lines.append(args.instruction.strip())
    if args.instruction_file:
        lines.append(Path(args.instruction_file).read_text(encoding="utf-8").strip())

    if args.default_continue:
        lines.append("Default all interim prompts to Continue / C.")
    if args.disable_advanced_elicitation:
        lines.append("Do not enter Advanced Elicitation / A unless explicitly required by the user.")
    if args.disable_party_mode:
        lines.append("Do not enter Party Mode / P unless explicitly requested by the user.")
    if args.auto_exit:
        lines.append("Once the target workflow has produced its intended artifact or terminal status, exit the agent.")

    return "\n".join(line for line in lines if line)


def build_command(args: argparse.Namespace, workflow: str, prompt_file: str) -> list[str]:
    cmd = [
        sys.executable,
        str(CLAUDE_CODE_RUN),
        "--mode",
        "interactive",
        "--cwd",
        args.cwd,
        "--workflow",
        workflow,
        "--prompt-file",
        prompt_file,
    ]

    if args.permission_mode:
        cmd += ["--permission-mode", args.permission_mode]
    if args.allowed_tools:
        cmd += ["--allowedTools", args.allowed_tools]
    if args.story_id:
        cmd += ["--story-id", args.story_id]
    if args.story_path:
        cmd += ["--story-path", args.story_path]
    if args.orchestrator_profile:
        cmd += ["--orchestrator-profile", args.orchestrator_profile]
    elif args.permission_mode == "bypassPermissions":
        if "alphaclaw" in str(Path(args.cwd).resolve()):
            cmd += ["--orchestrator-profile", "alphaclaw-local"]
        else:
            cmd += ["--orchestrator-profile", "local-bypass"]

    if args.orchestrator_profiles_file:
        cmd += ["--orchestrator-profiles-file", args.orchestrator_profiles_file]
    if args.notify_account:
        cmd += ["--notify-account", args.notify_account]
    if args.notify_target:
        cmd += ["--notify-target", args.notify_target]
    if args.notify_channel:
        cmd += ["--notify-channel", args.notify_channel]
    if args.notify_parent_session:
        cmd += ["--notify-parent-session", args.notify_parent_session]
    if args.notify_dry_run:
        cmd += ["--notify-dry-run"]
    if args.no_notify_final_update:
        cmd += ["--no-notify-final-update"]
    if args.stop_on_artifact_complete or workflow in ARTIFACT_STOP_WORKFLOWS:
        cmd += ["--stop-on-artifact-complete"]

    return cmd


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run official BMad agent personas and trigger commands via Claude Code orchestrator")
    ap.add_argument("--cwd", required=True, help="Project root containing _bmad and .claude/commands")
    ap.add_argument("--persona", help="Persona such as sm, dev, pm, architect, analyst, qa, tea, agent-builder")
    ap.add_argument("--trigger", help="Agent trigger such as CS, DS, CR, SP, ER, CP, CE, QA, TD, or a direct command like bmad-bmm-create-story")
    ap.add_argument("--story-id", help="Story id used for artifact probing, e.g. 4-1-agent-api-auth-and-security")
    ap.add_argument("--story-path", help="Explicit story file path for artifact probing")
    ap.add_argument("--epic", help="Optional epic identifier to mention in the prompt")
    ap.add_argument("--target-file", help="Optional target artifact path to mention in the prompt")
    ap.add_argument("--instruction", help="Additional instruction appended after the trigger")
    ap.add_argument("--instruction-file", help="Read additional instruction from file")
    ap.add_argument("--permission-mode", default="bypassPermissions")
    ap.add_argument("--allowedTools", dest="allowed_tools")
    ap.add_argument("--orchestrator-profile")
    ap.add_argument("--orchestrator-profiles-file")
    ap.add_argument("--notify-account")
    ap.add_argument("--notify-target")
    ap.add_argument("--notify-channel")
    ap.add_argument("--notify-parent-session")
    ap.add_argument("--notify-dry-run", action="store_true")
    ap.add_argument("--no-notify-final-update", action="store_true")
    ap.add_argument("--stop-on-artifact-complete", action="store_true")
    ap.add_argument("--list", action="store_true", help="List discovered BMad codes from _bmad/_config/bmad-help.csv")
    ap.add_argument("--print-prompt", action="store_true", help="Print the generated prompt and exit")
    ap.add_argument("--default-continue", action="store_true", default=True)
    ap.add_argument("--disable-advanced-elicitation", action="store_true", default=True)
    ap.add_argument("--disable-party-mode", action="store_true", default=True)
    ap.add_argument("--auto-exit", action="store_true", default=True)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    catalog = load_catalog(args.cwd)

    if args.list:
        print(list_catalog(catalog))
        return 0

    if not args.trigger:
        raise SystemExit("--trigger is required unless --list is used")

    persona = normalize_persona(args.persona)
    entry = resolve_entry(catalog, persona, args.trigger)
    resolved_persona = entry.get("agent-name", "").strip() or persona

    prompt = build_prompt(args, entry, resolved_persona)
    workflow = workflow_for_entry(entry, resolved_persona)

    if args.print_prompt:
        print(prompt)
        return 0

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as fp:
        fp.write(prompt)
        prompt_path = fp.name

    cmd = build_command(args, workflow, prompt_path)
    print("[run_bmad_persona]", shlex.join(cmd), file=sys.stderr)
    # return subprocess.run(cmd, text=True).returncode
    import os
    os.execv(cmd[0], cmd)


if __name__ == "__main__":
    raise SystemExit(main())
