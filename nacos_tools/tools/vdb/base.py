"""
Base class for virtual database tools in Nacos Tools with async support.
"""

from abc import ABC, abstractmethod

class DatabaseTool(ABC):
    @abstractmethod
    async def connect(self):
        """Asynchronously establish a connection to the database via SQLAlchemy ORM."""
        pass

    @abstractmethod
    async def get_session(self):
        """Asynchronously retrieve a SQLAlchemy session (AsyncSession or Session)."""
        pass

    @abstractmethod
    async def close(self):
        """Asynchronously close the database session or engine."""
        pass