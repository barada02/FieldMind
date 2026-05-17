"""
Configuration management for Field Mind application.
Uses Pydantic Settings for environment variable validation and type safety.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI-compatible LLM Configuration
    openai_api_key: str = Field(..., description="OpenAI API key or compatible provider key")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for OpenAI-compatible API"
    )
    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="Model name to use"
    )
    
    # Jina AI Configuration
    jina_api_key: str = Field(..., description="Jina AI API key for embeddings")
    jina_model: str = Field(
        default="jina-embeddings-v5-text-small",
        description="Jina embedding model to use"
    )
    jina_task: str = Field(
        default="retrieval.query",
        description="Jina task type (retrieval.query or retrieval.passage)"
    )
    
    # IBM Cloudant Configuration
    cloudant_url: Optional[str] = Field(default=None, description="Cloudant instance URL")
    cloudant_username: str = Field(default="", description="Cloudant username")
    cloudant_password: str = Field(default="", description="Cloudant password")
    cloudant_api_key: Optional[str] = Field(default=None, description="Cloudant API key")
    
    # Database Names
    cloudant_machines_db: str = Field(default="machines", description="Machines database name")
    cloudant_inventory_db: str = Field(default="inventory", description="Inventory database name")
    cloudant_tickets_db: str = Field(default="tickets", description="Tickets database name")
    
    # ChromaDB Configuration
    chroma_persist_directory: str = Field(
        default="../data/chromadb",
        description="ChromaDB persistence directory"
    )
    chroma_collection_name: str = Field(
        default="sops",
        description="ChromaDB collection name for SOPs"
    )
    
    # Application Configuration
    app_host: str = Field(default="0.0.0.0", description="Application host")
    app_port: int = Field(default=8000, description="Application port")
    app_debug: bool = Field(default=False, description="Debug mode")
    app_reload: bool = Field(default=False, description="Auto-reload on code changes")
    
    # MCP Server Configuration
    mcp_server_host: str = Field(default="localhost", description="MCP server host")
    mcp_server_port: int = Field(default=8001, description="MCP server port")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/fieldmind.log", description="Log file path")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:8000", "http://127.0.0.1:8000"],
        description="Allowed CORS origins"
    )
    
    # Security
    secret_key: str = Field(
        default="change_this_secret_key_in_production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    
    @validator("chroma_persist_directory")
    def validate_chroma_directory(cls, v):
        """Ensure ChromaDB directory exists."""
        abs_path = os.path.abspath(v)
        os.makedirs(abs_path, exist_ok=True)
        return abs_path
    
    @validator("log_file")
    def validate_log_directory(cls, v):
        """Ensure log directory exists."""
        log_dir = os.path.dirname(v)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        return v
    
    @property
    def mcp_server_url(self) -> str:
        """Get full MCP server URL."""
        return f"http://{self.mcp_server_host}:{self.mcp_server_port}"
    
    @property
    def cloudant_auth(self) -> dict:
        """Get Cloudant authentication configuration."""
        if self.cloudant_api_key:
            return {"api_key": self.cloudant_api_key}
        return {
            "username": self.cloudant_username,
            "password": self.cloudant_password
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings

# Made with Bob
