#!/usr/bin/env python3
"""Queue all NEW items from VeX's TODO.md update (2026-03-10 00:19)."""
import sys, json
sys.path.insert(0, '/home/oblio/.openclaw/workspace')
sys.path.insert(0, '/home/oblio/.openclaw/workspace/infrastructure')
from infrastructure.sql_memory import SQLMemory
m = SQLMemory('cloud')

tasks = [
  # ── SQL Testing & Verification ───────────────────────────────────────
  ('qa_agent', 'comprehensive_sql_write_testing', 'high',
   'Test all SQL write operations to ensure data integrity',
   'Create test fixtures for: queue_task (verify ID returned), log_event (verify logged_at), remember/recall (verify retrieval), complete_task (verify status update). Run from cron context to catch .env issues. Report pass/fail for each operation.'),

  ('qa_agent', 'unit_test_sql_operations', 'high',
   'Write unit tests for sql_memory.py covering all CRUD operations',
   'Tests must cover: cloud backend, local backend (if applicable), .env loading, error handling, timeouts. Fixtures should mock SQL responses. Achieve 80%+ coverage. Run in CI/CD before deployment.'),

  # ── File Organization & Cleanup ──────────────────────────────────────
  ('oblio_core', 'cleanup_workspace_md_files', 'high',
   'Remove random .md report files from workspace root (move to SQL)',
   'Find and migrate: SPRINT_COMPLETE_*.md, STATUS_LIVE_*.md, and any other non-essential .md files. Content goes to memory.SpecializedReports table (agent_id, report_type, period, content). Delete .md after migration. Daily task to keep workspace tidy.'),

  ('oblio_core', 'create_agent_metadata_sql_table', 'high',
   'Create memory.AgentMetadata table for agent config (charter, threat model, etc.)',
   'Schema: agent_id, charter (goals/mission), threat_model (security concerns), escalation_rules (when to ask VeX), approved_models (which LLMs can use), max_retries, timeout_secs, created_at, updated_at. Agents read this at startup instead of .md files.'),

  ('maintenance', 'daily_workspace_tidiness_check', 'medium',
   'Daily task to scan workspace for stray files and organize',
   'Look for: *.md files outside /logs and /memory, leftover temp files, build artifacts. Move to appropriate location or delete. Report findings. Keep workspace clean for faster navigation and mental clarity.'),

  # ── Dashboard Visual Improvements ────────────────────────────────────
  ('frontend', 'dashboard_center_labels_and_add_model', 'high',
   'Center Last/Current/Next labels and add current model indicator',
   'In queue view header: center the "Last | Current | Next" labels. Below avatar status ("ready"), add one-line model indicator: "Using: [model name]" (e.g., "Using: ollama/gemma3:4b" or "Using: claude-haiku"). Updates per task execution.'),

  ('frontend', 'dashboard_3x3_button_grid_agents_view', 'high',
   'Expand 4-button grid to 3x3 with new Agents button (top-right)',
   'New grid layout: chat | report | queue / logs | [empty] | [empty] / agents | [empty] | [empty]. Agents button shows per-agent status card in body frame: agent_name | uptime | last_task | next_task | tasks_completed | learning_level (L0-L5).'),

  ('frontend', 'dashboard_persistent_chat_bottom_right', 'high',
   'Bottom-right icon: persistent chat using free Ollama (no gateway restart needed)',
   'Chat window that persists across page refreshes. Uses Ollama (free local model, ~2s latency acceptable). VeX can drop random thoughts/updates without restarting gateway. Separate context from main workflow tasks. Send button queues to informal_notes or similar.'),

  ('frontend', 'dashboard_report_body_padding', 'medium',
   'Add padding to report body frame so content doesn\'t press against border',
   'Apply 1rem padding to .body-frame or report-content div. Improves readability. Also add two blank lines before headers, one after (markdown formatting improvement).'),

  # ── GitHub Integration ───────────────────────────────────────────────
  ('oblio_core', 'process_github_contributor_access', 'high',
   'Acknowledge and configure access to 4 new GitHub repos where Oblio is contributor',
   'Repos: VeXHarbinger/timeline, VeXHarbinger/VeXHarbinger, VeXHarbinger/BlazorAnalytics, VeXHarbinger/Tripatourium. Verify GITHUB_TOKEN in .env works for each repo. Clone locally to workspace/github-repos/. Document each repo purpose. Queue initial review tasks per repo.'),

  # ── Personal Context & Learning ──────────────────────────────────────
  ('oblio_core', 'process_vex_personal_context_files', 'high',
   'Read and process all files in C:\\Library\\InBox\\Personal\\ (esp. Alex Pearlstein_2025_R19.pdf)',
   'Extract: education, work history, technical philosophy, strengths, weak points, communication preferences. Move processed files to C:\\Library\\Processed\\. Store key insights in memory.Memories table (domain=vex_context). This context will shape how we communicate and collaborate.'),

  ('oblio_core', 'ingest_inbox_files_to_knowledge_base', 'high',
   'Process ALL files in C:\\Library\\InBox\\ (PDFs, docs, spreadsheets, etc.) and move to Processed',
   'For each file: determine content type (personal, technical, business, training). Extract key info. Store to appropriate KnowledgeIndex domain. Move to Processed/ after ingestion. This is a one-time backfill + builds foundation for Oblio\'s understanding of VeX and context.'),

  ('oblio_core', 'store_vex_developer_profile', 'medium',
   'Create memory entry: VeX is 26+ year developer with deep SOLID/DI knowledge',
   'This context shapes communication style. VeX doesn\'t need basics explained. Can use technical language directly. SOLID principles + design patterns can be assumed. This is a key insight for agent interactions and technical discussions.'),
]

queued = 0
for agent, typ, pri, macro, micro in tasks:
    m.queue_task(agent, typ, json.dumps({'macro': macro, 'micro': micro, 'source': 'TODO.md VeX update 2026-03-10 00:19'}), pri)
    print(f'  [{pri:6s}] {agent}/{typ}')
    queued += 1

m.log_event('todo_audit', 'oblio', f'Queued {queued} tasks from TODO.md VeX update (2026-03-10 00:19)', json.dumps({'count': queued}))
print(f'\nDone: {queued} tasks queued')
