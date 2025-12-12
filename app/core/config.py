import yaml
import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator


class AppConfig(BaseSettings):
    """应用配置"""
    name: str = Field(default="MemoryService", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    url: str = Field(default="sqlite:///./data/memory.db", env="DATABASE_URL")


class LLMConfig(BaseSettings):
    """大模型配置"""
    model: str = Field(default="glm-4-flash", env="LLM_MODEL")
    api_key: str = Field(default="", env="LLM_API_KEY")
    base_url: Optional[str] = Field(default="https://open.bigmodel.cn/api/paas/v4/", env="LLM_BASE_URL")
    timeout: int = Field(default=360, env="LLM_TIMEOUT")
    max_retries: int = Field(default=3, env="LLM_MAX_RETRIES")
    temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2048, env="LLM_MAX_TOKENS")


class EmbeddingConfig(BaseSettings):
    """嵌入服务配置"""
    model: str = Field(default="embedding-3", env="EMBEDDING_MODEL")
    api_key: str = Field(default="", env="EMBEDDING_API_KEY")
    base_url: Optional[str] = Field(default="https://open.bigmodel.cn/api/paas/v4/", env="EMBEDDING_BASE_URL")
    timeout: int = Field(default=30, env="EMBEDDING_TIMEOUT")
    max_retries: int = Field(default=3, env="EMBEDDING_MAX_RETRIES")
    dimension: int = Field(default=1536, env="EMBEDDING_DIMENSION")
    normalize: bool = Field(default=True, env="EMBEDDING_NORMALIZE")


class ChromaConfig(BaseSettings):
    """Chroma向量数据库配置"""
    host: str = Field(default="localhost", env="CHROMA_HOST")
    port: int = Field(default=8999, env="CHROMA_PORT")
    collection_name: str = Field(default="prompts", env="CHROMA_COLLECTION_NAME")
    timeout: int = Field(default=30, env="CHROMA_TIMEOUT")
    persist_directory: Optional[str] = Field(default="./data/chroma_data", env="CHROMA_PERSIST_DIRECTORY")
    use_persistent_client: bool = Field(default=False, env="CHROMA_USE_PERSISTENT_CLIENT")


class SchedulerConfig(BaseSettings):
    """定时任务配置"""
    merge_interval_minutes: int = Field(default=60, env="MERGE_INTERVAL_MINUTES")
    cleanup_interval_minutes: int = Field(default=1440, env="CLEANUP_INTERVAL_MINUTES")


class MemoryConfig(BaseSettings):
    """记忆管理默认配置"""
    default_extraction_prompt: str = Field(
        default="Extract key elements from the following conversation. Focus on important facts, preferences, and any other information that should be remembered.",
        env="DEFAULT_EXTRACTION_PROMPT"
    )
    default_merge_threshold: float = Field(default=0.8, env="DEFAULT_MERGE_THRESHOLD")
    default_expiry_strategy: str = Field(default="last_access", env="DEFAULT_EXPIRY_STRATEGY")
    default_expiry_days: int = Field(default=30, env="DEFAULT_EXPIRY_DAYS")
    max_memories_per_user: int = Field(default=1000, env="MAX_MEMORIES_PER_USER")
    max_memories_per_app: int = Field(default=500, env="MAX_MEMORIES_PER_APP")
    embedding_cache_ttl: int = Field(default=604800, env="EMBEDDING_CACHE_TTL")  # 7天
    llm_cache_ttl: int = Field(default=604800, env="LLM_CACHE_TTL")  # 7天
    
    class PriorityWeights(BaseSettings):
        """优先级权重配置"""
        content_length: float = Field(default=0.3, env="PRIORITY_WEIGHT_CONTENT_LENGTH")
        element_count: float = Field(default=0.4, env="PRIORITY_WEIGHT_ELEMENT_COUNT")
        access_frequency: float = Field(default=0.3, env="PRIORITY_WEIGHT_ACCESS_FREQUENCY")
    
    priority_weights: PriorityWeights = PriorityWeights()


class LoggingConfig(BaseSettings):
    """日志配置"""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH")
    max_size: int = Field(default=10485760, env="LOG_MAX_SIZE")  # 10MB
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    use_json: bool = Field(default=False, env="LOG_USE_JSON")


class Settings(BaseSettings):
    """主配置类"""
    app: AppConfig = AppConfig()
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    embedding: EmbeddingConfig = EmbeddingConfig()
    chroma: ChromaConfig = ChromaConfig()
    scheduler: SchedulerConfig = SchedulerConfig()
    memory: MemoryConfig = MemoryConfig()
    logging: LoggingConfig = LoggingConfig()
    timezone: str = Field(default="Asia/Shanghai", env="TIMEZONE")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        extra="ignore"  # 忽略额外的输入，保持向后兼容性
    )
    
    @classmethod
    def from_yaml(cls, yaml_path: str = None):
        """从YAML文件加载配置"""
        config_data = {}
        
        # 读取YAML配置文件
        if yaml_path is None:
            yaml_path = os.environ.get("CONFIG_PATH", "config.yaml")
        
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
        
        # 从环境变量加载配置，覆盖YAML配置
        env_settings = cls()
        
        # 合并YAML配置和环境变量配置
        return cls(**cls._merge_configs(config_data, env_settings.model_dump()))
    
    @staticmethod
    def _merge_configs(yaml_config: Dict[str, Any], env_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并YAML配置和环境变量配置"""
        merged = {}
        
        # 先添加YAML配置
        for key, value in yaml_config.items():
            merged[key] = value
        
        # 然后添加环境变量配置，覆盖YAML配置
        for key, value in env_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # 递归合并嵌套配置
                merged[key] = Settings._merge_configs(merged[key], value)
            else:
                # 直接覆盖
                merged[key] = value
        
        return merged


# 加载配置
settings = Settings.from_yaml()

