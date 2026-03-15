"""Shared FastAPI dependencies for dependency injection."""

from app.config import Settings, settings


def get_settings() -> Settings:
    """Return the global settings instance."""
    return settings
