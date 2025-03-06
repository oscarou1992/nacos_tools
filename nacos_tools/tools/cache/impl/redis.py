"""
Redis cache implementation for Nacos Tools with async/sync support.
"""
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
        self._connection_pool = None

        # 设置默认配置
        self.default_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'username': None,
            'password': None,
            'encoding': 'utf-8',
            'decode_responses': True,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'socket_keepalive': True,
            'health_check_interval': 30,
            'retry_on_timeout': True,
            'max_connections': 10
        }

        # 更新配置
        self.default_config.update(config)
        self.config = self.default_config

    def _build_redis_url(self):
        """构建 Redis URL，包含认证信息"""
        auth_part = ""
        if self.config.get('username') and self.config.get('password'):
            auth_part = f"{quote_plus(self.config['username'])}:{quote_plus(self.config['password'])}@"
        elif self.config.get('password'):
            auth_part = f":{quote_plus(self.config['password'])}@"

        return f"redis://{auth_part}{self.config['host']}:{self.config['port']}/{self.config['db']}"

    def _create_connection_pool(self):
        """创建连接池"""
        if self.async_mode:
            return aioredis.ConnectionPool.from_url(
                self._build_redis_url(),
                decode_responses=self.config['decode_responses'],
                encoding=self.config['encoding'],
                socket_timeout=self.config['socket_timeout'],
                socket_connect_timeout=self.config['socket_connect_timeout'],
                health_check_interval=self.config['health_check_interval'],
                max_connections=self.config['max_connections'],
                retry_on_timeout=self.config['retry_on_timeout']
            )
        else:
            return redis.ConnectionPool.from_url(
                self._build_redis_url(),
                decode_responses=self.config['decode_responses'],
                encoding=self.config['encoding'],
                socket_timeout=self.config['socket_timeout'],
                socket_connect_timeout=self.config['socket_connect_timeout'],
                health_check_interval=self.config['health_check_interval'],
                max_connections=self.config['max_connections'],
                retry_on_timeout=self.config['retry_on_timeout']
            )

    async def connect(self):
        """Asynchronously establish a connection to Redis."""
        try:
            if self._connection_pool is None:
                self._connection_pool = self._create_connection_pool()

            if self.async_mode:
                self.client = aioredis.Redis(
                    connection_pool=self._connection_pool
                )
                # 测试连接
                await self.client.ping()
            else:
                self.client = redis.Redis(
                    connection_pool=self._connection_pool
                )
                # 测试连接
                self.client.ping()

        except Exception as e:
            await self.close()
            raise ConnectionError(f"Failed to connect to Redis: {str(e)}")

    def get_client(self):
        if not self.client:
            asyncio.run(self.connect())
        return self.client

    async def close(self):
        """Close the Redis connection."""
        try:
            if self.client:
                if self.async_mode:
                    await self.client.close()
                else:
                    self.client.close()

            if self._connection_pool:
                # 获取所有活跃连接并关闭
                if hasattr(self._connection_pool, '_connections'):
                    for conn in self._connection_pool._connections:
                        try:
                            conn.disconnect()
                        except:
                            pass
                self._connection_pool.disconnect()

            # 强制清理内存
            import gc
            gc.collect()

            self.client = None
            self._connection_pool = None
        except Exception as e:
            raise Exception(f"Failed to close Redis connection: {str(e)}")
