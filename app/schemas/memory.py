from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class ChatMessage(BaseModel):
    """聊天消息Schema"""
    role: str = Field(..., description="角色", examples=["user", "assistant"])
    content: str = Field(..., description="内容", min_length=1)
    timestamp: Optional[datetime] = Field(None, description="时间戳")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant']:
            raise ValueError('角色必须是user或assistant')
        return v


class ChatHistoryCreate(BaseModel):
    """聊天历史创建Schema"""
    user_id: str = Field(..., description="用户ID", min_length=1)
    app_name: str = Field(..., description="应用名称", min_length=1)
    messages: List[ChatMessage] = Field(..., description="聊天消息列表", min_items=1)


class ChatHistoryResponse(BaseModel):
    """聊天历史响应Schema"""
    id: int
    user_id: str
    app_name: str
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class MemoryCreate(BaseModel):
    """记忆创建Schema"""
    user_id: str = Field(..., description="用户ID", min_length=1)
    app_name: str = Field(..., description="应用名称", min_length=1)
    memory_content: str = Field(..., description="记忆内容", min_length=1)
    extracted_elements: Optional[Dict[str, Any]] = Field(None, description="抽取的要素")
    expiry_time: Optional[datetime] = Field(None, description="过期时间")


class MemoryResponse(BaseModel):
    """记忆响应Schema"""
    id: int
    user_id: str
    app_name: str
    memory_content: str
    extracted_elements: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    expiry_time: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class MemoryQuery(BaseModel):
    """记忆查询Schema"""
    user_id: str = Field(..., description="用户ID", min_length=1)
    app_name: str = Field(..., description="应用名称", min_length=1)
    query: str = Field(..., description="查询内容", min_length=1)
    top_k: Optional[int] = Field(5, description="返回结果数量", ge=1, le=20)


class MemoryQueryResult(BaseModel):
    """记忆查询结果Schema"""
    memory_id: int
    memory_content: str
    extracted_elements: Optional[Dict[str, Any]]
    similarity: float = Field(..., description="相似度", ge=0.0, le=1.0)
    created_at: datetime


class MemoryConfigCreate(BaseModel):
    """记忆配置创建Schema"""
    user_id: str = Field(..., description="用户ID", min_length=1)
    app_name: str = Field(..., description="应用名称", min_length=1)
    extraction_prompt: Optional[str] = Field(None, description="要素抽取提示词")
    merge_threshold: Optional[float] = Field(0.8, description="合并阈值", ge=0.0, le=1.0)
    expiry_strategy: Optional[str] = Field("last_access", description="过期策略", examples=["never", "last_access"])
    expiry_days: Optional[int] = Field(30, description="过期天数", ge=1)
    
    @validator('expiry_strategy')
    def validate_expiry_strategy(cls, v):
        if v not in ['never', 'last_access']:
            raise ValueError('过期策略必须是never或last_access')
        return v


class MemoryConfigUpdate(BaseModel):
    """记忆配置更新Schema"""
    extraction_prompt: Optional[str] = Field(None, description="要素抽取提示词")
    merge_threshold: Optional[float] = Field(None, description="合并阈值", ge=0.0, le=1.0)
    expiry_strategy: Optional[str] = Field(None, description="过期策略", examples=["never", "last_access"])
    expiry_days: Optional[int] = Field(None, description="过期天数", ge=1)
    
    @validator('expiry_strategy')
    def validate_expiry_strategy(cls, v):
        if v is not None and v not in ['never', 'last_access']:
            raise ValueError('过期策略必须是never或last_access')
        return v


class MemoryConfigResponse(BaseModel):
    """记忆配置响应Schema"""
    id: int
    user_id: str
    app_name: str
    extraction_prompt: str
    merge_threshold: float
    expiry_strategy: str
    expiry_days: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class APIResponse(BaseModel):
    """通用API响应Schema"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
