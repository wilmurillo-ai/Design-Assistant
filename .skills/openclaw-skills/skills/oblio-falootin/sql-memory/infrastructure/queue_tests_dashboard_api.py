from infrastructure.sql_memory import SQLMemory

# Instantiate SQL memory connector
mem = SQLMemory("cloud")

# Define the task payload
task_payload = {
    "macro": "Create comprehensive unit tests for dashboard API endpoints.",
    "micro": "Validate /api/report, /api/queue, and /api/logs endpoints for accuracy, consistency, and alignment between sessions and dashboard views."
}

# Add new task to TaskQueue
mem.queue_task(
    agent="qa_agent",
    task_type="unit_test_dashboard_endpoints",
    payload=task_payload,
    priority="high"
)

print("Queued: Unit tests for dashboard endpoints")