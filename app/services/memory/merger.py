from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import numpy as np

from app.models import UserMemory, MemoryConfig
from app.services.embedding import EmbeddingServiceFactory


class MemoryMerger:
    """记忆合并服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingServiceFactory.get_embedding_service()
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """计算两个Embedding向量的相似度
        
        Args:
            embedding1: 第一个Embedding向量
            embedding2: 第二个Embedding向量
            
        Returns:
            相似度值（0-1之间）
        """
        # 计算余弦相似度
        embedding1 = np.array(embedding1)
        embedding2 = np.array(embedding2)
        similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        return float(similarity)
    
    def get_all_active_memories(self) -> List[UserMemory]:
        """获取所有活跃的记忆
        
        Returns:
            活跃记忆列表
        """
        memories = self.db.query(UserMemory).filter(UserMemory.is_active == True).all()
        return memories
    
    def group_memories_by_user_app(self, memories: List[UserMemory]) -> Dict[str, List[UserMemory]]:
        """按用户ID和应用名称分组记忆
        
        Args:
            memories: 记忆列表
            
        Returns:
            分组后的记忆字典，键为"user_id:app_name"
        """
        grouped = {}
        for memory in memories:
            key = f"{memory.user_id}:{memory.app_name}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(memory)
        return grouped
    
    def merge_similar_memories(self, memories: List[UserMemory], merge_threshold: float) -> None:
        """合并相似记忆
        
        Args:
            memories: 记忆列表
            merge_threshold: 合并阈值
        """
        # 如果记忆数量小于2，不需要合并
        if len(memories) < 2:
            return
        
        # 生成所有记忆的Embedding
        memory_contents = [memory.memory_content for memory in memories]
        embeddings = self.embedding_service.generate_embeddings(memory_contents)
        
        # 建立记忆和Embedding的映射
        memory_embeddings = dict(zip(memories, embeddings))
        
        # 标记已经处理过的记忆
        processed = set()
        
        # 比较每对记忆的相似度
        for i, memory1 in enumerate(memories):
            if memory1 in processed:
                continue
            
            similar_memories = [memory1]
            
            for j, memory2 in enumerate(memories[i+1:], start=i+1):
                if memory2 in processed:
                    continue
                    
                similarity = self.calculate_similarity(
                    memory_embeddings[memory1],
                    memory_embeddings[memory2]
                )
                
                if similarity >= merge_threshold:
                    similar_memories.append(memory2)
                    processed.add(memory2)
            
            # 如果找到相似记忆，合并它们
            if len(similar_memories) > 1:
                self._merge_memories(similar_memories)
    
    def _merge_memories(self, memories: List[UserMemory]) -> None:
        """合并多个记忆
        
        Args:
            memories: 要合并的记忆列表
        """
        # 按创建时间排序，保留最新的记忆
        memories.sort(key=lambda x: x.created_at, reverse=True)
        
        # 主记忆（保留的记忆）
        main_memory = memories[0]
        
        # 合并内容
        merged_content = [main_memory.memory_content]
        merged_elements = main_memory.extracted_elements or {}
        
        # 合并其他记忆的内容和要素
        for memory in memories[1:]:
            merged_content.append(memory.memory_content)
            
            # 合并要素
            if memory.extracted_elements:
                for key, value in memory.extracted_elements.items():
                    if key not in merged_elements:
                        merged_elements[key] = value
        
        # 更新主记忆
        main_memory.memory_content = "\n\n---\n\n".join(merged_content)
        main_memory.extracted_elements = merged_elements
        main_memory.updated_at = datetime.utcnow()
        
        # 软删除其他记忆
        for memory in memories[1:]:
            memory.is_active = False
            memory.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    def run_merge(self) -> None:
        """执行记忆合并
        """
        # 获取所有活跃记忆
        all_memories = self.get_all_active_memories()
        
        # 按用户ID和应用名称分组
        grouped_memories = self.group_memories_by_user_app(all_memories)
        
        # 对每个组进行合并
        for key, memories in grouped_memories.items():
            user_id, app_name = key.split(":")
            
            # 获取该用户和应用的合并阈值
            config = self.db.query(MemoryConfig).filter(
                and_(
                    MemoryConfig.user_id == user_id,
                    MemoryConfig.app_name == app_name
                )
            ).first()
            
            merge_threshold = config.merge_threshold if config else 0.8
            
            # 执行合并
            self.merge_similar_memories(memories, merge_threshold)
