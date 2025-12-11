from typing import List, Optional
import openai
import numpy as np
from app.services.embedding.base import EmbeddingService, cached_embedding
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI Embedding服务"""
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: Optional[str] = None,
                 base_url: Optional[str] = None,
                 timeout: Optional[int] = None,
                 max_retries: Optional[int] = None,
                 dimension: Optional[int] = None,
                 normalize: Optional[bool] = None):
        """初始化OpenAI Embedding服务
        
        Args:
            api_key: OpenAI API密钥
            model: Embedding模型名称
            base_url: 自定义API基础URL
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
            dimension: 嵌入向量维度
            normalize: 是否归一化向量
        """
        super().__init__()  # 调用父类初始化，设置缓存
        try:
            logger.info("Initializing OpenAI Embedding Service...")
            
            # 使用新的配置结构
            self.api_key = api_key or settings.embedding.api_key
            self.model = model or settings.embedding.model
            self.base_url = base_url or settings.embedding.base_url
            self.timeout = timeout or settings.embedding.timeout
            self.max_retries = max_retries or settings.embedding.max_retries
            self.dimension = dimension or settings.embedding.dimension
            self.normalize = normalize or settings.embedding.normalize
            
            logger.info(f"Using embedding model: {self.model}")
            logger.info(f"Using base_url: {self.base_url}")
            logger.info(f"Embedding dimension: {self.dimension}")
            logger.info(f"Vector normalization: {self.normalize}")
            
            # 初始化OpenAI客户端
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
            logger.info("OpenAI Embedding Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI Embedding Service: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """归一化向量
        
        Args:
            vector: 原始向量
            
        Returns:
            归一化后的向量
        """
        if not self.normalize:
            return vector
        
        vec = np.array(vector)
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vector
        return (vec / norm).tolist()
    
    @cached_embedding
    def generate_embedding(self, text: str) -> List[float]:
        """生成单个文本的Embedding（同步方法，用于兼容现有代码）
        
        Args:
            text: 要生成Embedding的文本
            
        Returns:
            Embedding向量列表
        """
        return self.generate_embedding_sync(text)
    
    def generate_embedding_sync(self, text: str) -> List[float]:
        """生成单个文本的Embedding（同步实现）
        
        Args:
            text: 要生成Embedding的文本
            
        Returns:
            Embedding向量列表
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            embedding = response.data[0].embedding
            return self._normalize_vector(embedding)
        except Exception as e:
            logger.error(f"Failed to generate embedding for text '{text[:50]}...': {e}")
            # 生成随机向量作为降级方案
            return self._normalize_vector(np.random.rand(self.dimension).tolist())
    
    async def generate_embedding_async(self, text: str) -> List[float]:
        """生成单个文本的Embedding（异步实现）
        
        Args:
            text: 要生成Embedding的文本
            
        Returns:
            Embedding向量列表
        """
        from openai import AsyncOpenAI
        
        # 创建异步客户端
        async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
        
        try:
            response = await async_client.embeddings.create(
                input=text,
                model=self.model
            )
            embedding = response.data[0].embedding
            return self._normalize_vector(embedding)
        except Exception as e:
            logger.error(f"Failed to generate embedding for text '{text[:50]}...': {e}")
            # 生成随机向量作为降级方案
            return self._normalize_vector(np.random.rand(self.dimension).tolist())
        finally:
            await async_client.close()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """生成多个文本的Embedding（兼容旧代码）
        
        Args:
            texts: 要生成Embedding的文本列表
            
        Returns:
            Embedding向量列表的列表
        """
        return self.generate_embeddings_sync(texts)
    
    def generate_embeddings_sync(self, texts: List[str]) -> List[List[float]]:
        """生成多个文本的Embedding（同步实现）
        
        Args:
            texts: 要生成Embedding的文本列表
            
        Returns:
            Embedding向量列表的列表
        """
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [self._normalize_vector(item.embedding) for item in response.data]
        except Exception as e:
            logger.error(f"Failed to generate embeddings for {len(texts)} texts: {e}")
            # 生成随机向量作为降级方案
            return [self._normalize_vector(np.random.rand(self.dimension).tolist()) for _ in texts]
    
    async def generate_embeddings_async(self, texts: List[str]) -> List[List[float]]:
        """生成多个文本的Embedding（异步实现）
        
        Args:
            texts: 要生成Embedding的文本列表
            
        Returns:
            Embedding向量列表的列表
        """
        from openai import AsyncOpenAI
        
        # 创建异步客户端
        async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
        
        try:
            response = await async_client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [self._normalize_vector(item.embedding) for item in response.data]
        except Exception as e:
            logger.error(f"Failed to generate embeddings for {len(texts)} texts: {e}")
            # 生成随机向量作为降级方案
            return [self._normalize_vector(np.random.rand(self.dimension).tolist()) for _ in texts]
        finally:
            await async_client.close()
