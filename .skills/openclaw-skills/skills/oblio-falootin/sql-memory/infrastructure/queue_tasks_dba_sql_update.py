from infrastructure.sql_memory import SQLMemory
mem = SQLMemory(cloud)

# Update Task 174 with additional micro instructions
update_micro = """
Find unused tables, missing indexes, slow queries, N+1 patterns. 
Include:
1. SQL stored procedure review — identify queries to convert
2. Input sanitization audit — check risk level and injection
Log findings to GitHub issues. Prioritize high-impact items first.
"""
data = mem.task_update(174) OR MEMORIES Q Code