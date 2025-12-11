from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.models import BusinessTemplate
from app.schemas.memory import (
    BusinessTemplateCreate,
    BusinessTemplateUpdate,
    BusinessTemplateResponse,
    APIResponse
)

router = APIRouter()


@router.post("/templates", response_model=APIResponse)
async def create_business_template(
    template: BusinessTemplateCreate,
    db: Session = Depends(get_db)
):
    """创建业务模板"""
    try:
        # 检查是否已存在同名模板
        existing_template = db.query(BusinessTemplate).filter(
            BusinessTemplate.app_name == template.app_name,
            BusinessTemplate.template_name == template.template_name
        ).first()
        
        if existing_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template with name {template.template_name} already exists for app {template.app_name}"
            )
        
        # 如果设置为默认模板，取消其他模板的默认状态
        if template.is_default:
            db.query(BusinessTemplate).filter(
                BusinessTemplate.app_name == template.app_name,
                BusinessTemplate.is_default == True
            ).update({"is_default": False})
        
        # 创建新模板
        new_template = BusinessTemplate(
            template_name=template.template_name,
            app_name=template.app_name,
            extraction_prompt=template.extraction_prompt,
            priority_fields=template.priority_fields,
            is_default=template.is_default
        )
        
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        
        # 转换为Schema格式
        template_response = BusinessTemplateResponse.model_validate(new_template)
        
        return APIResponse(
            success=True,
            message="Business template created successfully",
            data={"template": template_response}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create business template: {str(e)}"
        )


@router.get("/templates", response_model=APIResponse)
async def get_business_templates(
    app_name: Optional[str] = None,
    is_default: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取业务模板列表"""
    try:
        # 构建查询
        query = db.query(BusinessTemplate)
        
        if app_name:
            query = query.filter(BusinessTemplate.app_name == app_name)
        if is_default is not None:
            query = query.filter(BusinessTemplate.is_default == is_default)
        
        templates = query.all()
        
        # 转换为Schema格式
        template_responses = [BusinessTemplateResponse.model_validate(template) for template in templates]
        
        return APIResponse(
            success=True,
            message="Business templates retrieved successfully",
            data={"templates": template_responses}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business templates: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=APIResponse)
async def get_business_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """获取单个业务模板"""
    try:
        template = db.query(BusinessTemplate).filter(
            BusinessTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with id {template_id} not found"
            )
        
        # 转换为Schema格式
        template_response = BusinessTemplateResponse.model_validate(template)
        
        return APIResponse(
            success=True,
            message="Business template retrieved successfully",
            data={"template": template_response}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get business template: {str(e)}"
        )


@router.put("/templates/{template_id}", response_model=APIResponse)
async def update_business_template(
    template_id: int,
    template_update: BusinessTemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新业务模板"""
    try:
        template = db.query(BusinessTemplate).filter(
            BusinessTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with id {template_id} not found"
            )
        
        # 如果更新模板名称，检查是否已存在
        if template_update.template_name and template_update.template_name != template.template_name:
            existing_template = db.query(BusinessTemplate).filter(
                BusinessTemplate.app_name == template.app_name,
                BusinessTemplate.template_name == template_update.template_name
            ).first()
            
            if existing_template:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Template with name {template_update.template_name} already exists for app {template.app_name}"
                )
            template.template_name = template_update.template_name
        
        # 更新其他字段
        if template_update.extraction_prompt is not None:
            template.extraction_prompt = template_update.extraction_prompt
        if template_update.priority_fields is not None:
            template.priority_fields = template_update.priority_fields
        if template_update.is_default is not None:
            if template_update.is_default:
                # 取消其他模板的默认状态
                db.query(BusinessTemplate).filter(
                    BusinessTemplate.app_name == template.app_name,
                    BusinessTemplate.is_default == True
                ).update({"is_default": False})
            template.is_default = template_update.is_default
        
        db.commit()
        db.refresh(template)
        
        # 转换为Schema格式
        template_response = BusinessTemplateResponse.model_validate(template)
        
        return APIResponse(
            success=True,
            message="Business template updated successfully",
            data={"template": template_response}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update business template: {str(e)}"
        )


@router.delete("/templates/{template_id}", response_model=APIResponse)
async def delete_business_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """删除业务模板"""
    try:
        template = db.query(BusinessTemplate).filter(
            BusinessTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with id {template_id} not found"
            )
        
        db.delete(template)
        db.commit()
        
        return APIResponse(
            success=True,
            message="Business template deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete business template: {str(e)}"
        )
