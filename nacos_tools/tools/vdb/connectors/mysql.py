"""
MySQL connector for VDB using SQLAlchemy ORM with async/sync support.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
from ..base import DatabaseTool


class MySQLConnector(DatabaseTool):
    def __init__(self, config, async_mode=True):
        """Initialize MySQL connector with configuration and mode (async/sync)."""
        self.config = config
        self.async_mode = async_mode
        self.engine = None
        self.session_factory = None
        self.session = None

    async def connect(self):
        """Asynchronously create a SQLAlchemy ORM connection to MySQL."""
        if self.async_mode:
            url = f"mysql+aiomysql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config.get('port', 3306)}/{self.config['database']}"
            self.engine = create_async_engine(url)
            self.session_factory = sessionmaker(self.engine, class_=AsyncSession)
            self.session = await self.session_factory().__aenter__()
        else:
            url = f"mysql+pymysql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config.get('port', 3306)}/{self.config['database']}"
            self.engine = create_engine(url)
            self.session_factory = sessionmaker(bind=self.engine)
            self.session = self.session_factory()

    async def get_session(self):
        """Get the SQLAlchemy session, reconnecting if necessary."""
        if not self.session or (self.async_mode and self.session.closed) or (
                not self.async_mode and self.session.closed):
            await self.connect()
        return self.session

    async def close(self):
        """Close the SQLAlchemy session."""
        if self.session:
            if self.async_mode:
                await self.session.close()
            else:
                self.session.close()
        # Optionally dispose engine: await self.engine.dispose() if async
