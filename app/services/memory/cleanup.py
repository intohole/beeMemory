from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import UserMemory, AppConfig
from app.services.chroma import ChromaClient


class MemoryCleanupService:
    """记忆清理服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.chroma_client = ChromaClient()
    
    def get_expired_memories(self) -> List[UserMemory]:
        """获取所有过期记忆
        
        Returns:
            过期记忆列表，排除已归档的记忆
        """
        now = datetime.utcnow()
        
        # 查询所有过期的活跃且未归档的记忆
        expired_memories = self.db.query(UserMemory).filter(
            and_(
                UserMemory.is_active == True,
                UserMemory.is_archived == False,
                UserMemory.expiry_time <= now
            )
        ).all()
        
        return expired_memories
    
    def get_app_config(self, app_name: str) -> AppConfig:
        """获取应用配置
        
        Args:
            app_name: 应用名称
            
        Returns:
            应用配置对象
        """
        config = self.db.query(AppConfig).filter(AppConfig.app_name == app_name).first()
        return config
    
    def get_memories_to_cleanup_by_last_access(self) -> List[UserMemory]:
        """根据最后访问时间和优先级获取需要清理的记忆
        
        Returns:
            需要清理的记忆列表，按优先级升序排列
        """
        now = datetime.utcnow()
        
        # 获取所有活跃且未归档的记忆
        active_memories = self.db.query(UserMemory).filter(
            and_(
                UserMemory.is_active == True,
                UserMemory.is_archived == False
            )
        ).all()
        
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
            
            # 获取该应用的配置
            app_config = self.get_app_config(app_name)
            
            # 如果配置为last_access策略
            if app_config and app_config.expiry_strategy == "last_access":
                expiry_days = app_config.expiry_days
                expiry_time = now - timedelta(days=expiry_days)
                
                # 查找超过expiry_days未访问的记忆
                for memory in memories:
                    if memory.last_accessed_at < expiry_time:
                        memories_to_cleanup.append(memory)
        
        # 按优先级升序，创建时间升序排序，优先清理低优先级、旧的记忆
        memories_to_cleanup.sort(key=lambda x: (x.memory_priority, x.created_at))
        return memories_to_cleanup
    
    def get_memories_to_cleanup_by_priority(self, max_memory_count: int = 1000) -> List[UserMemory]:
        """根据优先级获取需要清理的记忆，当总记忆数超过阈值时执行
        
        Args:
            max_memory_count: 最大记忆数阈值
            
        Returns:
            需要清理的记忆列表，按优先级升序排列
        """
        # 获取所有活跃且未归档的记忆
        active_memories = self.db.query(UserMemory).filter(
            and_(
                UserMemory.is_active == True,
                UserMemory.is_archived == False
            )
        ).all()
        
        # 如果总记忆数未超过阈值，不需要清理
        if len(active_memories) <= max_memory_count:
            return []
        
        # 按优先级升序，创建时间升序排序，优先清理低优先级、旧的记忆
        active_memories.sort(key=lambda x: (x.memory_priority, x.created_at))
        
        # 计算需要清理的记忆数量
        memories_to_cleanup_count = len(active_memories) - max_memory_count
        
        # 返回需要清理的记忆
        return active_memories[:memories_to_cleanup_count]
    
    def get_memories_to_cleanup_by_app_limit(self) -> List[UserMemory]:
        """根据应用配置的记忆数量限制获取需要清理的记忆
        
        Returns:
            需要清理的记忆列表，按评分升序排列
        """
        now = datetime.utcnow()
        
        # 获取所有活跃且未归档的记忆
        active_memories = self.db.query(UserMemory).filter(
            UserMemory.is_active == True,
            UserMemory.is_archived == False
        ).all()
        
        memories_to_cleanup = []
        
        # 按用户ID和应用名称分组
        grouped = {}
        for memory in active_memories:
            key = f"{memory.user_id}:{memory.app_name}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(memory)
        
        # 检查每个组的记忆数
        for key, memories in grouped.items():
            user_id, app_name = key.split(":")
            
            # 获取应用配置
            app_config = self.get_app_config(app_name)
            
            if not app_config:
                continue
            
            # 应用配置的记忆数量限制
            memory_limit = app_config.memory_limit
            
            # 如果应用内记忆数超过阈值，需要清理
            if len(memories) > memory_limit:
                # 计算需要清理的记忆数量
                cleanup_count = len(memories) - memory_limit
                
                # 计算每个记忆的评分
                scored_memories = []
                for memory in memories:
                    # 基于多维度的评分系统
                    # 1. 访问频率评分
                    days_since_access = (now - memory.last_accessed_at).days
                    access_score = max(0, 1 - days_since_access / app_config.expiry_days) if app_config.expiry_days > 0 else 1
                    
                    # 2. 优先级评分
                    priority_score = memory.memory_priority / 5.0  # 假设优先级是1-5
                    
                    # 3. 时效性评分
                    days_since_created = (now - memory.created_at).days
                    recency_score = max(0, 1 - days_since_created / (app_config.expiry_days * 2)) if app_config.expiry_days > 0 else 1
                    
                    # 4. 内容质量评分（基于提取的元素数量）
                    content_quality_score = 0.5  # 默认值
                    if memory.extracted_elements:
                        element_count = len(memory.extracted_elements)
                        # 元素越多，内容质量越高，但有上限
                        content_quality_score = min(1.0, 0.3 + element_count * 0.1)
                    
                    # 5. 标签数量评分
                    tag_score = 0.5  # 默认值
                    if memory.memory_tags:
                        tag_count = len(memory.memory_tags)
                        # 标签越多，记忆越结构化，评分越高
                        tag_score = min(1.0, 0.3 + tag_count * 0.15)
                    
                    # 计算最终评分，使用配置的权重 + 内容质量和标签权重
                    final_score = (
                        access_score * app_config.access_score_weight +
                        priority_score * app_config.priority_score_weight +
                        recency_score * app_config.recency_score_weight +
                        content_quality_score * 0.1 +  # 内容质量权重10%
                        tag_score * 0.1  # 标签权重10%
                    )
                    
                    scored_memories.append((memory, final_score))
                
                # 按评分升序排序，优先清理评分低的记忆
                scored_memories.sort(key=lambda x: x[1])
                
                # 添加需要清理的记忆
                for i in range(cleanup_count):
                    memories_to_cleanup.append(scored_memories[i][0])
        
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
        
        # 清理超出应用记忆数量限制的记忆
        over_limit_memories = self.get_memories_to_cleanup_by_app_limit()
        for memory in over_limit_memories:
            self.delete_memory(memory)
