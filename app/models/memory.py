from sqlalchemy import String, Text, Boolean, DateTime, JSON, ForeignKey, LargeBinary, Float, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import Optional, List





class MemoryPriority(Base):
    """记忆优先级表，定义不同内容类型的优先级"""
    __tablename__ = "memory_priorities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    priority_level: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1-5，5最高
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 复合唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'app_name', 'content_type', name='_user_app_content_priority_uc'),
    )


class UserMemory(Base):
    """用户记忆表"""
    __tablename__ = "user_memories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    memory_content: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_elements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    memory_priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)  # 1-5，5最高
    memory_tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    last_accessed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expiry_time: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否归档
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AppConfig(Base):
    """应用配置表，存储应用级别的配置"""
    __tablename__ = "app_configs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    app_name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    extraction_template: Mapped[str] = mapped_column(Text, nullable=False, default="请从以下记忆内容中提取关键信息，按照指定的字段格式返回JSON。用户意图、关键点列表、实体列表是必须包含的关键字段，不可遗漏。\n\n记忆内容：\n{{memory_content}}\n\n请提取以下要素：\n{{fields_desc}}\n\n请严格按照以下要求返回：\n{{return_requirements}}")
    extraction_fields: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default={
        "user_intent": "用户的主要意图",
        "key_points": "关键点列表",
        "entities": "实体列表",
        "preferences": "用户偏好",
        "basic_info": "基本信息",
        "time_info": "时间信息",
        "location_info": "地点信息"
    })
    conversation_rounds: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    max_summary_length: Mapped[int] = mapped_column(Integer, default=500, nullable=False)
    enable_auto_summarize: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enable_element_extraction: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    similarity_threshold: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)
    priority_weights: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default={
        "content_length": 0.3,
        "element_count": 0.4,
        "access_frequency": 0.3
    })
    
    # 记忆合并配置
    merge_strategy: Mapped[str] = mapped_column(String(50), default="similarity", nullable=False)  # 合并策略：similarity, time_window, clustering
    merge_threshold: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)  # 相似度阈值
    merge_window_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)  # 时间窗口（分钟）
    
    # 记忆过期和淘汰配置
    expiry_strategy: Mapped[str] = mapped_column(String(50), default="never", nullable=False)  # 过期策略：never, last_access
    expiry_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)  # 过期天数
    memory_limit: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)  # 每个用户的记忆数量限制
    
    # 记忆评分配置
    enable_semantic_scoring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 是否启用语义评分
    access_score_weight: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)  # 访问频率权重
    priority_score_weight: Mapped[float] = mapped_column(Float, default=0.3, nullable=False)  # 优先级权重
    recency_score_weight: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)  # 时效性权重
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ChatHistory(Base):
    """聊天历史表"""
    __tablename__ = "chat_histories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())



