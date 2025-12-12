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


class MemoryPriorityCreate(BaseModel):
    """记忆优先级创建Schema"""
    user_id: str = Field(..., description="用户ID", min_length=1)
    app_name: str = Field(..., description="应用名称", min_length=1)
    content_type: str = Field(..., description="内容类型", min_length=1)
    priority_level: int = Field(3, description="优先级等级", ge=1, le=5)
    description: Optional[str] = Field(None, description="优先级描述")


class MemoryPriorityUpdate(BaseModel):
    """记忆优先级更新Schema"""
    priority_level: Optional[int] = Field(None, description="优先级等级", ge=1, le=5)
    description: Optional[str] = Field(None, description="优先级描述")


class MemoryPriorityResponse(BaseModel):
    """记忆优先级响应Schema"""
    id: int
    user_id: str
    app_name: str
    content_type: str
    priority_level: int
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @property
    def priority_id(self) -> int:
        return self.id


class APIResponse(BaseModel):
    """通用API响应Schema"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
