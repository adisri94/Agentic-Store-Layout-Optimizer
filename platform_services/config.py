"""Central configuration (Layer 4).

All environment-variable access lives here (architecture.md §5.5): no other module
calls ``os.environ`` directly. Settings load from the process environment and an
optional ``.env`` file.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings and feature flags.

    Attributes:
        anthropic_api_key: Anthropic key; empty string selects LLM mock mode.
        api_key: Value the API expects in the ``X-API-Key`` header.
        llm_model: Default Claude model id.
        data_dir: Root directory for data artifacts (Parquet, SQLite, audit log).
        log_level: Logging level name.
        enable_governance: Feature flag for the governance-in-path wrapper.
        mock_llm: Force LLM mock mode regardless of key presence.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    api_key: str = "demo-key"
    llm_model: str = "claude-sonnet-4.5"
    data_dir: Path = Path("data")
    log_level: str = "INFO"
    enable_governance: bool = True
    mock_llm: bool = False


settings = Settings()
