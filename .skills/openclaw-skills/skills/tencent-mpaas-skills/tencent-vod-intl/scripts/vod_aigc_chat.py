#!/usr/bin/env python3
"""
Tencent Cloud VOD AIGC Text Generation (LLM Chat) Tool

Calls large language model capabilities through the LLM proxy interface
provided by Tencent Cloud VOD. The interface is fully compatible with the
OpenAI standard chat completions API (same protocol, request/response format).

Endpoint: https://text-aigc.vod-qcloud.com/v1/chat/completions
Authentication: Bearer Token (create via vod_aigc_token.py)

Supported models (as of 2026-03-19):
  OpenAI: gpt-5.4, gpt-5.2, gpt-5.1, gpt-5-chat, gpt-5-nano, gpt-4o
  Gemini: gemini-3.1-pro-preview, gemini-3.1-flash-lite-preview,
          gemini-3-flash-preview, gemini-2.5-pro, gemini-2.5-flash

Supports multimodal input: text, images (URL), audio (Base64), files/video (URL)

Subcommands:
  chat     Send a chat request (non-streaming, returns full response at once)
  stream   Send a chat request (streaming, outputs incrementally)

Usage examples:
  # Basic chat
  python scripts/vod_aigc_chat.py chat \
      --token <YOUR_API_TOKEN> \
      --model gpt-5.1 \
      --message "Hello, please introduce Tencent Cloud VOD"

  # Streaming output
  python scripts/vod_aigc_chat.py stream \
      --token <YOUR_API_TOKEN> \
      --model gemini-2.5-flash \
      --message "Write a poem about cloud computing"

  # With system prompt
  python scripts/vod_aigc_chat.py chat \
      --token <YOUR_API_TOKEN> \
      --model gpt-5.1 \
      --system "You are a professional video processing expert" \
      --message "What is the difference between H.264 and H.265?"

  # Multi-turn conversation (specify full messages in JSON format)
  python scripts/vod_aigc_chat.py chat \
      --token <YOUR_API_TOKEN> \
      --model gpt-5.1 \
      --messages '[{"role":"user","content":"Hello"},{"role":"assistant","content":"Hello!"},{"role":"user","content":"Introduce yourself"}]'

  # Image understanding
  python scripts/vod_aigc_chat.py chat \
      --token <YOUR_API_TOKEN> \
      --model gpt-5.1 \
      --message "Please describe the content of this image" \
      --image-url "https://example.com/image.jpg"

  # Enable reasoning/thinking mode
  python scripts/vod_aigc_chat.py chat \
      --token <YOUR_API_TOKEN> \
      --model gpt-5.4 \
      --message "Please solve a math problem: ..." \
      --thinking

  # Function Calling (tool use)
  python scripts/vod_aigc_chat.py chat \
      --token <YOUR_API_TOKEN> \
      --model gpt-5.1 \
      --message "What is the weather like in Beijing today?" \
      --tools '[{"type":"function","function":{"name":"get_weather","description":"Get weather for a specified city","parameters":{"type":"object","properties":{"city":{"type":"string","description":"City name"}},"required":["city"]}}}]' \
      --tool-choice auto

  # Read token from environment variable
  export TENCENTCLOUD_VOD_AIGC_TOKEN=<YOUR_API_TOKEN>
  python scripts/vod_aigc_chat.py chat --model gpt-5.1 --message "Hello"
"""

import argparse
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    print("❌ Missing dependency, please install first: pip install requests", file=sys.stderr)
    sys.exit(1)

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

AIGC_CHAT_URL  = "https://text-aigc.vod-qcloud.com/v1/chat/completions"
DEFAULT_MODEL  = "gpt-5.1"
DEFAULT_TIMEOUT = 120  # seconds

# Supported model list
SUPPORTED_MODELS = [
    # OpenAI series
    "gpt-5.4",
    "gpt-5.2",
    "gpt-5.1",
    "gpt-5-chat",
    "gpt-5-nano",
    "gpt-4o",
    # Gemini series
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
]

# Models that do not support thinking_enabled
NO_THINKING_MODELS = {"gpt-5.1", "gpt-5.2", "gpt-4o"}


# ─────────────────────────────────────────────
# Core request functions
# ─────────────────────────────────────────────

def build_messages(
    message: str = None,
    system: str = None,
    messages_json: str = None,
    image_url: str = None,
    audio_base64: str = None,
    audio_format: str = None,
    file_url: str = None,
    file_name: str = None,
) -> list:
    """
    Build the messages array.
    Supports plain text, multimodal (image/audio/file), and full JSON format.
    """
    # If a complete messages JSON is provided, use it directly
    if messages_json:
        try:
            return json.loads(messages_json)
        except json.JSONDecodeError as e:
            print(f"❌ --messages JSON format error: {e}", file=sys.stderr)
            sys.exit(1)

    msgs = []

    # System prompt
    if system:
        msgs.append({"role": "system", "content": system})

    # User message (supports multimodal)
    if message:
        if image_url or audio_base64 or file_url:
            # Multimodal message: content is an array of Parts
            parts = [{"type": "text", "text": message}]

            if image_url:
                parts.append({
                    "type": "image_url",
                    "image_url": image_url,
                })

            if audio_base64:
                fmt = audio_format or "mp3"
                parts.append({
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_base64,
                        "format": fmt,
                    },
                })

            if file_url:
                part = {
                    "type": "file",
                    "file_url": file_url,
                }
                if file_name:
                    part["file_name"] = file_name
                parts.append(part)

            msgs.append({"role": "user", "content": parts})
        else:
            # Plain text message
            msgs.append({"role": "user", "content": message})

    if not msgs:
        print("❌ Please provide conversation content via --message or --messages", file=sys.stderr)
        sys.exit(1)

    return msgs


def build_request_body(
    model: str,
    messages: list,
    stream: bool = False,
    thinking: bool = False,
    temperature: float = None,
    max_tokens: int = None,
    reasoning_effort: str = None,
    response_format: str = None,
    tools: list = None,
    tool_choice=None,
) -> dict:
    """Build the request body"""
    body = {
        "model":    model,
        "messages": messages,
        "stream":   stream,
    }

    # thinking_enabled (not supported by some models)
    if thinking and model not in NO_THINKING_MODELS:
        body["thinking_enabled"] = True

    if temperature is not None:
        body["temperature"] = temperature

    if max_tokens is not None:
        body["max_tokens"] = max_tokens

    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort

    if response_format == "json":
        body["response_format"] = {"type": "json_object"}
    elif response_format == "json_schema":
        # json_schema type requires a specific schema; otherwise the API returns an error
        # Fall back to json_object if no schema is provided
        body["response_format"] = {"type": "json_object"}

    if tools:
        body["tools"] = tools

    if tool_choice is not None:
        body["tool_choice"] = tool_choice

    return body


def send_chat_request(
    token: str,
    body: dict,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """Send a non-streaming request and return the complete response"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }
    try:
        resp = requests.post(
            AIGC_CHAT_URL,
            headers=headers,
            json=body,
            timeout=timeout,
        )
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out ({timeout}s), please increase the --timeout parameter", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle HTTP errors
    if resp.status_code != 200:
        _handle_http_error(resp)

    try:
        return resp.json()
    except json.JSONDecodeError:
        print(f"❌ Failed to parse response, raw content: {resp.text[:500]}", file=sys.stderr)
        sys.exit(1)



def send_stream_request(
    token: str,
    body: dict,
    timeout: int = DEFAULT_TIMEOUT,
) -> str:
    """Send a streaming request, output content progressively, and return the full text"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }
    body["stream"] = True

    try:
        resp = requests.post(
            AIGC_CHAT_URL,
            headers=headers,
            json=body,
            stream=True,
            timeout=timeout,
        )
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out ({timeout}s)", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed: {e}", file=sys.stderr)
        sys.exit(1)

    if resp.status_code != 200:
        _handle_http_error(resp)

    full_text = []
    print()  # blank line before output begins

    for line in resp.iter_lines():
        if not line:
            continue
        line_str = line.decode("utf-8") if isinstance(line, bytes) else line

        # SSE format: data: {...}
        if line_str.startswith("data: "):
            data_str = line_str[6:].strip()
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
                delta = (chunk.get("choices") or [{}])[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    print(content, end="", flush=True)
                    full_text.append(content)
            except json.JSONDecodeError:
                continue

    print()  # newline after streaming output ends
    return "".join(full_text)


def _handle_http_error(resp):
    """Handle HTTP error responses"""
    status = resp.status_code
    error_map = {
        400: "Bad request parameters (400)",
        401: "Authentication failed (401) — Please check if the Token is correct, or if the Token has been synced to the gateway (may take ~1 minute)",
        403: "Insufficient permissions or service suspended (403) — Possible overdue balance, please check your account",
        404: "Model/endpoint not found (404) — Please check if the model parameter is correct",
        429: "Rate limit exceeded (429) — Default RPM: 10 requests/min, TPM: 100K tokens/min",
        500: "Internal server error (500)",
        502: "Gateway error (502)",
        503: "Service unavailable (503)",
    }
    msg = error_map.get(status, f"HTTP error {status}")
    try:
        err_body = resp.json()
        err_detail = err_body.get("error", {})
        if isinstance(err_detail, dict):
            err_msg = err_detail.get("message", "")
        else:
            err_msg = str(err_detail)
        req_id = resp.headers.get("X-Request-Id", "")
        print(f"❌ {msg}", file=sys.stderr)
        if err_msg:
            print(f"   Error details: {err_msg}", file=sys.stderr)
        if req_id:
            print(f"   Request-Id: {req_id}", file=sys.stderr)
    except Exception:
        print(f"❌ {msg}", file=sys.stderr)
        print(f"   Raw response: {resp.text[:500]}", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────
# Output Formatting
# ─────────────────────────────────────────────

def print_chat_result(
    resp: dict,
    as_json: bool = False,
    output_file: str = None,
    show_usage: bool = True,
):
    """Print non-streaming chat result"""
    if as_json:
        print(json.dumps(resp, ensure_ascii=False, indent=2))
    else:
        choices = resp.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            content = msg.get("content", "")
            finish_reason = choices[0].get("finish_reason", "")
            sep = "─" * 60
            print(f"\n{sep}")
            print(content)
            print(f"{sep}")

            if show_usage:
                usage = resp.get("usage", {})
                if usage:
                    p_tokens = usage.get("prompt_tokens", 0)
                    c_tokens = usage.get("completion_tokens", 0)
                    t_tokens = usage.get("total_tokens", 0)
                    print(f"📊 Token usage: input {p_tokens} + output {c_tokens} = total {t_tokens}")

            model = resp.get("model", "")
            req_id = resp.get("id", "")
            print(f"🤖 Model: {model}  |  ID: {req_id}")
            if finish_reason and finish_reason != "stop":
                print(f"⚠️  Stop reason: {finish_reason}")
            print()
        else:
            print("⚠️  No reply content received", file=sys.stderr)

    if output_file:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)
        print(f"💾 Result saved: {output_file}")


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────

def add_common_args(parser):
    """Add common arguments"""
    parser.add_argument(
        "--token",
        default=os.environ.get("TENCENTCLOUD_VOD_AIGC_TOKEN", ""),
        help="AIGC API Token (can also be set via environment variable TENCENTCLOUD_VOD_AIGC_TOKEN)",
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        choices=SUPPORTED_MODELS,
        help=f"Model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--message", "-q",
        help="User message content (simple single-turn conversation)",
    )
    parser.add_argument(
        "--messages",
        help="Full messages JSON array (for multi-turn conversations, mutually exclusive with --message)",
    )
    parser.add_argument(
        "--system", "-s",
        help="System prompt (sets the AI role/persona)",
    )
    # Multimodal parameters
    parser.add_argument(
        "--image-url",
        help="Image URL (supports multimodal, size limit 70MB)",
    )
    parser.add_argument(
        "--audio-base64",
        help="Base64-encoded audio data (supports mp3/wav)",
    )
    parser.add_argument(
        "--audio-format",
        choices=["mp3", "wav"],
        default="mp3",
        help="Audio format (default: mp3)",
    )
    parser.add_argument(
        "--file-url",
        help="File/video URL (supports multimodal, size limit 70MB)",
    )
    parser.add_argument(
        "--file-name",
        help="File name (used together with --file-url)",
    )
    # Generation parameters
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        help="Output randomness (0~2, default 0.7; lower = more precise, higher = more creative)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum number of tokens to generate",
    )
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="Enable reasoning/thinking mode (CoT, suitable for complex logic/math/code; note: gpt-5.1/5.2/4o do not support this)",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=["none", "minimal", "low", "medium", "high", "xhigh"],
        help="Thinking level (used together with --thinking; this parameter takes precedence)",
    )
    parser.add_argument(
        "--response-format",
        choices=["text", "json", "json_schema"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output full response in JSON format",
    )
    parser.add_argument(
        "--output-file",
        help="Save response JSON to the specified file path",
    )
    parser.add_argument(
        "--no-usage",
        action="store_true",
        help="Do not display Token usage statistics",
    )
    parser.add_argument(
        "--tools",
        help="Function Calling tool definitions, JSON array format (OpenAI tools field), example: '[{\"type\":\"function\",\"function\":{\"name\":\"get_weather\",\"description\":\"Get weather\",\"parameters\":{}}}]'",
    )
    parser.add_argument(
        "--tool-choice",
        help="Tool invocation strategy: 'auto' (model decides automatically), 'none' (do not call tools), 'required' (must call a tool), or JSON to specify a specific tool (e.g. '{\"type\":\"function\",\"function\":{\"name\":\"get_weather\"}}')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print request body preview only, do not send the request",
    )



def build_parser():
    parser = argparse.ArgumentParser(
        description="Tencent Cloud VOD AIGC Text Generation (LLM Chat)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # ── chat (non-streaming) ──
    p_chat = subparsers.add_parser(
        "chat",
        help="Send a chat request (non-streaming, waits for complete response)",
    )
    add_common_args(p_chat)

    # ── stream (streaming) ──
    p_stream = subparsers.add_parser(
        "stream",
        help="Send a chat request (streaming, outputs content incrementally)",
    )
    add_common_args(p_stream)

    # ── models (view supported models) ──
    subparsers.add_parser(
        "models",
        help="View the list of all currently supported models",
    )

    return parser


def validate_args(args):
    """Argument validation"""
    if args.command in ("chat", "stream"):
        if not args.token:
            print("❌ No Token provided. Please set it via --token or the environment variable TENCENTCLOUD_VOD_AIGC_TOKEN", file=sys.stderr)
            print("   Use vod_aigc_token.py create to create a Token", file=sys.stderr)
            sys.exit(1)

        if not args.message and not args.messages:
            print("❌ Please provide conversation content via --message or --messages", file=sys.stderr)
            sys.exit(1)

        if args.message and args.messages:
            print("❌ --message and --messages cannot be used at the same time", file=sys.stderr)
            sys.exit(1)

        if args.thinking and args.model in NO_THINKING_MODELS:
            print(f"⚠️  Model {args.model} does not support the thinking parameter, it has been automatically ignored", file=sys.stderr)


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # View model list
    if args.command == "models":
        print("\nSupported model list:")
        print("\n  OpenAI series (supports text and image input):")
        for m in [m for m in SUPPORTED_MODELS if m.startswith("gpt")]:
            note = " (thinking not supported)" if m in NO_THINKING_MODELS else ""
            print(f"    {m}{note}")
        print("\n  Gemini series (supports text, code, image, audio, and video input):")
        for m in [m for m in SUPPORTED_MODELS if m.startswith("gemini")]:
            print(f"    {m}")
        print("\n⚠️  Rate limit: default RPM 10 requests/minute, TPM 100K tokens/minute")
        print("📌 gemini-3-pro-preview was taken offline on March 9\n")
        return

    validate_args(args)

    # Parse tools argument
    tools_list = None
    if getattr(args, "tools", None):
        try:
            tools_list = json.loads(args.tools)
            if not isinstance(tools_list, list):
                print("❌ --tools must be in JSON array format", file=sys.stderr)
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ --tools JSON format error: {e}", file=sys.stderr)
            sys.exit(1)

    # Parse tool_choice argument
    tool_choice_val = None
    if getattr(args, "tool_choice", None):
        raw = args.tool_choice.strip()
        if raw in ("auto", "none", "required"):
            tool_choice_val = raw
        else:
            try:
                tool_choice_val = json.loads(raw)
            except json.JSONDecodeError as e:
                print(f"❌ --tool-choice JSON format error: {e}", file=sys.stderr)
                sys.exit(1)

    # Build messages
    messages = build_messages(
        message=args.message,
        system=args.system,
        messages_json=args.messages,
        image_url=args.image_url,
        audio_base64=args.audio_base64,
        audio_format=args.audio_format,
        file_url=args.file_url,
        file_name=args.file_name,
    )

    # Build request body
    body = build_request_body(
        model=args.model,
        messages=messages,
        stream=(args.command == "stream"),
        thinking=args.thinking,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        reasoning_effort=args.reasoning_effort,
        response_format=args.response_format if args.response_format != "text" else None,
        tools=tools_list,
        tool_choice=tool_choice_val,
    )

    # dry-run preview
    if args.dry_run:
        print("🔍 dry-run request body preview:")
        print(json.dumps(body, ensure_ascii=False, indent=2))
        print(f"\nRequest URL: POST {AIGC_CHAT_URL}")
        print(f"Authorization: Bearer {args.token[:8]}... (hidden)")
        return

    # Print request info (in --json mode, output to stderr to avoid polluting JSON stdout)
    _out = sys.stderr if args.json_output else sys.stdout
    model_info = args.model
    msg_count  = len(messages)
    print(f"🚀 Sending request | Model: {model_info} | Message count: {msg_count}", file=_out)
    if args.thinking and args.model not in NO_THINKING_MODELS:
        print("   🧠 Reasoning/thinking mode enabled", file=_out)
    if args.reasoning_effort:
        print(f"   🎯 Thinking level: {args.reasoning_effort}", file=_out)

    start_time = time.time()

    if args.command == "chat":
        resp = send_chat_request(
            token=args.token,
            body=body,
            timeout=args.timeout,
        )
        elapsed = time.time() - start_time
        print(f"⏱️  Elapsed: {elapsed:.1f}s", file=_out)
        print_chat_result(
            resp,
            as_json=args.json_output,
            output_file=args.output_file,
            show_usage=not args.no_usage,
        )

    elif args.command == "stream":
        print("📡 Streaming output:", file=_out)
        full_text = send_stream_request(
            token=args.token,
            body=body,
            timeout=args.timeout,
        )
        elapsed = time.time() - start_time
        print(f"⏱️  Elapsed: {elapsed:.1f}s  |  Output characters: {len(full_text)}", file=_out)

        if args.output_file:
            os.makedirs(os.path.dirname(os.path.abspath(args.output_file)), exist_ok=True)
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"💾 Result saved: {args.output_file}")


if __name__ == "__main__":
    main()