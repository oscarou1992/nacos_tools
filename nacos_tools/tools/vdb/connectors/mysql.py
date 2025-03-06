"""
MySQL connector for VDB using SQLAlchemy ORM with async/sync support.
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, declared_attr
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
from ..base import DatabaseTool


class MySQLConnector(DatabaseTool):
    def __init__(self, config, async_mode=True):
        """Initialize MySQL connector with configuration and mode (async/sync)."""
        self.config = config
        self.async_mode = async_mode
        self.engines = {}  # 存储多个数据库引擎
        self.session_factories = {}  # 存储多个会话工厂
        self.sessions = {}  # 存储多个会话

        # 直接使用 MetaData
        # 修改 MetaData 的配置
        self.metadata = MetaData(
            # 设置命名约定，使用原始的表名，不转义
            naming_convention={
                "ix": "ix_%(column_0_label)s",
                "uq": "uq_%(table_name)s_%(column_0_name)s",
                "ck": "ck_%(table_name)s_%(constraint_name)s",
                "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
                "pk": "pk_%(table_name)s"
            }
        )
        self.metadata.bind_keys = {}  # 添加 bind_keys 属性

        # 创建基础模型类，支持 __bind_key__
        class BindModel:
            @classmethod
            def set_bind_key(cls, bind_key):
                if hasattr(cls, '__table__'):
                    cls.__table__.info['bind_key'] = bind_key

        self.Model = declarative_base(cls=BindModel, metadata=self.metadata)

    def _create_engine(self, db_config, bind_key=None):
        """创建数据库引擎"""
        if self.async_mode:
            url = f"mysql+aiomysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config.get('port', 3306)}/{db_config['database']}"
            engine = create_async_engine(
                url,
                echo=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
                pool_use_lifo=True,
                connect_args={'charset': 'utf8mb4'}
            )
        else:
            url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config.get('port', 3306)}/{db_config['database']}"
            engine = create_engine(
                url,
                echo=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
                pool_use_lifo=True,
                connect_args={'charset': 'utf8mb4'}
            )

        if bind_key:
            self.metadata.bind_keys[bind_key] = engine
        return engine

    async def connect(self, bind_key=None):
        """Asynchronously create SQLAlchemy ORM connections to MySQL databases."""
        # 处理默认连接
        default_engine = self._create_engine(self.config)
        self.engines['default'] = default_engine

        # 处理其他绑定的数据库
        if 'binds' in self.config:
            for bind_key, bind_config in self.config['binds'].items():
                engine = self._create_engine(bind_config, bind_key)
                self.engines[bind_key] = engine

        # 创建会话工厂
        for bind_key, engine in self.engines.items():
            if self.async_mode:
                session_factory = sessionmaker(
                    engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
            else:
                session_factory = sessionmaker(
                    bind=engine,
                    expire_on_commit=False
                )
            self.session_factories[bind_key] = session_factory
            self.sessions[bind_key] = session_factory()

        # 设置默认会话
        self.session = self.sessions['default']

    async def close(self):
        """Close all database connections."""
        for engine in self.engines.values():
            if self.async_mode:
                await engine.dispose()
            else:
                engine.dispose()

    def get_engine(self, bind_key='default'):
        """获取指定绑定键的引擎"""
        return self.engines.get(bind_key)

    def get_session(self, bind_key='default'):
        """获取指定绑定键的会话"""
        return self.sessions.get(bind_key)
