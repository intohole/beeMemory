from fastapi import APIRouter

from .core import router as core_router
from .config import router as config_router
from .priorities import router as priorities_router
from .manual import router as manual_router

# 创建主路由
router = APIRouter(
    tags=["memory"],
    responses={404: {"description": "Not found"}},
)

# 包含所有子路由
router.include_router(core_router)
router.include_router(config_router)
router.include_router(priorities_router)
router.include_router(manual_router)
