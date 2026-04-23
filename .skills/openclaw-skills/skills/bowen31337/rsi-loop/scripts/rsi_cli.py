#!/usr/bin/env python3
"""
RSI Loop CLI - Unified interface for the Recursive Self-Improvement loop.
Run `uv run python skills/rsi-loop/scripts/rsi_cli.py --help` for usage.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent

def run_script(script: str, args: list) -> int:
    cmd = [sys.executable, str(SCRIPTS_DIR / script)] + args
    result = subprocess.run(cmd)
    return result.returncode

def cmd_gene(args):
    """Handle `gene` subcommands: list, show, validate, stats."""
    import subprocess as _sp
    sys.path.insert(0, str(SCRIPTS_DIR))
    from gene_registry import load_genes, get_gene
    from selector import select_gene

    sub = args.gene_cmd

    if sub == "list":
        genes = load_genes()
        if not genes:
            print("No genes in registry. Run: gene_registry.py")
            return
        print(f"\n{'GENE ID':<45} {'TYPE':<10} {'APPLIED':>7} {'SUCCESS':>8}")
        print("─" * 75)
        for g in genes:
            meta = g.get("meta", {})
            print(
                f"{g['gene_id']:<45} "
                f"{g.get('mutation_type', '?'):<10} "
                f"{meta.get('times_applied', 0):>7} "
                f"{meta.get('success_rate', 0.0):>7.0%}"
            )
        print(f"\n{len(genes)} gene(s) in registry.")

    elif sub == "show":
        gene = get_gene(args.gene_id)
        if gene is None:
            print(f"Gene '{args.gene_id}' not found.")
            sys.exit(1)
        print(json.dumps(gene, indent=2))

    elif sub == "validate":
        gene = get_gene(args.gene_id)
        if gene is None:
            print(f"Gene '{args.gene_id}' not found.")
            sys.exit(1)
        commands = gene.get("validation", {}).get("commands", [])
        if not commands:
            print("No validation commands defined for this gene.")
            return
        print(f"\nValidating gene: {gene['gene_id']}")
        print(f"Running {len(commands)} command(s)...\n")
        all_passed = True
        for i, cmd in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] $ {cmd}")
            result = _sp.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"  ✓ PASSED")
                if result.stdout.strip():
                    print(f"    {result.stdout.strip()[:200]}")
            else:
                all_passed = False
                print(f"  ✗ FAILED (exit {result.returncode})")
                if result.stderr.strip():
                    print(f"    {result.stderr.strip()[:200]}")
        print(f"\nResult: {'ALL PASSED ✓' if all_passed else 'SOME FAILED ✗'}")

    elif sub == "stats":
        genes = load_genes()
        if not genes:
            print("No genes in registry.")
            return
        # Group by mutation_type
        from collections import defaultdict
        groups = defaultdict(list)
        for g in genes:
            groups[g.get("mutation_type", "unknown")].append(g)
        print(f"\n{'MUTATION TYPE':<15} {'GENES':>6} {'TOTAL APPLIED':>14} {'AVG SUCCESS':>12}")
        print("─" * 52)
        for mtype, glist in sorted(groups.items()):
            total_applied = sum(g["meta"].get("times_applied", 0) for g in glist)
            applied_genes = [g for g in glist if g["meta"].get("times_applied", 0) > 0]
            if applied_genes:
                avg_success = sum(g["meta"].get("success_rate", 0) for g in applied_genes) / len(applied_genes)
            else:
                avg_success = 0.0
            print(
                f"{mtype:<15} {len(glist):>6} {total_applied:>14} {avg_success:>11.0%}"
            )

    else:
        print(f"Unknown gene subcommand: '{sub}'")
        print("Available: list, show <gene_id>, validate <gene_id>, stats")
        sys.exit(1)


def cmd_status(args):
    """Show overall RSI loop status."""
    from observer import stats_summary, load_outcomes
    from analyzer import load_patterns, compute_repair_ratio, should_force_innovate
    from synthesizer import load_all_proposals

    print("\n=== RSI Loop Status ===\n")

    # Outcomes
    stats = stats_summary(7)
    if stats["total"] == 0:
        print("Outcomes: No data yet. Start logging with: rsi_cli.py log ...")
    else:
        print(f"Outcomes (7d): {stats['total']} logged | "
              f"Success: {stats['success_rate']*100:.0f}% | "
              f"Avg quality: {stats['avg_quality']}/5")
        if stats.get("top_issues"):
            issues = ", ".join(f"{k}({v})" for k, v in stats["top_issues"][:3])
            print(f"  Top issues: {issues}")

    # Patterns
    data = load_patterns()
    if data:
        meta = data.get("meta", {})
        patterns = data.get("patterns", [])
        print(f"\nPatterns: {len(patterns)} detected | "
              f"Health score: {meta.get('health_score', 'N/A')} | "
              f"Analyzed: {meta.get('generated_at', 'unknown')[:10]}")
        for p in patterns[:3]:
            print(f"  [{p['impact_score']:.3f}] {p['description'][:70]}")
    else:
        print("\nPatterns: Not analyzed yet. Run: rsi_cli.py analyze")

    # Proposals
    all_proposals = load_all_proposals()
    draft = [p for p in all_proposals if p["status"] == "draft"]
    approved = [p for p in all_proposals if p["status"] == "approved"]
    deployed = [p for p in all_proposals if p["status"] == "deployed"]

    print(f"\nProposals: {len(draft)} draft | {len(approved)} approved | {len(deployed)} deployed")

    if approved:
        print("  Ready to deploy:")
        for p in approved:
            print(f"  - {p['id']}: {p['title'][:60]}")
            print(f"    Deploy: uv run python skills/rsi-loop/scripts/rsi_cli.py deploy {p['id']}")

    # Repair ratio (Phase 3 — only if --repair-ratio flag)
    if getattr(args, "repair_ratio", False):
        try:
            from event_logger import load_events
            events = load_events()
            ratio = compute_repair_ratio(events)
            force_innovate = should_force_innovate()
            total_events = len(events)
            print(f"\nRepair Ratio (last 8 cycles): {ratio:.0%} "
                  f"[{total_events} total events]")
            if force_innovate:
                print("  ⚠️  Stagnation detected — next cycle will force INNOVATE")
            else:
                print("  ✓ No stagnation detected")
        except Exception as e:
            print(f"\nRepair Ratio: unavailable ({e})")

    print("\nQuick actions:")
    print("  uv run python skills/rsi-loop/scripts/rsi_cli.py cycle   # Run full RSI cycle")
    print("  uv run python skills/rsi-loop/scripts/rsi_cli.py log     # Log a turn outcome")


def cmd_events(args):
    """Show last N EvolutionEvents."""
    from event_logger import load_events

    last_n = getattr(args, "last", 10)
    events = load_events(last_n=last_n)

    if not events:
        print("No EvolutionEvents logged yet.")
        print("Events are written to data/events.jsonl during synthesis and deploy cycles.")
        return

    print(f"\n=== Last {len(events)} EvolutionEvent(s) ===\n")
    print(f"{'EVENT ID':<25} {'TYPE':<10} {'STATUS':<10} {'GENE':<40} {'TIMESTAMP'}")
    print("─" * 110)
    for e in events:
        event_id = e.get("event_id", "?")
        mtype = e.get("mutation_type", "?")
        status = e.get("outcome", {}).get("status", "?")
        gene = e.get("gene_id") or "-"
        ts = e.get("timestamp", "")[:19]
        print(f"{event_id:<25} {mtype:<10} {status:<10} {gene:<40} {ts}")

    print(f"\n{len(events)} event(s) shown.")
    if events:
        last = events[-1]
        signals = last.get("signals", {})
        print(f"\nLatest signals:")
        print(f"  Top pattern:       {signals.get('top_pattern', '-')}")
        print(f"  Repair ratio (8):  {signals.get('repair_ratio_last8', 0):.0%}")
        print(f"  Forced innovate:   {signals.get('forced_innovate', False)}")
        notes = last.get("outcome", {}).get("notes", "")
        if notes:
            print(f"  Notes:             {notes[:80]}")


def cmd_personality(args):
    """Show current PersonalityState with bias."""
    from personality import load_personality

    p = load_personality()
    stats = p.get("stats", {})
    ns = p.get("natural_selection", {})
    traits = p.get("trait_scores", {})

    print("\n=== PersonalityState ===\n")
    print(f"Current bias:     {p.get('current_bias', 'balanced').upper()}")
    print(f"Updated:          {p.get('updated_at', '?')[:19]}")
    print()
    print("Mutation Stats:")
    for mtype in ("repair", "optimize", "innovate"):
        total = stats.get(f"{mtype}_total", 0)
        rate = stats.get(f"{mtype}_success_rate", 0.0)
        bar = "█" * int(rate * 10) + "░" * (10 - int(rate * 10))
        print(f"  {mtype:<10}  {bar}  {rate:.0%}  ({total} total)")

    print()
    print("Trait Scores:")
    for trait, score in traits.items():
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        print(f"  {trait:<12}  {bar}  {score:.2f}")

    print()
    print("Natural Selection:")
    print(f"  Total cycles:          {ns.get('total_cycles', 0)}")
    print(f"  Successful repairs:    {ns.get('successful_repairs', 0)}")
    print(f"  Successful innovations:{ns.get('successful_innovations', 0)}")

def main():
    parser = argparse.ArgumentParser(
        description="RSI Loop - Recursive Self-Improvement for EvoClaw agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  status    Show RSI loop status
  log       Log a turn outcome (observer)
  analyze   Detect patterns from outcomes
  propose   Generate improvement proposals
  approve   Approve a proposal for deployment
  deploy    Deploy an approved proposal
  cycle     Run full RSI cycle (analyze + propose + deploy)

Examples:
  # Log a successful code generation task
  rsi_cli.py log --task code_generation --success true --quality 4 --model glm-4.7

  # Log a failed task with issue
  rsi_cli.py log --task code_debug --success false --quality 2 --issues skill_gap --notes "No skill for Rust debugging"

  # Run full improvement cycle
  rsi_cli.py cycle

  # Manual workflow
  rsi_cli.py analyze
  rsi_cli.py propose
  rsi_cli.py approve <id>
  rsi_cli.py deploy <id>
        """
    )
    sub = parser.add_subparsers(dest="cmd")

    # status
    status_p = sub.add_parser("status", help="Show RSI loop status")
    status_p.add_argument("--repair-ratio", action="store_true",
                          help="Include stagnation repair ratio in output")

    # log
    log_p = sub.add_parser("log", help="Log a turn outcome")
    log_p.add_argument("--task", required=True, help="Task type")
    log_p.add_argument("--success", required=True, choices=["true", "false"])
    log_p.add_argument("--quality", type=int, default=3)
    log_p.add_argument("--model", default="")
    log_p.add_argument("--duration-ms", type=int, default=0)
    log_p.add_argument("--issues", nargs="*", default=[])
    log_p.add_argument("--tags", nargs="*", default=[])
    log_p.add_argument("--notes", default="")
    log_p.add_argument("--agent-id", default="main")

    # analyze
    analyze_p = sub.add_parser("analyze", help="Detect patterns from logged outcomes")
    analyze_p.add_argument("--days", type=int, default=7)
    analyze_p.add_argument("--top", type=int, default=5)

    # propose
    propose_p = sub.add_parser("propose", help="Generate improvement proposals")
    propose_p.add_argument("--top", type=int, default=5)

    # approve
    approve_p = sub.add_parser("approve", help="Approve a proposal")
    approve_p.add_argument("proposal_id")

    # reject
    reject_p = sub.add_parser("reject", help="Reject a proposal")
    reject_p.add_argument("proposal_id")

    # deploy
    deploy_p = sub.add_parser("deploy", help="Deploy an approved proposal")
    deploy_p.add_argument("proposal_id")
    deploy_p.add_argument("--dry-run", action="store_true")

    # cycle
    cycle_p = sub.add_parser("cycle", help="Run full RSI cycle")
    cycle_p.add_argument("--days", type=int, default=7)
    cycle_p.add_argument("--auto-approve-below-mins", type=int, default=20)
    cycle_p.add_argument("--dry-run", action="store_true")
    cycle_p.add_argument("--auto", action="store_true",
                         help="Run auto-fix for safe categories after analysis")

    # gene
    gene_p = sub.add_parser("gene", help="Manage the Gene registry")
    gene_sub = gene_p.add_subparsers(dest="gene_cmd")
    gene_sub.add_parser("list", help="List all genes")
    gene_show = gene_sub.add_parser("show", help="Show full gene JSON")
    gene_show.add_argument("gene_id")
    gene_val = gene_sub.add_parser("validate", help="Run validation commands for a gene")
    gene_val.add_argument("gene_id")
    gene_sub.add_parser("stats", help="Success rate per mutation type")

    # events (Phase 2 — EvolutionEvent audit log)
    events_p = sub.add_parser("events", help="Show EvolutionEvent audit log")
    events_p.add_argument("--last", type=int, default=10,
                          help="Show last N events (default: 10)")

    # auto-observe
    ao_p = sub.add_parser("auto-observe", help="Feed task outcomes programmatically (JSON)")
    ao_p.add_argument("--input", "-i", required=True, help="JSON string with task outcome")
    ao_p.add_argument("--quiet", "-q", action="store_true")

    # auto-fix
    af_p = sub.add_parser("auto-fix", help="Attempt to auto-fix a detected pattern")
    af_p.add_argument("--pattern-id", "-p", help="Pattern ID to fix")
    af_p.add_argument("--all-safe", action="store_true", help="Fix all safe-category patterns")
    af_p.add_argument("--dry-run", action="store_true")

    # personality (Phase 3 — PersonalityState)
    sub.add_parser("personality", help="Show current PersonalityState with bias")

    # === RSI v2 subcommands ===

    # lineage
    lineage_p = sub.add_parser("lineage", help="Show proposal lineage tree")
    lineage_p.add_argument("--node", help="Show lineage for specific proposal ID")
    lineage_p.add_argument("--format", choices=["tree", "json", "flat"], default="tree")

    # kb
    kb_p = sub.add_parser("kb", help="Query or update knowledge base")
    kb_sub = kb_p.add_subparsers(dest="kb_cmd")
    kb_query_p = kb_sub.add_parser("query", help="Query KB for relevant entries")
    kb_query_p.add_argument("--issue", default="")
    kb_query_p.add_argument("--task-type", default="")
    kb_query_p.add_argument("--category", default="")
    kb_query_p.add_argument("--top", type=int, default=3)
    kb_sub.add_parser("update", help="Update KB from lineage history")
    kb_sub.add_parser("stats", help="Show KB statistics")

    args = parser.parse_args()

    if args.cmd == "status":
        sys.path.insert(0, str(SCRIPTS_DIR))
        from observer import stats_summary
        from analyzer import load_patterns
        from synthesizer import load_all_proposals
        cmd_status(args)

    elif args.cmd == "log":
        extra = []
        if args.issues:
            extra += ["--issues"] + args.issues
        if args.tags:
            extra += ["--tags"] + args.tags
        run_script("observer.py", [
            "log",
            "--task", args.task,
            "--success", args.success,
            "--quality", str(args.quality),
            "--model", args.model,
            "--duration-ms", str(args.duration_ms),
            "--notes", args.notes,
            "--agent-id", args.agent_id,
        ] + extra)

    elif args.cmd == "analyze":
        run_script("analyzer.py", ["--days", str(args.days), "--top", str(args.top)])

    elif args.cmd == "propose":
        run_script("synthesizer.py", ["generate", "--top", str(args.top)])

    elif args.cmd == "approve":
        run_script("synthesizer.py", ["approve", args.proposal_id])

    elif args.cmd == "reject":
        run_script("synthesizer.py", ["reject", args.proposal_id])

    elif args.cmd == "deploy":
        extra = ["--dry-run"] if args.dry_run else []
        run_script("deployer.py", ["deploy", args.proposal_id] + extra)

    elif args.cmd == "cycle":
        extra = []
        if args.dry_run:
            extra.append("--dry-run")
        run_script("deployer.py", [
            "full-cycle",
            "--days", str(args.days),
            "--auto-approve-below-mins", str(args.auto_approve_below_mins),
        ] + extra)

        # Auto-fix for safe categories if --auto
        if getattr(args, "auto", False):
            print("\n=== Auto-Fix Phase ===")
            sys.path.insert(0, str(SCRIPTS_DIR))
            from auto_fix import auto_fix_all_safe
            results = auto_fix_all_safe(dry_run=args.dry_run)
            for r in results:
                if "error" in r:
                    print(f"  ✗ {r['error']}")
                else:
                    p = r["proposal"]
                    print(f"  📝 [{p['id']}] {p['title'][:70]}")
            if not results:
                print("  No patterns in safe/high-severity categories.")

    elif args.cmd == "gene":
        sys.path.insert(0, str(SCRIPTS_DIR))
        if not args.gene_cmd:
            gene_p.print_help()
        else:
            cmd_gene(args)

    elif args.cmd == "events":
        sys.path.insert(0, str(SCRIPTS_DIR))
        cmd_events(args)

    elif args.cmd == "auto-observe":
        sys.path.insert(0, str(SCRIPTS_DIR))
        from auto_observe import auto_observe
        input_data = json.loads(args.input)
        result = auto_observe(input_data)
        if not args.quiet:
            record = result["record"]
            print(f"Logged: {record['id']} | {record['source']} | {record['task_type']} | "
                  f"success={record['success']} | quality={record['quality']} | "
                  f"issues={record.get('issues', [])}")
            if result["recurrence_flags"]:
                print("\n⚠️  RECURRING PATTERNS DETECTED:")
                for flag in result["recurrence_flags"]:
                    severity = "🔴" if flag["severity"] == "high" else "🟡"
                    print(f"  {severity} {flag['issue']}: {flag['count']}x in {flag['days']} days")
        else:
            print(json.dumps(result))

    elif args.cmd == "auto-fix":
        sys.path.insert(0, str(SCRIPTS_DIR))
        from auto_fix import auto_fix, auto_fix_all_safe
        if args.all_safe:
            results = auto_fix_all_safe(dry_run=args.dry_run)
            for r in results:
                if "error" in r:
                    print(f"  ✗ {r['error']}")
                else:
                    p = r["proposal"]
                    print(f"  📝 [{p['id']}] {p['title'][:70]}")
            if not results:
                print("No patterns in safe/high-severity categories.")
        elif args.pattern_id:
            result = auto_fix(args.pattern_id, dry_run=args.dry_run)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                p = result["proposal"]
                print(f"Proposal: {p['id']} | {p['title'][:70]}")
                print(f"  Saved to: {result.get('proposal_path', 'N/A')}")
        else:
            print("Specify --pattern-id <id> or --all-safe")

    elif args.cmd == "personality":
        sys.path.insert(0, str(SCRIPTS_DIR))
        cmd_personality(args)

    elif args.cmd == "lineage":
        sys.path.insert(0, str(SCRIPTS_DIR))
        from lineage import LineageStore
        store = LineageStore()

        if args.node:
            node = store.get_node(args.node)
            if not node:
                print(f"Node '{args.node}' not found in lineage.")
                sys.exit(1)
            ancestors = store.get_ancestors(args.node)
            descendants = store.get_descendants(args.node)

            print(f"\n=== Lineage for {args.node} ===\n")
            print(f"Node: {node.id} | {node.issue} | {node.outcome}")
            print(f"  Proposal: {node.proposal_text[:80]}")
            print(f"  Parent: {node.parent_id or '(root)'}")
            print(f"  Timestamp: {node.timestamp[:19]}")

            if ancestors:
                print(f"\nAncestors ({len(ancestors)}):")
                for a in ancestors:
                    print(f"  ← {a.id}: {a.proposal_text[:60]} [{a.outcome}]")

            if descendants:
                print(f"\nDescendants ({len(descendants)}):")
                for d in descendants:
                    print(f"  → {d.id}: {d.proposal_text[:60]} [{d.outcome}]")
        else:
            # Show full tree
            tree = store.get_lineage_tree()
            all_nodes = {n.id: n for n in store.load_all()}
            roots = tree.get("__roots__", [])

            if not all_nodes:
                print("No lineage data yet. Run a cycle to generate proposals.")
                sys.exit(0)

            if args.format == "json":
                print(json.dumps(tree, indent=2))
            elif args.format == "flat":
                print(f"\n{'ID':<12} {'PARENT':<12} {'ISSUE':<20} {'OUTCOME':<12} {'TITLE'}")
                print("─" * 90)
                for n in all_nodes.values():
                    print(f"{n.id:<12} {(n.parent_id or '-'):<12} "
                          f"{n.issue:<20} {n.outcome:<12} {n.proposal_text[:40]}")
            else:  # tree format
                print(f"\n=== Proposal Lineage Tree ({len(all_nodes)} nodes) ===\n")

                def print_tree(node_id: str, indent: int = 0):
                    node = all_nodes.get(node_id)
                    if not node:
                        return
                    prefix = "  " * indent + ("├─ " if indent > 0 else "")
                    outcome_icon = {"deployed": "✓", "rejected": "✗", "pending": "…", "superseded": "→"}.get(node.outcome, "?")
                    print(f"{prefix}[{outcome_icon}] {node.id}: {node.proposal_text[:50]} ({node.issue})")
                    children = tree.get(node_id, [])
                    for child_id in children:
                        print_tree(child_id, indent + 1)

                for root_id in roots:
                    print_tree(root_id)

                # Show orphaned nodes (parent_id set but parent not in lineage)
                orphans = [n for n in all_nodes.values()
                           if n.parent_id and n.parent_id not in all_nodes and n.id not in roots]
                if orphans:
                    print(f"\nOrphaned nodes ({len(orphans)}):")
                    for o in orphans:
                        print(f"  [?] {o.id}: {o.proposal_text[:50]} (parent {o.parent_id} missing)")

    elif args.cmd == "kb":
        sys.path.insert(0, str(SCRIPTS_DIR))
        if not args.kb_cmd:
            kb_p.print_help()
        elif args.kb_cmd == "query":
            from kb_manager import kb_query_cli
            results = kb_query_cli(
                issue=args.issue,
                task_type=args.task_type,
                category=args.category,
                top_k=args.top,
            )
            if not results:
                print("No matching KB entries found.")
            else:
                print(f"\nTop {len(results)} KB results:\n")
                for r in results:
                    print(f"  [{r['score']:.1f}] {r['reference']}")
        elif args.kb_cmd == "update":
            from kb_manager import kb_update_cli
            stats = kb_update_cli()
            print(f"KB updated: {stats['added']} added, {stats['updated']} updated")
        elif args.kb_cmd == "stats":
            from kb_manager import KBManager
            kb = KBManager()
            for kind, label in [("failure", "Failure"), ("success", "Success"), ("anti", "Anti")]:
                entries = kb._parse_entries(kb._get_filepath(kind))
                print(f"  {label} patterns: {len(entries)}")
                for e in entries[:3]:
                    print(f"    - {e.id}: {e.title[:60]} ({e.occurrences} occurrences)")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
