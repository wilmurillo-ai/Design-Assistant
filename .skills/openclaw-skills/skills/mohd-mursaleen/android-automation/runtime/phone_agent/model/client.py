"""Model client for Gemini/OpenAI via the OpenAI-compatible API."""

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from http.client import IncompleteRead
from typing import Any

from phone_agent.config import (
    PROVIDER_OPENAI,
    get_default_api_key,
    get_default_base_url,
    get_default_model_name,
    infer_default_provider,
    normalize_provider,
)
from phone_agent.config.i18n import get_message


@dataclass
class ModelConfig:
    """Configuration for the model backend."""

    provider: str = field(default_factory=infer_default_provider)
    base_url: str | None = None
    api_key: str | None = None
    model_name: str | None = None
    max_tokens: int = 3000
    temperature: float = 0.0
    top_p: float = 0.85
    extra_body: dict[str, Any] = field(default_factory=dict)
    lang: str = "en"

    def __post_init__(self) -> None:
        self.provider = normalize_provider(self.provider)
        if self.base_url is None:
            self.base_url = get_default_base_url(self.provider)
        if self.api_key is None:
            self.api_key = get_default_api_key(self.provider)
        if self.model_name is None:
            self.model_name = get_default_model_name(self.provider)


@dataclass
class ModelResponse:
    """Response returned by the model client."""

    thinking: str
    action: str
    raw_content: str
    time_to_first_token: float | None = None
    time_to_thinking_end: float | None = None
    total_time: float | None = None


class ModelClient:
    """Client for OpenAI-compatible multimodal models."""

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()

    def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
        """Send a request to the model and stream the response."""

        start_time = time.time()
        time_to_first_token = None
        time_to_thinking_end = None

        payload: dict[str, Any] = {
            "messages": messages,
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "stream": True,
        }
        if self.config.provider == PROVIDER_OPENAI:
            payload["max_completion_tokens"] = self.config.max_tokens
        else:
            payload["max_tokens"] = self.config.max_tokens
        if self.config.extra_body:
            payload["extra_body"] = self.config.extra_body

        raw_content = ""
        buffer = ""
        action_markers = ["<answer>", "finish(", "do("]
        in_action_phase = False
        first_token_received = False

        for chunk in _stream_chat_completion(
            base_url=self.config.base_url or "",
            api_key=self.config.api_key or "",
            payload=payload,
        ):
            content = _extract_stream_chunk_content(chunk)
            if not content:
                continue

            raw_content += content

            if not first_token_received:
                time_to_first_token = time.time() - start_time
                first_token_received = True

            if in_action_phase:
                continue

            buffer += content
            marker_found = False

            for marker in action_markers:
                if marker in buffer:
                    thinking_part = buffer.split(marker, 1)[0]
                    cleaned_thinking = self._clean_reasoning(thinking_part)
                    if cleaned_thinking:
                        print(cleaned_thinking, end="", flush=True)
                        print()
                    in_action_phase = True
                    marker_found = True
                    if time_to_thinking_end is None:
                        time_to_thinking_end = time.time() - start_time
                    break

            if marker_found:
                continue

            is_potential_marker = False
            for marker in action_markers:
                for index in range(1, len(marker)):
                    if buffer.endswith(marker[:index]):
                        is_potential_marker = True
                        break
                if is_potential_marker:
                    break

            if not is_potential_marker:
                print(buffer, end="", flush=True)
                buffer = ""

        total_time = time.time() - start_time
        thinking, action = self._parse_response(raw_content)

        print()
        print("=" * 50)
        print(f"{get_message('performance_metrics', self.config.lang)}:")
        print("-" * 50)
        if time_to_first_token is not None:
            print(
                f"{get_message('time_to_first_token', self.config.lang)}: "
                f"{time_to_first_token:.3f}s"
            )
        if time_to_thinking_end is not None:
            print(
                f"{get_message('time_to_thinking_end', self.config.lang)}: "
                f"{time_to_thinking_end:.3f}s"
            )
        print(
            f"{get_message('total_inference_time', self.config.lang)}: "
            f"{total_time:.3f}s"
        )
        print("=" * 50)

        return ModelResponse(
            thinking=thinking,
            action=action,
            raw_content=raw_content,
            time_to_first_token=time_to_first_token,
            time_to_thinking_end=time_to_thinking_end,
            total_time=total_time,
        )

    def _parse_response(self, content: str) -> tuple[str, str]:
        """Split model output into freeform reasoning and the final command."""

        content = content.strip()
        if not content:
            return "", ""

        if "<answer>" in content:
            parts = content.split("<answer>", 1)
            thinking = self._clean_reasoning(parts[0])
            answer_section = parts[1].split("</answer>", 1)[0].strip()
            command_span = self._find_command_span(answer_section)
            if command_span is not None:
                start, end = command_span
                return thinking, answer_section[start:end].strip()
            return thinking, self._clean_reasoning(answer_section)

        command_span = self._find_command_span(content)
        if command_span is not None:
            start, end = command_span
            thinking = self._clean_reasoning(content[:start])
            action = content[start:end].strip()
            return thinking, action

        return self._clean_reasoning(content), content

    @staticmethod
    def _clean_reasoning(content: str) -> str:
        """Remove tag wrappers and formatting noise from model reasoning."""

        cleaned = content
        for token in ("<think>", "</think>", "<answer>", "</answer>", "```"):
            cleaned = cleaned.replace(token, "")
        return cleaned.strip()

    @staticmethod
    def _find_command_span(content: str) -> tuple[int, int] | None:
        """Return the span of the first balanced `do(...)` or `finish(...)` call."""

        starts = [index for index in (content.find("do("), content.find("finish(")) if index != -1]
        if not starts:
            return None

        start = min(starts)
        depth = 0
        quote_char: str | None = None
        escaped = False

        for index in range(start, len(content)):
            char = content[index]

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
                    return start, index + 1

        return None


class MessageBuilder:
    """Helpers for building chat-completion message payloads."""

    @staticmethod
    def create_system_message(content: str) -> dict[str, Any]:
        return {"role": "system", "content": content}

    @staticmethod
    def create_user_message(
        text: str, image_base64: str | None = None
    ) -> dict[str, Any]:
        content: list[dict[str, Any]] = []
        if image_base64:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                }
            )
        content.append({"type": "text", "text": text})
        return {"role": "user", "content": content}

    @staticmethod
    def create_assistant_message(content: str) -> dict[str, Any]:
        return {"role": "assistant", "content": content}

    @staticmethod
    def remove_images_from_message(message: dict[str, Any]) -> dict[str, Any]:
        if isinstance(message.get("content"), list):
            message["content"] = [
                item for item in message["content"] if item.get("type") == "text"
            ]
        return message

    @staticmethod
    def build_screen_info(current_app: str, **extra_info) -> str:
        info = {"current_app": current_app, **extra_info}
        return json.dumps(info, ensure_ascii=False)


def create_chat_completion(
    *,
    base_url: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Send a non-streaming OpenAI-compatible chat completion request."""

    request = urllib.request.Request(
        _build_chat_completions_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers=_build_headers(api_key),
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP {error.code} from model API: {detail or error.reason}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Model API request failed: {error.reason}") from error

    try:
        return json.loads(raw_body)
    except json.JSONDecodeError as error:
        raise RuntimeError("Model API returned invalid JSON.") from error


def _stream_chat_completion(
    *,
    base_url: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: float = 300.0,
):
    """Yield streamed OpenAI-compatible chat completion chunks."""

    headers = _build_headers(api_key)
    headers["Accept"] = "text/event-stream"
    request = urllib.request.Request(
        _build_chat_completions_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            event_lines: list[str] = []
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line:
                    if event_lines:
                        yield from _parse_sse_event_data(event_lines)
                        event_lines = []
                    continue
                if line.startswith("data:"):
                    event_lines.append(line[5:].strip())

            if event_lines:
                yield from _parse_sse_event_data(event_lines)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"HTTP {error.code} from model API: {detail or error.reason}"
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Model API request failed: {error.reason}") from error
    except IncompleteRead as error:
        partial = error.partial.decode("utf-8", errors="replace")
        raise RuntimeError(f"Model stream ended unexpectedly: {partial}") from error


def _parse_sse_event_data(event_lines: list[str]):
    """Decode SSE event payloads into JSON objects."""

    event_data = "\n".join(event_lines).strip()
    if not event_data or event_data == "[DONE]":
        return []

    try:
        return [json.loads(event_data)]
    except json.JSONDecodeError:
        return []


def _build_chat_completions_url(base_url: str) -> str:
    """Return the REST URL for the chat completions endpoint."""

    return f"{base_url.rstrip('/')}/chat/completions"


def _build_headers(api_key: str) -> dict[str, str]:
    """Build the shared request headers for the compatibility API."""

    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _extract_stream_chunk_content(chunk: dict[str, Any]) -> str:
    """Extract assistant text from a streamed chat-completions chunk."""

    choices = chunk.get("choices")
    if not choices:
        return ""

    delta = choices[0].get("delta", {})
    content = delta.get("content")
    return _coerce_content_to_text(content)


def _coerce_content_to_text(content: Any) -> str:
    """Coerce OpenAI-compatible content shapes to plain text."""

    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") in {"text", "output_text"}:
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return ""
