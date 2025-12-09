from sqlalchemy import String, Text, Boolean, DateTime, JSON, ForeignKey, LargeBinary, Float, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import Optional


class UserMemory(Base):
    """用户记忆表"""
    __tablename__ = "user_memories"
    
    user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    memory_content: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_elements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    last_accessed_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP")
    expiry_time: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 关系
    embedding = relationship("MemoryEmbedding", back_populates="memory", uselist=False, cascade="all, delete-orphan")


class MemoryEmbedding(Base):
    """记忆Embedding表"""
    __tablename__ = "memory_embeddings"
    
    memory_id: Mapped[int] = mapped_column(ForeignKey("user_memories.id"), unique=True, nullable=False)
    embedding_vector: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    
    # 关系
    memory = relationship("UserMemory", back_populates="embedding")


class ChatHistory(Base):
    """聊天历史表"""
    __tablename__ = "chat_histories"
    
    user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="CURRENT_TIMESTAMP")


class MemoryConfig(Base):
    """记忆配置表"""
    __tablename__ = "memory_configs"
    
    user_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    app_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    extraction_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    merge_threshold: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)
    expiry_strategy: Mapped[str] = mapped_column(String(50), default="last_access", nullable=False)
    expiry_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    
    # 复合唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'app_name', name='_user_app_uc'),
    )
