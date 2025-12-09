from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import api_router
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.core.task_scheduler import task_scheduler

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 初始化FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于大模型的轻量化记忆系统",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 包含API路由
app.include_router(api_router)

# 启动定时任务
task_scheduler.start()


@app.get("/")
async def root():
    """根路径，返回前端页面"""
    return FileResponse("app/static/index.html")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件，停止定时任务"""
    task_scheduler.stop()
