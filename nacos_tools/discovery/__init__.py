"""
Service discovery module for Nacos Tools.

Manages service registration and discovery.
"""

from .manager import DiscoveryManager
from .nacos import NacosDiscovery

__all__ = ["DiscoveryManager", "NacosDiscovery"]