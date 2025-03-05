"""
Nacos-specific implementation of service discovery.
"""

from .manager import DiscoveryManager


class NacosDiscovery(DiscoveryManager):
    def __init__(self, client):
        """Initialize with a Nacos client instance."""
        self.client = client

    def register_service(self, service_name, ip, port):
        """Register a service to Nacos with custom IP and port."""
        self.client.register_service(service_name, ip, port, group_name="DEFAULT_GROUP")

    def get_service_url(self, service_name, endpoint):
        """Retrieve the URL of a service instance from Nacos."""
        instances = self.client.get_service_instances(service_name, "DEFAULT_GROUP")
        if not instances:
            raise Exception(f"未找到服务: {service_name}")
        instance = instances[0]  # Simple selection of the first instance
        return f"http://{instance['ip']}:{instance['port']}/{endpoint}"
