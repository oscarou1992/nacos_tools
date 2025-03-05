"""
Tool manager for handling various tools (vdb, cache, storage, etc.) with async/sync support.
"""

from .vdb.connectors.mysql import MySQLConnector
from .vdb.connectors.postgres import PostgresConnector
from .cache.impl.redis import RedisCache
from .storage.impl.aliyun_oss import AliyunOSS
import asyncio


class ToolProxy:
    def __init__(self, tool_instance=None):
        """Initialize proxy with an optional initial tool instance."""
        self.instance = tool_instance

    async def update(self, new_instance):
        """Update the proxied instance, closing the old one if it exists."""
        if self.instance:
            await self.instance.close()
        self.instance = new_instance

    def __getattr__(self, name):
        """Delegate attribute access to the current instance."""
        if self.instance is None:
            raise AttributeError("Tool instance not initialized")
        return getattr(self.instance, name)


class ToolManager:
    def __init__(self):
        """Initialize with an empty tools dictionary and tool registry."""
        self.tools = {}  # 存储工具实例，键为工具类别（如 "vdb"、"cache"）
        self.tool_registry = {}  # 工具类型注册表，键为类别，值为类型到类的映射

        # 默认注册常用工具
        self.register_tool("vdb", "mysql", MySQLConnector)
        self.register_tool("vdb", "postgresql", PostgresConnector)
        self.register_tool("cache", "redis", RedisCache)
        self.register_tool("storage", "aliyun", AliyunOSS)

    def register_tool(self, category, type_name, tool_class):
        """
        Register a new tool implementation for a category.

        Args:
            category (str): Tool category (e.g., "vdb", "cache", "storage").
            type_name (str): Specific type name (e.g., "mysql", "redis", "aliyun").
            tool_class (class): The tool implementation class.
        """
        if category not in self.tool_registry:
            self.tool_registry[category] = {}
        self.tool_registry[category][type_name.lower()] = tool_class

    def _validate_config(self, category, config):
        """
        Validate the configuration for a specific tool category.

        Args:
            category (str): Tool category.
            config (dict): Configuration dictionary for the tool.

        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = {
            "vdb": ["type", "host", "user", "password", "database"],
            "cache": ["type", "host", "port", "db"],
            "storage": ["type", "endpoint", "access_key_id", "access_key_secret", "bucket_name"]
        }
        if category not in required_fields:
            return  # 未定义校验规则的类别跳过校验

        missing = [field for field in required_fields[category] if field not in config or config[field] is None]
        if missing:
            raise ValueError(f"Missing required fields for {category}: {missing}")

    def initialize(self, tools_config, async_mode=True):
        """
        Initialize tools based on a unified configuration dictionary.

        Args:
            tools_config (dict): A dictionary with tool categories as keys and their configurations as values.
            async_mode (bool): Whether to use async mode for tool operations.

        Raises:
            ValueError: If configuration or tool type is invalid.
        """
        for tool_category, config in tools_config.items():
            self._validate_config(tool_category, config)
            tool_type = config.get("type", "").lower()

            if tool_category not in self.tool_registry or tool_type not in self.tool_registry[tool_category]:
                raise ValueError(f"Unsupported {tool_category} type: {tool_type}")

            tool_class = self.tool_registry[tool_category][tool_type]
            tool_instance = tool_class(config, async_mode=async_mode)
            asyncio.run(tool_instance.connect())
            self.tools[tool_category] = ToolProxy(tool_instance)

    async def update_tool(self, category, config, async_mode):
        """Update a specific tool instance with new configuration."""
        tool_type = config.get("type", "").lower()
        if tool_type not in self.tool_registry[category]:
            raise ValueError(f"Unsupported {category} type: {tool_type}")
        tool_class = self.tool_registry[category][tool_type]
        new_instance = tool_class(config, async_mode=async_mode)
        await new_instance.connect()
        await self.tools[category].update(new_instance)

    async def get_tool(self, category):
        """
        Get the tool instance for the specified category.

        Args:
            category (str): The tool category (e.g., "vdb", "cache", "storage").

        Returns:
            The tool instance if available, else None.
        """
        return self.tools.get(category)

    # 便捷方法，保持向后兼容
    async def get_db(self):
        """Get the database tool instance (alias for get_tool('vdb'))."""
        return await self.get_tool("vdb")

    async def get_cache(self):
        """Get the cache tool instance (alias for get_tool('cache'))."""
        return await self.get_tool("cache")

    async def get_storage(self):
        """Get the storage tool instance (alias for get_tool('storage'))."""
        return await self.get_tool("storage")

    async def shutdown(self):
        """Asynchronously close all initialized tools."""
        for tool in self.tools.values():
            await tool.close()
        self.tools.clear()
