from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import json
import numpy as np

from app.models import UserMemory, ChatHistory, AppConfig
from app.core.logging import get_logger

logger = get_logger(__name__)
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
    
    def get_or_create_config(self, user_id: str, app_name: str) -> AppConfig:
        """获取或创建应用配置
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            
        Returns:
            应用配置对象
        """
        config = self.db.query(AppConfig).filter(
            AppConfig.app_name == app_name
        ).first()
        
        if not config:
            # 如果应用配置不存在，创建默认配置
            config = AppConfig(
                app_name=app_name
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        
        return config
    
    def get_or_create_app_config(self, app_name: str) -> AppConfig:
        """获取或创建应用配置
        
        Args:
            app_name: 应用名称
            
        Returns:
            应用配置对象
        """
        config = self.db.query(AppConfig).filter(
            AppConfig.app_name == app_name
        ).first()
        
        if not config:
            # 创建默认应用配置
            config = AppConfig(
                app_name=app_name
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)
        
        return config
    
    def update_app_config(self, app_name: str, **kwargs) -> AppConfig:
        """更新应用配置
        
        Args:
            app_name: 应用名称
            **kwargs: 配置参数
            
        Returns:
            更新后的应用配置对象
        """
        config = self.get_or_create_app_config(app_name)
        
        # 更新配置参数
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def store_chat_history(self, user_id: str, app_name: str, messages: List[ChatMessage], session_id: str = None) -> None:
        """存储聊天历史
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            messages: 聊天消息列表
            session_id: 会话ID，用于关联同一会话的消息
        """
        import uuid
        
        # 如果没有提供session_id，生成一个新的
        if not session_id:
            session_id = str(uuid.uuid4())
        
        for message in messages:
            chat_history = ChatHistory(
                user_id=user_id,
                app_name=app_name,
                session_id=session_id,
                role=message.role,
                content=message.content,
                timestamp=message.timestamp or datetime.utcnow()
            )
            self.db.add(chat_history)
        
        self.db.commit()
        return session_id
    
    def summarize_dialogue(self, messages: List[ChatMessage]) -> str:
        """对对话进行总结
        
        Args:
            messages: 聊天消息列表
            
        Returns:
            对话总结
        """
        if not messages:
            return ""
        
        # 构建对话上下文
        dialogue = "\n".join([f"{msg.role}: {msg.content}" for msg in messages])
        
        # 构建统一的总结和提取prompt
        prompt = f"请对以下对话进行处理，完成以下任务：\n\n1. 总结对话的核心内容，提取关键信息\n2. 提取对话中的重要要素\n3. 确保结果简洁明了\n\n对话内容：\n{dialogue}\n\n请直接返回总结结果，不要添加任何额外内容："
        
        # 调用LLM进行总结
        try:
            summary = self.llm_service.generate_text(prompt)
            return summary.strip()
        except Exception as e:
            logger.error(f"Failed to summarize dialogue: {e}")
            # 如果总结失败，返回简洁的对话拼接
            return dialogue
    
    def generate_memory_content(self, messages: List[ChatMessage]) -> str:
        """生成记忆内容
        
        Args:
            messages: 聊天消息列表
            
        Returns:
            生成的记忆内容
        """
        # 对对话进行总结，生成记忆内容
        return self.summarize_dialogue(messages)
    
    def should_process_content(self, user_id: str, app_name: str, content: str) -> bool:
        """判断内容是否需要处理为记忆
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            content: 要判断的内容
            
        Returns:
            是否需要处理
        """
        # 过滤空内容
        if not content or content.strip() == "":
            return False
        
        # 过滤过短的内容（少于10个字符）
        if len(content.strip()) < 10:
            return False
        
        # 过滤常见的无意义内容
        trivial_patterns = ["你好", "早上好", "晚上好", "再见", "谢谢", "不客气", "好的", "是的", "不是", "嗯", "哦", "啊", "哦", "好", "行", "可以"]
        if content.strip() in trivial_patterns:
            return False
        
        return True
    
    def get_similar_memory(self, user_id: str, app_name: str, content: str, threshold: float = 0.85) -> Optional[UserMemory]:
        """查找相似的记忆
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            content: 要比较的内容
            threshold: 相似度阈值
            
        Returns:
            相似的记忆对象，没有则返回None
        """
        try:
            # 生成内容的Embedding（使用缓存）
            content_embedding = self.embedding_service.get_cached_embedding(content)
            
            # 查询相似记忆
            chroma_results = self.chroma_client.query_embeddings(
                query_embedding=content_embedding,
                user_id=user_id,
                app_name=app_name,
                top_k=1
            )
            
            if chroma_results and len(chroma_results) > 0:
                similarity = 1 - chroma_results[0]["similarity"]
                if similarity >= threshold:
                    return self.get_memory(chroma_results[0]["memory_id"])
        except Exception as e:
            # 如果查询失败，返回None
            return None
        
        return None
    
    def extract_elements(self, user_id: str, app_name: str, memory_content: str) -> Dict[str, Any]:
        """抽取记忆要素
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            memory_content: 记忆内容
            
        Returns:
            抽取的要素
        """
        import hashlib
        from app.utils.cache import cache
        
        # 检查内容是否需要提取要素
        if len(memory_content.strip()) < 10:
            return {}
        
        # 获取应用配置
        app_config = self.get_or_create_app_config(app_name)
        
        # 生成缓存键
        cache_key = f"llm_extract:{app_name}:{hashlib.md5((memory_content + str(app_config.extraction_fields)).encode('utf-8')).hexdigest()}"
        
        # 尝试从缓存获取
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 构建动态的抽取prompt，使用应用配置中的extraction_fields
        fields_desc = "\n".join([f"{key}: {desc}" for key, desc in app_config.extraction_fields.items()])
        
        # 提取字段列表，用于模板变量渲染
        field_list = list(app_config.extraction_fields.keys())
        
        # 定义返回要求，作为模板变量
        return_requirements = "1. 使用JSON格式\n2. 键名必须与上述要素列表完全一致\n3. 每个键对应的值必须准确反映记忆中的内容\n4. 如果某个要素不存在，可省略该字段\n5. 不要添加任何额外内容\n\n请直接返回JSON结果："
        
        # 准备所有模板变量
        template_vars = {
            "field_list": ", ".join(field_list),
            "field_count": str(len(field_list)),
            "fields_desc": fields_desc,
            "memory_content": memory_content,
            "return_requirements": return_requirements
        }
        
        # 渲染模板变量，支持多种模板变量
        rendered_template = app_config.extraction_template
        for var_name, var_value in template_vars.items():
            rendered_template = rendered_template.replace(f"{{{{{var_name}}}}}", var_value)
        
        # 使用完全渲染后的模板作为最终prompt
        prompt = rendered_template
        
        # 调用LLM进行要素提取
        response = self.llm_service.generate_text(prompt, app_name=app_name)
        
        # 解析结果
        try:
            elements = json.loads(response)
            
            # 缓存结果
            cache.set(cache_key, elements, expiry=settings.memory.llm_cache_ttl)
            
            return elements
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction response: {e}. Response: {response}")
            return {}
        except Exception as e:
            logger.error(f"Failed to extract elements: {e}")
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
    
    def create_memory(self, user_id: str, app_name: str, memory_content: str, is_summary: bool = False) -> UserMemory:
        """创建记忆
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            memory_content: 记忆内容
            is_summary: 是否是对话总结结果
            
        Returns:
            创建的记忆对象
        """
        # 如果不是总结结果，对内容进行总结
        if not is_summary:
            # 先对内容进行总结
            summary = self.summarize_dialogue([ChatMessage(role="user", content=memory_content)])
            # 使用总结作为记忆内容
            memory_content = summary
        
        # 检查内容是否需要处理
        if not self.should_process_content(user_id, app_name, memory_content):
            # 如果内容不需要处理，创建一个低优先级的记忆
            expiry_time = self.calculate_expiry_time(user_id, app_name)
            memory = UserMemory(
                user_id=user_id,
                app_name=app_name,
                memory_content=memory_content,
                extracted_elements={},
                memory_priority=1,  # 低优先级
                memory_tags=["trivial"],
                expiry_time=expiry_time,
                last_accessed_at=datetime.utcnow()
            )
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            return memory
        
        # 查找相似记忆，如果存在则更新
        similar_memory = self.get_similar_memory(user_id, app_name, memory_content)
        if similar_memory:
            # 更新相似记忆，实现增量抽取
            updated_content = f"{similar_memory.memory_content}\n\n---\n\n{memory_content}"
            
            # 重新抽取要素
            updated_elements = self.extract_elements(user_id, app_name, updated_content)
            
            # 合并要素
            merged_elements = similar_memory.extracted_elements or {}
            merged_elements.update(updated_elements)
            
            # 更新记忆
            similar_memory.memory_content = updated_content
            similar_memory.extracted_elements = merged_elements
            similar_memory.last_accessed_at = datetime.utcnow()
            similar_memory.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(similar_memory)
            
            # 更新Embedding
            updated_embedding = self.embedding_service.generate_embedding(updated_content)
            self.chroma_client.update_embedding(
                memory_id=similar_memory.id,
                embedding=updated_embedding,
                document=updated_content,
                user_id=user_id,
                app_name=app_name
            )
            
            return similar_memory
        
        # 抽取要素
        extracted_elements = self.extract_elements(user_id, app_name, memory_content)
        
        # 计算过期时间
        expiry_time = self.calculate_expiry_time(user_id, app_name)
        
        # 设置记忆优先级（基于内容长度和要素数量）
        priority = 3  # 默认优先级
        if len(memory_content) > 1000:
            priority = 4
        if len(extracted_elements) > 5:
            priority = 5
        elif len(extracted_elements) < 2:
            priority = 2
        
        # 自动生成记忆标签
        tags = []
        if "name" in extracted_elements:
            tags.append("personal_info")
        if "preference" in extracted_elements or "hobby" in extracted_elements:
            tags.append("preference")
        if "plan" in extracted_elements or "schedule" in extracted_elements:
            tags.append("plan")
        if "question" in extracted_elements or "problem" in extracted_elements:
            tags.append("question")
        
        # 创建记忆对象
        memory = UserMemory(
            user_id=user_id,
            app_name=app_name,
            memory_content=memory_content,
            extracted_elements=extracted_elements,
            memory_priority=priority,
            memory_tags=tags if tags else None,
            expiry_time=expiry_time,
            last_accessed_at=datetime.utcnow()
        )
        
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        
        # 生成并存储Embedding（使用缓存）
        embedding = self.embedding_service.get_cached_embedding(memory_content)
        
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
        try:
            # 生成查询内容的Embedding（使用缓存）
            query_embedding = self.embedding_service.get_cached_embedding(query)
            
            # 查询相似记忆
            chroma_results = self.chroma_client.query_embeddings(
                query_embedding=query_embedding,
                user_id=user_id,
                app_name=app_name,
                top_k=top_k
            )
            
            # 构建结果
            results = []
            for result in chroma_results:
                # 获取记忆详情
                memory = self.get_memory(result["memory_id"])
                if memory:
                    similarity = 1 - result["similarity"]  # Chroma返回的是距离，转换为相似度
                    # 确保相似度在合理范围内
                    similarity = max(0.0, min(1.0, similarity))
                    results.append({
                        "memory_id": memory.id,
                        "memory_content": memory.memory_content,
                        "extracted_elements": memory.extracted_elements,
                        "similarity": similarity,
                        "created_at": memory.created_at
                    })
            
            # 如果Chroma查询返回空结果，进入降级方案
            if not results:
                logger.info("Chroma query returned empty results, falling back to keyword-based query")
                raise Exception("Chroma query returned empty results")
            
            return results
        except Exception as e:
            logger.error(f"Failed to query memories with embedding: {e}")
            # 如果嵌入查询失败或返回空结果，回退到基于关键词的查询作为降级方案
            # 获取该用户该应用下的所有记忆
            memories = self.db.query(UserMemory).filter(
                and_(
                    UserMemory.user_id == user_id,
                    UserMemory.app_name == app_name,
                    UserMemory.is_active == True
                )
            ).all()
            
            # 对所有记忆进行相似度计算
            memory_scores = []
            
            for memory in memories:
                # 初始化相似度
                similarity = 0.0
                
                # 只有当查询不为空时才计算相似度
                if query:
                    # 改进的文本匹配算法
                    query_lower = query.lower()
                    memory_lower = memory.memory_content.lower()
                    
                    # 完全匹配
                    if query_lower == memory_lower:
                        similarity = 1.0
                    # 包含匹配
                    elif query_lower in memory_lower:
                        similarity = 0.8
                    # 关键词匹配
                    else:
                        # 提取关键词
                        query_words = set(query_lower.split())
                        memory_words = set(memory_lower.split())
                        
                        if query_words or memory_words:
                            # Jaccard相似度
                            intersection = len(query_words.intersection(memory_words))
                            union = len(query_words.union(memory_words))
                            jaccard_similarity = intersection / union
                            
                            # 余弦相似度（基于词频）
                            from collections import Counter
                            query_counter = Counter(query_words)
                            memory_counter = Counter(memory_words)
                            
                            # 计算点积
                            dot_product = sum(query_counter[word] * memory_counter[word] for word in query_counter if word in memory_counter)
                            
                            # 计算模长
                            query_norm = sum(count ** 2 for count in query_counter.values()) ** 0.5
                            memory_norm = sum(count ** 2 for count in memory_counter.values()) ** 0.5
                            
                            # 计算余弦相似度
                            cosine_similarity = dot_product / (query_norm * memory_norm) if query_norm * memory_norm > 0 else 0.0
                            
                            # 综合相似度：Jaccard相似度占40%，余弦相似度占60%
                            similarity = 0.4 * jaccard_similarity + 0.6 * cosine_similarity
                            
                            # 确保相似度至少为0.1，避免返回0%相似度
                            similarity = max(0.1, similarity)
                        else:
                            # 至少返回0.1的相似度，避免返回0%相似度
                            similarity = 0.1
                else:
                    # 如果查询为空，返回所有记忆，相似度为0.5
                    similarity = 0.5
                
                memory_scores.append({
                    "memory": memory,
                    "similarity": similarity
                })
            
            # 按相似度降序排序
            memory_scores.sort(key=lambda x: x["similarity"], reverse=True)
            
            # 取前top_k个结果
            top_results = memory_scores[:top_k]
            
            # 构建最终结果
            results = []
            for item in top_results:
                memory = item["memory"]
                similarity = item["similarity"]
                
                # 更新最后访问时间
                memory.last_accessed_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(memory)
                
                results.append({
                    "memory_id": memory.id,
                    "memory_content": memory.memory_content,
                    "extracted_elements": memory.extracted_elements,
                    "similarity": similarity,
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
        ).order_by(
            UserMemory.last_accessed_at.desc()
        ).all()
        
        return memories
    
    def get_chat_history(self, user_id: str, app_name: str, session_id: str = None) -> List[Dict[str, Any]]:
        """获取聊天历史
        
        Args:
            user_id: 用户ID
            app_name: 应用名称
            session_id: 会话ID（可选）
            
        Returns:
            聊天历史列表
        """
        # 构建查询条件
        query = self.db.query(ChatHistory).filter(
            and_(
                ChatHistory.user_id == user_id,
                ChatHistory.app_name == app_name
            )
        )
        
        # 如果提供了session_id，添加到查询条件
        if session_id:
            query = query.filter(ChatHistory.session_id == session_id)
        
        # 按时间戳升序排列
        chat_history = query.order_by(ChatHistory.timestamp.asc()).all()
        
        # 转换为字典列表
        return [{
            "id": chat.id,
            "user_id": chat.user_id,
            "app_name": chat.app_name,
            "session_id": chat.session_id,
            "role": chat.role,
            "content": chat.content,
            "timestamp": chat.timestamp.isoformat()
        } for chat in chat_history]
