"""English UI messages for Phone Agent."""

MESSAGES = {
    "thinking": "Thinking",
    "action": "Action",
    "task_completed": "Task completed",
    "done": "Done",
    "starting_task": "Starting task",
    "final_result": "Final result",
    "task_result": "Task result",
    "confirmation_required": "Confirmation required",
    "continue_prompt": "Continue? (y/n)",
    "manual_operation_required": "Manual action required",
    "manual_operation_hint": "Complete the action manually on the device.",
    "press_enter_when_done": "Press Enter when done",
    "connection_failed": "Connection failed",
    "connection_successful": "Connection successful",
    "step": "Step",
    "task": "Task",
    "result": "Result",
    "performance_metrics": "Performance metrics",
    "time_to_first_token": "Time to first token",
    "time_to_thinking_end": "Time to first command token",
    "total_inference_time": "Total inference time",
}


def get_messages(lang: str = "en") -> dict[str, str]:
    """Return English messages. The `lang` argument is ignored."""

    _ = lang
    return MESSAGES


def get_message(key: str, lang: str = "en") -> str:
    """Return a single English message. The `lang` argument is ignored."""

    _ = lang
    return MESSAGES.get(key, key)
