#!/usr/bin/env python3
"""
RSI Loop - Deployer
Deploys approved improvement proposals into the agent's live configuration.
Each action_type has a dedicated handler.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Gene Registry integration (Phase 2 of RSI loop)
try:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from gene_registry import get_gene, update_gene_stats
    _GENE_REGISTRY_AVAILABLE = True
except ImportError:
    _GENE_REGISTRY_AVAILABLE = False

# EvolutionEvent logging (Phase 2)
try:
    from event_logger import log_event
    _EVENT_LOGGER_AVAILABLE = True
except ImportError:
    _EVENT_LOGGER_AVAILABLE = False

# RSI v2 — Critique phase
try:
    from critique import CritiqueAgent
    _CRITIQUE_AVAILABLE = True
except ImportError:
    _CRITIQUE_AVAILABLE = False

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
PROPOSALS_DIR = DATA_DIR / "proposals"
WORKSPACE = Path.home() / ".openclaw" / "workspace"

# ---------------------------------------------------------------------------
# IMMUTABLE_CORE — files that block auto-deploy and require --force-core
# ---------------------------------------------------------------------------
IMMUTABLE_CORE = [
    "SOUL.md",
    "AGENTS.md",
    "TOOLS.md",
    "USER.md",
    "skills/rsi-loop/scripts/deployer.py",
    "skills/rsi-loop/scripts/observer.py",
    "skills/rsi-loop/data/genes.json",
    "skills/rsi-loop/data/events.jsonl",
]

# Default max_files per mutation type (when no gene blast_radius present)
_BLAST_DEFAULTS = {"repair": 5, "optimize": 10, "innovate": 20}


def check_blast_radius(proposal: dict, gene: dict = None) -> tuple:
    """
    Validate that a proposal's blast radius is within acceptable limits.

    Returns (ok: bool, reason: str).
      ok=False means deployment should be aborted.
    """
    mutation_type = proposal.get("mutation_type", "optimize")

    # Determine max_files: gene takes precedence, else defaults
    if gene is not None:
        max_files = gene.get("blast_radius", {}).get(
            "max_files", _BLAST_DEFAULTS.get(mutation_type, 10)
        )
        allowed_paths = gene.get("blast_radius", {}).get("allowed_paths", [])
    else:
        max_files = _BLAST_DEFAULTS.get(mutation_type, 10)
        allowed_paths = []

    # Collect file count from implementation.changes (if list) or allowed_paths
    impl = proposal.get("implementation", {})
    changes = impl.get("changes", "")

    # Count from allowed_paths if present, otherwise use 1 (single target_file)
    if allowed_paths:
        file_count = len(allowed_paths)
        paths_to_check = allowed_paths
    elif isinstance(changes, list):
        file_count = len(changes)
        paths_to_check = changes
    else:
        target = impl.get("target_file", "")
        file_count = 1 if target else 0
        paths_to_check = [target] if target else []

    # Check IMMUTABLE_CORE presence in allowed paths
    for p in paths_to_check:
        # Normalise path for comparison
        p_norm = p.lstrip("/").lstrip("./")
        for core in IMMUTABLE_CORE:
            core_norm = core.lstrip("/").lstrip("./")
            if p_norm == core_norm or p_norm.endswith(core_norm):
                return False, f"blocked: immutable core path '{p}'"

    if file_count > max_files:
        return (
            False,
            f"blast radius exceeded: {file_count} files > max {max_files} for '{mutation_type}'",
        )

    return True, ""


def _is_immutable(target_file: str) -> bool:
    """Return True if target_file matches any IMMUTABLE_CORE entry."""
    t = target_file.lstrip("/").lstrip("./")
    for core in IMMUTABLE_CORE:
        c = core.lstrip("/").lstrip("./")
        if t == c or t.endswith(c):
            return True
    return False

def load_proposal(proposal_id: str) -> dict:
    path = PROPOSALS_DIR / f"{proposal_id}.json"
    if not path.exists():
        matches = list(PROPOSALS_DIR.glob(f"{proposal_id}*.json"))
        if not matches:
            raise FileNotFoundError(f"Proposal '{proposal_id}' not found")
        path = matches[0]
    with open(path) as f:
        return json.load(f)

def save_proposal(p: dict):
    path = PROPOSALS_DIR / f"{p['id']}.json"
    with open(path, "w") as f:
        json.dump(p, f, indent=2)

def mark_deployed(p: dict, notes: str = ""):
    p["status"] = "deployed"
    p["deployed_at"] = datetime.now(timezone.utc).isoformat()
    if notes:
        p["deployment_notes"] = notes
    save_proposal(p)

def deploy_create_skill(p: dict, dry_run: bool = False) -> str:
    """Scaffold a new skill directory using skill-creator's init script."""
    task_type = p["pattern"]["task_type"]
    skill_name = task_type.replace("_", "-")
    init_script = Path("/home/bowen/.local/share/fnm/node-versions/v22.22.0/installation/lib/node_modules/openclaw/skills/skill-creator/scripts/init_skill.py")

    if not init_script.exists():
        return f"ERROR: skill-creator init script not found at {init_script}"

    target = WORKSPACE / "skills" / skill_name
    if target.exists():
        return f"SKIP: Skill '{skill_name}' already exists at {target}"

    cmd = [
        sys.executable, str(init_script),
        skill_name,
        "--path", str(WORKSPACE / "skills"),
        "--resources", "scripts,references"
    ]

    if dry_run:
        return f"DRY RUN: Would run: {' '.join(cmd)}"

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return f"Created skill scaffold at {target}\nNext: implement SKILL.md and scripts"
    else:
        return f"ERROR: {result.stderr}"

def deploy_update_soul(p: dict, dry_run: bool = False, force_core: bool = False) -> str:
    """Append lesson learned to SOUL.md."""
    target = p["implementation"].get("target_file", "SOUL.md")

    # IMMUTABLE_CORE guard
    for check in [target, "SOUL.md", "AGENTS.md"]:
        if _is_immutable(check):
            if not force_core:
                print(f"\n⛔  IMMUTABLE_CORE WARNING: '{check}' requires human review.")
                print("    Re-run with --force-core to override (use with caution).")
                return f"BLOCKED: '{check}' is immutable core. Use --force-core to proceed."
            print(f"\n⚠️  --force-core override active for immutable path: '{check}'")
            break

    soul_path = WORKSPACE / "SOUL.md"
    if not soul_path.exists():
        return "ERROR: SOUL.md not found"

    lesson = p["implementation"].get("changes", "")
    issue = p["pattern"]["issue"]
    task = p["pattern"]["task_type"]

    # Extract the lesson from the proposal
    lesson_entry = (
        f"\n- **[auto-rsi]** [{task}] Avoid '{issue}': {p['description']}\n"
    )

    if dry_run:
        return f"DRY RUN: Would append to SOUL.md:\n{lesson_entry}"

    with open(soul_path, "a") as f:
        f.write(lesson_entry)

    return f"Appended lesson to SOUL.md: {lesson_entry.strip()}"

def deploy_fix_routing(p: dict, dry_run: bool = False) -> str:
    """Print routing fix instructions (requires manual application)."""
    config_path = WORKSPACE / "skills" / "intelligent-router" / "config.json"
    if not config_path.exists():
        return "ERROR: intelligent-router config.json not found"

    changes = ""
    if "implementation" in p:
        changes = p["implementation"].get("changes", "")
    elif "suggested_changes" in p:
        changes = "\n".join(f"- {c.get('file','')}: {c.get('action','')} — {c.get('detail','')}" for c in p["suggested_changes"])
    else:
        changes = p.get("description", "No details available")

    if dry_run:
        return f"DRY RUN: Would update {config_path}\n{changes}"

    # For routing, we output the guidance for the agent to apply
    return (
        f"MANUAL ACTION REQUIRED - Update {config_path}:\n"
        f"{changes}\n\n"
        f"After updating, reload config with: openclaw gateway config.get"
    )

def deploy_update_memory(p: dict, dry_run: bool = False) -> str:
    """Append memory improvement to HEARTBEAT.md or tiered memory."""
    heartbeat_path = WORKSPACE / "HEARTBEAT.md"
    task = p["pattern"]["task_type"]
    changes = p["implementation"].get("changes", "")

    if dry_run:
        return f"DRY RUN: Would update HEARTBEAT.md for {task} memory continuity"

    return (
        f"MANUAL ACTION REQUIRED - Improve memory for '{task}':\n"
        f"{changes}\n\n"
        f"Suggested: Add '{task}' context retrieval to HEARTBEAT.md hydration section"
    )

def deploy_apply_gene(p: dict, dry_run: bool = False, force_core: bool = False) -> str:
    """
    Deploy an apply_gene proposal by:
    1. Loading the referenced Gene from the registry
    2. Checking blast radius and IMMUTABLE_CORE
    3. Printing its implementation template
    4. Running each validation command and reporting pass/fail
    5. Updating gene stats (success_rate, times_applied, last_applied)
    6. Logging an EvolutionEvent
    """
    if not _GENE_REGISTRY_AVAILABLE:
        return "ERROR: gene_registry module not available — cannot apply gene proposal"

    gene_id = p.get("implementation", {}).get("gene_id")
    if not gene_id:
        return "ERROR: proposal.implementation.gene_id is missing"

    gene = get_gene(gene_id)
    if gene is None:
        return f"ERROR: Gene '{gene_id}' not found in registry"

    # ── Blast Radius check ──────────────────────────────────────────────────
    br_ok, br_reason = check_blast_radius(p, gene)
    if not br_ok:
        if "immutable core" in br_reason and force_core:
            print(f"\n⚠️  --force-core override active: {br_reason}")
        else:
            msg = f"BLOCKED: {br_reason}"
            if "immutable core" in br_reason:
                print(f"\n⛔  IMMUTABLE_CORE WARNING: {br_reason}")
                print("    Re-run with --force-core to override (use with caution).")
            if _EVENT_LOGGER_AVAILABLE:
                log_event(
                    mutation_type=gene.get("mutation_type", "optimize"),
                    gene_id=gene_id,
                    outcome={"status": "skipped", "validation_passed": False,
                             "quality": None, "notes": msg},
                )
            return msg

    # ── IMMUTABLE_CORE check on allowed_paths ───────────────────────────────
    allowed = gene.get("blast_radius", {}).get("allowed_paths", [])
    for path in allowed:
        if _is_immutable(path):
            if not force_core:
                print(f"\n⛔  IMMUTABLE_CORE WARNING: Gene targets protected path '{path}'")
                print("    Re-run with --force-core to override (use with caution).")
                if _EVENT_LOGGER_AVAILABLE:
                    log_event(
                        mutation_type=gene.get("mutation_type", "optimize"),
                        gene_id=gene_id,
                        outcome={"status": "skipped", "validation_passed": False,
                                 "quality": None, "notes": f"blocked: immutable path '{path}'"},
                    )
                return f"BLOCKED: gene targets immutable core path '{path}'. Use --force-core."
            print(f"\n⚠️  --force-core override for immutable path: '{path}'")

    print(f"\n{'='*60}")
    print(f"Gene: {gene['gene_id']}")
    print(f"Title: {gene['meta']['title']}")
    print(f"Mutation type: {gene['mutation_type']}")
    print(f"Success rate: {gene['meta']['success_rate']:.0%} ({gene['meta']['times_applied']}x applied)")
    print(f"\nImplementation Template:")
    print(f"{'─'*60}")
    print(gene["implementation"].get("template", "(no template)"))
    print(f"{'─'*60}")

    # Blast radius summary
    blast = gene.get("blast_radius", {})
    print(f"\nBlast Radius: max {blast.get('max_files', '?')} files")
    if allowed:
        print("  Allowed paths:")
        for path in allowed:
            print(f"    • {path}")
    immutable_gene = blast.get("immutable_paths", [])
    if immutable_gene:
        print("  Immutable paths (require Bowen approval):")
        for path in immutable_gene:
            print(f"    ⛔ {path}")

    if dry_run:
        print(f"\n[DRY RUN] Would run {len(gene['validation']['commands'])} validation command(s)")
        return f"DRY RUN: Gene '{gene_id}' template printed. Validation skipped."

    # Run validation commands
    print(f"\nValidation Commands:")
    validation = gene.get("validation", {})
    commands = validation.get("commands", [])
    all_passed = True
    for i, cmd in enumerate(commands, 1):
        print(f"\n  [{i}/{len(commands)}] $ {cmd}")
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                print(f"  ✓ PASSED (exit 0)")
                if result.stdout.strip():
                    print(f"    stdout: {result.stdout.strip()[:300]}")
            else:
                all_passed = False
                print(f"  ✗ FAILED (exit {result.returncode})")
                if result.stderr.strip():
                    print(f"    stderr: {result.stderr.strip()[:300]}")
        except subprocess.TimeoutExpired:
            all_passed = False
            print(f"  ✗ TIMEOUT (>60s)")
        except Exception as e:
            all_passed = False
            print(f"  ✗ ERROR: {e}")

    # Update gene stats
    update_gene_stats(gene_id, success=all_passed)
    status_str = "SUCCESS" if all_passed else "FAILED"
    print(f"\n{'='*60}")
    print(f"Gene deployment: {status_str}")
    print(f"Stats updated: times_applied +1, success recorded: {all_passed}")

    # Log EvolutionEvent
    if _EVENT_LOGGER_AVAILABLE:
        log_event(
            mutation_type=gene.get("mutation_type", "optimize"),
            gene_id=gene_id,
            outcome={
                "status": "success" if all_passed else "failure",
                "validation_passed": all_passed,
                "quality": None,
                "notes": f"Gene deployment: {status_str}",
            },
            files_changed=allowed,
        )

    return f"Gene '{gene_id}' applied — validation: {status_str}"


def deploy_proposal(proposal_id: str, dry_run: bool = False, force_core: bool = False) -> str:
    p = load_proposal(proposal_id)

    if p["status"] == "deployed":
        return f"SKIP: Proposal '{proposal_id}' already deployed — skipping."
    if p["status"] not in ("approved", "draft"):
        return f"Proposal '{proposal_id}' status is '{p['status']}' - only 'approved' or 'draft' can be deployed"

    action_type = p.get("action_type") or p.get("fix_type", "routing_config")
    print(f"\nDeploying: [{p['priority'].upper()}] {p['title']}")
    print(f"Action: {action_type}")
    print(f"Dry run: {dry_run}\n")

    # ── Blast Radius check (non-gene proposals) ─────────────────────────────
    if action_type != "apply_gene":
        br_ok, br_reason = check_blast_radius(p)
        if not br_ok:
            if "immutable core" in br_reason and force_core:
                print(f"\n⚠️  --force-core override: {br_reason}")
            else:
                if "immutable core" in br_reason:
                    print(f"\n⛔  IMMUTABLE_CORE WARNING: {br_reason}")
                    print("    Re-run with --force-core to override (use with caution).")
                if _EVENT_LOGGER_AVAILABLE:
                    log_event(
                        mutation_type=p.get("mutation_type", "optimize"),
                        outcome={"status": "skipped", "validation_passed": False,
                                 "quality": None, "notes": f"blocked: {br_reason}"},
                    )
                return f"BLOCKED: {br_reason}"

    # ── IMMUTABLE_CORE check on target_file (skip for apply_gene — handled in handler) ──
    target_file = p.get("implementation", {}).get("target_file", "")
    if action_type != "apply_gene" and target_file and _is_immutable(target_file):
        if not force_core:
            print(f"\n⛔  IMMUTABLE_CORE WARNING: proposal targets '{target_file}'")
            print("    Re-run with --force-core to override (use with caution).")
            if _EVENT_LOGGER_AVAILABLE:
                log_event(
                    mutation_type=p.get("mutation_type", "optimize"),
                    outcome={"status": "skipped", "validation_passed": False,
                             "quality": None, "notes": f"blocked: immutable core '{target_file}'"},
                )
            return f"BLOCKED: '{target_file}' is immutable core. Use --force-core."
        print(f"\n⚠️  --force-core override active for immutable path: '{target_file}'")

    def _deploy_note(proposal: dict, dry_run: bool) -> str:
        """Log proposal recommendation as a memory note (no file changes needed)."""
        title = proposal.get("title", "unnamed")
        desc = proposal.get("description", "")
        changes = proposal.get("implementation", {}).get("changes", "")
        note = f"RSI recommendation logged: {title}. {desc} {changes}".strip()
        if dry_run:
            return f"DRY_RUN: would log note: {note[:100]}"
        return f"NOTE_LOGGED: {note[:200]}"

    handlers = {
        "create_skill": lambda p, dr: deploy_create_skill(p, dr),
        "update_skill": lambda p, dr: deploy_create_skill(p, dr),
        "update_soul": lambda p, dr: deploy_update_soul(p, dr, force_core),
        "update_agents": lambda p, dr: deploy_update_soul(p, dr, force_core),
        "fix_routing": lambda p, dr: deploy_fix_routing(p, dr),
        "routing_config": lambda p, dr: deploy_fix_routing(p, dr),
        "update_memory": lambda p, dr: deploy_update_memory(p, dr),
        "add_cron": lambda p, dr: "add_cron: Use cron tool to implement: " + p["implementation"]["changes"],
        "apply_gene": lambda p, dr: deploy_apply_gene(p, dr, force_core),
        # retry_logic / threshold_tuning: emit a memory note, no direct code change
        "retry_logic": lambda p, dr: _deploy_note(p, dr),
        "threshold_tuning": lambda p, dr: _deploy_note(p, dr),
    }

    handler = handlers.get(action_type)
    if not handler:
        return f"No handler for action_type '{action_type}'"

    result = handler(p, dry_run)

    if not dry_run and "ERROR" not in result and "MANUAL" not in result and "BLOCKED" not in result:
        mark_deployed(p, notes=result[:200])
        # === INTEGRATION HOOK: RSI v2 lineage outcome update ===
        try:
            from lineage import LineageStore
            LineageStore().update_outcome(p["id"], "deployed", result[:200])
        except Exception:
            pass
        # Log EvolutionEvent for non-gene deploys
        if _EVENT_LOGGER_AVAILABLE and action_type != "apply_gene":
            log_event(
                mutation_type=p.get("mutation_type", "optimize"),
                outcome={
                    "status": "success",
                    "validation_passed": True,
                    "quality": None,
                    "notes": result[:200],
                },
                files_changed=[target_file] if target_file else [],
            )

    return result

def main():
    parser = argparse.ArgumentParser(description="RSI Deployer - Deploy approved improvement proposals")
    sub = parser.add_subparsers(dest="cmd")

    # deploy command
    dep = sub.add_parser("deploy", help="Deploy a specific proposal")
    dep.add_argument("proposal_id", help="Proposal ID or prefix")
    dep.add_argument("--dry-run", action="store_true", help="Show what would happen without doing it")
    dep.add_argument("--force-core", action="store_true",
                     help="Override IMMUTABLE_CORE protection (requires human approval)")

    # deploy-all command
    dep_all = sub.add_parser("deploy-all", help="Deploy all approved proposals")
    dep_all.add_argument("--dry-run", action="store_true")
    dep_all.add_argument("--force-core", action="store_true",
                         help="Override IMMUTABLE_CORE protection")

    # full-cycle command
    cycle = sub.add_parser("full-cycle", help="Run full RSI cycle: analyze -> synthesize -> auto-deploy low-effort items")
    cycle.add_argument("--days", type=int, default=7)
    cycle.add_argument("--auto-approve-below-mins", type=int, default=20,
                       help="Auto-approve proposals estimated under N minutes effort")
    cycle.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.cmd == "deploy":
        force_core = getattr(args, "force_core", False)
        result = deploy_proposal(args.proposal_id, dry_run=args.dry_run, force_core=force_core)
        print(result)

    elif args.cmd == "deploy-all":
        force_core = getattr(args, "force_core", False)
        from synthesizer import load_all_proposals
        approved = load_all_proposals("approved")
        if not approved:
            print("No approved proposals to deploy.")
            return
        for p in approved:
            print(f"\n--- {p['id']} ---")
            result = deploy_proposal(p["id"], dry_run=args.dry_run, force_core=force_core)
            print(result)

    elif args.cmd == "full-cycle":
        print("=== RSI Full Cycle ===\n")

        # Step 1: Analyze
        print("Step 1: Analyzing outcomes...")
        import analyzer
        data = analyzer.analyze(args.days)
        meta = data["meta"]
        patterns = data["patterns"]
        print(f"  {meta['outcomes']} outcomes | health score: {meta.get('health_score', 'N/A')} | {len(patterns)} patterns found")

        # Step 2: Synthesize
        print("\nStep 2: Synthesizing proposals...")
        import synthesizer
        proposals = synthesizer.generate_proposals_heuristic(patterns, max_proposals=5)
        saved = synthesizer.save_proposals(proposals)
        print(f"  Generated {len(proposals)} proposals")

        # Step 3: Auto-approve low-effort items (skip already deployed)
        print(f"\nStep 3: Auto-approving proposals < {args.auto_approve_below_mins}min effort...")
        auto_approved = []
        for p in proposals:
            if p.get("status") == "deployed":
                print(f"  Skipping {p['id']} (already deployed)")
                continue
            effort = p["implementation"].get("estimated_effort", 999)
            if effort <= args.auto_approve_below_mins:
                p["status"] = "approved"
                synthesizer.save_proposals([p])
                auto_approved.append(p)
                print(f"  Auto-approved: {p['id']} ({effort}min)")

        # Step 3.5: Critique phase (RSI v2)
        if _CRITIQUE_AVAILABLE:
            print(f"\nStep 3.5: Running critique on {len(auto_approved)} proposals...")
            critic = CritiqueAgent()
            critique_passed = []
            for p in auto_approved:
                result = critic.critique(p)
                if result.verdict == "approve":
                    critique_passed.append(p)
                    print(f"  ✓ {p['id']}: approved — {result.reason[:80]}")
                elif result.verdict == "reject":
                    # Update proposal status to rejected
                    p["status"] = "rejected"
                    synthesizer.save_proposals([p])
                    # Update lineage
                    try:
                        from lineage import LineageStore
                        LineageStore().update_outcome(p["id"], "rejected", result.reason[:200])
                    except Exception:
                        pass
                    print(f"  ✗ {p['id']}: REJECTED — {result.reason[:80]}")
                else:  # defer
                    p["status"] = "draft"  # back to draft for manual review
                    synthesizer.save_proposals([p])
                    print(f"  ⏸ {p['id']}: DEFERRED — {result.reason[:80]}")
            auto_approved = critique_passed
        else:
            print("\n(Critique module not available — skipping critique phase)")

        # Step 4: Deploy auto-approved
        print(f"\nStep 4: Deploying {len(auto_approved)} auto-approved proposals...")
        for p in auto_approved:
            result = deploy_proposal(p["id"], dry_run=args.dry_run)
            print(f"  {p['id']}: {result[:100]}")

        # Summary — only count genuinely new (draft) proposals as awaiting review
        remaining = [p for p in proposals if p not in auto_approved and p.get("status") == "draft"]
        print(f"\n=== Cycle Complete ===")
        print(f"  Patterns found: {len(patterns)}")
        print(f"  Proposals generated: {len(proposals)}")
        print(f"  Auto-deployed: {len(auto_approved)}")
        if remaining:
            print(f"  Awaiting review: {len(remaining)} proposals")
            print("  Review with: uv run python skills/rsi-loop/scripts/synthesizer.py list")
        else:
            print(f"  Awaiting review: 0 (all proposals already deployed or auto-approved)")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
