"""Centralized project configuration loading."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_LLM_PROVIDER = "gemini"
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
_CONFIG_LOADED = False


def get_project_root() -> Path:
    """Return the repository root resolved from this file location."""

    return Path(__file__).resolve().parents[2]


def get_env_path() -> Path:
    """Return the project-root .env path."""

    return get_project_root() / ".env"


def load_project_env() -> None:
    """Load project .env values, overriding stale shell variables."""

    global _CONFIG_LOADED
    env_path = get_env_path()

    try:
        from dotenv import load_dotenv
    except ImportError:
        _force_env_values(_parse_env_file(env_path))
        _CONFIG_LOADED = True
        return

    load_dotenv(dotenv_path=env_path, override=True)
    _force_env_values(_parse_env_file(env_path))
    _CONFIG_LOADED = True


def ensure_config_loaded() -> None:
    """Load project config once before reading environment values."""

    if not _CONFIG_LOADED:
        load_project_env()


def get_env(name: str, default: str | None = None) -> str | None:
    """Read an environment value."""

    ensure_config_loaded()
    return os.getenv(name, default)


def get_llm_provider() -> str:
    """Return the configured LLM provider in lowercase."""

    ensure_config_loaded()
    provider = os.environ.get("LLM_PROVIDER")
    if provider is None or not provider.strip():
        provider = DEFAULT_LLM_PROVIDER

    return provider.strip().lower()


def get_active_llm_model() -> str:
    """Return the active model name for the configured provider."""

    provider = get_llm_provider()
    if provider == "groq":
        return get_env("GROQ_MODEL", DEFAULT_GROQ_MODEL) or DEFAULT_GROQ_MODEL

    if provider == "openai":
        return get_env("LLM_MODEL", DEFAULT_OPENAI_MODEL) or DEFAULT_OPENAI_MODEL

    return get_env("LLM_MODEL", DEFAULT_GEMINI_MODEL) or DEFAULT_GEMINI_MODEL


def get_llm_model_label() -> str:
    """Return provider:model for display."""

    return f"{get_llm_provider()}:{get_active_llm_model()}"


def has_env_value(name: str) -> bool:
    """Return whether an environment variable is present and non-empty."""

    value = get_env(name, "")
    return bool(value and value.strip())


def get_raw_env_value(name: str) -> str | None:
    """Read a value directly from the project .env file."""

    return _parse_env_file(get_env_path()).get(name)


def _parse_env_file(env_path: Path) -> dict[str, str]:
    """Parse simple KEY=VALUE lines from the project .env file."""

    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def _force_env_values(values: dict[str, str]) -> None:
    """Force parsed .env values into os.environ."""

    for key, value in values.items():
        os.environ[key] = value
