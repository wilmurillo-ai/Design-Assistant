from infrastructure.sql_memory import SQLMemory

# Instantiate SQL memory connector
mem = SQLMemory("cloud")

# Create task for adding positive feedback button
task_payload = {
    "macro": "Add Positive Feedback Button under Avatar (second row, left column)",
    "micro": "Add a clickable Praise button under avatar. On click, sends a POST to /api/feedback with metadata (timestamp, praise_type, optional message). Log feedback to SQL for visualization."
}

mem.queue_task(
    agent="frontend",
    task_type="dashboard_add_praise_button",
    payload=task_payload,
    priority="high"
)

print("Queued: Positive Feedback Button Task")