import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    AI_PROVIDER: str = "gemini"
    GEMINI_API_KEYS: str = ""
    AI_FALLBACK_PROVIDER: str = "fallback"
    REPLICATE_API_TOKEN: str = ""
    
    DATABASE_URL: str = f"sqlite:///{BASE_DIR.as_posix()}/stylemirror.db"
    STORAGE_DIR: str = str(BASE_DIR / "storage")
    PHOTO_TTL_HOURS: int = 24
    
    RATE_LIMIT_ANON_PER_HOUR: int = 10
    DAILY_GENERATION_CAP: int = 500
    ALLOWED_ORIGIN: str = "http://localhost:8000"
    SECRET_KEY: str = "stylemirror-secret-key-development"
    SENTRY_DSN: str = ""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "photos"), exist_ok=True)
