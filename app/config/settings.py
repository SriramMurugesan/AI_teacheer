"""
Application settings loaded from environment variables.
Uses pydantic-settings for type-safe configuration.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized configuration — reads from .env or environment."""

    # ── LLM Provider ──────────────────────────────────────────
    LLM_PROVIDER: str = "ollama"  # "ollama" | "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # ── Embeddings ────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── Chunking ──────────────────────────────────────────────
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 50

    # ── Vector search ─────────────────────────────────────────
    TOP_K: int = 5

    # ── Uploads ───────────────────────────────────────────────
    UPLOAD_DIR: str = "data/uploads"

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def upload_path(self) -> Path:
        return Path(self.UPLOAD_DIR)


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()
