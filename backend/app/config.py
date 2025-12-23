"""
Configuration management for RAG Chatbot Backend
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file
    """

    # API Keys & Connections - Ye fields exactly .env ke variable names se match karenge
    cohere_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    database_url: str

    # Application settings
    app_name: str = "RAG Chatbot Backend"
    debug: bool = False
    environment: str = "development"

    # Performance settings
    max_response_time: float = 60.0  # seconds
    embedding_dimensions: int = 512

    # Pydantic v2 ke liye config yahan define hoti hai
    model_config = SettingsConfigDict(
        env_file=".env",          # .env file load karega
        env_ignore_empty=True,    # empty env vars ignore karega
        extra="ignore",           # extra env vars ko ignore karega (safe hai)
        case_sensitive=False      # case insensitive (COHERE_API_KEY ya cohere_api_key dono kaam karega)
    )


# Singleton instance
settings = Settings()