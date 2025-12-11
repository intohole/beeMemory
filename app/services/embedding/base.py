from abc import ABC, abstractmethod
from typing import List, Optional
from app.utils.cache import cache, ONE_WEEK
from functools import wraps


def cached_embedding(func):
    """Embedding生成的缓存装饰器"""
    @wraps(func)
    def wrapper(self, text):
        # 使用文本内容的哈希值作为缓存键，更高效
        import hashlib
        cache_key = f"embedding:{hashlib.md5(text.encode('utf-8')).hexdigest()}"
        
        # 尝试从缓存获取
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 生成新的Embedding
        result = func(self, text)
        
        # 缓存结果，有效期7天（更长时间，因为embedding生成成本高）
        cache.set(cache_key, result, expiry=ONE_WEEK)
        
        return result
    return wrapper


class EmbeddingService(ABC):
    """Embedding服务基类"""
    
    def __init__(self):
        self.cache = cache
    
    def get_cached_embedding(self, text: str) -> List[float]:
        """获取缓存的Embedding，如果没有则生成并缓存
        
        Args:
            text: 要生成Embedding的文本
            
        Returns:
            Embedding向量列表
        """
        # 使用文本内容的哈希值作为缓存键，更高效
        import hashlib
        cache_key = f"embedding:{hashlib.md5(text.encode('utf-8')).hexdigest()}"
        
        # 尝试从缓存获取
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 生成新的Embedding
        result = self.generate_embedding(text)
        
        # 缓存结果，有效期7天（更长时间，因为embedding生成成本高）
        self.cache.set(cache_key, result, expiry=ONE_WEEK)
        
        return result
    
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """生成单个文本的Embedding
        
        Args:
            text: 要生成Embedding的文本
            
        Returns:
            Embedding向量列表
        """
        pass
    
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """生成多个文本的Embedding
        
        Args:
            texts: 要生成Embedding的文本列表
            
        Returns:
            Embedding向量列表的列表
        """
        pass


class EmbeddingServiceFactory:
    """Embedding服务工厂类"""
    
    @staticmethod
    def get_embedding_service(service_type: str = "openai", **kwargs) -> EmbeddingService:
        """获取Embedding服务实例
        
        Args:
            service_type: Embedding服务类型
            kwargs: 服务配置参数
            
        Returns:
            Embedding服务实例
        """
        if service_type == "openai":
            from app.services.embedding.openai import OpenAIEmbeddingService
            return OpenAIEmbeddingService(**kwargs)
        else:
            raise ValueError(f"不支持的Embedding服务类型: {service_type}")
