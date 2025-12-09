from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import json
import numpy as np

from app.models import UserMemory, ChatHistory, MemoryConfig, MemoryEmbedding
from app.schemas.memory import MemoryCreate, MemoryResponse, ChatMessage
from app.services.embedding import EmbeddingServiceFactory
from app.services.llm import LLMServiceFactory
from app.services.chroma import ChromaClient
from app.core.config import settings


class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingServiceFactory.get_embedding_service()
        self.llm_service = LLMServiceFactory.get_llm_service()
        self.chroma_client = ChromaClient()
    
    def get_or_create_config(self, user_id: str, app_name: str) -> MemoryConfig:
        """获取或创建记忆配置
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            
        Returns:
            记忆配置对象
        """
        config = self.db.query(MemoryConfig).filter(
            and_(
                MemoryConfig.user_id == user_id,
                MemoryConfig.app_name == app_name
            )
        ).first()
        
        if not config:
            config = MemoryConfig(
                user_id=user_id,
                app_name=app_name,
                extraction_prompt=settings.DEFAULT_EXTRACTION_PROMPT,
                merge_threshold=settings.DEFAULT_MERGE_THRESHOLD,
                expiry_strategy=settings.DEFAULT_EXPIRY_STRATEGY,
                expiry_days=settings.DEFAULT_EXPIRY_DAYS
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        
        return config
    
    def store_chat_history(self, user_id: str, app_name: str, messages: List[ChatMessage]) -> None:
        """存储聊天历史
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            messages: 聊天消息列表
        """
        for message in messages:
            chat_history = ChatHistory(
                user_id=user_id,
                app_name=app_name,
                role=message.role,
                content=message.content,
                timestamp=message.timestamp or datetime.utcnow()
            )
            self.db.add(chat_history)
        
        self.db.commit()
    
    def generate_memory_content(self, messages: List[ChatMessage]) -> str:
        """生成记忆内容
        
        Args:
            messages: 聊天消息列表
            
        Returns:
            生成的记忆内容
        """
        memory_content = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
        return memory_content
    
    def extract_elements(self, user_id: str, app_name: str, memory_content: str) -> Dict[str, Any]:
        """抽取记忆要素
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            memory_content: 记忆内容
            
        Returns:
            抽取的要素
        """
        # 获取记忆配置
        config = self.get_or_create_config(user_id, app_name)
        
        # 构建提示词
        prompt = f"{config.extraction_prompt}\n\n{memory_content}\n\n请以JSON格式返回抽取的要素，确保JSON格式正确，不要包含其他内容。"
        
        # 调用大模型抽取要素
        try:
            response = self.llm_service.generate_text(prompt)
            elements = json.loads(response)
            return elements
        except Exception as e:
            # 如果抽取失败，返回空字典
            return {}
    
    def calculate_expiry_time(self, user_id: str, app_name: str) -> Optional[datetime]:
        """计算记忆过期时间
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            
        Returns:
            过期时间，None表示永不过期
        """
        # 获取记忆配置
        config = self.get_or_create_config(user_id, app_name)
        
        if config.expiry_strategy == "never":
            return None
        else:
            return datetime.utcnow() + timedelta(days=config.expiry_days)
    
    def create_memory(self, user_id: str, app_name: str, memory_content: str) -> UserMemory:
        """创建记忆
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            memory_content: 记忆内容
            
        Returns:
            创建的记忆对象
        """
        # 抽取要素
        extracted_elements = self.extract_elements(user_id, app_name, memory_content)
        
        # 计算过期时间
        expiry_time = self.calculate_expiry_time(user_id, app_name)
        
        # 创建记忆对象
        memory = UserMemory(
            user_id=user_id,
            app_name=app_name,
            memory_content=memory_content,
            extracted_elements=extracted_elements,
            expiry_time=expiry_time,
            last_accessed_at=datetime.utcnow()
        )
        
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        
        # 生成并存储Embedding
        embedding = self.embedding_service.generate_embedding(memory_content)
        
        # 存储到Chroma
        self.chroma_client.add_embedding(
            embedding=embedding,
            document=memory_content,
            memory_id=memory.id,
            user_id=user_id,
            app_name=app_name
        )
        
        return memory
    
    def get_memory(self, memory_id: int) -> Optional[UserMemory]:
        """获取单个记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆对象，不存在返回None
        """
        memory = self.db.query(UserMemory).filter(
            and_(
                UserMemory.id == memory_id,
                UserMemory.is_active == True
            )
        ).first()
        
        if memory:
            # 更新最后访问时间
            memory.last_accessed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(memory)
        
        return memory
    
    def query_memories(self, user_id: str, app_name: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """查询相似记忆
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            query: 查询内容
            top_k: 返回结果数量
            
        Returns:
            相似记忆列表
        """
        # 生成查询Embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # 查询Chroma
        chroma_results = self.chroma_client.query_embeddings(
            query_embedding=query_embedding,
            user_id=user_id,
            app_name=app_name,
            top_k=top_k
        )
        
        # 获取记忆对象并更新访问时间
        results = []
        for result in chroma_results:
            memory = self.get_memory(result["memory_id"])
            if memory:
                results.append({
                    "memory_id": memory.id,
                    "memory_content": memory.memory_content,
                    "extracted_elements": memory.extracted_elements,
                    "similarity": 1 - result["similarity"],  # Chroma返回的是距离，转换为相似度
                    "created_at": memory.created_at
                })
        
        return results
    
    def delete_memory(self, memory_id: int) -> bool:
        """删除记忆
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否删除成功
        """
        memory = self.db.query(UserMemory).filter(UserMemory.id == memory_id).first()
        
        if memory:
            # 软删除记忆
            memory.is_active = False
            self.db.commit()
            
            # 从Chroma中删除Embedding
            self.chroma_client.delete_embedding(memory_id)
            
            return True
        
        return False
    
    def update_memory(self, memory_id: int, memory_content: Optional[str] = None, 
                     extracted_elements: Optional[Dict[str, Any]] = None) -> Optional[UserMemory]:
        """更新记忆
        
        Args:
            memory_id: 记忆ID
            memory_content: 新的记忆内容
            extracted_elements: 新的抽取要素
            
        Returns:
            更新后的记忆对象，不存在返回None
        """
        memory = self.db.query(UserMemory).filter(UserMemory.id == memory_id).first()
        
        if memory:
            update_embedding = False
            
            if memory_content is not None:
                memory.memory_content = memory_content
                update_embedding = True
            
            if extracted_elements is not None:
                memory.extracted_elements = extracted_elements
            
            memory.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(memory)
            
            # 如果记忆内容更新了，需要更新Embedding
            if update_embedding:
                embedding = self.embedding_service.generate_embedding(memory.memory_content)
                self.chroma_client.update_embedding(
                    memory_id=memory.id,
                    embedding=embedding,
                    document=memory.memory_content,
                    user_id=memory.user_id,
                    app_name=memory.app_name
                )
            
            return memory
        
        return None
    
    def get_memories_by_user_app(self, user_id: str, app_name: str) -> List[UserMemory]:
        """获取用户在特定应用下的所有记忆
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            
        Returns:
            记忆列表
        """
        memories = self.db.query(UserMemory).filter(
            and_(
                UserMemory.user_id == user_id,
                UserMemory.app_name == app_name,
                UserMemory.is_active == True
            )
        ).all()
        
        return memories
