"""
Abstract base class for configuration management in Nacos Tools.
"""

from abc import ABC, abstractmethod
from threading import Thread


class ConfigManager(ABC):
    @abstractmethod
    def load_config(self, data_id):
        """Load configuration from a given source identified by data_id."""
        pass

    @abstractmethod
    def listen_config(self, data_id, callback):
        """Listen for configuration changes and invoke the callback on updates."""
        pass

    def start_listening(self, data_id, callback):
        """Start a background thread to listen for configuration changes."""
        Thread(target=self.listen_config, args=(data_id, callback), daemon=True).start()
