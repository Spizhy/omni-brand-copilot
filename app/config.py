from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # AI Configuration
    LLM_PROVIDER: Literal["mock", "openai", "gemini"] = "mock"
    LLM_MODEL: str = "gpt-4o-mini"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Brand Guardrails
    STRICT_BUZZWORD_FILTER: bool = True
    MIN_COMPLIANCE_SCORE_PERCENT: float = 85.0
    DATABASE_PATH: str = "data/omni_brand.sqlite3"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
