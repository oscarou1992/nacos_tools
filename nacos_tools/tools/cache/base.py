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
    async def close(self):
        """Asynchronously close the cache connection if needed."""
        pass
