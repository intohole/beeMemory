from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import api_router
from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.core.task_scheduler import task_scheduler
from app.core.logging import setup_logging, get_logger

# 初始化日志系统
setup_logging()
logger = get_logger(__name__)

# 创建数据库表
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully.")

# 初始化FastAPI应用
logger.info(f"Initializing FastAPI application: {settings.app.name} v{settings.app.version}")
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="基于大模型的轻量化记忆系统",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.app.debug,
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

# 包含API路由，添加/api前缀
app.include_router(api_router, prefix="/api")

# 启动定时任务
logger.info("Starting task scheduler...")
task_scheduler.start()
logger.info("Task scheduler started successfully.")


@app.get("/")
async def root():
    """根路径，返回前端页面"""
    return FileResponse("app/static/index.html")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"Application {settings.app.name} v{settings.app.version} started successfully!")
    logger.info(f"Using timezone: {settings.timezone}")
    logger.info(f"LLM Model: {settings.llm.model}")
    logger.info(f"Embedding Model: {settings.embedding.model}")
    logger.info(f"Chroma Collection: {settings.chroma.collection_name}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件，停止定时任务"""
    logger.info("Shutting down application...")
    task_scheduler.stop()
    logger.info("Task scheduler stopped.")
    logger.info(f"Application {settings.app.name} v{settings.app.version} shutdown completed!")
