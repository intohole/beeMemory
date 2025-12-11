from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.models import MemoryConfig
from app.schemas.memory import (
    MemoryConfigCreate,
    MemoryConfigUpdate,
    MemoryConfigResponse,
    APIResponse
)
from app.core.config import settings
from app.services.memory import MemoryManager

router = APIRouter()


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
                extraction_prompt=config_update.extraction_prompt or settings.memory.default_extraction_prompt,
                merge_threshold=config_update.merge_threshold or settings.memory.default_merge_threshold,
                expiry_strategy=config_update.expiry_strategy or settings.memory.default_expiry_strategy,
                expiry_days=config_update.expiry_days or settings.memory.default_expiry_days
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
