from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.models import MemoryPriority
from app.schemas.memory import (
    MemoryPriorityCreate,
    MemoryPriorityUpdate,
    MemoryPriorityResponse,
    APIResponse
)

router = APIRouter()


@router.post("/priorities", response_model=APIResponse)
async def create_memory_priority(
    priority: MemoryPriorityCreate,
    db: Session = Depends(get_db)
):
    """创建记忆优先级"""
    try:
        # 检查是否已存在相同的内容类型优先级
        existing_priority = db.query(MemoryPriority).filter(
            MemoryPriority.user_id == priority.user_id,
            MemoryPriority.app_name == priority.app_name,
            MemoryPriority.content_type == priority.content_type
        ).first()
        
        if existing_priority:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Priority for content type {priority.content_type} already exists for user {priority.user_id} and app {priority.app_name}"
            )
        
        # 创建新优先级
        new_priority = MemoryPriority(
            user_id=priority.user_id,
            app_name=priority.app_name,
            content_type=priority.content_type,
            priority_level=priority.priority_level,
            description=priority.description
        )
        
        db.add(new_priority)
        db.commit()
        db.refresh(new_priority)
        
        # 转换为Schema格式
        priority_response = MemoryPriorityResponse.model_validate(new_priority)
        
        return APIResponse(
            success=True,
            message="Memory priority created successfully",
            data={"priority": priority_response}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create memory priority: {str(e)}"
        )


@router.get("/priorities", response_model=APIResponse)
async def get_memory_priorities(
    user_id: Optional[str] = None,
    app_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取记忆优先级列表"""
    try:
        # 构建查询
        query = db.query(MemoryPriority)
        
        if user_id:
            query = query.filter(MemoryPriority.user_id == user_id)
        if app_name:
            query = query.filter(MemoryPriority.app_name == app_name)
        
        priorities = query.all()
        
        # 转换为Schema格式
        priority_responses = [MemoryPriorityResponse.model_validate(priority) for priority in priorities]
        
        return APIResponse(
            success=True,
            message="Memory priorities retrieved successfully",
            data={"priorities": priority_responses}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory priorities: {str(e)}"
        )


@router.get("/priorities/{priority_id}", response_model=APIResponse)
async def get_memory_priority(
    priority_id: int,
    db: Session = Depends(get_db)
):
    """获取单个记忆优先级"""
    try:
        priority = db.query(MemoryPriority).filter(
            MemoryPriority.id == priority_id
        ).first()
        
        if not priority:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Priority with id {priority_id} not found"
            )
        
        # 转换为Schema格式
        priority_response = MemoryPriorityResponse.model_validate(priority)
        
        return APIResponse(
            success=True,
            message="Memory priority retrieved successfully",
            data={"priority": priority_response}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory priority: {str(e)}"
        )


@router.put("/priorities/{priority_id}", response_model=APIResponse)
async def update_memory_priority(
    priority_id: int,
    priority_update: MemoryPriorityUpdate,
    db: Session = Depends(get_db)
):
    """更新记忆优先级"""
    try:
        priority = db.query(MemoryPriority).filter(
            MemoryPriority.id == priority_id
        ).first()
        
        if not priority:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Priority with id {priority_id} not found"
            )
        
        # 更新字段
        if priority_update.priority_level is not None:
            priority.priority_level = priority_update.priority_level
        if priority_update.description is not None:
            priority.description = priority_update.description
        
        db.commit()
        db.refresh(priority)
        
        # 转换为Schema格式
        priority_response = MemoryPriorityResponse.model_validate(priority)
        
        return APIResponse(
            success=True,
            message="Memory priority updated successfully",
            data={"priority": priority_response}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update memory priority: {str(e)}"
        )


@router.delete("/priorities/{priority_id}", response_model=APIResponse)
async def delete_memory_priority(
    priority_id: int,
    db: Session = Depends(get_db)
):
    """删除记忆优先级"""
    try:
        priority = db.query(MemoryPriority).filter(
            MemoryPriority.id == priority_id
        ).first()
        
        if not priority:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Priority with id {priority_id} not found"
            )
        
        db.delete(priority)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Memory priority deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memory priority: {str(e)}"
        )
