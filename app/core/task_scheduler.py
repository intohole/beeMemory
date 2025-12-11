import schedule
import time
import threading
from typing import Callable
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.memory import MemoryMerger, MemoryCleanupService
from app.core.config import settings
from app.core.logging import get_logger
from app.utils.timezone import get_local_now

logger = get_logger(__name__)


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
    
    def get_db(self) -> Session:
        """获取数据库会话"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def run_merge_task(self) -> None:
        """执行记忆合并任务"""
        logger.info("Running memory merge task...")
        db = next(self.get_db())
        try:
            merger = MemoryMerger(db)
            merger.run_merge()
            logger.info("Memory merge task completed.")
        except Exception as e:
            logger.error(f"Error running memory merge task: {str(e)}")
        finally:
            db.close()
    
    def run_cleanup_task(self) -> None:
        """执行记忆清理任务"""
        logger.info("Running memory cleanup task...")
        db = next(self.get_db())
        try:
            cleanup_service = MemoryCleanupService(db)
            cleanup_service.run_cleanup()
            logger.info("Memory cleanup task completed.")
        except Exception as e:
            logger.error(f"Error running memory cleanup task: {str(e)}")
        finally:
            db.close()
    
    def start(self) -> None:
        """启动定时任务"""
        if self.is_running:
            logger.info("Task scheduler is already running.")
            return
        
        # 设置合并任务 - 使用新的配置结构
        merge_interval = settings.scheduler.merge_interval_minutes
        schedule.every(merge_interval).minutes.do(self.run_merge_task)
        logger.info(f"Scheduled memory merge task every {merge_interval} minutes.")
        
        # 设置清理任务 - 使用新的配置结构
        cleanup_interval = settings.scheduler.cleanup_interval_minutes
        schedule.every(cleanup_interval).minutes.do(self.run_cleanup_task)
        logger.info(f"Scheduled memory cleanup task every {cleanup_interval} minutes.")
        
        # 立即执行一次任务
        self.run_merge_task()
        self.run_cleanup_task()
        
        # 启动任务线程
        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Task scheduler started.")
    
    def stop(self) -> None:
        """停止定时任务"""
        if not self.is_running:
            logger.info("Task scheduler is not running.")
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Task scheduler stopped.")
    
    def _run_scheduler(self) -> None:
        """运行调度器"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)


# 初始化任务调度器实例
task_scheduler = TaskScheduler()
