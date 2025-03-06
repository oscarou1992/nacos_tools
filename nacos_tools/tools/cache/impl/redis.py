"""
Redis cache implementation for Nacos Tools with async/sync support.
"""
import json
from typing import Any, Optional, Dict
from urllib.parse import quote_plus

import redis
import redis.asyncio as aioredis
import asyncio
from ..base import CacheTool


class RedisCache(CacheTool):
    def __init__(self, config, async_mode=True):
        """Initialize Redis cache with configuration and mode (async/sync)."""
        self.config = config
        self.async_mode = async_mode
        self.client = None

    def _build_redis_url(self):
        """构建 Redis URL，包含认证信息"""
        auth_part = ""
        if self.config.get('username') and self.config.get('password'):
            auth_part = f"{quote_plus(self.config['username'])}:{quote_plus(self.config['password'])}@"
        elif self.config.get('password'):
            auth_part = f":{quote_plus(self.config['password'])}@"

        return f"redis://{auth_part}{self.config['host']}:{self.config['port']}/{self.config['db']}"

    async def connect(self):
        """Asynchronously establish a connection to Redis."""
        if self.async_mode:
            self.client = await aioredis.from_url(
                self._build_redis_url(),
                decode_responses=True  # 自动解码为字符串
            )
        else:
            self.client = redis.StrictRedis(
                host=self.config["host"],
                port=self.config["port"],
                db=self.config["db"],
                password=self.config["password"],
                username=self.config["username"],
                decode_responses=True  # 自动解码为字符串
            )

    async def close(self):
        """Close the Redis connection."""
        if self.client:
            if self.async_mode:
                await self.client.close()
            else:
                self.client.close()

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a key-value pair in Redis with optional TTL, serializing the value."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()

        if isinstance(value, (int, float, dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, (str, bytes)):
            raise ValueError(f"Unsupported type for Redis value: {type(value)}")

        if self.async_mode:
            return asyncio.run(self.client.set(key, value, ex=ttl))
        else:
            return self.client.set(key, value, ex=ttl)

    def get(self, key: str, return_type: str = "str") -> Any:
        """
        Get a value from Redis by key with type conversion (sync/async handled).
        """
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()

        if self.async_mode:
            value = asyncio.run(self.client.get(key))
        else:
            value = self.client.get(key)

        if value is None:
            return None

        if return_type == "str":
            return value
        elif return_type == "int":
            return int(value)
        elif return_type == "float":
            return float(value)
        elif return_type == "json":
            return json.loads(value)
        else:
            raise ValueError(f"Unsupported return_type: {return_type}")

    def connect_sync(self):
        """Synchronously establish a connection to Redis."""
        if not self.async_mode:
            self.client = redis.StrictRedis(
                host=self.config["host"],
                port=self.config["port"],
                db=self.config["db"],
                decode_responses=True
            )

    def delete(self, key: str) -> int:
        """Delete a key from Redis and return the number of keys deleted."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()
        if self.async_mode:
            return asyncio.run(self.client.delete(key))
        else:
            return self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()
        if self.async_mode:
            return bool(asyncio.run(self.client.exists(key)))
        else:
            return bool(self.client.exists(key))

    def incr(self, key: str, amount: int = 1) -> int:
        """Increment the value of a key by amount (default 1)."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()
        if self.async_mode:
            return asyncio.run(self.client.incr(key, amount))
        else:
            return self.client.incr(key, amount)

    def decr(self, key: str, amount: int = 1) -> int:
        """Decrement the value of a key by amount (default 1)."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()
        if self.async_mode:
            return asyncio.run(self.client.decr(key, amount))
        else:
            return self.client.decr(key, amount)

    def hset(self, name: str, key: str, value: Any) -> int:
        """Set a field in a Redis hash, serializing the value."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()

        if isinstance(value, (int, float, dict, list)):
            value = json.dumps(value)
        elif not isinstance(value, (str, bytes)):
            raise ValueError(f"Unsupported type for Redis hash value: {type(value)}")

        if self.async_mode:
            return asyncio.run(self.client.hset(name, key, value))
        else:
            return self.client.hset(name, key, value)

    def hget(self, name: str, key: str, return_type: str = "str") -> Any:
        """Get a field value from a Redis hash with type conversion."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()

        if self.async_mode:
            value = asyncio.run(self.client.hget(name, key))
        else:
            value = self.client.hget(name, key)

        if value is None:
            return None

        if return_type == "str":
            return value
        elif return_type == "int":
            return int(value)
        elif return_type == "float":
            return float(value)
        elif return_type == "json":
            return json.loads(value)
        else:
            raise ValueError(f"Unsupported return_type: {return_type}")

    def hgetall(self, name: str, return_type: str = "str") -> Dict[str, Any]:
        """Get all fields and values from a Redis hash with type conversion."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()

        if self.async_mode:
            result = asyncio.run(self.client.hgetall(name))
        else:
            result = self.client.hgetall(name)

        if not result:
            return {}

        if return_type == "str":
            return result
        decoded_result = {}
        for k, v in result.items():
            if return_type == "int":
                decoded_result[k] = int(v)
            elif return_type == "float":
                decoded_result[k] = float(v)
            elif return_type == "json":
                decoded_result[k] = json.loads(v)
            else:
                raise ValueError(f"Unsupported return_type: {return_type}")
        return decoded_result

    def expire(self, key: str, ttl: int) -> bool:
        """Set an expiration time (TTL) on a key in seconds."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()
        if self.async_mode:
            return bool(asyncio.run(self.client.expire(key, ttl)))
        else:
            return bool(self.client.expire(key, ttl))

    def ttl(self, key: str) -> int:
        """Get the remaining time to live (TTL) of a key in seconds."""
        if not self.client:
            if self.async_mode:
                asyncio.run(self.connect())
            else:
                self.connect_sync()
        if self.async_mode:
            return asyncio.run(self.client.ttl(key))
        else:
            return self.client.ttl(key)
