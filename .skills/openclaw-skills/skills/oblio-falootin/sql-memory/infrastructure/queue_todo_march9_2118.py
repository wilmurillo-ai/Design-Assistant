#!/usr/bin/env python3
"""Queue new action items from VeX's TODO.md update (2026-03-09 21:18)."""
import sys, json
sys.path.insert(0, '/home/oblio/.openclaw/workspace')
sys.path.insert(0, '/home/oblio/.openclaw/workspace/infrastructure')
from infrastructure.sql_memory import SQLMemory
m = SQLMemory('cloud')

tasks = [
  # ── Dashboard enhancements ───────────────────────────────────────────
  ('frontend', 'dashboard_center_last_current_next', 'high',
   'Center Last, Current, Next labels in queue view',
   'These labels should be centered, not left-aligned. Verify on dashboard that values update (not just static placeholders).'),

  ('frontend', 'dashboard_model_indicator_line', 'high',
   'Add current model indicator line under avatar in status area',
   'Below "ready" status, show a line: "Using: [model name]" e.g. "Using: ollama/gemma3:4b" or "Using: claude-haiku". Updates per task.'),

  ('frontend', 'dashboard_button_grid_3x3_agents', 'high',
   'Expand button grid from 4 buttons to 3x3 grid; add Agents button top-right',
   'New 3x3 grid: chat | report | queue / logs | ? | ? / agents | ? | ?. Agents button shows per-agent status: name, uptime, last task, next task, task count, learning metrics.'),

  ('frontend', 'dashboard_agents_status_card', 'high',
   'Build agent status card view (shown in body frame when Agents button clicked)',
   'Table/cards showing: agent_name | uptime (hrs:mins) | last_task | next_task | tasks_completed | learning_level (L0-L5). Make it beautiful and satisfying to look at.'),

  ('frontend', 'dashboard_chat_always_on_bottom_right', 'high',
   'Bottom-right icon opens persistent chat using free Ollama (or gpt-4o)',
   'Chat window that uses Ollama (free, local) for quick back-and-forth. VeX can drop random items here without restarting gateway. Persists session context. Separate from main workflow.'),

  # ── SQL & Testing ────────────────────────────────────────────────────
  ('dba_agent', 'verify_all_sql_writes_tested', 'high',
   'Re-examine SQL testing — did we miss .env bug before because tests weren\'t comprehensive?',
   'Review: sql_memory.py unit tests, test coverage for all CRUD operations, mock .env scenarios, verify cloud DB writes in test fixtures. Create comprehensive test suite if missing.'),

  # ── Agent Training & Learning ────────────────────────────────────────
  ('nlp_agent', 'nlp_train_manual_pdf_and_videos', 'high',
   'Queue NLP training from manual.pdf + video clips + Logic & Thought PDFs from Library',
   'Process: manual.pdf (primary), subdirectory video clips (transcribe or describe), /mnt/c/Library/*.pdf (related topics). Agent chunks, summarizes, stores to KnowledgeIndex domain=nlp with training_count incremented per pass. Allow multi-pass learning.'),

  ('lightsound_agent', 'ls_train_avs_journals', 'high',
   'Queue L&S training from AVS Journals + other Light & Sound materials',
   'Process all L&S resources in Library. Agent learns iteratively (can re-read same material multiple times to refine understanding). Store to KnowledgeIndex domain=lightsound.'),

  ('agent_evolution', 'multi_epoch_training_framework', 'high',
   'Design framework where agents can read same materials multiple times (epochs) to refine learning',
   'Each training run = one epoch. Agent stores: domain, topic, material_id, epoch_number, confidence_score, last_updated. Supports progressive refinement. Dashboard shows training_count per agent+domain.'),

  ('agent_validation', 'query_test_framework_for_agents', 'medium',
   'Build query-test system so VeX can validate agent learning ("did you understand X?")',
   'VeX asks agent a question, system compares answer to expected response (via dashboard inline buttons or Telegram). Correct/incorrect vote trains the agent or flags misunderstanding.'),

  # ── File Management & Organization ───────────────────────────────────
  ('oblio_core', 'migrate_md_reports_to_sql', 'high',
   'Move all report *.md files (report-*.md, security-*.md, etc.) to SQL tables',
   'Create memory.SpecializedReports table (agent_id, report_type, period, content). Migrate existing .md files. Keep only dynamic outputs in /logs (don\'t persist).'),

  ('oblio_core', 'create_agent_metadata_table', 'high',
   'Create memory.AgentMetadata table to store per-agent config (like SECURITY-CHECKLIST.md)',
   'Schema: agent_id, charter (goals), threat_model (what we defend), escalation_rules, approved_models, etc. Agents read this at startup instead of .md files.'),

  # ── SQL & Performance ────────────────────────────────────────────────
  ('dba_agent', 'comprehensive_sql_audit', 'high',
   'Full audit of SQL usage, indexes, query plans, and performance bottlenecks',
   'Find: unused tables, missing indexes, slow queries, N+1 patterns. Log findings as GitHub issues. Prioritize by impact. DBA agent should run this weekly.'),
]

queued = 0
for agent, typ, pri, macro, micro in tasks:
    m.queue_task(agent, typ, json.dumps({'macro': macro, 'micro': micro, 'source': 'TODO.md VeX update 2026-03-09 21:18'}), pri)
    print(f'  [{pri:6s}] {agent}/{typ}')
    queued += 1

m.log_event('todo_audit', 'oblio', f'Queued {queued} tasks from TODO.md VeX update (2026-03-09 21:18)', json.dumps({'count': queued}))
print(f'\nDone: {queued} tasks queued')
