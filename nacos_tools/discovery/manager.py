"""
Abstract base class for service discovery in Nacos Tools.
"""

from abc import ABC, abstractmethod


class DiscoveryManager(ABC):
    @abstractmethod
    def register_service(self, service_name, ip, port):
        """Register a service with the given name, IP, and port."""
        pass

    @abstractmethod
    def get_service_url(self, service_name):
        """Get the URL of a service instance."""
        pass
