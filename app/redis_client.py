import logging
import json
import hashlib
from typing import Any, Optional

from app.config import RedisConfig
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self, config: RedisConfig) -> None:
        self.config = config
        self._redis: Optional[redis.Redis] = None

    async def init(self) -> None:
        if self._redis is None:
            self._redis = redis.Redis.from_url(
                self.config.url,
                decode_responses=True,
                max_connections=self.config.max_connections
            )
        # Test connection
        try:
            await self._redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error("Redis connection failed: %s", e)
            raise

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> Any:
        if not self._redis:
            return None
        try:
            value = await self._redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ex: int = None) -> None:
        if not self._redis:
            return
        try:
            await self._redis.set(key, json.dumps(value), ex=ex or self.config.ttl_seconds)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        if not self._redis:
            return
        try:
            await self._redis.delete(key)
        except Exception:
            pass

    def _hash_key(self, data: str) -> str:
        return hashlib.md5(data.encode()).hexdigest()

    async def cache_get(self, key: str) -> Any:
        return await self.get(key)

    async def cache_set(self, key: str, value: Any, ttl: int = None) -> None:
        cache_key = f"cache:{key}"
        await self.set(cache_key, value, ex=ttl)

    async def cache_delete(self, key: str) -> None:
        cache_key = f"cache:{key}"
        await self.delete(cache_key)

    async def rate_limit_get(self, user_id: int, limit_type: str = "message") -> int:
        if not self._redis:
            return 0
        try:
            key = f"rate_limit:{user_id}:{limit_type}"
            current = await self._redis.get(key)
            return int(current) if current else 0
        except Exception:
            return 0

    async def rate_limit_incr(self, user_id: int, limit_type: str = "message", ttl: int = 3600) -> None:
        if not self._redis:
            return
        try:
            key = f"rate_limit:{user_id}:{limit_type}"
            await self._redis.incr(key)
            await self._redis.expire(key, ttl)
        except Exception:
            pass