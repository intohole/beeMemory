from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = Field(default="MemoryService", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # 数据库配置
    DATABASE_URL: str = Field(default="sqlite:///./memory.db", env="DATABASE_URL")
    
    # Embedding服务配置
    EMBEDDING_API_KEY: str = Field(default="", env="EMBEDDING_API_KEY")
    EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    EMBEDDING_BASE_URL: Optional[str] = Field(default=None, env="EMBEDDING_BASE_URL")
    
    # LLM服务配置
    LLM_API_KEY: str = Field(default="", env="LLM_API_KEY")
    LLM_MODEL: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL")
    LLM_BASE_URL: Optional[str] = Field(default=None, env="LLM_BASE_URL")
    LLM_TEMPERATURE: float = Field(default=0.0, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=1000, env="LLM_MAX_TOKENS")
    
    # Chroma配置
    CHROMA_HOST: str = Field(default="localhost", env="CHROMA_HOST")
    CHROMA_PORT: int = Field(default=8000, env="CHROMA_PORT")
    CHROMA_COLLECTION_NAME: str = Field(default="user_memories", env="CHROMA_COLLECTION_NAME")
    
    # 定时任务配置
    MERGE_INTERVAL_MINUTES: int = Field(default=60, env="MERGE_INTERVAL_MINUTES")
    CLEANUP_INTERVAL_MINUTES: int = Field(default=1440, env="CLEANUP_INTERVAL_MINUTES")
    
    # 默认配置
    DEFAULT_EXTRACTION_PROMPT: str = Field(
        default="Extract key elements from the following conversation. Focus on important facts, preferences, and any other information that should be remembered.",
        env="DEFAULT_EXTRACTION_PROMPT"
    )
    DEFAULT_MERGE_THRESHOLD: float = Field(default=0.8, env="DEFAULT_MERGE_THRESHOLD")
    DEFAULT_EXPIRY_STRATEGY: str = Field(default="last_access", env="DEFAULT_EXPIRY_STRATEGY")
    DEFAULT_EXPIRY_DAYS: int = Field(default=30, env="DEFAULT_EXPIRY_DAYS")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
