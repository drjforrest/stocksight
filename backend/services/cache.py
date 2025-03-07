import json
from typing import Any, Optional
from datetime import timedelta
import redis
from redis import asyncio as aioredis
from functools import wraps
import hashlib
import logging
import os

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class CacheService:
    """Redis-based cache service with both sync and async support."""
    
    def __init__(self):
        # Sync client
        self.redis = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
        # Async client
        self.async_redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key based on function arguments"""
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    # Sync methods
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (sync)"""
        try:
            value = self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration (sync)"""
        try:
            return self.redis.setex(
                key,
                timedelta(seconds=expire),
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache (sync)"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    # Async methods
    async def aget(self, key: str) -> Optional[Any]:
        """Get value from cache (async)"""
        try:
            value = await self.async_redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Async cache get error: {e}")
            return None

    async def aset(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration (async)"""
        try:
            return await self.async_redis.setex(
                key,
                timedelta(seconds=expire),
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Async cache set error: {e}")
            return False

    async def adelete(self, key: str) -> bool:
        """Delete value from cache (async)"""
        try:
            return bool(await self.async_redis.delete(key))
        except Exception as e:
            logger.error(f"Async cache delete error: {e}")
            return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.async_redis.close()

def cache_result(prefix: str, expire: int = 3600):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = CacheService()
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache.aget(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # If not in cache, compute result
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.aset(cache_key, result, expire)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        return wrapper
    return decorator 

# Cache key prefixes
MARKET_DATA_PREFIX = "market:"
SEC_DATA_PREFIX = "sec:"
FDA_DATA_PREFIX = "fda:"
SEARCH_RESULTS_PREFIX = "search:"

# Cache expiration times (in seconds)
MARKET_DATA_EXPIRY = 300  # 5 minutes
SEC_DATA_EXPIRY = 86400  # 24 hours
FDA_DATA_EXPIRY = 86400  # 24 hours
SEARCH_RESULTS_EXPIRY = 3600  # 1 hour 