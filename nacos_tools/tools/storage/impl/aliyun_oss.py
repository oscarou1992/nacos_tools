"""
Aliyun OSS storage implementation for Nacos Tools with async/sync support.
"""

import oss2
import asyncio
from io import BytesIO
from ..base import StorageTool


class AliyunOSS(StorageTool):
    def __init__(self, config, async_mode=True):
        """Initialize Aliyun OSS with configuration and mode (async/sync)."""
        self.config = config
        self.async_mode = async_mode
        self.auth = None
        self.bucket = None

    async def connect(self):
        """Asynchronously establish a connection to Aliyun OSS."""
        self.auth = oss2.Auth(self.config["access_key_id"], self.config["access_key_secret"])
        self.bucket = oss2.Bucket(self.auth, self.config["endpoint"], self.config["bucket_name"])

    async def upload(self, bucket, key, data):
        """Asynchronously upload data to Aliyun OSS."""
        if not self.bucket:
            await self.connect()
        if isinstance(data, str):
            data = data.encode("utf-8")
        if not isinstance(data, (bytes, BytesIO)):
            raise ValueError("Data must be str, bytes, or BytesIO")

        if self.async_mode:
            await asyncio.to_thread(self.bucket.put_object, key, data)
        else:
            self.bucket.put_object(key, data)

    async def download(self, bucket, key):
        """Asynchronously download data from Aliyun OSS."""
        if not self.bucket:
            await self.connect()

        if self.async_mode:
            result = await asyncio.to_thread(self.bucket.get_object, key)
        else:
            result = self.bucket.get_object(key)

        return result.read()

    async def close(self):
        """Close the OSS connection (no-op for oss2)."""
        pass
