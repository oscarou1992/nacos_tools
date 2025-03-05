"""
Nacos-specific implementation of configuration management.
"""

import os
from nacos import NacosClient
from .manager import ConfigManager


class NacosConfig(ConfigManager):
    def __init__(self, server_addr, namespace="public", group="DEFAULT_GROUP"):
        """Initialize Nacos client with server address, namespace, and group."""
        self.client = NacosClient(server_addr, namespace=namespace)
        self.group = group

    def load_config(self, data_id):
        """Load configuration from Nacos and set it as environment variables."""
        config = self.client.get_config(data_id, self.group)
        if config:
            for line in config.splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
            return True
        return False

    def listen_config(self, data_id, callback):
        """Add a watcher to listen for configuration changes in Nacos."""
        self.client.add_config_watcher(data_id, self.group, callback)
