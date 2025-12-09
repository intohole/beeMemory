from typing import List, Optional, Dict, Any
import openai
from app.services.llm.base import LLMService
from app.core.config import settings


class OpenAILLMService(LLMService):
    """OpenAI大模型服务"""
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: Optional[str] = None,
                 base_url: Optional[str] = None,
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None):
        """初始化OpenAI大模型服务
        
        Args:
            api_key: OpenAI API密钥
            model: 大模型名称
            base_url: 自定义API基础URL
            temperature: 温度参数，控制生成文本的随机性
            max_tokens: 最大生成 tokens 数
        """
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL
        self.base_url = base_url or settings.LLM_BASE_URL
        self.temperature = temperature or settings.LLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        messages = [{
            "role": "system",
            "content": "你是一个智能助手，根据用户的提示生成相应的文本。"
        }, {
            "role": "user",
            "content": prompt
        }]
        
        return self.chat_completion(messages, **kwargs)
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天补全
        
        Args:
            messages: 聊天消息列表，每个消息包含role和content
            kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            top_p=kwargs.get("top_p", 1.0),
            frequency_penalty=kwargs.get("frequency_penalty", 0.0),
            presence_penalty=kwargs.get("presence_penalty", 0.0)
        )
        
        return response.choices[0].message.content
