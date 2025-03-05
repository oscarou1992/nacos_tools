"""
Abstract base class for configuration management in Nacos Tools.
"""

from abc import ABC, abstractmethod


class ConfigManager(ABC):
    @abstractmethod
    def load_config(self, data_id):
        """Load configuration from a given source identified by data_id."""
        pass

    @abstractmethod
    def start_listening(self, data_id, callback):
        """Start a background thread to listen for configuration changes."""
        pass
