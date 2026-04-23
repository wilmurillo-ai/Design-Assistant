"""Configuration helpers for the Android-only Phone Agent build."""

from phone_agent.config.apps import (
    APP_PACKAGES,
    get_app_name,
    get_package_name,
    list_supported_apps,
)
from phone_agent.config.defaults import (
    DEFAULT_API_KEY,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_STEPS,
    DEFAULT_MODEL_NAME,
    DEFAULT_PROVIDER,
    GEMINI_BASE_URL,
    GEMINI_DEFAULT_MODEL,
    OPENAI_BASE_URL,
    OPENAI_DEFAULT_MODEL,
    PROVIDER_CHATGPT,
    PROVIDER_GEMINI,
    PROVIDER_OPENAI,
    VALID_PROVIDERS,
    get_default_api_key,
    get_default_base_url,
    get_default_model_name,
    infer_default_provider,
    normalize_provider,
)
from phone_agent.config.i18n import get_message, get_messages
from phone_agent.config.prompts import SYSTEM_PROMPT
from phone_agent.config.timing import (
    TIMING_CONFIG,
    ActionTimingConfig,
    ConnectionTimingConfig,
    DeviceTimingConfig,
    TimingConfig,
    get_timing_config,
    update_timing_config,
)


def get_system_prompt(lang: str = "en") -> str:
    """Return the single supported system prompt."""

    _ = lang
    return SYSTEM_PROMPT


__all__ = [
    "APP_PACKAGES",
    "DEFAULT_API_KEY",
    "DEFAULT_BASE_URL",
    "DEFAULT_MAX_STEPS",
    "DEFAULT_MODEL_NAME",
    "DEFAULT_PROVIDER",
    "GEMINI_BASE_URL",
    "GEMINI_DEFAULT_MODEL",
    "OPENAI_BASE_URL",
    "OPENAI_DEFAULT_MODEL",
    "PROVIDER_CHATGPT",
    "PROVIDER_GEMINI",
    "PROVIDER_OPENAI",
    "SYSTEM_PROMPT",
    "TIMING_CONFIG",
    "VALID_PROVIDERS",
    "ActionTimingConfig",
    "ConnectionTimingConfig",
    "DeviceTimingConfig",
    "TimingConfig",
    "get_default_api_key",
    "get_default_base_url",
    "get_default_model_name",
    "get_app_name",
    "get_message",
    "get_messages",
    "get_package_name",
    "get_system_prompt",
    "get_timing_config",
    "infer_default_provider",
    "list_supported_apps",
    "normalize_provider",
    "update_timing_config",
]
