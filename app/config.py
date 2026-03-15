"""Application configuration loaded from environment variables via pydantic-settings."""

import logging
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from .env file or environment variables."""

    OPENROUTER_API_KEY: str
    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    MODEL_NAME: str = "meta-llama/llama-3.1-8b-instruct:free"
    MAX_TOKENS: int = 2048
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx"]
    SITE_URL: str = "http://localhost:8000"
    SITE_NAME: str = "AI Resume Coach"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
