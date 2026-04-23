#!/usr/bin/env python3
"""
queue_todo_items.py — One-time script to queue all outstanding TODO items
and store the Task Decomposition Pattern to SQL memory.
"""
import sys, os, json
from pathlib import Path

WORKSPACE = Path('/home/oblio/.openclaw/workspace')
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / 'infrastructure'))

try:
    from dotenv import load_dotenv
    load_dotenv(WORKSPACE / '.env')
except: pass

from infrastructure.sql_memory import SQLMemory

mem = SQLMemory('cloud')

# ── 1. Store Task Decomposition Pattern to SQL memory ────────────────────────
print("Storing Task Decomposition Pattern to SQL...")
mem.remember(
    category='patterns',
    key='task_decomposition_v2',
    content=json.dumps({
        "description": "Recursive MACRO→MICRO task decomposition pattern",
        "rule": "Unless a task is atomic (e.g. 'write this function'), always look at the GOAL the task is meant to accomplish, then create subtasks needed to accomplish that goal. Queue them with MACRO context (why) and MICRO context (how). Agents decide whether to decompose further or execute.",
        "steps": [
            "1. Understand the GOAL — what outcome does this task enable?",
            "2. Break into recursive subtasks — each should be atomic or decomposable",
            "3. Queue with MACRO (why) + MICRO (specific steps)",
            "4. Let agents choose — decompose further OR execute",
            "5. Composition not monoliths — tasks nest like Russian dolls"
        ],
        "parallel_ok": "Identification agent + writing agent can run simultaneously",
        "quality_gates": ["Developer writes + tests", "Security reviews", "Git handler commits + CI"],
        "anti_patterns": ["Execute without understanding goal", "Monolithic tasks", "Silent failures", "Hardcoded credentials"]
    }),
    importance=10,
    tags='architecture,decomposition,agents,core_pattern'
)
print("  ✅ Task Decomposition Pattern stored")

# ── 2. Store 'always write to SQL memory' pattern ────────────────────────────
mem.remember(
    category='patterns',
    key='memory_persistence_rule',
    content=json.dumps({
        "rule": "ALL significant decisions, events, and context MUST be written to SQL (cloud DB). Never rely on markdown alone. Markdown = human-readable notes. SQL = machine-queryable truth.",
        "primary_backend": "cloud (SQL5112.site4now.net / db_99ba1f_memory4oblio)",
        "tables": {
            "Memories": "Long-term facts and patterns (remember/recall)",
            "ActivityLog": "Agent actions and events (log_event)",
            "TaskQueue": "Work to be done (queue_task/get_pending_tasks)",
            "Sessions": "Session context for continuity across restarts",
            "KnowledgeIndex": "Domain knowledge (stamps, NLP, FACS, etc.)"
        },
        "trigger": "On every session start, restore context from Sessions table"
    }),
    importance=10,
    tags='memory,sql,persistence,core_rule'
)
print("  ✅ Memory persistence rule stored")

# ── 3. Queue outstanding TODO items (not already queued) ─────────────────────
print("\nQueuing outstanding TODO items...")

todo_items = [
    # From TODO.md — Immediate Blockers
    {"agent": "infrastructure", "type": "fix_hosts_file", "priority": "high",
     "macro": "DEAUS needs to be resolvable by hostname in WSL for all SQL agents",
     "micro": "Add '10.0.0.110 DEAUS' to /etc/hosts. Run: echo '10.0.0.110 DEAUS' | sudo tee -a /etc/hosts"},

    # From TODO.md — Infrastructure
    {"agent": "infrastructure", "type": "pull_vision_models", "priority": "medium",
     "macro": "Stamp agent needs vision model to identify stamps in images",
     "micro": "On DEAUS run: ollama pull llava && ollama pull moondream. Confirm both accessible at http://10.0.0.110:11434"},

    # From TODO.md — Stamps
    {"agent": "agent_stamps", "type": "run_initial_catalog", "priority": "medium",
     "macro": "33 stamp scan images are queued and need cataloging to build stamps knowledge base",
     "micro": "Run agent_stamps.py. Verify /mnt/c/Library/Stamps/ path, use OpenCV for crop extraction, moondream for identification, store to SQL KnowledgeIndex domain='stamps'"},
    {"agent": "agent_stamps", "type": "dedupe_stamps_md", "priority": "low",
     "macro": "knowledge-base/Stamps/ has existing MDs that may duplicate each other",
     "micro": "Read all MDs in knowledge-base/Stamps/, identify duplicates by stamp ID, merge or remove dupes"},
    {"agent": "agent_stamps", "type": "build_valuation_pipeline", "priority": "low",
     "macro": "Stamps catalog needs estimated values for business purposes (Tripatourium)",
     "micro": "Research Scott catalog API or web lookup. Implement valuation lookup in agent_stamps.py after identification step"},

    # From TODO.md — FACS
    {"agent": "agent_facs", "type": "process_facs_manual", "priority": "medium",
     "macro": "FACS Manual.pdf contains core training data not yet ingested",
     "micro": "Verify pypdf2 installed. Run agent_facs.py targeting Manual.pdf in /mnt/c/Library/. Store extracts to KnowledgeIndex domain='facs'"},
    {"agent": "agent_facs", "type": "process_facs_examples", "priority": "low",
     "macro": "Examples and Practice directories contain supplementary FACS training material",
     "micro": "Process all PDFs/images in Examples + Practice dirs with agent_facs.py"},
    {"agent": "agent_facs", "type": "integrate_body_language_pdfs", "priority": "low",
     "macro": "Body Language PDFs extend FACS training with complementary non-verbal data",
     "micro": "Locate body language PDFs in Library, add to agent_facs.py processing pipeline"},

    # From TODO.md — NLP
    {"agent": "agent_nlp", "type": "process_nlp_materials", "priority": "medium",
     "macro": "NLP training materials (Big Book, Logic & Thought resources) need to be ingested",
     "micro": "Run agent_nlp.py. Target /mnt/c/Library/InBox/Logic & Thought/NLP/. Store to KnowledgeIndex domain='nlp'. Skip already processed files."},

    # From TODO.md — Business
    {"agent": "business_analyst", "type": "tripatourium_seo_audit", "priority": "medium",
     "macro": "Tripatourium.com needs SEO improvements to drive organic traffic to blotter art",
     "micro": "Audit tripatourium.com + Etsy/eBay profiles for SEO. Check title tags, descriptions, keywords, backlinks. Produce recommendations report."},
    {"agent": "business_analyst", "type": "tripatourium_sales_integration", "priority": "medium",
     "macro": "Automate Tripatourium sales across eBay, Etsy, Instagram, Facebook",
     "micro": "Research APIs for each platform. Design integration architecture. Queue subtasks per platform."},
    {"agent": "business_analyst", "type": "tripatourium_website_review", "priority": "low",
     "macro": "Tripatourium website (C#/Razor/SQL) may have performance or code quality issues",
     "micro": "Review website codebase at tripatourium.com. Identify improvements. Queue fix tasks."},
    {"agent": "business_analyst", "type": "tripatourium_swot", "priority": "medium",
     "macro": "Understanding competitive position will guide Tripatourium marketing strategy",
     "micro": "Analyze FP + IG competitors. Build SWOT matrix. Store to knowledge-base/business-plans/"},
    {"agent": "business_analyst", "type": "hftc_project_structure", "priority": "low",
     "macro": "High Falootin Technology Corp needs an umbrella project structure for all VeX projects",
     "micro": "Define project registry doc. Identify all HFTC projects (Tripatourium, Oblio, etc.). Create structure in knowledge-base/"},

    # From TODO.md — Token Alerts
    {"agent": "oblio_core", "type": "implement_token_alerts", "priority": "medium",
     "macro": "VeX needs to be warned before hitting token limits to avoid losing context mid-session",
     "micro": "Add token tracking to main session. Alert at 25%, 50%, 75%, 100% of session token budget. Check at natural breakpoints and warn proactively."},

    # From TODO-highcpu.md — still pending items
    {"agent": "infrastructure", "type": "shared_backup_folder", "priority": "low",
     "macro": "DB backups need to be accessible from both DEAUS and Puck for redundancy",
     "micro": "Share C:\\Library\\Backups on DEAUS. Map from Puck as /mnt/deaus/. Update db_backup.py backup_dir to use share."},

    # Dashboard (core fix just done — but add endpoint tests)
    {"agent": "unit_test_writer", "type": "write_unit_tests", "priority": "high",
     "macro": "server.js dashboard endpoints need tests to prevent regression (they were broken and had no tests)",
     "micro": "Write tests for: /api/logs (returns 200 + logs array), /api/report (returns 200 + report data), /api/queue (returns 200 + tasks array + counts). Use supertest or similar. Mock filesystem + SQL calls."},

    # Memory continuity (VeX is sad we lost Sunday memories)
    {"agent": "oblio_core", "type": "implement_session_restore", "priority": "high",
     "macro": "Oblio lost memories on Sunday — sessions need to save+restore context from SQL so restarts don't lose history",
     "micro": "On session start: query memory.Sessions for last session context. On session end/heartbeat: save current context snapshot to memory.Sessions. Include recent decisions, active tasks, VeX preferences."},
]

queued = 0
for item in todo_items:
    mem.queue_task(
        agent=item['agent'],
        task_type=item['type'],
        payload=json.dumps({
            'macro': item['macro'],
            'micro': item['micro'],
            'source': 'TODO.md / TODO-highcpu.md audit 2026-03-09'
        }),
        priority=item['priority']
    )
    print(f"  ✅ Queued [{item['priority']:6s}] {item['agent']} / {item['type']}")
    queued += 1

print(f"\n{'='*60}")
print(f"COMPLETE: {queued} tasks queued to SQL")
print(f"{'='*60}")

# Log the whole operation
mem.log_event(
    event_type='todo_audit',
    agent='oblio',
    description=f"Queued {queued} outstanding TODO items to TaskQueue. Stored 2 core patterns to SQL memory.",
    metadata=json.dumps({'items_queued': queued, 'patterns_stored': 2})
)
print("ActivityLog entry written ✅")
