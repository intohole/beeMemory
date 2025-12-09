from typing import List, Optional
import openai
from app.services.embedding.base import EmbeddingService
from app.core.config import settings


class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI Embedding服务"""
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: Optional[str] = None,
                 base_url: Optional[str] = None):
        """初始化OpenAI Embedding服务
        
        Args:
            api_key: OpenAI API密钥
            model: Embedding模型名称
            base_url: 自定义API基础URL
        """
        self.api_key = api_key or settings.EMBEDDING_API_KEY
        self.model = model or settings.EMBEDDING_MODEL
        self.base_url = base_url or settings.EMBEDDING_BASE_URL
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """生成单个文本的Embedding
        
        Args:
            text: 要生成Embedding的文本
            
        Returns:
            Embedding向量列表
        """
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """生成多个文本的Embedding
        
        Args:
            texts: 要生成Embedding的文本列表
            
        Returns:
            Embedding向量列表的列表
        """
        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]
