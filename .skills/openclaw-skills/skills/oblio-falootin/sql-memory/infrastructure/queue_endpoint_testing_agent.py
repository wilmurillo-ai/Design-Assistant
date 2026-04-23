from infrastructure.sql_memory import SQLMemory

# Instantiate SQL memory connector
mem = SQLMemory("cloud")

# Define the task payload
task_payload = {
    "macro": "Build an Endpoint Testing Agent for API health & unit tests.",
    "micro": "Scan all REST API endpoints to auto-generate missing unit tests and validate adherence to standard HTTP best practices (e.g., proper response codes: 200, 401, 404). Prioritize endpoints without existing tests."
}

# Add new task to TaskQueue
mem.queue_task(
    agent="qa_agent",
    task_type="create_endpoint_testing_agent",
    payload=task_payload,
    priority="high"
)

print("Queued: Endpoint Testing Agent task")