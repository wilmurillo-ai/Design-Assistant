"""Default runtime settings for the Android-only build."""

import os

from dotenv import load_dotenv

load_dotenv()

PROVIDER_GEMINI = "gemini"
PROVIDER_OPENAI = "openai"
PROVIDER_CHATGPT = "chatgpt"
VALID_PROVIDERS = (
    PROVIDER_GEMINI,
    PROVIDER_OPENAI,
    PROVIDER_CHATGPT,
)
_PROVIDER_ALIASES = {
    PROVIDER_GEMINI: PROVIDER_GEMINI,
    PROVIDER_OPENAI: PROVIDER_OPENAI,
    PROVIDER_CHATGPT: PROVIDER_OPENAI,
}

GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta/openai/",
)
GEMINI_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")


def normalize_provider(provider: str | None) -> str:
    """Normalize provider names and aliases to the supported runtime values."""

    value = (provider or "").strip().lower()
    if not value:
        return infer_default_provider()
    return _PROVIDER_ALIASES.get(value, PROVIDER_GEMINI)


def infer_default_provider() -> str:
    """Infer the provider from env vars, defaulting to Gemini."""

    configured = os.getenv("PHONE_AGENT_PROVIDER")
    if configured:
        return _PROVIDER_ALIASES.get(configured.strip().lower(), PROVIDER_GEMINI)

    if os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        return PROVIDER_OPENAI

    return PROVIDER_GEMINI


def get_default_base_url(provider: str | None = None) -> str:
    """Resolve the default base URL for the selected provider."""

    generic = os.getenv("PHONE_AGENT_BASE_URL")
    if generic:
        return generic

    provider = normalize_provider(provider)
    if provider == PROVIDER_OPENAI:
        return OPENAI_BASE_URL
    return GEMINI_BASE_URL


def get_default_model_name(provider: str | None = None) -> str:
    """Resolve the default model name for the selected provider."""

    generic = os.getenv("PHONE_AGENT_MODEL")
    if generic:
        return generic

    provider = normalize_provider(provider)
    if provider == PROVIDER_OPENAI:
        return OPENAI_DEFAULT_MODEL
    return GEMINI_DEFAULT_MODEL


def get_default_api_key(provider: str | None = None) -> str:
    """Resolve the default API key for the selected provider."""

    generic = os.getenv("PHONE_AGENT_API_KEY")
    provider = normalize_provider(provider)

    if provider == PROVIDER_OPENAI:
        return os.getenv("OPENAI_API_KEY") or generic or ""
    return os.getenv("GEMINI_API_KEY") or generic or ""


DEFAULT_PROVIDER = infer_default_provider()
DEFAULT_BASE_URL = get_default_base_url(DEFAULT_PROVIDER)
DEFAULT_MODEL_NAME = get_default_model_name(DEFAULT_PROVIDER)
DEFAULT_API_KEY = get_default_api_key(DEFAULT_PROVIDER)
DEFAULT_MAX_STEPS = 100
