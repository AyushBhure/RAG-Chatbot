"""Application configuration using Pydantic settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseModel):
    """LLM configuration."""

    provider: Literal["openai", "mock"] = "openai"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_tokens: int = 512


class Settings(BaseSettings):
    """Main application settings."""

    app_name: str = "RAG Chatbot"
    environment: Literal["dev", "test", "prod"] = "dev"
    upload_dir: Path = Path("data/uploads")

    # Embeddings / vector store
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_cache_dir: Path | None = None
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 4
    vector_store_dir: Path = Path("vectorstore")

    # LLM + LangChain
    llm: LLMSettings = LLMSettings()
    openai_api_key: str | None = None

    # MLflow
    mlflow_tracking_uri: str = str(Path("mlflow").resolve())

    # Feature toggles
    enable_mlflow: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    Path(settings.vector_store_dir).mkdir(parents=True, exist_ok=True)
    return settings

