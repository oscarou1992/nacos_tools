"""
Base class for storage tools in Nacos Tools with async support.
"""

from abc import ABC, abstractmethod


class StorageTool(ABC):
    @abstractmethod
    async def connect(self):
        """Asynchronously establish a connection to the storage system."""
        pass

    @abstractmethod
    async def upload(self, bucket, key, data):
        """Asynchronously upload data to the specified bucket and key."""
        pass

    @abstractmethod
    async def download(self, bucket, key):
        """Asynchronously download data from the specified bucket and key."""
        pass

    @abstractmethod
    async def close(self):
        """Asynchronously close the storage connection if needed."""
        pass
