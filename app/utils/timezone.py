from datetime import datetime, timezone, timedelta
from typing import Optional
from app.core.config import settings

try:
    import zoneinfo
    
    def get_timezone():
        """获取配置的时区对象"""
        return zoneinfo.ZoneInfo(settings.timezone)
    
    def utc_to_local(utc_dt: datetime) -> datetime:
        """将UTC时间转换为配置时区的本地时间"""
        if utc_dt.tzinfo is None:
            # 如果没有时区信息，假设是UTC时间
            utc_dt = utc_dt.replace(tzinfo=timezone.utc)
        return utc_dt.astimezone(get_timezone())
    
    def local_to_utc(local_dt: datetime) -> datetime:
        """将配置时区的本地时间转换为UTC时间"""
        if local_dt.tzinfo is None:
            # 如果没有时区信息，假设是配置时区的本地时间
            local_dt = local_dt.replace(tzinfo=get_timezone())
        return local_dt.astimezone(timezone.utc)
    
    def get_local_now() -> datetime:
        """获取配置时区的当前时间"""
        return datetime.now(get_timezone())
    
    def get_utc_now() -> datetime:
        """获取当前UTC时间"""
        return datetime.now(timezone.utc)
except ImportError:
    # 兼容Python 3.8及以下版本
    import pytz
    
    def get_timezone():
        """获取配置的时区对象"""
        return pytz.timezone(settings.timezone)
    
    def utc_to_local(utc_dt: datetime) -> datetime:
        """将UTC时间转换为配置时区的本地时间"""
        if utc_dt.tzinfo is None:
            # 如果没有时区信息，假设是UTC时间
            utc_dt = timezone.utc.localize(utc_dt)
        return utc_dt.astimezone(get_timezone())
    
    def local_to_utc(local_dt: datetime) -> datetime:
        """将配置时区的本地时间转换为UTC时间"""
        if local_dt.tzinfo is None:
            # 如果没有时区信息，假设是配置时区的本地时间
            local_dt = get_timezone().localize(local_dt)
        return local_dt.astimezone(timezone.utc)
    
    def get_local_now() -> datetime:
        """获取配置时区的当前时间"""
        return get_timezone().localize(datetime.now())
    
    def get_utc_now() -> datetime:
        """获取当前UTC时间"""
        return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式化字符串
        
    Returns:
        格式化后的日期时间字符串
    """
    if dt.tzinfo is None:
        # 如果没有时区信息，使用配置时区
        dt = dt.replace(tzinfo=get_timezone())
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析日期时间字符串
    
    Args:
        dt_str: 日期时间字符串
        format_str: 格式化字符串
        
    Returns:
        日期时间对象，带有时区信息
    """
    dt = datetime.strptime(dt_str, format_str)
    # 添加配置时区信息
    return dt.replace(tzinfo=get_timezone())
