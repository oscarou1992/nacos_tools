"""
Nacos-specific implementation of service discovery.
"""
import random
from typing import List, Dict

from .manager import DiscoveryManager


class NacosDiscovery(DiscoveryManager):
    def __init__(self, client):
        """Initialize with a Nacos client instance."""
        self.client = client

    def register_service(self, service_name, ip, port):
        """Register a service to Nacos with custom IP and port."""
        self.client.add_naming_instance(service_name, ip, port, group_name="DEFAULT_GROUP")

    def get_service_url(self, service_name: str, strategy: str = 'random'):
        """Retrieve the URL of a service instance from Nacos."""
        instances = self.get_service_instances(service_name)
        if not instances:
            return None

        if strategy == 'random':
            # 随机策略
            instance = random.choice(instances)
            return instance['url']
        elif strategy == 'round_robin':
            # 轮询策略
            if not hasattr(self, '_counter'):
                self._counter = {}
            self._counter[service_name] = self._counter.get(service_name, 0) + 1
            index = (self._counter[service_name] - 1) % len(instances)
            return instances[index]['url']
        else:
            return instances[0]['url']

    def get_service_instances(self, service_name: str) -> List[Dict]:
        """
        获取服务实例列表
        :param service_name: 服务名称
        :return: 服务实例列表
        """
        try:
            # 使用 list_naming_instance 获取服务实例
            instances = self.client.list_naming_instance(service_name)
            if instances and 'hosts' in instances:
                # 只返回健康的实例
                return [
                    {
                        'ip': host['ip'],
                        'port': host['port'],
                        'weight': host.get('weight', 1),
                        'url': f"http://{host['ip']}:{host['port']}"
                    }
                    for host in instances['hosts']
                    if host.get('healthy', True)
                ]
            return []
        except Exception as e:
            print(f"Error getting service instances: {e}")
            return []
