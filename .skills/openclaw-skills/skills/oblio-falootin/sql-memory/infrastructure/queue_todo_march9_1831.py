#!/usr/bin/env python3
"""Queue all TODO items from VeX's 2026-03-09 18:31 update."""
import sys, json
sys.path.insert(0, '/home/oblio/.openclaw/workspace')
sys.path.insert(0, '/home/oblio/.openclaw/workspace/infrastructure')
from infrastructure.sql_memory import SQLMemory
m = SQLMemory('cloud')

tasks = [
  ('frontend', 'dashboard_layout_two_row', 'high',
   'Redesign dashboard so avatar stays visible while body frame shows dynamic content',
   'Top row: name + 4-icon button grid + status gauges. Bottom row: col1=avatar (constant), col2=body frame. 4 icon buttons switch body content only. Avatar never hides.'),

  ('frontend', 'dashboard_queue_layout', 'high',
   'Queue tab: button bar centered at top, tasks left-aligned with padding below',
   'Filter buttons in centered button bar at top of body frame. Task rows below: left-aligned, padded. Scrollable.'),

  ('frontend', 'dashboard_logs_paged', 'high',
   'Logs tab: paged table, filter toggles (INFO/WARN/ERROR), frozen header, H+V scroll',
   'Top row: record count left + toggle buttons + refresh right. Paged table with footer showing now-showing range. Frozen header. Page size ~50. Toggle colors: INFO=blue, WARNING=yellow, ERROR=red. All on by default.'),

  ('frontend', 'dashboard_report_padding', 'medium',
   'Report body frame needs padding, two blank lines before headers, one after',
   'Add 1rem padding inside report body frame. Format headers with spacing for readability. Archive links must be clickable.'),

  ('frontend', 'dashboard_report_archive_links', 'high',
   'Archive report links in report tab are not clickable - broken regression',
   'loadReportByName(name) must fetch /api/report?name=FILENAME and render it. Each archive link calls this function. Fix immediately.'),

  ('backend', 'reports_store_to_sql', 'high',
   'All 4:20 reports should be stored in SQL not just .md files',
   'After agent_report.py generates a report, INSERT into memory.Reports table. Serve /api/report from SQL. Keep .md as human-readable copy only.'),

  ('dba_agent', 'create_reports_table', 'high',
   'Create memory.Reports SQL table for storing all generated reports',
   'Schema: id INT IDENTITY PK, generated_at DATETIME2, period TEXT, content NVARCHAR(MAX), summary NVARCHAR(1000), shared_at DATETIME2 NULL. Index on generated_at.'),

  ('error_investigator', 'investigate_idle_sql_error', 'high',
   'idle_agent SQL errors must be investigated and resolved before next 4:20 report',
   'Error: SQL failed after 3 attempts: expected str bytes or os.PathLike object not NoneType. Root cause: .env not found from cron. Fix applied to sql_memory.py - verify idle_agent picks it up and errors stop.'),

  ('error_investigator', 'auto_error_to_workitem', 'high',
   'Any ERROR in logs must auto-generate a work item for investigation',
   'In agent_report.py: scan log files for ERROR/CRITICAL lines since last report. For each unique error queue an error_investigator task. Add error count to report. Errors unresolved after 2 reports = CRITICAL escalation to VeX.'),

  ('memory_architect', 'design_memory_rollup_system', 'high',
   'Design tiered memory rollup: Daily to Weekly to Bi-Monthly to Quarterly to Yearly with back-references',
   'Each tier summarizes the tier below. Each entry references source IDs so original memories preserved. Schema: memory.MemoryRollup. Auto-trigger jobs for each rollup tier. DB bloat plan: archive old tiers to cold storage table.'),

  ('memory_architect', 'ponder_llm_vs_sql_memory', 'medium',
   'Evaluate: should specialized agents train their own fine-tuned LLMs vs SQL knowledge base?',
   'Research: for FACS/NLP/stamps - is SQL+RAG sufficient or do we need fine-tuned models? Draft pros/cons recommendation. Log findings as GitHub issue on Oblio-Falootin repo.'),

  ('dba_agent', 'audit_sql_for_stored_procs', 'medium',
   'Review all SQL usage across codebase and identify candidates for stored procedures',
   'Scan all .py files for raw SQL strings. Identify: queue_task, log_event, get_pending_tasks, complete_task, remember, recall. Evaluate each for SP candidacy. Log findings as GitHub issues.'),

  ('dba_agent', 'create_core_stored_procs', 'medium',
   'Create stored procedures for core SQL operations',
   'Write SPs: sp_QueueTask, sp_LogEvent, sp_GetPendingTasks, sp_CompleteTask, sp_FailTask. Update sql_memory.py to call SPs. Test each.'),

  ('dba_agent', 'create_sql_dba_agent', 'medium',
   'Build agent_dba.py: SQL DBA agent for best practices and optimization review',
   'Reviews: indexes, unused tables, query plans, bloat, security. Generates GitHub issues. Runs weekly. Logs to ActivityLog.'),

  ('agent_stamps', 'stamps_write_results_to_sql', 'high',
   'Stamps agent running and identifying stamps but SQL writes failing - verify fix',
   'Root cause was .env not found from cron. sql_memory.py fix applied. Verify stamps_agent.py uses infrastructure.sql_memory. Re-run to flush pending stamps to KnowledgeIndex domain=stamps.'),

  ('nlp_agent', 'nlp_queue_training_tasks', 'high',
   'NLP agent ran but found no pending tasks - queue training materials now',
   'Queue nlp_train tasks for PDFs in /mnt/c/Library/InBox/Logic & Thought/. Each PDF = one task with pdf_path in payload.'),

  ('lightsound_agent', 'ls_queue_training_tasks', 'medium',
   'L&S agent ran but found no pending tasks - queue training materials',
   'Queue ls_train tasks for Light & Sound materials in Library. Agent processes and stores to KnowledgeIndex domain=lightsound.'),

  ('agent_evolution', 'design_agent_readiness_framework', 'high',
   'Define framework for when an agent is ready for autonomous task assignment',
   'Readiness levels: L0=no data, L1=ingested, L2=indexed, L3=can answer queries, L4=can generate tasks, L5=autonomous. Track per agent in SQL. Dashboard widget per agent. VeX can assign tasks to L3+ agents.'),

  ('dispatcher', 'clone_oblio_profile_repo', 'high',
   'Clone Oblio GitHub profile repo and build README with personality',
   'git clone https://github.com/Oblio-Falootin/Oblio-Falootin.git. Write README.md: smart warm funny - fav langs, coding philosophy. Run NLP agent review. Commit and push.'),

  ('dispatcher', 'clone_gaeta_towing', 'high',
   'Clone GaetaTowing site, add gitignore and README, review code and security',
   'git clone https://github.com/VeXHarbinger/gaetatowing.com. Create .gitignore and README.md. Review all links and company info. Code review. Security review. Log findings as GitHub issues.'),

  ('agent_report', 'fix_factoids_from_real_data', 'high',
   'Factoids in 4:20 report must come from actual SQL data not hallucinated content',
   'agent_report.py must query KnowledgeIndex, ActivityLog, TaskQueue for real data. Factoids = real insights from this data. If sparse say so honestly. NEVER invent content. Fix raw data zeroes - ActivityLog uses logged_at not timestamp.'),

  ('agent_report', 'fix_raw_data_zeroes', 'high',
   'Raw data section shows all zeroes but there are completed tasks and activity in SQL',
   'Fix SQL queries in agent_report.py. ActivityLog column is logged_at not timestamp. KnowledgeIndex uses domain/topic. TaskQueue has 17+ completed items. Queries must match actual schema.'),

  ('oblio_core', 'log_errors_to_activity_log', 'high',
   'All agent errors should be logged to ActivityLog so report agent can surface them',
   'Wrap all agent run() methods so uncaught exceptions log to ActivityLog with event_type=error. This feeds the auto-error-to-workitem pipeline.'),
]

queued = 0
for agent, typ, pri, macro, micro in tasks:
    m.queue_task(agent, typ, json.dumps({'macro': macro, 'micro': micro, 'source': 'TODO.md VeX update 2026-03-09 18:31'}), pri)
    print(f'  [{pri:6s}] {agent}/{typ}')
    queued += 1

m.log_event('todo_audit', 'oblio', f'Queued {queued} tasks from TODO.md VeX update 2026-03-09 18:31', json.dumps({'count': queued}))
print(f'\nDone: {queued} tasks queued')
