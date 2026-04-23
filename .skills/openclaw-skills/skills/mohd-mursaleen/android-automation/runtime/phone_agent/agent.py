"""Main PhoneAgent class for orchestrating Android automation."""

import base64
import json
import os
import tempfile
import traceback
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Callable

from PIL import Image

from phone_agent.actions import ActionHandler
from phone_agent.actions.handler import finish, parse_action
from phone_agent.config import get_messages, get_system_prompt
from phone_agent.device_factory import get_device_factory
from phone_agent.model import ModelClient, ModelConfig
from phone_agent.model.client import MessageBuilder


@dataclass
class AgentConfig:
    """Configuration for the PhoneAgent."""

    max_steps: int = 100
    device_id: str | None = None
    lang: str = "en"
    system_prompt: str | None = None
    verbose: bool = True

    def __post_init__(self) -> None:
        if self.system_prompt is None:
            self.system_prompt = get_system_prompt(self.lang)


@dataclass
class StepResult:
    """Result of a single agent step."""

    success: bool
    finished: bool
    action: dict[str, Any] | None
    thinking: str
    message: str | None = None


class PhoneAgent:
    """AI-powered agent for Android phone automation."""

    _MAX_REPLAN_ATTEMPTS = 4
    _SCREEN_HASH_DISTANCE_THRESHOLD = 24
    _MAX_SCREEN_VISITS_BEFORE_STOP = 3
    _MIN_DISTINCT_FAILED_ACTIONS_BEFORE_STOP = 2
    _SCREEN_HISTORY_WINDOW = 6
    _MAX_UNIQUE_SCREENS_IN_LOOP = 2

    def __init__(
        self,
        model_config: ModelConfig | None = None,
        agent_config: AgentConfig | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
        progress_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self.model_config = model_config or ModelConfig()
        self.agent_config = agent_config or AgentConfig()

        self.model_client = ModelClient(self.model_config)
        self.action_handler = ActionHandler(
            device_id=self.agent_config.device_id,
            confirmation_callback=confirmation_callback,
            takeover_callback=takeover_callback,
        )
        self.progress_callback = progress_callback

        self._context: list[dict[str, Any]] = []
        self._step_count = 0
        self._last_action: dict[str, Any] | None = None
        self._current_task: str | None = None
        self._last_app: str | None = None
        self._last_screen_key: str | None = None
        self._screen_visit_counts: dict[str, int] = {}
        self._screen_action_counts: dict[str, dict[str, int]] = {}
        self._screen_failed_actions: dict[str, dict[str, int]] = {}
        self._screen_representatives: dict[str, str] = {}
        self._last_action_by_screen: dict[str, str] = {}
        self._recent_screen_keys: list[str] = []
        self._recent_attempt_summaries: list[str] = []
        self._last_transition_summary: str | None = None

    def _emit_progress(
        self,
        *,
        state: str,
        message: str = "",
        current_app: str = "",
        action: dict[str, Any] | None = None,
        screen_description: str = "",
    ) -> None:
        """Report a lightweight runtime heartbeat to the outer wrapper."""

        if self.progress_callback is None:
            return

        try:
            payload: dict[str, Any] = {
                "state": state,
                "message": message,
                "step": self._step_count,
                "current_app": current_app,
                "screenshot_path": self._get_latest_screenshot_path(),
            }
            action_signature = self._format_action_signature(action or {})
            if action_signature:
                payload["last_action"] = action_signature
            if screen_description:
                payload["screen_description"] = screen_description
            self.progress_callback(payload)
        except Exception:
            if self.agent_config.verbose:
                print("Warning: could not update runtime progress heartbeat.")

    def run(self, task: str) -> str:
        """Run the agent until it finishes or reaches the step limit."""

        self.reset()
        result = self._execute_step(task, is_first=True)

        if result.finished:
            return result.message or "Task completed"

        while self._step_count < self.agent_config.max_steps:
            result = self._execute_step(is_first=False)
            if result.finished:
                return result.message or "Task completed"

        return "Max steps reached"

    def step(self, task: str | None = None) -> StepResult:
        """Execute a single agent step."""

        is_first = len(self._context) == 0
        if is_first and not task:
            raise ValueError("Task is required for the first step.")
        return self._execute_step(task, is_first=is_first)

    def reset(self) -> None:
        """Reset the agent state for a new task."""

        self._context = []
        self._step_count = 0
        self._last_action = None
        self._current_task = None
        self._last_app = None
        self._last_screen_key = None
        self._screen_visit_counts = {}
        self._screen_action_counts = {}
        self._screen_failed_actions = {}
        self._screen_representatives = {}
        self._last_action_by_screen = {}
        self._recent_screen_keys = []
        self._recent_attempt_summaries = []
        self._last_transition_summary = None

    def _execute_step(
        self, user_prompt: str | None = None, is_first: bool = False
    ) -> StepResult:
        """Execute a single step of the agent loop."""

        self._step_count += 1

        device_factory = get_device_factory()
        screenshot = device_factory.get_screenshot(self.agent_config.device_id)
        self._save_latest_screenshot(screenshot.base64_data)
        current_app = device_factory.get_current_app(self.agent_config.device_id)
        self._emit_progress(
            state="step_start",
            message="Captured the latest screen.",
            current_app=current_app,
        )
        current_screen_hash = self._compute_screen_hash(screenshot.base64_data)
        current_screen_key = self._resolve_screen_key(current_app, current_screen_hash)
        memory_note = self._update_memory(current_screen_key, current_app)
        self._record_screen_visit(current_screen_key)

        stuck_reason = self._get_stuck_reason(current_screen_key, current_app)

        if is_first and user_prompt:
            self._current_task = user_prompt

        if stuck_reason:
            action = finish(message=stuck_reason)
            self._emit_progress(
                state="stuck",
                message=stuck_reason,
                current_app=current_app,
            )
            if self.agent_config.verbose:
                msgs = get_messages(self.agent_config.lang)
                print("\n" + "=" * 50)
                print(f"{msgs['thinking']}:")
                print("-" * 50)
                print(stuck_reason)
                print("-" * 50)
                print(f"{msgs['action']}:")
                print(json.dumps(action, ensure_ascii=False, indent=2))
                print("=" * 50 + "\n")
                print("\n" + "=" * 50)
                print(f"{msgs['task_completed']}: {stuck_reason}")
                print("=" * 50 + "\n")
            return StepResult(
                success=False,
                finished=True,
                action=action,
                thinking=stuck_reason,
                message=stuck_reason,
            )

        if is_first:
            self._context.append(
                MessageBuilder.create_system_message(self.agent_config.system_prompt)
            )
        screen_info = MessageBuilder.build_screen_info(
            current_app,
            step=self._step_count,
        )
        text_sections = []
        if self._current_task:
            text_sections.append(f"Task\n\n{self._current_task}")
        text_sections.append(f"Screen Info\n\n{screen_info}")

        if memory_note:
            text_sections.append(f"Memory\n\n{memory_note}")

        text_content = "\n\n".join(text_sections)

        self._context.append(
            MessageBuilder.create_user_message(
                text=text_content,
                image_base64=screenshot.base64_data,
            )
            )

        msgs = get_messages(self.agent_config.lang)
        print("\n" + "=" * 50)
        print(f"{msgs['thinking']}:")
        print("-" * 50)

        user_message_index = len(self._context) - 1
        blocked_action_reason: str | None = None
        response = None
        action: dict[str, Any] | None = None

        for attempt in range(self._MAX_REPLAN_ATTEMPTS + 1):
            self._emit_progress(
                state="model_request",
                message=(
                    f"Requesting the next action from the model "
                    f"(attempt {attempt + 1}/{self._MAX_REPLAN_ATTEMPTS + 1})."
                ),
                current_app=current_app,
            )
            try:
                response = self.model_client.request(self._context)
            except Exception as error:
                if self.agent_config.verbose:
                    traceback.print_exc()
                return StepResult(
                    success=False,
                    finished=True,
                    action=None,
                    thinking="",
                    message=f"Model error: {error}",
                )

            try:
                action = parse_action(response.action)
            except ValueError as error:
                if self.agent_config.verbose:
                    print(
                        "Warning: could not parse model action. "
                        f"Falling back to finish(). Error: {error}"
                    )
                action = finish(message=response.action)

            self._emit_progress(
                state="action_selected",
                message="Selected the next action.",
                current_app=current_app,
                action=action,
            )
            blocked_action_reason = self._get_blocked_action_reason(
                current_screen_key,
                action,
            )
            if not blocked_action_reason:
                break

            if self.agent_config.verbose:
                print(
                    "Warning: model selected an action that already failed on this "
                    "screen. Requesting a different action."
                )

            self._context.append(
                MessageBuilder.create_assistant_message(
                    "\n".join(
                        part for part in (response.thinking, response.action) if part
                    )
                )
            )

            if attempt == self._MAX_REPLAN_ATTEMPTS:
                action = finish(message=blocked_action_reason)
                break

            self._context.append(
                MessageBuilder.create_user_message(
                    text=blocked_action_reason,
                )
            )

        screen_observation = self._extract_screen_observation(
            response.thinking if response else ""
        )

        if self.agent_config.verbose:
            print("-" * 50)
            print(f"{msgs['action']}:")
            print(json.dumps(action, ensure_ascii=False, indent=2))
            print("=" * 50 + "\n")

        self._context[user_message_index] = MessageBuilder.remove_images_from_message(
            self._context[user_message_index]
        )

        try:
            result = self.action_handler.execute(
                action, screenshot.width, screenshot.height
            )
        except Exception as error:
            if self.agent_config.verbose:
                traceback.print_exc()
            result = self.action_handler.execute(
                finish(message=str(error)),
                screenshot.width,
                screenshot.height,
            )

        self._emit_progress(
            state="action_executed",
            message=result.message or "Executed the selected action.",
            current_app=current_app,
            action=action,
            screen_description=screen_observation,
        )

        self._context.append(
            MessageBuilder.create_assistant_message(
                "\n".join(part for part in (response.thinking, response.action) if part)
            )
        )

        self._last_action = action
        self._last_app = current_app
        self._last_screen_key = current_screen_key
        action_signature = self._format_action_signature(action)
        if current_screen_key and action_signature:
            self._last_action_by_screen[current_screen_key] = action_signature

        finished = action.get("_metadata") == "finish" or result.should_finish

        if finished:
            terminal_state = "done"
            terminal_message = result.message or action.get("message", "")
            if not result.success:
                terminal_state = "failed"
            self._emit_progress(
                state=terminal_state,
                message=terminal_message,
                current_app=current_app,
                action=action,
                screen_description=screen_observation,
            )

        if finished and self.agent_config.verbose:
            print("\n" + "=" * 50)
            print(
                f"{msgs['task_completed']}: "
                f"{result.message or action.get('message', msgs['done'])}"
            )
            print("=" * 50 + "\n")

        return StepResult(
            success=result.success,
            finished=finished,
            action=action,
            thinking=response.thinking,
            message=result.message or action.get("message"),
        )

    @property
    def context(self) -> list[dict[str, Any]]:
        """Return a copy of the current conversation context."""

        return self._context.copy()

    @property
    def step_count(self) -> int:
        """Return the number of executed steps."""

        return self._step_count

    def _save_latest_screenshot(self, image_base64: str) -> None:
        """Persist the latest screenshot to a stable temp-file path."""

        if not image_base64:
            return

        screenshot_path = self._get_latest_screenshot_path()
        temp_path = f"{screenshot_path}.tmp"

        try:
            with open(temp_path, "wb") as handle:
                handle.write(base64.b64decode(image_base64))
            os.replace(temp_path, screenshot_path)
        except (OSError, ValueError) as error:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if self.agent_config.verbose:
                print(
                    "Warning: could not save the latest screenshot "
                    f"to `{screenshot_path}`: {error}"
                )

    @staticmethod
    def _get_latest_screenshot_path() -> str:
        """Return the stable file path used for the most recent screenshot."""

        return os.path.join(
            tempfile.gettempdir(),
            "phone-agent-last.png",
        )

    def _compute_screen_hash(self, image_base64: str) -> str | None:
        """Build a coarse visual hash so minor UI changes do not reset memory."""

        if not image_base64:
            return None

        try:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes)).convert("L").resize((16, 16))
            pixels = list(image.getdata())
        except Exception:
            return None

        if not pixels:
            return None

        average = sum(pixels) / len(pixels)
        return "".join("1" if pixel >= average else "0" for pixel in pixels)

    def _resolve_screen_key(
        self, current_app: str, current_screen_hash: str | None
    ) -> str | None:
        """Group visually similar screens in the same app under one memory key."""

        if current_screen_hash is None:
            return None

        app_prefix = current_app or "unknown"
        best_key: str | None = None
        best_distance: int | None = None

        for screen_key, representative_hash in self._screen_representatives.items():
            key_prefix, _, _ = screen_key.partition("#")
            if key_prefix != app_prefix:
                continue

            distance = self._hamming_distance(current_screen_hash, representative_hash)
            if best_distance is None or distance < best_distance:
                best_key = screen_key
                best_distance = distance

        if (
            best_key is not None
            and best_distance is not None
            and best_distance <= self._SCREEN_HASH_DISTANCE_THRESHOLD
        ):
            self._screen_representatives[best_key] = current_screen_hash
            return best_key

        next_index = (
            sum(
                1
                for screen_key in self._screen_representatives
                if screen_key.startswith(f"{app_prefix}#")
            )
            + 1
        )
        screen_key = f"{app_prefix}#{next_index}"
        self._screen_representatives[screen_key] = current_screen_hash
        return screen_key

    def _update_memory(self, current_screen_key: str | None, current_app: str) -> str:
        """Summarize what has already been tried on the current screen."""

        if current_screen_key is None:
            return ""

        revisiting_screen = current_screen_key in self._screen_visit_counts
        last_action_signature = ""
        transition_summary = ""

        if self._last_screen_key and self._last_action:
            action_signature = self._format_action_signature(self._last_action)
            if action_signature:
                action_counts = self._screen_action_counts.setdefault(
                    self._last_screen_key, {}
                )
                action_counts[action_signature] = (
                    action_counts.get(action_signature, 0) + 1
                )
                last_action_signature = action_signature
                transition_summary = self._summarize_transition(
                    source_screen_key=self._last_screen_key,
                    target_screen_key=current_screen_key,
                    action_signature=action_signature,
                    current_app=current_app,
                    revisiting_screen=revisiting_screen,
                )
                self._append_recent_attempt_summary(transition_summary)

                if current_screen_key == self._last_screen_key:
                    self._mark_failed_action(self._last_screen_key, action_signature)

        if revisiting_screen:
            previous_action = self._last_action_by_screen.get(current_screen_key)
            if previous_action and not (
                current_screen_key == self._last_screen_key
                and previous_action == last_action_signature
            ):
                self._mark_failed_action(current_screen_key, previous_action)

        self._last_transition_summary = transition_summary or self._last_transition_summary
        self._screen_visit_counts[current_screen_key] = (
            self._screen_visit_counts.get(current_screen_key, 0) + 1
        )

        memory_lines: list[str] = []
        if self._last_transition_summary:
            memory_lines.append(f"Last observed outcome: {self._last_transition_summary}")

        if self._recent_attempt_summaries:
            recent_attempts = "\n".join(
                f"- {summary}" for summary in self._recent_attempt_summaries[-4:]
            )
            memory_lines.append(f"Recent attempts:\n{recent_attempts}")

        visit_count = self._screen_visit_counts[current_screen_key]
        if visit_count > 1:
            memory_lines.append(
                f"You have already seen this screen {visit_count} times."
            )

        failed_actions = self._screen_failed_actions.get(current_screen_key, {})
        if failed_actions:
            sorted_failed = sorted(
                failed_actions.items(),
                key=lambda item: (-item[1], item[0]),
            )[:4]
            failed_actions_text = ", ".join(
                f"{action} ({count}x)" for action, count in sorted_failed
            )
            memory_lines.append(
                "Do not repeat on this screen: "
                f"{failed_actions_text}. These actions already failed or led back here."
            )

        action_counts = self._screen_action_counts.get(current_screen_key, {})
        if action_counts:
            sorted_actions = sorted(
                action_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )[:3]
            tried_actions = ", ".join(
                f"{action} ({count}x)" for action, count in sorted_actions
            )
            memory_lines.append(f"Already tried on this screen: {tried_actions}.")

        if (
            visit_count > 1
            and self._last_screen_key == current_screen_key
            and self._last_action is not None
        ):
            action_signature = self._format_action_signature(self._last_action)
            if action_signature:
                memory_lines.append(
                    f"The last action did not move away from this screen: {action_signature}."
                )

        if visit_count > 1 and (failed_actions or action_counts):
            memory_lines.append(
                "Do not repeat the same failed tap pattern. Try a different control or a different navigation step."
            )

        adaptation_hint = self._build_adaptation_hint(current_screen_key)
        if adaptation_hint:
            memory_lines.append(f"Adaptation hint: {adaptation_hint}")

        return "\n".join(memory_lines)

    def _get_blocked_action_reason(
        self,
        current_screen_key: str | None,
        action: dict[str, Any],
    ) -> str | None:
        """Return a corrective prompt if the proposed action already failed here."""

        if current_screen_key is None:
            return None

        if not self._is_repeat_sensitive_action(action):
            return None

        action_signature = self._format_action_signature(action)
        if not action_signature:
            return None

        failed_actions = self._screen_failed_actions.get(current_screen_key, {})
        if action_signature not in failed_actions:
            return None

        failed_actions_text = ", ".join(
            sorted(failed_actions.keys())
        )
        return (
            f"The proposed action `{action_signature}` was already tried on this "
            "screen and did not help. Choose a different next action on the same "
            f"screenshot. Avoid repeating any of: {failed_actions_text}."
        )

    def _mark_failed_action(self, screen_key: str, action_signature: str) -> None:
        """Record that an action was tried on a screen without useful progress."""

        if not action_signature:
            return

        failed_actions = self._screen_failed_actions.setdefault(screen_key, {})
        failed_actions[action_signature] = failed_actions.get(action_signature, 0) + 1

    def _record_screen_visit(self, current_screen_key: str | None) -> None:
        """Track the recent sequence of screen keys for loop detection."""

        if current_screen_key is None:
            return

        self._recent_screen_keys.append(current_screen_key)
        if len(self._recent_screen_keys) > self._SCREEN_HISTORY_WINDOW:
            self._recent_screen_keys = self._recent_screen_keys[
                -self._SCREEN_HISTORY_WINDOW :
            ]

    def _append_recent_attempt_summary(self, summary: str) -> None:
        """Keep a short rolling history of recent action outcomes."""

        if not summary:
            return

        self._recent_attempt_summaries.append(summary)
        if len(self._recent_attempt_summaries) > self._SCREEN_HISTORY_WINDOW:
            self._recent_attempt_summaries = self._recent_attempt_summaries[
                -self._SCREEN_HISTORY_WINDOW :
            ]

    def _summarize_transition(
        self,
        source_screen_key: str,
        target_screen_key: str,
        action_signature: str,
        current_app: str,
        revisiting_screen: bool,
    ) -> str:
        """Describe what the last action actually achieved."""

        outcome = self._classify_transition(
            source_screen_key=source_screen_key,
            target_screen_key=target_screen_key,
            current_app=current_app,
            revisiting_screen=revisiting_screen,
        )
        if outcome == "same_screen":
            return f"{action_signature} kept the agent on the same screen."
        if outcome == "returned_to_known_screen":
            return (
                f"{action_signature} led back to a previously seen screen "
                f"({target_screen_key})."
            )
        if outcome == "changed_app":
            return (
                f"{action_signature} moved the agent into a different app "
                f"({current_app})."
            )
        return f"{action_signature} moved to a new screen ({target_screen_key})."

    def _classify_transition(
        self,
        source_screen_key: str,
        target_screen_key: str,
        current_app: str,
        revisiting_screen: bool,
    ) -> str:
        """Classify the observed result of the previous action."""

        if target_screen_key == source_screen_key:
            return "same_screen"
        if revisiting_screen:
            return "returned_to_known_screen"
        if self._last_app and current_app != self._last_app:
            return "changed_app"
        return "new_screen"

    def _build_adaptation_hint(self, current_screen_key: str) -> str:
        """Suggest how to change strategy based on the local failure pattern."""

        failed_actions = self._screen_failed_actions.get(current_screen_key, {})
        if not failed_actions:
            return ""

        hints: list[str] = []
        action_names = {action.split(" ", 1)[0] for action in failed_actions}
        if "Tap" in action_names or "Double" in action_names or "Long" in action_names:
            hints.append(
                "Avoid tapping the same region again. Use a different visible control or dismiss the blocking element first."
            )
        if "Swipe" in action_names:
            hints.append(
                "Do not repeat the same swipe path. Try a different direction or a specific visible control."
            )
        if "Launch" in action_names:
            hints.append(
                "Launching again is unlikely to help. Continue from the current app state instead of restarting."
            )

        if self._screen_visit_counts.get(current_screen_key, 0) >= (
            self._MAX_SCREEN_VISITS_BEFORE_STOP - 1
        ):
            hints.append(
                "If no clearly different action is available, stop and explain what is blocking progress."
            )

        return " ".join(hints)

    def _get_stuck_reason(
        self,
        current_screen_key: str | None,
        current_app: str,
    ) -> str | None:
        """Return a terminal blocked reason if the agent is clearly looping."""

        if current_screen_key is None:
            return None

        failed_actions = self._screen_failed_actions.get(current_screen_key, {})
        visit_count = self._screen_visit_counts.get(current_screen_key, 0)
        if (
            visit_count >= self._MAX_SCREEN_VISITS_BEFORE_STOP
            and len(failed_actions) >= self._MIN_DISTINCT_FAILED_ACTIONS_BEFORE_STOP
        ):
            return self._build_stuck_message(
                current_app,
                current_screen_key,
                "The agent returned to the same screen multiple times without progress.",
            )

        if len(self._recent_screen_keys) < self._SCREEN_HISTORY_WINDOW:
            return None

        loop_window = self._recent_screen_keys[-self._SCREEN_HISTORY_WINDOW :]
        unique_screens = {screen_key for screen_key in loop_window if screen_key}
        if len(unique_screens) > self._MAX_UNIQUE_SCREENS_IN_LOOP:
            return None

        distinct_failed_actions = {
            action_signature
            for screen_key in unique_screens
            for action_signature in self._screen_failed_actions.get(screen_key, {})
        }
        if len(distinct_failed_actions) < self._MIN_DISTINCT_FAILED_ACTIONS_BEFORE_STOP:
            return None

        return self._build_stuck_message(
            current_app,
            current_screen_key,
            "The agent is oscillating between the same screens without progress.",
        )

    def _build_stuck_message(
        self,
        current_app: str,
        current_screen_key: str,
        problem: str,
    ) -> str:
        """Build a user-facing blocked message with the last screenshot path."""

        failed_actions = self._screen_failed_actions.get(current_screen_key, {})
        if failed_actions:
            sorted_failed = sorted(
                failed_actions.items(),
                key=lambda item: (-item[1], item[0]),
            )[:4]
            failed_actions_text = ", ".join(
                f"{action} ({count}x)" for action, count in sorted_failed
            )
        else:
            failed_actions_text = "No stable failed-action summary available."

        return (
            f"{problem} Current app: {current_app}. "
            f"Repeated failed actions: {failed_actions_text}. "
            f"Last screenshot saved at {self._get_latest_screenshot_path()}. "
            "Review the screen and provide the next instruction."
        )

    @staticmethod
    def _extract_screen_observation(thinking: str) -> str:
        """Extract the first 1-2 sentences from the model's thinking text.

        Args:
            thinking: The model's full reasoning text for the current step.

        Returns:
            A short screen observation (max 200 chars).
        """

        if not thinking or not thinking.strip():
            return ""

        text = thinking.strip()
        parts = text.split(". ", 2)
        if len(parts) >= 2:
            observation = parts[0] + ". " + parts[1]
            if not observation.endswith("."):
                observation += "."
        else:
            observation = parts[0]
            if not observation.endswith("."):
                observation += "."

        if len(observation) > 200:
            observation = observation[:200] + "..."
        return observation

    @classmethod
    def _is_repeat_sensitive_action(cls, action: dict[str, Any]) -> bool:
        """Return whether repeated execution should trigger replanning."""

        if action.get("_metadata") != "do":
            return False

        action_name = action.get("action")
        return action_name in {
            "Tap",
            "Double Tap",
            "Long Press",
            "Swipe",
            "Launch",
        }

    @staticmethod
    def _hamming_distance(left: str, right: str) -> int:
        """Compute the Hamming distance between two equal-length hashes."""

        if len(left) != len(right):
            return max(len(left), len(right))
        return sum(left_char != right_char for left_char, right_char in zip(left, right))

    @staticmethod
    def _format_action_signature(action: dict[str, Any]) -> str:
        """Return a compact action label for memory hints."""

        metadata = action.get("_metadata")
        if metadata == "finish":
            return 'finish(message="...")'

        action_name = action.get("action")
        if not action_name:
            return ""

        if action_name in {"Tap", "Long Press", "Double Tap"} and action.get("element"):
            return f'{action_name} {PhoneAgent._bucket_point(action.get("element"))}'
        if action_name == "Swipe" and action.get("start") and action.get("end"):
            return (
                "Swipe "
                f"{PhoneAgent._bucket_point(action.get('start'))} -> "
                f"{PhoneAgent._bucket_point(action.get('end'))}"
            )
        if action_name == "Launch" and action.get("app"):
            return f'Launch "{action.get("app")}"'
        if action_name == "Type" and action.get("text") is not None:
            return f'Type "{str(action.get("text"))[:24]}"'
        return action_name

    @staticmethod
    def _bucket_point(point: Any) -> list[int]:
        """Bucket coordinates so near-identical taps count as the same action."""

        if not isinstance(point, list) or len(point) != 2:
            return point

        x_bucket = 50 if 0 <= point[0] <= 999 else 100
        y_bucket = 50 if 0 <= point[1] <= 999 else 100
        return [
            int(round(point[0] / x_bucket) * x_bucket),
            int(round(point[1] / y_bucket) * y_bucket),
        ]
