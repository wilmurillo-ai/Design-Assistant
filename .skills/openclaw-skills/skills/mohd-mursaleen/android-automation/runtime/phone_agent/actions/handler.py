"""Action handler for Android automation."""

import ast
import time
from dataclasses import dataclass
from typing import Any, Callable

from phone_agent.config.timing import TIMING_CONFIG
from phone_agent.device_factory import get_device_factory


@dataclass
class ActionResult:
    """Result of an action execution."""

    success: bool
    should_finish: bool
    message: str | None = None
    requires_confirmation: bool = False


class ActionHandler:
    """Execute model-selected actions against the Android device."""

    def __init__(
        self,
        device_id: str | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ) -> None:
        self.device_id = device_id
        self.confirmation_callback = confirmation_callback or self._default_confirmation
        self.takeover_callback = takeover_callback or self._default_takeover

    def execute(
        self, action: dict[str, Any], screen_width: int, screen_height: int
    ) -> ActionResult:
        """Execute a parsed action."""

        action_type = action.get("_metadata")
        if action_type == "finish":
            return ActionResult(
                success=True,
                should_finish=True,
                message=action.get("message"),
            )

        if action_type != "do":
            return ActionResult(
                success=False,
                should_finish=True,
                message=f"Unknown action type: {action_type}",
            )

        action_name = action.get("action")
        handler_method = self._get_handler(action_name)
        if handler_method is None:
            return ActionResult(
                success=False,
                should_finish=False,
                message=f"Unknown action: {action_name}",
            )

        try:
            return handler_method(action, screen_width, screen_height)
        except Exception as error:
            return ActionResult(
                success=False,
                should_finish=False,
                message=f"Action failed: {error}",
            )

    def _get_handler(self, action_name: str) -> Callable | None:
        handlers = {
            "Launch": self._handle_launch,
            "Tap": self._handle_tap,
            "Type": self._handle_type,
            "Type_Name": self._handle_type,
            "Swipe": self._handle_swipe,
            "Back": self._handle_back,
            "Home": self._handle_home,
            "Double Tap": self._handle_double_tap,
            "Long Press": self._handle_long_press,
            "Wait": self._handle_wait,
            "Take_over": self._handle_takeover,
            "Interact": self._handle_interact,
        }
        return handlers.get(action_name)

    @staticmethod
    def _convert_to_absolute(
        element: list[int], screen_width: int, screen_height: int
    ) -> tuple[int, int]:
        raw_x, raw_y = int(element[0]), int(element[1])

        if 0 <= raw_x <= 999 and 0 <= raw_y <= 999:
            x = int(raw_x / 1000 * screen_width)
            y = int(raw_y / 1000 * screen_height)
        else:
            x = raw_x
            y = raw_y

        x = max(0, min(x, screen_width - 1))
        y = max(0, min(y, screen_height - 1))
        return x, y

    def _handle_launch(self, action: dict, width: int, height: int) -> ActionResult:
        app_name = action.get("app")
        if not app_name:
            return ActionResult(False, False, "No app name specified")

        success = get_device_factory().launch_app(app_name, self.device_id)
        if success:
            return ActionResult(True, False)
        return ActionResult(False, False, f"App not found: {app_name}")

    def _handle_tap(self, action: dict, width: int, height: int) -> ActionResult:
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_to_absolute(element, width, height)

        if "message" in action:
            if not self.confirmation_callback(action["message"]):
                return ActionResult(
                    success=True,
                    should_finish=True,
                    message=(
                        "Stopped before a sensitive action because explicit approval "
                        f"was not available: {action['message']}"
                    ),
                )

        get_device_factory().tap(x, y, self.device_id)
        return ActionResult(True, False)

    def _handle_type(self, action: dict, width: int, height: int) -> ActionResult:
        text = action.get("text", "")
        device_factory = get_device_factory()

        original_ime = device_factory.detect_and_set_adb_keyboard(self.device_id)
        time.sleep(TIMING_CONFIG.action.keyboard_switch_delay)

        device_factory.clear_text(self.device_id)
        time.sleep(TIMING_CONFIG.action.text_clear_delay)

        device_factory.type_text(text, self.device_id)
        time.sleep(TIMING_CONFIG.action.text_input_delay)

        device_factory.restore_keyboard(original_ime, self.device_id)
        time.sleep(TIMING_CONFIG.action.keyboard_restore_delay)

        return ActionResult(True, False)

    def _handle_swipe(self, action: dict, width: int, height: int) -> ActionResult:
        start = action.get("start")
        end = action.get("end")
        if not start or not end:
            return ActionResult(False, False, "Missing swipe coordinates")

        start_x, start_y = self._convert_to_absolute(start, width, height)
        end_x, end_y = self._convert_to_absolute(end, width, height)

        get_device_factory().swipe(
            start_x,
            start_y,
            end_x,
            end_y,
            device_id=self.device_id,
        )
        return ActionResult(True, False)

    def _handle_back(self, action: dict, width: int, height: int) -> ActionResult:
        get_device_factory().back(self.device_id)
        return ActionResult(True, False)

    def _handle_home(self, action: dict, width: int, height: int) -> ActionResult:
        get_device_factory().home(self.device_id)
        return ActionResult(True, False)

    def _handle_double_tap(self, action: dict, width: int, height: int) -> ActionResult:
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_to_absolute(element, width, height)
        get_device_factory().double_tap(x, y, self.device_id)
        return ActionResult(True, False)

    def _handle_long_press(self, action: dict, width: int, height: int) -> ActionResult:
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_to_absolute(element, width, height)
        get_device_factory().long_press(x, y, device_id=self.device_id)
        return ActionResult(True, False)

    @staticmethod
    def _handle_wait(action: dict, width: int, height: int) -> ActionResult:
        duration_str = action.get("duration", "1 seconds")
        try:
            duration = float(duration_str.replace("seconds", "").strip())
        except ValueError:
            duration = 1.0

        time.sleep(duration)
        return ActionResult(True, False)

    def _handle_takeover(self, action: dict, width: int, height: int) -> ActionResult:
        message = action.get("message", "Manual action required.")
        return ActionResult(
            success=True,
            should_finish=True,
            message=message,
        )

    def _handle_interact(self, action: dict, width: int, height: int) -> ActionResult:
        message = action.get("message", "User interaction required.")
        return ActionResult(
            success=True,
            should_finish=True,
            message=message,
        )

    @staticmethod
    def _default_confirmation(message: str) -> bool:
        return False

    @staticmethod
    def _default_takeover(message: str) -> None:
        input(f"{message}\nPress Enter after completing the action...")


def parse_action(response: str) -> dict[str, Any]:
    """Parse a `do(...)` or `finish(...)` command from model output."""

    response = _extract_action_call(response.strip())
    if not response:
        raise ValueError("Empty action response")

    sanitized = (
        response.replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )

    try:
        tree = ast.parse(sanitized, mode="eval")
    except SyntaxError as error:
        raise ValueError(f"Invalid action syntax: {error}") from error

    if not isinstance(tree.body, ast.Call):
        raise ValueError("Expected a function call")

    call = tree.body
    if not isinstance(call.func, ast.Name):
        raise ValueError("Expected a simple function call")

    func_name = call.func.id
    if func_name not in {"do", "finish"}:
        raise ValueError(f"Unknown action function: {func_name}")

    action: dict[str, Any] = {"_metadata": func_name}
    for keyword in call.keywords:
        if keyword.arg is None:
            raise ValueError("Action arguments must be keyword arguments")
        action[keyword.arg] = ast.literal_eval(keyword.value)

    return action


def _extract_action_call(response: str) -> str:
    """Extract the first balanced `do(...)` or `finish(...)` call from text."""

    cleaned = response
    for token in ("<think>", "</think>", "<answer>", "</answer>", "```"):
        cleaned = cleaned.replace(token, "")
    cleaned = cleaned.strip()

    starts = [index for index in (cleaned.find("do("), cleaned.find("finish(")) if index != -1]
    if not starts:
        return cleaned

    start = min(starts)
    depth = 0
    quote_char: str | None = None
    escaped = False

    for index in range(start, len(cleaned)):
        char = cleaned[index]

        if quote_char is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote_char:
                quote_char = None
            continue

        if char in {'"', "'"}:
            quote_char = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return cleaned[start : index + 1]

    return cleaned[start:]


def do(**kwargs) -> dict[str, Any]:
    """Helper for creating `do` actions."""

    kwargs["_metadata"] = "do"
    return kwargs


def finish(**kwargs) -> dict[str, Any]:
    """Helper for creating `finish` actions."""

    kwargs["_metadata"] = "finish"
    return kwargs
