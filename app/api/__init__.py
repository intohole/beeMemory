from fastapi import APIRouter
from app.api.memory import router as memory_router

api_router = APIRouter()

# 为memory路由添加正确的前缀
api_router.include_router(memory_router, prefix="/memory")
