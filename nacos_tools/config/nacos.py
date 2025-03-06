"""
Nacos-specific implementation of configuration management.
"""
import asyncio
import hashlib
import os
import threading
import time

from nacos import NacosClient
from .manager import ConfigManager


class NacosConfig(ConfigManager):
    def __init__(self, server_addr, namespace="public", group="DEFAULT_GROUP", username=None, password=None):
        """Initialize Nacos client with server address, namespace, and group."""
        self.client = NacosClient(server_addr, namespace=namespace, username=username, password=password)
        self.group = group

        # 配置监听相关
        self._running = False
        self._listener_thread = None
        self._loop = None
        self.listener_interval = 5  # 监听间隔（秒）

        # 心跳检测相关
        self._heartbeat_thread = None
        self._heartbeat_running = False
        self.heartbeat_interval = 5  # 心跳间隔（秒）

    async def _run_callback(self, callback, args):
        """异步执行回调"""
        try:
            await callback(args)
        except Exception as e:
            print(f"Error in callback: {e}")

    def _get_config_with_no_cache(self, data_id):
        """
        获取配置时添加时间戳避免缓存
        """
        try:
            # 添加时间戳参数避免缓存
            timestamp = int(time.time() * 1000)
            params = {
                'dataId': data_id,
                'group': self.group,
                'tenant': self.client.namespace,
                'timestamp': timestamp  # 添加时间戳
            }

            # 直接调用 Nacos 的配置接口
            response = self.client._do_sync_req(
                '/nacos/v1/cs/configs',
                params=params
            )

            return response.read().decode("UTF-8")
        except Exception as e:
            print(f"Error getting config: {e}")
            return None

    def _calculate_md5(self, content):
        """计算配置内容的MD5值"""
        if content is None:
            return None
        md5 = hashlib.md5()
        md5.update(content.encode('utf-8'))
        return md5.hexdigest()

    def _watch_config(self, data_id, callback):
        """监听配置变更的内部方法"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        last_md5 = None
        while self._running:
            try:
                # 获取最新配置（无缓存）
                current_content = self._get_config_with_no_cache(data_id)
                current_md5 = self._calculate_md5(current_content)

                # 检查配置是否发生变化
                if current_md5 != last_md5:
                    if current_content is not None:  # 不是首次获取
                        # 异步执行回调
                        self._loop.run_until_complete(
                            self._run_callback(callback, {
                                "data_id": data_id,
                                "group": self.group,
                                "config": current_content
                            })
                        )
                    last_md5 = current_md5

                # 等待一段时间后再次检查
                time.sleep(self.listener_interval)

            except Exception as e:
                print(f"Error in config watcher: {e}")
                time.sleep(5)

        if self._loop:
            self._loop.close()

    def _send_heartbeat(self, service_name, ip, port):
        """发送心跳的内部方法"""
        while self._heartbeat_running:
            try:
                self.client.send_heartbeat(
                    service_name,
                    ip,
                    port,
                    group_name=self.group
                )
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                print(f"Error sending heartbeat: {e}")
                time.sleep(1)  # 出错后等待短暂时间再重试

    def update_config(self, args):
        """更新配置变更的内部方法"""
        config = args.get("config")
        if config:
            for line in config.splitlines():
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

    def load_config(self, data_id):
        """Load configuration from Nacos and set it as environment variables."""
        try:
            config = self.client.get_config(data_id, self.group)
            if config:
                for line in config.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
                return True
            return False
        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def start_listening(self, data_id, callback):
        """实现配置监听"""
        if self._listener_thread is None or not self._listener_thread.is_alive():
            self._running = True
            self._listener_thread = threading.Thread(
                target=self._watch_config,
                args=(data_id, callback),
                daemon=True
            )
            self._listener_thread.start()

    def stop_listening(self):
        """Stop listening for configuration changes."""
        self._running = False
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=2)  # 等待线程结束，最多等待2秒
        if self._loop:
            self._loop.stop()

    def start_heartbeat(self, service_name, ip, port):
        """启动心跳检测"""
        if self._heartbeat_thread is None or not self._heartbeat_thread.is_alive():
            self._heartbeat_running = True
            self._heartbeat_thread = threading.Thread(
                target=self._send_heartbeat,
                args=(service_name, ip, port),
                daemon=True
            )
            self._heartbeat_thread.start()

    def stop_heartbeat(self):
        """停止心跳检测"""
        self._heartbeat_running = False
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=2)

    def __del__(self):
        """Cleanup when the object is destroyed."""
        self.stop_heartbeat()
        self.stop_listening()
