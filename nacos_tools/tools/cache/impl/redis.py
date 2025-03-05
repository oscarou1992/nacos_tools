"""
Redis cache implementation for Nacos Tools with async/sync support.
"""

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

    async def connect(self):
        """Asynchronously establish a connection to Redis."""
        if self.async_mode:
            self.client = await aioredis.from_url(
                f"redis://{self.config['host']}:{self.config['port']}/{self.config['db']}"
            )
        else:
            self.client = redis.StrictRedis(
                host=self.config["host"],
                port=self.config["port"],
                db=self.config["db"]
            )

    async def set(self, key, value, ttl=None):
        """Set a key-value pair in Redis with optional TTL."""
        if not self.client:
            await self.connect()
        if self.async_mode:
            await self.client.set(key, value, ex=ttl)
        else:
            self.client.set(key, value, ex=ttl)

    async def get(self, key):
        """Get a value from Redis by key."""
        if not self.client:
            await self.connect()
        if self.async_mode:
            value = await self.client.get(key)
        else:
            value = self.client.get(key)
        return value

    async def close(self):
        """Close the Redis connection."""
        if self.client:
            if self.async_mode:
                await self.client.close()
            else:
                self.client.close()
