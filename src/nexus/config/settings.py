"""
Central application settings for NEXUS-SENSE AI.

Configuration is loaded from environment variables with
sensible development defaults.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration."""

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------

    app_name: str = "NEXUS-SENSE AI"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8000",
        ]
    )

    # ------------------------------------------------------------------
    # LLM
    # ------------------------------------------------------------------

    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_api_key: str = ""

    llm_temperature: float = 0.2
    llm_max_tokens: int = 4096

    # ------------------------------------------------------------------
    # Embeddings
    # ------------------------------------------------------------------

    embedding_provider: str = "huggingface"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ------------------------------------------------------------------
    # MongoDB
    # ------------------------------------------------------------------

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "nexus_sense"

    # ------------------------------------------------------------------
    # PostgreSQL
    # ------------------------------------------------------------------

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "nexus_sense"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    # ------------------------------------------------------------------
    # Vector database
    # ------------------------------------------------------------------

    vector_store_provider: str = "chroma"
    vector_store_path: str = "./data/vector_store"

    # ------------------------------------------------------------------
    # Agent system
    # ------------------------------------------------------------------

    agent_max_iterations: int = 8
    agent_timeout_seconds: int = 120

    enable_research_agent: bool = True
    enable_extraction_agent: bool = True
    enable_reasoning_agent: bool = True
    enable_anomaly_agent: bool = True
    enable_verification_agent: bool = True
    enable_report_agent: bool = True
    enable_decision_agent: bool = True

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    retrieval_top_k: int = 10
    retrieval_candidate_limit: int = 50
    retrieval_score_threshold: float = 0.25

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 60

    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    log_level: str = "INFO"
    enable_metrics: bool = True
    enable_tracing: bool = False

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    raw_data_path: str = "./data/raw"
    processed_data_path: str = "./data/processed"

    # ------------------------------------------------------------------
    # Pydantic configuration
    # ------------------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached application settings instance.

    Using a cached instance prevents repeatedly parsing
    environment configuration throughout the application.
    """
    return Settings()