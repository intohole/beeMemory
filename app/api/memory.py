from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models import MemoryConfig
from app.schemas.memory import (
    ChatHistoryCreate,
    MemoryQuery,
    MemoryQueryResult,
    MemoryConfigCreate,
    MemoryConfigUpdate,
    MemoryConfigResponse,
    APIResponse
)
from app.services.memory import MemoryManager
from app.core.config import settings

router = APIRouter(
    prefix="/api/memory",
    tags=["memory"],
    responses={404: {"description": "Not found"}},
)


@router.post("/submit", response_model=APIResponse)
async def submit_chat_history(
    chat_history: ChatHistoryCreate,
    db: Session = Depends(get_db)
):
    """提交聊天历史，生成记忆"""
    try:
        memory_manager = MemoryManager(db)
        
        # 存储聊天历史
        memory_manager.store_chat_history(
            user_id=chat_history.user_id,
            app_name=chat_history.app_name,
            messages=chat_history.messages
        )
        
        # 生成记忆内容
        memory_content = memory_manager.generate_memory_content(chat_history.messages)
        
        # 创建记忆
        memory = memory_manager.create_memory(
            user_id=chat_history.user_id,
            app_name=chat_history.app_name,
            memory_content=memory_content
        )
        
        return APIResponse(
            success=True,
            message="Chat history submitted successfully",
            data={"memory_id": memory.id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit chat history: {str(e)}"
        )


@router.post("/query", response_model=APIResponse)
async def query_memory(
    memory_query: MemoryQuery,
    db: Session = Depends(get_db)
):
    """根据查询内容获取相似记忆"""
    try:
        memory_manager = MemoryManager(db)
        
        # 查询记忆
        results = memory_manager.query_memories(
            user_id=memory_query.user_id,
            app_name=memory_query.app_name,
            query=memory_query.query,
            top_k=memory_query.top_k
        )
        
        # 转换为Schema格式
        memory_results = [
            MemoryQueryResult(
                memory_id=result["memory_id"],
                memory_content=result["memory_content"],
                extracted_elements=result["extracted_elements"],
                similarity=result["similarity"],
                created_at=result["created_at"]
            )
            for result in results
        ]
        
        return APIResponse(
            success=True,
            message="Memory queried successfully",
            data={"results": memory_results}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query memory: {str(e)}"
        )


@router.delete("/{memory_id}", response_model=APIResponse)
async def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db)
):
    """删除指定记忆"""
    try:
        memory_manager = MemoryManager(db)
        
        # 删除记忆
        success = memory_manager.delete_memory(memory_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with id {memory_id} not found"
            )
        
        return APIResponse(
            success=True,
            message="Memory deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memory: {str(e)}"
        )


@router.get("/config", response_model=APIResponse)
async def get_memory_config(
    user_id: str,
    app_name: str,
    db: Session = Depends(get_db)
):
    """获取记忆配置"""
    try:
        memory_manager = MemoryManager(db)
        
        # 获取或创建配置
        config = memory_manager.get_or_create_config(user_id, app_name)
        
        # 转换为Schema格式
        config_response = MemoryConfigResponse.model_validate(config)
        
        return APIResponse(
            success=True,
            message="Config retrieved successfully",
            data={"config": config_response}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory config: {str(e)}"
        )


@router.put("/config", response_model=APIResponse)
async def update_memory_config(
    user_id: str,
    app_name: str,
    config_update: MemoryConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新记忆配置"""
    try:
        # 获取配置
        config = db.query(MemoryConfig).filter(
            MemoryConfig.user_id == user_id,
            MemoryConfig.app_name == app_name
        ).first()
        
        if not config:
            # 如果配置不存在，创建新配置
            config = MemoryConfig(
                user_id=user_id,
                app_name=app_name,
                extraction_prompt=config_update.extraction_prompt or settings.DEFAULT_EXTRACTION_PROMPT,
                merge_threshold=config_update.merge_threshold or settings.DEFAULT_MERGE_THRESHOLD,
                expiry_strategy=config_update.expiry_strategy or settings.DEFAULT_EXPIRY_STRATEGY,
                expiry_days=config_update.expiry_days or settings.DEFAULT_EXPIRY_DAYS
            )
            db.add(config)
        else:
            # 更新配置
            if config_update.extraction_prompt is not None:
                config.extraction_prompt = config_update.extraction_prompt
            if config_update.merge_threshold is not None:
                config.merge_threshold = config_update.merge_threshold
            if config_update.expiry_strategy is not None:
                config.expiry_strategy = config_update.expiry_strategy
            if config_update.expiry_days is not None:
                config.expiry_days = config_update.expiry_days
        
        db.commit()
        db.refresh(config)
        
        # 转换为Schema格式
        config_response = MemoryConfigResponse.model_validate(config)
        
        return APIResponse(
            success=True,
            message="Config updated successfully",
            data={"config": config_response}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update memory config: {str(e)}"
        )
