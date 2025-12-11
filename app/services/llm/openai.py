from typing import List, Optional, Dict, Any
import openai
from app.services.llm.base import LLMService
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAILLMService(LLMService):
    """OpenAI大模型服务"""
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: Optional[str] = None,
                 base_url: Optional[str] = None,
                 timeout: Optional[int] = None,
                 max_retries: Optional[int] = None,
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None):
        """初始化OpenAI大模型服务
        
        Args:
            api_key: OpenAI API密钥
            model: 大模型名称
            base_url: 自定义API基础URL
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
            temperature: 温度参数，控制生成文本的随机性
            max_tokens: 最大生成 tokens 数
        """
        # 使用新的配置结构
        self.api_key = api_key or settings.llm.api_key
        self.model = model or settings.llm.model
        self.base_url = base_url or settings.llm.base_url
        self.timeout = timeout or settings.llm.timeout
        self.max_retries = max_retries or settings.llm.max_retries
        self.temperature = temperature or settings.llm.temperature
        self.max_tokens = max_tokens or settings.llm.max_tokens
        
        logger.info(f"Initializing OpenAILLMService with model: {self.model}")
        logger.info(f"Using base_url: {self.base_url}")
        
        # 初始化OpenAI客户端
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本（同步方法，用于兼容现有代码）
        
        Args:
            prompt: 提示词
            kwargs: 其他参数，可包含app_name等上下文信息
            
        Returns:
            生成的文本
        """
        return self.generate_text_sync(prompt, **kwargs)
    
    def generate_text_sync(self, prompt: str, **kwargs) -> str:
        """生成文本（同步实现）
        
        Args:
            prompt: 提示词
            kwargs: 其他参数，可包含app_name等上下文信息
            
        Returns:
            生成的文本
        """
        app_name = kwargs.pop('app_name', None)
        
        # 根据不同任务类型和app_name，使用不同的系统提示词
        if "抽取" in prompt or "extract" in prompt.lower() or "要素" in prompt or "element" in prompt.lower():
            # 记忆要素抽取任务，根据app_name定制提示词
            app_specific_instructions = f"\n7. 特别注意：这是来自应用 '{app_name}' 的请求，请根据该应用的特性调整提取重点。" if app_name else ""
            
            # 记忆要素抽取任务
            system_prompt = f"""
            你是一个专业的记忆要素抽取专家，擅长从聊天记录中提取关键信息。
            
            请严格遵循以下要求：
            1. 只关注重要的事实、偏好、计划、事件和其他需要记住的信息
            2. 忽略无关的闲聊和重复内容
            3. 提取的要素要准确、简洁、结构化
            4. 确保输出的JSON格式正确，不包含任何额外内容
            5. 如果没有可提取的要素，返回空JSON对象 {{}}
            6. 提取的要素应该具有长期价值，能够帮助系统记住用户的重要信息
            {app_specific_instructions}
            """
        else:
            # 通用文本生成任务
            system_prompt = "你是一个智能助手，根据用户的提示生成相应的文本。"
        
        messages = [{
            "role": "system",
            "content": system_prompt
        }, {
            "role": "user",
            "content": prompt
        }]
        
        return self.chat_completion_sync(messages, **kwargs)
    
    async def generate_text_async(self, prompt: str, **kwargs) -> str:
        """生成文本（异步实现）
        
        Args:
            prompt: 提示词
            kwargs: 其他参数，可包含app_name等上下文信息
            
        Returns:
            生成的文本
        """
        app_name = kwargs.pop('app_name', None)
        
        # 根据不同任务类型和app_name，使用不同的系统提示词
        if "抽取" in prompt or "extract" in prompt.lower() or "要素" in prompt or "element" in prompt.lower():
            # 记忆要素抽取任务，根据app_name定制提示词
            app_specific_instructions = f"\n7. 特别注意：这是来自应用 '{app_name}' 的请求，请根据该应用的特性调整提取重点。" if app_name else ""
            
            # 记忆要素抽取任务
            system_prompt = f"""
            你是一个专业的记忆要素抽取专家，擅长从聊天记录中提取关键信息。
            
            请严格遵循以下要求：
            1. 只关注重要的事实、偏好、计划、事件和其他需要记住的信息
            2. 忽略无关的闲聊和重复内容
            3. 提取的要素要准确、简洁、结构化
            4. 确保输出的JSON格式正确，不包含任何额外内容
            5. 如果没有可提取的要素，返回空JSON对象 {{}}
            6. 提取的要素应该具有长期价值，能够帮助系统记住用户的重要信息
            {app_specific_instructions}
            """
        else:
            # 通用文本生成任务
            system_prompt = "你是一个智能助手，根据用户的提示生成相应的文本。"
        
        messages = [{
            "role": "system",
            "content": system_prompt
        }, {
            "role": "user",
            "content": prompt
        }]
        
        return await self.chat_completion_async(messages, **kwargs)
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天补全（兼容旧代码）
        
        Args:
            messages: 聊天消息列表，每个消息包含role和content
            kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        return self.chat_completion_sync(messages, **kwargs)
    
    def chat_completion_sync(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天补全（同步实现）
        
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
    
    async def chat_completion_async(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """聊天补全（异步实现）
        
        Args:
            messages: 聊天消息列表，每个消息包含role和content
            kwargs: 其他参数
            
        Returns:
            生成的文本
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
            response = await async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0)
            )
            
            return response.choices[0].message.content
        finally:
            await async_client.close()
