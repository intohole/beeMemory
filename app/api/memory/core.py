from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.logging import get_logger

from app.db.session import get_db
from app.schemas.memory import (
    ChatHistoryCreate,
    MemoryQuery,
    MemoryQueryResult,
    APIResponse
)
from app.services.memory import MemoryManager

router = APIRouter()


logger = get_logger(__name__)


def process_chat_history_background(
    chat_history: ChatHistoryCreate,
    db: Session,
    memory_id: str
):
    """后台处理聊天历史，生成记忆"""
    try:
        logger.info(f"Processing chat history for memory_id: {memory_id}")
        
        memory_manager = MemoryManager(db)
        
        # 存储聊天历史
        memory_manager.store_chat_history(
            user_id=chat_history.user_id,
            app_name=chat_history.app_name,
            messages=chat_history.messages
        )
        
        # 生成记忆内容
        memory_content = memory_manager.generate_memory_content(chat_history.messages)
        
        # 创建记忆，设置is_summary为True，避免重复总结
        memory = memory_manager.create_memory(
            user_id=chat_history.user_id,
            app_name=chat_history.app_name,
            memory_content=memory_content,
            is_summary=True
        )
        
        logger.info(f"Memory generated successfully for memory_id: {memory_id}, actual memory_id: {memory.id}")
    except Exception as e:
        logger.error(f"Failed to process chat history for memory_id: {memory_id}: {str(e)}")


@router.post("/submit", response_model=APIResponse)
async def submit_chat_history(
    chat_history: ChatHistoryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """异步提交聊天历史，生成记忆"""
    try:
        # 生成唯一的记忆ID，用于异步处理
        import uuid
        memory_id = str(uuid.uuid4())
        
        # 立即返回响应，不阻塞
        background_tasks.add_task(
            process_chat_history_background,
            chat_history, 
            db, 
            memory_id
        )
        
        return APIResponse(
            success=True,
            message="Chat history submitted successfully, memory is being generated in background",
            data={"memory_id": memory_id}
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


@router.get("/list", response_model=APIResponse)
async def get_memories_list(
    user_id: str,
    app_name: str,
    db: Session = Depends(get_db)
):
    """获取用户在特定应用下的所有记忆列表"""
    try:
        memory_manager = MemoryManager(db)
        
        # 获取记忆列表
        memories = memory_manager.get_memories_by_user_app(user_id, app_name)
        
        # 构建结果
        memory_list = []
        for memory in memories:
            memory_list.append({
                "memory_id": memory.id,
                "memory_content": memory.memory_content,
                "extracted_elements": memory.extracted_elements,
                "memory_tags": memory.memory_tags,
                "memory_priority": memory.memory_priority,
                "last_accessed_at": memory.last_accessed_at.isoformat(),
                "created_at": memory.created_at.isoformat()
            })
        
        return APIResponse(
            success=True,
            message="Memories retrieved successfully",
            data={"memories": memory_list}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memories list: {str(e)}"
        )
