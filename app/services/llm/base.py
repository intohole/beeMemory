from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class LLMService(ABC):
    """大模型服务基类"""
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        pass
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天补全
        
        Args:
            messages: 聊天消息列表，每个消息包含role和content
            kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        pass


class LLMServiceFactory:
    """大模型服务工厂类"""
    
    @staticmethod
    def get_llm_service(service_type: str = "openai", **kwargs) -> LLMService:
        """获取大模型服务实例
        
        Args:
            service_type: 大模型服务类型
            kwargs: 服务配置参数
            
        Returns:
            大模型服务实例
        """
        if service_type == "openai":
            from app.services.llm.openai import OpenAILLMService
            return OpenAILLMService(**kwargs)
        else:
            raise ValueError(f"不支持的大模型服务类型: {service_type}")
