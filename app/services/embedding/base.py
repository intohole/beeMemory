from abc import ABC, abstractmethod
from typing import List, Optional


class EmbeddingService(ABC):
    """Embedding服务基类"""
    
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
