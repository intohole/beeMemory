from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import numpy as np

from app.models import UserMemory, AppConfig
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
        
        try:
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
        except Exception as e:
            print(f"Error in merge_similar_memories: {str(e)}")
            # 如果Embedding生成失败，跳过合并
            return
    
    def merge_time_window_memories(self, memories: List[UserMemory], window_minutes: int) -> None:
        """基于时间窗口的记忆合并
        
        Args:
            memories: 记忆列表
            window_minutes: 时间窗口大小（分钟）
        """
        if len(memories) < 2:
            return
        
        # 按创建时间排序
        memories.sort(key=lambda x: x.created_at)
        
        # 初始化窗口
        current_window = [memories[0]]
        
        # 遍历所有记忆，按时间窗口合并
        for i in range(1, len(memories)):
            memory = memories[i]
            window_start = current_window[0].created_at
            time_diff = (memory.created_at - window_start).total_seconds() / 60
            
            if time_diff <= window_minutes:
                # 在同一时间窗口内，加入当前窗口
                current_window.append(memory)
            else:
                # 超出时间窗口，合并当前窗口的记忆
                if len(current_window) > 1:
                    self._merge_memories(current_window)
                
                # 开始新的窗口
                current_window = [memory]
        
        # 合并最后一个窗口的记忆
        if len(current_window) > 1:
            self._merge_memories(current_window)
    
    def merge_clustered_memories(self, memories: List[UserMemory], merge_threshold: float) -> None:
        """基于聚类的记忆合并
        
        Args:
            memories: 记忆列表
            merge_threshold: 合并阈值
        """
        if len(memories) < 2:
            return
        
        try:
            # 生成所有记忆的Embedding
            memory_contents = [memory.memory_content for memory in memories]
            embeddings = self.embedding_service.generate_embeddings(memory_contents)
            
            # 简单的基于距离的聚类
            clusters = []
            for i, embedding in enumerate(embeddings):
                added = False
                for cluster in clusters:
                    # 计算当前Embedding与聚类中心的距离
                    cluster_center = np.mean([embeddings[j] for j in cluster], axis=0)
                    similarity = self.calculate_similarity(embedding, cluster_center.tolist())
                    
                    if similarity >= merge_threshold:
                        cluster.append(i)
                        added = True
                        break
                
                if not added:
                    clusters.append([i])
            
            # 合并每个聚类中的记忆
            for cluster in clusters:
                if len(cluster) > 1:
                    cluster_memories = [memories[i] for i in cluster]
                    self._merge_memories(cluster_memories)
        except Exception as e:
            print(f"Error in merge_clustered_memories: {str(e)}")
            # 如果Embedding生成失败，跳过合并
            return
    
    def _merge_memories(self, memories: List[UserMemory]) -> None:
        """合并多个记忆，考虑记忆优先级
        
        Args:
            memories: 要合并的记忆列表
        """
        # 按优先级降序，创建时间降序排序
        memories.sort(key=lambda x: (x.memory_priority, x.created_at), reverse=True)
        
        # 主记忆（保留的记忆）- 优先级最高，或优先级相同但最新的
        main_memory = memories[0]
        
        # 合并内容，按优先级和重要性排序
        merged_content = [main_memory.memory_content]
        merged_elements = main_memory.extracted_elements or {}
        
        # 收集所有记忆的要素，按优先级加权
        all_elements = {}
        
        # 为每个记忆分配权重，优先级越高，权重越大
        for i, memory in enumerate(memories):
            # 计算权重：优先级 * (1 - 0.1 * i)，确保优先级高的记忆权重更大，同时考虑顺序
            weight = memory.memory_priority * (1 - 0.1 * i)
            
            # 合并内容，优先级高的放在前面
            if memory != main_memory:
                merged_content.append(memory.memory_content)
            
            # 合并要素，考虑权重
            if memory.extracted_elements:
                for key, value in memory.extracted_elements.items():
                    if key not in all_elements:
                        all_elements[key] = {
                            "value": value,
                            "weight": weight,
                            "sources": 1
                        }
                    else:
                        # 如果同一要素有多个值，保留权重更高的
                        if weight > all_elements[key]["weight"]:
                            all_elements[key]["value"] = value
                            all_elements[key]["weight"] = weight
                        all_elements[key]["sources"] += 1
        
        # 构建最终的要素字典，只保留重要的要素
        merged_elements = {}
        for key, info in all_elements.items():
            # 只保留来源大于1或权重较高的要素
            if info["sources"] > 1 or info["weight"] >= 4:  # 权重4以上的要素很重要
                merged_elements[key] = info["value"]
        
        # 更新主记忆，保留优先级高的记忆特征
        main_memory.memory_content = "\n\n---\n\n".join(merged_content)
        main_memory.extracted_elements = merged_elements
        main_memory.updated_at = datetime.utcnow()
        
        # 调整主记忆的优先级，取合并记忆中的最高优先级
        max_priority = max(memory.memory_priority for memory in memories)
        main_memory.memory_priority = max_priority
        
        # 合并标签，去重
        all_tags = set()
        for memory in memories:
            if memory.memory_tags:
                all_tags.update(memory.memory_tags)
        main_memory.memory_tags = list(all_tags) if all_tags else None
        
        # 软删除其他记忆
        for memory in memories[1:]:
            memory.is_active = False
            memory.updated_at = datetime.utcnow()
        
        self.db.commit()
    
    def get_app_config(self, app_name: str) -> AppConfig:
        """获取应用配置
        
        Args:
            app_name: 应用名称
            
        Returns:
            应用配置对象
        """
        config = self.db.query(AppConfig).filter(AppConfig.app_name == app_name).first()
        return config
    
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
            
            # 获取应用配置
            app_config = self.get_app_config(app_name)
            
            if not app_config:
                continue
            
            # 根据配置选择合并策略
            merge_strategy = app_config.merge_strategy
            merge_threshold = app_config.merge_threshold
            
            if merge_strategy == "similarity":
                # 基于相似度的合并
                self.merge_similar_memories(memories, merge_threshold)
            elif merge_strategy == "time_window":
                # 基于时间窗口的合并
                self.merge_time_window_memories(memories, app_config.merge_window_minutes)
            elif merge_strategy == "clustering":
                # 基于聚类的合并
                self.merge_clustered_memories(memories, merge_threshold)
            else:
                # 默认使用相似度合并
                self.merge_similar_memories(memories, merge_threshold)
