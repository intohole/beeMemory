from functools import lru_cache
from typing import Any, Dict, Optional, Callable, Tuple, List, Union
from datetime import datetime, timedelta
import hashlib
import pickle
import json
from collections import OrderedDict


class CacheItem:
    """缓存项类，包含缓存值、过期时间和元数据"""
    def __init__(self, value: Any, expiry: Optional[datetime] = None, metadata: Optional[Dict[str, Any]] = None):
        self.value = value
        self.expiry = expiry
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.access_count = 0  # 访问次数统计
    
    def is_expired(self) -> bool:
        """检查缓存项是否过期"""
        if self.expiry is None:
            return False
        return datetime.utcnow() > self.expiry
    
    def touch(self) -> None:
        """更新访问时间和访问次数"""
        self.access_count += 1


class MemoryCache:
    """增强的内存缓存类，支持过期时间、LRU淘汰策略和复杂数据结构"""
    
    def __init__(self, max_size: int = 2000):
        self.max_size = max_size
        # 使用OrderedDict实现LRU，最新访问的放在末尾
        self.cache: Dict[str, CacheItem] = {}
        self.access_order = OrderedDict()  # 用于LRU淘汰，最新访问的放在末尾
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0,
            "gets": 0
        }
    
    def _get_cache_key(self, func: Callable, *args, **kwargs) -> str:
        """生成缓存键"""
        # 序列化函数名、参数和关键字参数
        key_data = (func.__module__, func.__name__, args, tuple(sorted(kwargs.items())))
        key_bytes = pickle.dumps(key_data)
        return hashlib.md5(key_bytes).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值，如果缓存不存在或过期则返回
            
        Returns:
            缓存值或默认值
        """
        self.stats["gets"] += 1
        
        if key in self.cache:
            item = self.cache[key]
            if item.is_expired():
                # 缓存过期，删除
                self._remove_key(key)
                self.stats["misses"] += 1
                return default
            else:
                # 更新访问顺序和统计
                self._update_access_order(key)
                item.touch()
                self.stats["hits"] += 1
                return item.value
        
        self.stats["misses"] += 1
        return default
    
    def set(self, key: str, value: Any, expiry: Optional[timedelta] = None, metadata: Optional[Dict[str, Any]] = None):
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expiry: 过期时间，None表示永不过期
            metadata: 缓存项的元数据
        """
        self.stats["sets"] += 1
        expiry_time = datetime.utcnow() + expiry if expiry else None
        
        # 检查是否超过最大大小，超过则删除最久未访问的
        if key not in self.cache and len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # 创建缓存项
        self.cache[key] = CacheItem(value, expiry_time, metadata)
        
        # 更新访问顺序
        self._update_access_order(key)
    
    def get_or_set(self, key: str, func: Callable, expiry: Optional[timedelta] = None, **kwargs) -> Any:
        """获取缓存值，如果不存在则调用函数生成并缓存
        
        Args:
            key: 缓存键
            func: 生成缓存值的函数
            expiry: 过期时间
            kwargs: 传递给func的关键字参数
            
        Returns:
            缓存值
        """
        value = self.get(key)
        if value is not None:
            return value
        
        # 调用函数生成值
        value = func(**kwargs)
        self.set(key, value, expiry)
        return value
    
    def delete(self, key: str) -> bool:
        """删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        if key in self.cache:
            self._remove_key(key)
            return True
        return False
    
    def delete_many(self, keys: List[str]) -> int:
        """删除多个缓存值
        
        Args:
            keys: 缓存键列表
            
        Returns:
            成功删除的数量
        """
        count = 0
        for key in keys:
            if self.delete(key):
                count += 1
        return count
    
    def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存值
        
        Args:
            pattern: 正则表达式模式
            
        Returns:
            成功删除的数量
        """
        import re
        regex = re.compile(pattern)
        keys_to_delete = [key for key in self.cache if regex.match(key)]
        return self.delete_many(keys_to_delete)
    
    def exists(self, key: str) -> bool:
        """检查缓存键是否存在且未过期
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在且未过期
        """
        return key in self.cache and not self.cache[key].is_expired()
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.access_order.clear()
        # 重置统计
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "sets": 0,
            "gets": 0
        }
    
    def cache(self, expiry: Optional[timedelta] = None, **cache_kwargs):
        """缓存装饰器，支持过期时间和其他配置
        
        Args:
            expiry: 过期时间
            cache_kwargs: 其他缓存配置
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                key = self._get_cache_key(func, *args, **kwargs)
                
                # 尝试从缓存获取
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 缓存结果
                self.set(key, result, expiry, **cache_kwargs)
                
                return result
            return wrapper
        return decorator
    
    def cache_with_key(self, key_func: Callable, expiry: Optional[timedelta] = None, **cache_kwargs):
        """使用自定义键生成函数的缓存装饰器
        
        Args:
            key_func: 生成缓存键的函数
            expiry: 过期时间
            cache_kwargs: 其他缓存配置
            
        Returns:
            装饰器函数
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                key = key_func(*args, **kwargs)
                
                # 尝试从缓存获取
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 缓存结果
                self.set(key, result, expiry, **cache_kwargs)
                
                return result
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, int]:
        """获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        return self.stats.copy()
    
    def get_items(self, prefix: str = "") -> Dict[str, Any]:
        """获取所有缓存项，可选前缀过滤
        
        Args:
            prefix: 缓存键前缀
            
        Returns:
            缓存项字典
        """
        result = {}
        for key, item in self.cache.items():
            if key.startswith(prefix) and not item.is_expired():
                result[key] = item.value
        return result
    
    def _update_access_order(self, key: str) -> None:
        """更新访问顺序
        
        Args:
            key: 缓存键
        """
        if key in self.access_order:
            del self.access_order[key]
        self.access_order[key] = datetime.utcnow()
    
    def _remove_key(self, key: str) -> None:
        """删除缓存键
        
        Args:
            key: 缓存键
        """
        del self.cache[key]
        if key in self.access_order:
            del self.access_order[key]
    
    def _evict_lru(self) -> None:
        """执行LRU淘汰
        """
        if self.access_order:
            # 找到最久未访问的键
            oldest_key = next(iter(self.access_order))
            self._remove_key(oldest_key)
            self.stats["evictions"] += 1
    
    def __contains__(self, key: str) -> bool:
        """检查缓存中是否包含指定键"""
        return self.exists(key)
    
    def __len__(self) -> int:
        """获取缓存大小"""
        return len(self.cache)
    
    def __str__(self) -> str:
        """返回缓存的字符串表示"""
        return f"MemoryCache(size={len(self.cache)}, max_size={self.max_size}, stats={self.stats})"


# 创建全局缓存实例
cache = MemoryCache(max_size=2000)

# 便捷的缓存装饰器
def cached(expiry: Optional[timedelta] = None, **cache_kwargs):
    """便捷的缓存装饰器，使用全局缓存实例"""
    return cache.cache(expiry, **cache_kwargs)

# 便捷的带自定义键的缓存装饰器
def cached_with_key(key_func: Callable, expiry: Optional[timedelta] = None, **cache_kwargs):
    """便捷的带自定义键的缓存装饰器，使用全局缓存实例"""
    return cache.cache_with_key(key_func, expiry, **cache_kwargs)

# 常用的时间常量
ONE_MINUTE = timedelta(minutes=1)
FIVE_MINUTES = timedelta(minutes=5)
THIRTY_MINUTES = timedelta(minutes=30)
ONE_HOUR = timedelta(hours=1)
ONE_DAY = timedelta(days=1)
ONE_WEEK = timedelta(weeks=1)
