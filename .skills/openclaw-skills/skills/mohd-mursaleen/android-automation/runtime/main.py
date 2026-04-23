#!/usr/bin/env python3
"""
Phone Agent CLI for Android automation.

Usage:
    python main.py [OPTIONS] [TASK]

Environment Variables:
    PHONE_AGENT_PROVIDER: Model provider (`gemini`, `openai`, or `chatgpt`).
    PHONE_AGENT_BASE_URL: Model API base URL.
    PHONE_AGENT_MODEL: Model name.
    GEMINI_BASE_URL: Optional Gemini-specific base URL override.
    GEMINI_MODEL: Optional Gemini-specific model override.
    GEMINI_API_KEY: Preferred API key for Gemini authentication.
    OPENAI_BASE_URL: Optional OpenAI-specific base URL override.
    OPENAI_MODEL: Optional OpenAI-specific model override.
    OPENAI_API_KEY: Preferred API key for OpenAI authentication.
    PHONE_AGENT_API_KEY: Backward-compatible fallback API key name for either provider.
    PHONE_AGENT_MAX_STEPS: Maximum steps per task.
    PHONE_AGENT_DEVICE_ID: ADB device ID for multi-device setups.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.config import (
    DEFAULT_MAX_STEPS,
    DEFAULT_PROVIDER,
    PROVIDER_OPENAI,
    VALID_PROVIDERS,
    get_default_api_key,
    get_default_base_url,
    get_default_model_name,
    normalize_provider,
)
from phone_agent.config.apps import list_supported_apps
from phone_agent.device_factory import get_device_factory
from phone_agent.model import ModelConfig
from phone_agent.model.client import create_chat_completion


def _adb_prefix(device_id: str | None = None) -> list[str]:
    if device_id:
        return ["adb", "-s", device_id]
    return ["adb"]


def _utc_now() -> str:
    """Return an ISO8601 timestamp in UTC."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _get_latest_screenshot_path() -> str:
    """Return the stable screenshot path used by the runtime."""

    return os.path.join(tempfile.gettempdir(), "phone-agent-last.png")


def _classify_result_status(message: str) -> str:
    """Map the runtime's final message to one of the five contract statuses.

    Returns:
        One of: done, needs_input, stuck, max_steps, failed.
    """

    cleaned = (message or "").strip()
    if cleaned.startswith("Stopped before a sensitive action"):
        return "needs_input"
    if cleaned.startswith("Stuck:"):
        return "stuck"
    if "without progress" in cleaned and "failed actions" in cleaned:
        return "stuck"
    if "Max steps reached" in cleaned:
        return "max_steps"
    if cleaned.startswith("Model error:") or cleaned.startswith("Unhandled error:"):
        return "failed"
    if cleaned in {"System requirements check failed.", "Model API check failed."}:
        return "failed"
    if cleaned == "Interrupted by user.":
        return "failed"
    return "done"


def _build_result_payload(
    args: argparse.Namespace,
    status: str,
    message: str,
    step_log: list[dict[str, object]] | None = None,
    last_screen_description: str = "",
) -> dict[str, object]:
    """Build a machine-readable terminal result following the 5-status contract.

    Args:
        args: Parsed CLI arguments.
        status: One of done, needs_input, stuck, max_steps, failed.
        message: Human-readable reason the automation stopped.
        step_log: Accumulated step-by-step log from the runtime.
        last_screen_description: The most recent screen observation text.

    Returns:
        Result payload dict.
    """

    screenshot_path = _get_latest_screenshot_path()
    if not os.path.isfile(screenshot_path):
        screenshot_path = ""

    steps = step_log or []
    action_chain = [
        str(entry.get("action", ""))
        for entry in steps
        if entry.get("action")
    ]
    what_i_did = " -> ".join(action_chain[-15:]) if action_chain else ""

    return {
        "status": status,
        "why": message,
        "what_i_did": what_i_did,
        "where_i_am": last_screen_description,
        "steps": [
            {
                "step": entry.get("step", 0),
                "action": entry.get("action", ""),
                "saw": entry.get("saw", ""),
            }
            for entry in steps[-30:]
        ],
        "step_count": len(steps),
        "screenshot_path": screenshot_path,
        "task": args.task or "",
        "device_id": args.device_id or "",
        "finished_at": _utc_now(),
    }


def _write_result_json(path: str, payload: dict[str, object]) -> None:
    """Write the terminal result JSON atomically."""

    if not path:
        return

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temp_path, path)


def _build_progress_payload(
    args: argparse.Namespace,
    state: str,
    *,
    message: str = "",
    step: int = 0,
    current_app: str = "",
    last_action: str = "",
    screenshot_path: str | None = None,
    screen_description: str = "",
    step_log: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """Build a progress payload with live step log for blind orchestrators.

    Args:
        args: Parsed CLI arguments.
        state: Current runtime state.
        message: Human-readable status message.
        step: Current step number.
        current_app: Currently focused Android app.
        last_action: Signature of the last executed action.
        screenshot_path: Path to the latest screenshot.
        screen_description: Model's 1-2 sentence observation of the screen.
        step_log: Accumulated step log for live visibility.

    Returns:
        Progress payload dict.
    """

    resolved_screenshot_path = screenshot_path
    if resolved_screenshot_path is None:
        candidate = _get_latest_screenshot_path()
        resolved_screenshot_path = candidate if os.path.isfile(candidate) else ""

    return {
        "state": state,
        "message": message,
        "step": step,
        "current_app": current_app,
        "last_action": last_action,
        "screen_description": screen_description,
        "steps": [
            {
                "step": entry.get("step", 0),
                "action": entry.get("action", ""),
                "saw": entry.get("saw", ""),
            }
            for entry in (step_log or [])[-20:]
        ],
        "task": args.task or "",
        "device_id": args.device_id or "",
        "heartbeat_at": _utc_now(),
        "screenshot_path": resolved_screenshot_path,
    }


def _write_progress_json(path: str, payload: dict[str, object]) -> None:
    """Persist the latest runtime heartbeat atomically."""

    if not path:
        return

    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temp_path, path)


def _make_progress_reporter(
    args: argparse.Namespace,
    progress_json: str | None,
    step_log: list[dict[str, object]],
    screen_state: dict[str, str],
):
    """Create a callback that accumulates a step log and writes progress.

    Args:
        args: Parsed CLI arguments.
        progress_json: Path to write the live progress file, or None.
        step_log: Mutable list shared with the caller to accumulate steps.
        screen_state: Mutable dict shared with the caller; tracks
            ``last_description`` for the most recent screen observation.

    Returns:
        A callback compatible with PhoneAgent's progress_callback.
    """

    def report(update: dict[str, object]) -> None:
        screen_desc = str(update.get("screen_description", ""))

        if update.get("state") == "action_executed" and update.get("last_action"):
            step_log.append({
                "step": int(update.get("step", 0) or 0),
                "action": str(update.get("last_action", "")),
                "saw": screen_desc,
            })

        if screen_desc:
            screen_state["last_description"] = screen_desc

        if not progress_json:
            return

        payload = _build_progress_payload(
            args=args,
            state=str(update.get("state", "running")),
            message=str(update.get("message", "")),
            step=int(update.get("step", 0) or 0),
            current_app=str(update.get("current_app", "")),
            last_action=str(update.get("last_action", "")),
            screenshot_path=(
                str(update["screenshot_path"])
                if update.get("screenshot_path")
                else None
            ),
            screen_description=screen_desc,
            step_log=step_log,
        )
        _write_progress_json(progress_json, payload)

    return report


def _print_terminal_summary(payload: dict[str, object], result_json: str | None) -> None:
    """Print machine-readable terminal markers for wrapper scripts and logs."""

    print("\n" + "=" * 50)
    print(f"Terminal Status: {payload['status']}")
    print(f"Terminal Message: {payload['why']}")
    if payload.get("screenshot_path"):
        print(f"Terminal Screenshot: {payload['screenshot_path']}")
    if result_json:
        print(f"Terminal Result JSON: {result_json}")
    print("=" * 50 + "\n")


def check_system_requirements(device_id: str | None = None) -> bool:
    """
    Check system requirements before running the agent.

    Checks:
    1. ADB is installed.
    2. At least one Android device is connected.
    3. ADB Keyboard is installed on the selected device.
    """

    print("Checking system requirements...")
    print("-" * 50)

    all_passed = True

    print("1. Checking ADB installation...", end=" ")
    if shutil.which("adb") is None:
        print("FAILED")
        print("   Error: ADB is not installed or not in PATH.")
        print("   Install Android platform tools and ensure `adb` is available.")
        return False

    try:
        result = subprocess.run(
            ["adb", "version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version_line = result.stdout.strip().splitlines()[0]
            print(f"OK ({version_line})")
        else:
            print("FAILED")
            print("   Error: `adb version` returned a non-zero exit code.")
            return False
    except subprocess.TimeoutExpired:
        print("FAILED")
        print("   Error: `adb version` timed out.")
        return False

    print("2. Checking connected devices...", end=" ")
    device_factory = get_device_factory()
    devices = [device for device in device_factory.list_devices() if device.status == "device"]

    if device_id:
        devices = [device for device in devices if device.device_id == device_id]

    if not devices:
        print("FAILED")
        if device_id:
            print(f"   Error: Device `{device_id}` is not connected.")
        else:
            print("   Error: No Android devices are connected.")
        print("   Enable USB debugging and confirm the device with `adb devices`.")
        return False

    device_summary = ", ".join(device.device_id for device in devices[:2])
    if len(devices) > 2:
        device_summary += ", ..."
    print(f"OK ({device_summary})")

    print("3. Checking ADB Keyboard...", end=" ")
    try:
        result = subprocess.run(
            _adb_prefix(device_id) + ["shell", "ime", "list", "-s"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        ime_list = result.stdout.strip()
        if "com.android.adbkeyboard/.AdbIME" in ime_list:
            print("OK")
        else:
            print("FAILED")
            print("   Error: ADB Keyboard is not installed on the device.")
            print("   Install it and enable it before using text entry actions.")
            all_passed = False
    except subprocess.TimeoutExpired:
        print("FAILED")
        print("   Error: `adb shell ime list -s` timed out.")
        all_passed = False

    print("-" * 50)
    if all_passed:
        print("All system checks passed.\n")
    else:
        print("System check failed. Fix the issues above and try again.")
    return all_passed


def check_model_api(base_url: str, model_name: str, api_key: str, provider: str) -> bool:
    """Check that the model API is reachable."""

    print("Checking model API...")
    print("-" * 50)
    print(f"1. Checking API connectivity ({base_url})...", end=" ")

    if not api_key:
        print("FAILED")
        print(
            "   Error: No API key configured. Set GEMINI_API_KEY or OPENAI_API_KEY,"
        )
        print("   or pass --apikey explicitly.")
        return False

    try:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Reply with OK."}],
            "temperature": 0.0,
            "stream": False,
        }
        if provider == PROVIDER_OPENAI:
            payload["max_completion_tokens"] = 8
        else:
            payload["max_tokens"] = 8

        response = create_chat_completion(
            base_url=base_url,
            api_key=api_key,
            payload=payload,
            timeout=30.0,
        )

        if response.get("choices"):
            print("OK")
        else:
            print("FAILED")
            print("   Error: The API returned no choices.")
            return False
    except Exception as error:
        print("FAILED")
        print(f"   Error: {error}")
        return False

    print("-" * 50)
    print("Model API check passed.\n")
    return True


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Phone Agent - Android automation with ADB and Gemini/OpenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Open Chrome and search for wireless earbuds"
  python main.py --list-devices
  python main.py --connect 192.168.1.100:5555
  python main.py --enable-tcpip
  python main.py --model gemini-2.5-pro "Open Settings"
  python main.py --provider openai --model gpt-5.2 "Open Settings"
        """,
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=VALID_PROVIDERS,
        default=os.getenv("PHONE_AGENT_PROVIDER", DEFAULT_PROVIDER),
        help="Model provider to use",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Model API base URL",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name",
    )
    parser.add_argument(
        "--apikey",
        type=str,
        default=None,
        help="API key for model authentication",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=int(os.getenv("PHONE_AGENT_MAX_STEPS", str(DEFAULT_MAX_STEPS))),
        help="Maximum steps per task",
    )

    parser.add_argument(
        "--device-id",
        "-d",
        type=str,
        default=os.getenv("PHONE_AGENT_DEVICE_ID"),
        help="ADB device ID",
    )
    parser.add_argument(
        "--connect",
        "-c",
        type=str,
        metavar="ADDRESS",
        help="Connect to a remote ADB device (example: 192.168.1.100:5555)",
    )
    parser.add_argument(
        "--disconnect",
        type=str,
        nargs="?",
        const="all",
        metavar="ADDRESS",
        help="Disconnect from a remote device, or `all` to disconnect everything",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List connected Android devices and exit",
    )
    parser.add_argument(
        "--enable-tcpip",
        type=int,
        nargs="?",
        const=5555,
        metavar="PORT",
        help="Enable TCP/IP debugging on the USB-connected device",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress verbose model and action logs",
    )
    parser.add_argument(
        "--result-json",
        type=str,
        default=None,
        help="Write the final terminal result to this JSON file",
    )
    parser.add_argument(
        "--progress-json",
        type=str,
        default=None,
        help="Write the latest progress heartbeat to this JSON file",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip system requirements and model API checks",
    )
    parser.add_argument(
        "--list-apps",
        action="store_true",
        help="List supported launch aliases and exit",
    )
    parser.add_argument(
        "task",
        nargs="?",
        type=str,
        help="Task to execute. Interactive mode starts if omitted.",
    )

    return parser.parse_args()


def resolve_model_settings(args: argparse.Namespace) -> argparse.Namespace:
    """Resolve provider-aware defaults after CLI parsing."""

    args.provider = normalize_provider(args.provider)
    args.base_url = args.base_url or get_default_base_url(args.provider)
    args.model = args.model or get_default_model_name(args.provider)
    args.apikey = args.apikey or get_default_api_key(args.provider)
    return args


def handle_device_commands(args: argparse.Namespace) -> bool:
    """Handle device-related commands that do not need a running agent."""

    device_factory = get_device_factory()
    connection_class = device_factory.get_connection_class()
    conn = connection_class()

    if args.list_devices:
        devices = device_factory.list_devices()
        if not devices:
            print("No Android devices connected.")
        else:
            print("Connected Android devices:")
            print("-" * 60)
            for device in devices:
                status_icon = "OK" if device.status == "device" else "ERR"
                model_info = f" ({device.model})" if device.model else ""
                print(f"  {status_icon} {device.device_id:<30}{model_info}")
        return True

    if args.connect:
        print(f"Connecting to {args.connect}...")
        success, message = conn.connect(args.connect)
        print(message if success else f"Error: {message}")
        return not success

    if args.disconnect:
        target = args.disconnect if args.disconnect != "all" else None
        if target:
            print(f"Disconnecting from {target}...")
        else:
            print("Disconnecting from all remote devices...")
        success, message = conn.disconnect(target)
        print(message if success else f"Error: {message}")
        return True

    if args.enable_tcpip:
        print(f"Enabling TCP/IP debugging on port {args.enable_tcpip}...")
        success, message = conn.enable_tcpip(args.enable_tcpip, args.device_id)
        print(message if success else f"Error: {message}")
        if success:
            ip_address = conn.get_device_ip(args.device_id)
            if ip_address:
                print(f"Connect later with: adb connect {ip_address}:{args.enable_tcpip}")
        return True

    return False


def main() -> None:
    """Main entry point."""

    args = parse_args()
    args = resolve_model_settings(args)
    final_payload: dict[str, object] | None = None
    exit_code = 0
    should_stop = False
    step_log: list[dict[str, object]] = []
    screen_state: dict[str, str] = {"last_description": ""}
    report_progress = _make_progress_reporter(
        args, args.progress_json, step_log, screen_state,
    )

    try:
        report_progress({"state": "starting", "message": "Initializing automation runtime."})

        if args.list_apps:
            print("Supported launch aliases:")
            for app in sorted(list_supported_apps()):
                print(f"  - {app}")
            print("\nTip: You can also launch an app by Android package name.")
            should_stop = True

        elif handle_device_commands(args):
            should_stop = True

        elif not args.skip_checks and not check_system_requirements(args.device_id):
            final_payload = _build_result_payload(
                args=args,
                status="failed",
                message="System requirements check failed.",
            )
            report_progress(
                {
                    "state": "failed",
                    "message": "System requirements check failed.",
                }
            )
            exit_code = 1
            should_stop = True

        elif not args.skip_checks and not check_model_api(args.base_url, args.model, args.apikey, args.provider):
            final_payload = _build_result_payload(
                args=args,
                status="failed",
                message="Model API check failed.",
            )
            report_progress(
                {
                    "state": "failed",
                    "message": "Model API check failed.",
                }
            )
            exit_code = 1
            should_stop = True

        if not should_stop:
            report_progress({"state": "ready", "message": "Runtime checks passed."})
            model_config = ModelConfig(
                provider=args.provider,
                base_url=args.base_url,
                model_name=args.model,
                api_key=args.apikey,
            )
            agent_config = AgentConfig(
                max_steps=args.max_steps,
                device_id=args.device_id,
                verbose=not args.quiet,
                lang="en",
            )
            agent = PhoneAgent(
                model_config=model_config,
                agent_config=agent_config,
                progress_callback=report_progress,
            )

            print("=" * 50)
            print("Phone Agent - Android automation")
            print("=" * 50)
            print(f"Provider: {args.provider}")
            print(f"Model: {model_config.model_name}")
            print(f"Base URL: {model_config.base_url}")
            print(f"Max Steps: {agent_config.max_steps}")

            devices = get_device_factory().list_devices()
            if agent_config.device_id:
                print(f"Device: {agent_config.device_id}")
            elif devices:
                print(f"Device: {devices[0].device_id} (auto-detected)")
            print("=" * 50)

            if args.task:
                print(f"\nTask: {args.task}\n")
                report_progress(
                    {
                        "state": "running",
                        "message": "Starting automation task.",
                        "step": 0,
                    }
                )
                result = agent.run(args.task)
                print(f"\nResult: {result}")

                status = _classify_result_status(result)
                final_payload = _build_result_payload(
                    args=args,
                    status=status,
                    message=result,
                    step_log=step_log,
                    last_screen_description=screen_state.get("last_description", ""),
                )
                report_progress(
                    {
                        "state": status,
                        "message": result,
                        "step": agent.step_count,
                    }
                )
                _print_terminal_summary(final_payload, args.result_json)
                exit_code = 0 if status == "done" else 1
            else:
                print("\nInteractive mode. Type `quit` to exit.\n")
                while True:
                    try:
                        task = input("Enter your task: ").strip()
                        if task.lower() in ("quit", "exit", "q"):
                            print("Goodbye.")
                            break
                        if not task:
                            continue

                        print()
                        result = agent.run(task)
                        print(f"\nResult: {result}\n")
                        report_progress(
                            {
                                "state": _classify_result_status(result),
                                "message": result,
                                "step": agent.step_count,
                            }
                        )
                        agent.reset()
                    except KeyboardInterrupt:
                        print("\n\nInterrupted. Goodbye.")
                        break
                    except Exception as error:
                        print(f"\nError: {error}\n")
    except KeyboardInterrupt:
        final_payload = _build_result_payload(
            args=args,
            status="failed",
            message="Interrupted by user.",
        )
        report_progress({"state": "failed", "message": "Interrupted by user."})
        exit_code = 130
        print("\nInterrupted.")
    except Exception as error:
        final_payload = _build_result_payload(
            args=args,
            status="failed",
            message=f"Unhandled error: {error}",
        )
        report_progress({"state": "failed", "message": f"Unhandled error: {error}"})
        exit_code = 1
        print(f"\nError: {error}")
    finally:
        if args.result_json and final_payload is not None:
            _write_result_json(args.result_json, final_payload)

    if exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
