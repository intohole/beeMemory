from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import UserMemory, MemoryConfig
from app.services.chroma import ChromaClient


class MemoryCleanupService:
    """记忆清理服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.chroma_client = ChromaClient()
    
    def get_expired_memories(self) -> List[UserMemory]:
        """获取所有过期记忆
        
        Returns:
            过期记忆列表
        """
        now = datetime.utcnow()
        
        # 查询所有过期的活跃记忆
        expired_memories = self.db.query(UserMemory).filter(
            and_(
                UserMemory.is_active == True,
                UserMemory.expiry_time <= now
            )
        ).all()
        
        return expired_memories
    
    def get_memories_to_cleanup_by_last_access(self) -> List[UserMemory]:
        """根据最后访问时间获取需要清理的记忆
        
        Returns:
            需要清理的记忆列表
        """
        now = datetime.utcnow()
        
        # 获取所有活跃记忆
        active_memories = self.db.query(UserMemory).filter(UserMemory.is_active == True).all()
        
        memories_to_cleanup = []
        
        # 按用户ID和应用名称分组
        grouped = {}
        for memory in active_memories:
            key = f"{memory.user_id}:{memory.app_name}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(memory)
        
        # 检查每个组的配置
        for key, memories in grouped.items():
            user_id, app_name = key.split(":")
            
            # 获取该用户和应用的配置
            config = self.db.query(MemoryConfig).filter(
                and_(
                    MemoryConfig.user_id == user_id,
                    MemoryConfig.app_name == app_name
                )
            ).first()
            
            # 如果配置为last_access策略
            if config and config.expiry_strategy == "last_access":
                expiry_days = config.expiry_days
                expiry_time = now - timedelta(days=expiry_days)
                
                # 查找超过expiry_days未访问的记忆
                for memory in memories:
                    if memory.last_accessed_at < expiry_time:
                        memories_to_cleanup.append(memory)
        
        return memories_to_cleanup
    
    def delete_memory(self, memory: UserMemory) -> None:
        """删除单个记忆
        
        Args:
            memory: 要删除的记忆
        """
        # 软删除记忆
        memory.is_active = False
        memory.updated_at = datetime.utcnow()
        
        # 从Chroma中删除Embedding
        self.chroma_client.delete_embedding(memory.id)
        
        self.db.commit()
    
    def run_cleanup(self) -> None:
        """执行记忆清理
        """
        # 清理过期记忆
        expired_memories = self.get_expired_memories()
        for memory in expired_memories:
            self.delete_memory(memory)
        
        # 清理长期未访问的记忆
        unused_memories = self.get_memories_to_cleanup_by_last_access()
        for memory in unused_memories:
            self.delete_memory(memory)
