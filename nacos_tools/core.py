"""
Core integration module for Nacos Tools.

Combines configuration, service discovery, and tool management (vdb, cache, storage, etc., async/sync).
"""

from .config.nacos import NacosConfig
from .config.tools import get_tool_configs
from .discovery.nacos import NacosDiscovery
from .tools.manager import ToolManager
import os
import asyncio


class NacosTools:
    def __init__(self, server_addr="http://localhost:8848", namespace="public", group="DEFAULT_GROUP", data_id="",
                 username=None, password=None, async_mode=True):
        """Initialize NacosTools with server address, namespace, group, environment, and async mode."""

        # nacos 配置
        self.data_id = data_id

        # nacos tools
        self.async_mode = async_mode
        self.config = NacosConfig(server_addr, namespace, group, username, password)
        self.discovery = NacosDiscovery(self.config.client)
        self.tools = ToolManager()

        # 当前服务配置信息
        self.service_name = None
        self.service_ip = None
        self.service_port = None

    def init(self, service_name="default-service", service_ip="127.0.0.1", service_port=5000):
        """Initialize tools and register service synchronously."""
        self.service_name = service_name
        self.service_ip = service_ip
        self.service_port = service_port

        # 加载配置并监听变更
        self.config.load_config(self.data_id)
        self._initialize_tools()

        # 异步监听配置变更
        async def config_callback(args):
            self.config.update_config(args)
            await self._update_tools()

        self.config.start_listening(self.data_id, config_callback)

        # 注册服务
        self.discovery.register_service(service_name, service_ip, service_port)

        # 启动心跳
        self.config.start_heartbeat(service_name, service_ip, service_port)

    def get_service_url(self, service_name):
        return self.discovery.get_service_url(service_name)

    def _initialize_tools(self):
        """Initialize database, cache, and storage tools from environment variables."""

        # 工具类别和默认配置映射
        tool_configs = get_tool_configs()

        # 根据类型动态选择配置
        tools_config = {}
        for category, types in tool_configs.items():
            tool_type = os.getenv(f"{category.upper()}_TYPE", list(types.keys())[0]).lower()
            if tool_type in types:
                tools_config[category] = types[tool_type]
            else:
                raise ValueError(f"Unsupported {category} type: {tool_type}")

        self.tools.initialize(tools_config, async_mode=self.async_mode)

    async def _update_tools(self):
        """Update tools with new configurations on change."""
        tool_configs = get_tool_configs()
        tools_config = {}
        for category, types in tool_configs.items():
            tool_type = os.getenv(f"{category.upper()}_TYPE", list(types.keys())[0]).lower()
            if tool_type in types:
                tools_config[category] = types[tool_type]
            else:
                raise ValueError(f"Unsupported {category} type: {tool_type}")
            await self.tools.update_tool(category, tools_config[category], self.async_mode)

    async def get_db(self):
        """Get the database tool instance."""
        return await self.tools.get_db()

    async def get_cache(self):
        """Get the cache tool instance."""
        return await self.tools.get_cache()

    async def get_storage(self):
        """Get the storage tool instance."""
        return await self.tools.get_storage()

    async def get_tool(self, category):
        """Get a specific tool instance by category."""
        return await self.tools.get_tool(category)

    async def shutdown(self):
        """Shutdown all tools and clean up resources."""
        await self.tools.shutdown()
