from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.db.session import get_db
from app.models import UserMemory, AppConfig
from app.schemas.memory import APIResponse

router = APIRouter()


@router.put("/archive", response_model=APIResponse)
async def archive_memory(
    memory_id: int = Query(..., description="记忆ID"),
    db: Session = Depends(get_db)
):
    """归档记忆
    
    将记忆标记为归档状态，不会被自动清理
    """
    try:
        # 获取记忆
        memory = db.query(UserMemory).filter(UserMemory.id == memory_id).first()
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with id {memory_id} not found"
            )
        
        # 更新记忆状态为归档
        memory.is_archived = True
        memory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)
        
        return APIResponse(
            success=True,
            message="Memory archived successfully",
            data={
                "memory_id": memory.id,
                "is_archived": memory.is_archived
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to archive memory: {str(e)}"
        )


@router.put("/unarchive", response_model=APIResponse)
async def unarchive_memory(
    memory_id: int = Query(..., description="记忆ID"),
    db: Session = Depends(get_db)
):
    """取消归档记忆
    
    将记忆恢复为正常状态
    """
    try:
        # 获取记忆
        memory = db.query(UserMemory).filter(UserMemory.id == memory_id).first()
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with id {memory_id} not found"
            )
        
        # 更新记忆状态为未归档
        memory.is_archived = False
        memory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)
        
        return APIResponse(
            success=True,
            message="Memory unarchived successfully",
            data={
                "memory_id": memory.id,
                "is_archived": memory.is_archived
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unarchive memory: {str(e)}"
        )


@router.put("/priority", response_model=APIResponse)
async def update_memory_priority(
    memory_id: int = Query(..., description="记忆ID"),
    priority_level: int = Query(..., description="新的优先级级别", ge=1, le=5),
    db: Session = Depends(get_db)
):
    """更新记忆优先级
    
    Args:
        memory_id: 记忆ID
        priority_level: 新的优先级级别（1-5，5最高）
    """
    try:
        # 验证优先级范围
        if priority_level < 1 or priority_level > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Priority level must be between 1 and 5"
            )
        
        # 获取记忆
        memory = db.query(UserMemory).filter(UserMemory.id == memory_id).first()
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with id {memory_id} not found"
            )
        
        # 更新优先级
        memory.memory_priority = priority_level
        memory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)
        
        return APIResponse(
            success=True,
            message="Memory priority updated successfully",
            data={
                "memory_id": memory.id,
                "memory_priority": memory.memory_priority
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update memory priority: {str(e)}"
        )


@router.put("/tags", response_model=APIResponse)
async def update_memory_tags(
    memory_id: int = Query(..., description="记忆ID"),
    tags: List[str] = Query(..., description="标签列表"),
    db: Session = Depends(get_db)
):
    """更新记忆标签
    
    Args:
        memory_id: 记忆ID
        tags: 标签列表
    """
    try:
        # 获取记忆
        memory = db.query(UserMemory).filter(UserMemory.id == memory_id).first()
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with id {memory_id} not found"
            )
        
        # 更新标签
        memory.memory_tags = tags
        memory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)
        
        return APIResponse(
            success=True,
            message="Memory tags updated successfully",
            data={
                "memory_id": memory.id,
                "memory_tags": memory.memory_tags
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update memory tags: {str(e)}"
        )


@router.get("/score/{memory_id}", response_model=APIResponse)
async def get_memory_score(
    memory_id: int,
    db: Session = Depends(get_db)
):
    """获取记忆的评分信息
    
    Args:
        memory_id: 记忆ID
    """
    try:
        # 获取记忆
        memory = db.query(UserMemory).filter(UserMemory.id == memory_id).first()
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with id {memory_id} not found"
            )
        
        # 获取应用配置
        app_config = db.query(AppConfig).filter(AppConfig.app_name == memory.app_name).first()
        
        if not app_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"App config for {memory.app_name} not found"
            )
        
        # 计算记忆评分
        now = datetime.utcnow()
        days_since_access = (now - memory.last_accessed_at).days
        days_since_created = (now - memory.created_at).days
        
        # 1. 访问频率评分
        access_score = max(0, 1 - days_since_access / app_config.expiry_days) if app_config.expiry_days > 0 else 1
        
        # 2. 优先级评分
        priority_score = memory.memory_priority / 5.0
        
        # 3. 时效性评分
        recency_score = max(0, 1 - days_since_created / (app_config.expiry_days * 2)) if app_config.expiry_days > 0 else 1
        
        # 4. 内容质量评分（基于提取的元素数量）
        content_quality_score = 0.5  # 默认值
        if memory.extracted_elements:
            element_count = len(memory.extracted_elements)
            # 元素越多，内容质量越高，但有上限
            content_quality_score = min(1.0, 0.3 + element_count * 0.1)
        
        # 5. 标签数量评分
        tag_score = 0.5  # 默认值
        if memory.memory_tags:
            tag_count = len(memory.memory_tags)
            # 标签越多，记忆越结构化，评分越高
            tag_score = min(1.0, 0.3 + tag_count * 0.15)
        
        # 计算最终评分，使用配置的权重 + 内容质量和标签权重
        final_score = (
            access_score * app_config.access_score_weight +
            priority_score * app_config.priority_score_weight +
            recency_score * app_config.recency_score_weight +
            content_quality_score * 0.1 +  # 内容质量权重10%
            tag_score * 0.1  # 标签权重10%
        )
        
        return APIResponse(
            success=True,
            message="Memory score retrieved successfully",
            data={
                "memory_id": memory.id,
                "access_score": round(access_score, 2),
                "priority_score": round(priority_score, 2),
                "recency_score": round(recency_score, 2),
                "content_quality_score": round(content_quality_score, 2),
                "tag_score": round(tag_score, 2),
                "final_score": round(final_score, 2),
                "last_accessed_at": memory.last_accessed_at.isoformat(),
                "created_at": memory.created_at.isoformat(),
                "app_config": {
                    "access_score_weight": app_config.access_score_weight,
                    "priority_score_weight": app_config.priority_score_weight,
                    "recency_score_weight": app_config.recency_score_weight
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory score: {str(e)}"
        )
