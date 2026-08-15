"""Application configuration and environment settings."""

from typing import List, Union
import json
import os
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base backend directory: anchors paths directly to backend/ folder
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""

    PROJECT_NAME: str = "CivicFix"
    API_V1_STR: str = "/api"
    DEBUG: bool = True

    # Database: strictly located at backend/civicfix.db
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'civicfix.db'}"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    # File uploads: strictly anchored to backend/uploads/
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_IMAGE_SIZE_MB: int = 5
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"]
    ALLOWED_IMAGE_MIME_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
        "image/bmp",
    ]

    # AI Configuration (Groq placeholder for future expansion)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama3-70b-8192"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins if provided as a JSON string or comma-separated string."""
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
