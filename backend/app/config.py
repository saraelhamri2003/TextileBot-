import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./textilebot.db"
    SECRET_KEY: str = "supersecretjwtkeyfortextilebotcomplianceassistant2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    QDRANT_PATH: str = "./data/qdrant"
    QDRANT_HOST: str = ""
    QDRANT_PORT: int = 6333
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    LLM_MODEL_ID: str = "llama3.2:3b"
    USE_LOCAL_LLM: bool = True
    USE_OPENAI_LLM: bool = False
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_BASE_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
