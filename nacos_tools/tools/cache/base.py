"""
Base class for cache tools in Nacos Tools with async support.
"""

from abc import ABC, abstractmethod


class CacheTool(ABC):
    @abstractmethod
    async def connect(self):
        """Asynchronously establish a connection to the cache system."""
        pass

    @abstractmethod
    async def set(self, key, value, ttl=None):
        """Asynchronously set a key-value pair in the cache with optional TTL."""
        pass

    @abstractmethod
    async def get(self, key):
        """Asynchronously get a value from the cache by key."""
        pass

    @abstractmethod
    async def close(self):
        """Asynchronously close the cache connection if needed."""
        pass
