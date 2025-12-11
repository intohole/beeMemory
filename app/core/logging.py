import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志为JSON字符串"""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加额外的上下文信息
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return str(log_data)


def setup_logging():
    """设置日志系统"""
    log_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": settings.logging.format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": JSONFormatter,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": settings.logging.level,
                "class": "logging.StreamHandler",
                "formatter": "json" if settings.logging.use_json else "standard",
            },
        },
        "root": {
            "level": settings.logging.level,
            "handlers": ["console"],
        },
        "loggers": {
            "uvicorn": {
                "level": settings.logging.level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": settings.logging.level,
                "handlers": ["console"],
                "propagate": False,
            },
            "app": {
                "level": settings.logging.level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    
    # 添加文件日志处理器
    if settings.logging.file_path:
        # 确保日志目录存在
        log_dir = os.path.dirname(settings.logging.file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler_config = {
            "level": settings.logging.level,
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json" if settings.logging.use_json else "standard",
            "filename": settings.logging.file_path,
            "maxBytes": settings.logging.max_size,
            "backupCount": settings.logging.backup_count,
            "encoding": "utf-8",
        }
        
        log_config["handlers"]["file"] = file_handler_config
        
        # 将文件处理器添加到根日志器和app日志器
        log_config["root"]["handlers"].append("file")
        log_config["loggers"]["app"]["handlers"].append("file")
    
    # 配置日志系统
    logging.config.dictConfig(log_config)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        日志记录器实例
    """
    if name is None:
        name = "app"
    return logging.getLogger(name)


# 初始化日志系统
setup_logging()
