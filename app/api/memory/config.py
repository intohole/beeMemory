from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.schemas.memory import (
    APIResponse
)
from app.core.config import settings
from app.services.memory import MemoryManager

router = APIRouter()


@router.get("/app/config", response_model=APIResponse)
async def get_app_config(
    app_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取应用配置，可以获取单个应用配置或所有应用配置"""
    try:
        memory_manager = MemoryManager(db)
        
        if app_name:
            # 获取单个应用配置
            app_config = memory_manager.get_or_create_app_config(app_name)
            
            return APIResponse(
                success=True,
                message="App config retrieved successfully",
                data={
                    "app_name": app_config.app_name,
                    "extraction_template": app_config.extraction_template,
                    "extraction_fields": app_config.extraction_fields,
                    "conversation_rounds": app_config.conversation_rounds,
                    "max_summary_length": app_config.max_summary_length,
                    "enable_auto_summarize": app_config.enable_auto_summarize,
                    "enable_element_extraction": app_config.enable_element_extraction,
                    "similarity_threshold": app_config.similarity_threshold,
                    "priority_weights": app_config.priority_weights
                }
            )
        else:
            # 获取所有应用配置
            from app.models import AppConfig
            all_app_configs = db.query(AppConfig).all()
            
            # 构建结果
            app_configs_list = []
            for config in all_app_configs:
                app_configs_list.append({
                    "app_name": config.app_name,
                    "extraction_template": config.extraction_template,
                    "extraction_fields": config.extraction_fields,
                    "conversation_rounds": config.conversation_rounds,
                    "max_summary_length": config.max_summary_length,
                    "enable_auto_summarize": config.enable_auto_summarize,
                    "enable_element_extraction": config.enable_element_extraction,
                    "similarity_threshold": config.similarity_threshold,
                    "priority_weights": config.priority_weights
                })
            
            return APIResponse(
                success=True,
                message="All app configs retrieved successfully",
                data=app_configs_list
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get app config: {str(e)}"
        )


@router.put("/app/config", response_model=APIResponse)
async def update_app_config(
    app_name: str,
    config_data: dict,
    db: Session = Depends(get_db)
):
    """更新应用配置"""
    try:
        memory_manager = MemoryManager(db)
        
        # 更新应用配置
        app_config = memory_manager.update_app_config(app_name, **config_data)
        
        return APIResponse(
            success=True,
            message="App config updated successfully",
            data={
                "app_name": app_config.app_name,
                "extraction_template": app_config.extraction_template,
                "extraction_fields": app_config.extraction_fields,
                "conversation_rounds": app_config.conversation_rounds,
                "max_summary_length": app_config.max_summary_length,
                "enable_auto_summarize": app_config.enable_auto_summarize,
                "enable_element_extraction": app_config.enable_element_extraction,
                "similarity_threshold": app_config.similarity_threshold,
                "priority_weights": app_config.priority_weights
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update app config: {str(e)}"
        )


@router.get("/user/app/config", response_model=APIResponse)
async def get_user_app_config(
    user_id: str,
    app_name: str,
    db: Session = Depends(get_db)
):
    """获取用户应用配置"""
    try:
        memory_manager = MemoryManager(db)
        
        # 获取用户应用配置
        user_config = memory_manager.get_user_app_config(user_id, app_name)
        
        if not user_config:
            return APIResponse(
                success=True,
                message="User app config not found, using default",
                data={
                    "user_id": user_id,
                    "app_name": app_name,
                    "use_default": True
                }
            )
        
        return APIResponse(
            success=True,
            message="User app config retrieved successfully",
            data={
                "user_id": user_config.user_id,
                "app_name": user_config.app_name,
                "use_default": user_config.use_default,
                "custom_config": user_config.custom_config
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user app config: {str(e)}"
        )


@router.put("/user/app/config", response_model=APIResponse)
async def update_user_app_config(
    user_id: str,
    app_name: str,
    config_data: dict,
    db: Session = Depends(get_db)
):
    """更新用户应用配置"""
    try:
        memory_manager = MemoryManager(db)
        
        # 更新用户应用配置
        user_config = memory_manager.create_or_update_user_app_config(
            user_id=user_id,
            app_name=app_name,
            use_default=config_data.get("use_default", True),
            custom_config=config_data.get("custom_config")
        )
        
        return APIResponse(
            success=True,
            message="User app config updated successfully",
            data={
                "user_id": user_config.user_id,
                "app_name": user_config.app_name,
                "use_default": user_config.use_default,
                "custom_config": user_config.custom_config
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user app config: {str(e)}"
        )
