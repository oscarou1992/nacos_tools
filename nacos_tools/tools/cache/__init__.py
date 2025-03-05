"""
Cache system module for Nacos Tools.

Manages cache implementations with async/sync support (e.g., Redis).
"""

from .base import CacheTool
from .impl.redis import RedisCache

__all__ = ["CacheTool", "RedisCache"]
