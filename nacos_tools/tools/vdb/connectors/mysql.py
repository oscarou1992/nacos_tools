"""
MySQL connector for VDB using SQLAlchemy ORM with async/sync support.
"""
import contextlib
from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData, Column, Integer, String, TIMESTAMP, func, PrimaryKeyConstraint, text, \
    select
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
from ..base import DatabaseTool

# Import common SQLAlchemy types to make available
from sqlalchemy.types import (
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    BigInteger,
    Date,
    Time,
    JSON,
)

from sqlalchemy import (
    ForeignKeyConstraint,
    UniqueConstraint,
    CheckConstraint,
    Index
)


# 首先定义 classproperty 装饰器
class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


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

            @classproperty
            def query(cls):
                """动态返回查询对象，使用事务安全的会话"""
                if not hasattr(cls, '_connector'):
                    raise ValueError("Model is not bound to a connector. Ensure 'db.Model' is used.")

                bind_key = getattr(cls.__table__.info, 'bind_key', 'default') if hasattr(cls,
                                                                                         '__table__') else 'default'

                if cls._connector.async_mode:
                    raise ValueError("query property is not supported in async mode. Use get_query() instead.")

                session = cls._connector.get_session(bind_key)
                if session is None:
                    raise ValueError(
                        f"No session available for bind_key '{bind_key}'. Did you call connect_sync() or connect()?")
                return session.query(cls)

            @classmethod
            def get_query(cls):
                """类级别的查询对象，使用事务安全的会话"""
                if not hasattr(cls, '_connector'):
                    raise ValueError("Model is not bound to a connector. Ensure 'db.Model' is used.")

                bind_key = getattr(cls.__table__.info, 'bind_key', 'default') if hasattr(cls,
                                                                                         '__table__') else 'default'

                if cls._connector.async_mode:
                    with cls._connector.async_session_scope(bind_key) as session:
                        stmt = select(cls)
                        result = session.execute(stmt)
                        return result.scalars()
                else:
                    session = cls._connector.get_session(bind_key)
                    if session is None:
                        raise ValueError(
                            f"No session available for bind_key '{bind_key}'. Did you call connect_sync() or connect()?")
                    return session.query(cls)

            # Add Column as a class attribute
            Column = staticmethod(Column)
            PrimaryKeyConstraint = staticmethod(PrimaryKeyConstraint)
            ForeignKeyConstraint = staticmethod(ForeignKeyConstraint)
            UniqueConstraint = staticmethod(UniqueConstraint)
            CheckConstraint = staticmethod(CheckConstraint)
            Index = staticmethod(Index)
            text = staticmethod(text)  # Add text function for SQL expressions

            # Add common SQLAlchemy types
            Integer = Integer
            String = String
            Text = Text
            Boolean = Boolean
            DateTime = DateTime
            Float = Float
            BigInteger = BigInteger
            Date = Date
            Time = Time
            JSON = JSON
            TIMESTAMP = TIMESTAMP
            func = func  # For SQL functions like current_timestamp()

        # 创建 Model 类并绑定 connector 实例
        self.Model = declarative_base(cls=BindModel, metadata=self.metadata)
        self.Model._connector = self  # 将 connector 实例绑定到 Model 类

        # Make Column and types accessible through the connector instance
        self.Column = Column
        self.PrimaryKeyConstraint = PrimaryKeyConstraint
        self.ForeignKeyConstraint = ForeignKeyConstraint
        self.UniqueConstraint = UniqueConstraint
        self.CheckConstraint = CheckConstraint
        self.Index = Index
        self.text = text  # Add text function to connector instance
        self.Integer = Integer
        self.String = String
        self.Text = Text
        self.Boolean = Boolean
        self.DateTime = DateTime
        self.Float = Float
        self.BigInteger = BigInteger
        self.Date = Date
        self.Time = Time
        self.JSON = JSON
        self.TIMESTAMP = TIMESTAMP
        self.func = func

    def _create_engine(self, db_config, bind_key=None):
        """创建数据库引擎"""
        if self.async_mode:
            url = f"mysql+aiomysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config.get('port', 3306)}/{db_config['database']}"
            engine = create_async_engine(
                url,
                echo=False,
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
                echo=False,
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
                    expire_on_commit=False,
                    autocommit=False,
                    autoflush=True
                )
            else:
                session_factory = sessionmaker(
                    bind=engine,
                    expire_on_commit=False,
                    autocommit=False,
                    autoflush=True
                )
            self.session_factories[bind_key] = session_factory
            self.sessions[bind_key] = session_factory()

        # 设置默认会话
        self.session = self.sessions['default']

    async def close(self):
        """Close all database connections."""
        # 关闭所有会话
        for session in self.sessions.values():
            if self.async_mode:
                await session.close()
            else:
                session.close()
        self.sessions.clear()

        # 关闭所有引擎
        for engine in self.engines.values():
            if self.async_mode:
                await engine.dispose()
            else:
                engine.dispose()

    def get_engine(self, bind_key='default'):
        """获取指定绑定键的引擎"""
        return self.engines.get(bind_key)

    def get_session(self, bind_key='default'):
        """获取指定绑定键的会话，并确保事务状态正确"""
        if bind_key not in self.sessions:
            self.sessions[bind_key] = self.session_factories[bind_key]()

        session = self.sessions[bind_key]

        # 检查并处理无效事务
        if not self.async_mode:  # 同步模式
            if session.is_active and session.in_transaction():
                try:
                    session.rollback()
                except:
                    session.close()
                    self.sessions[bind_key] = self.session_factories[bind_key]()
                    session = self.sessions[bind_key]

        return session

    @contextmanager
    def session_scope(self, bind_key='default'):
        """提供事务范围的会话上下文管理器（同步模式）"""
        session = self.get_session(bind_key)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @contextlib.asynccontextmanager
    async def async_session_scope(self, bind_key='default'):
        """提供事务范围的会话上下文管理器（异步模式）"""
        session = self.get_session(bind_key)
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    def __del__(self):
        """确保在对象销毁时关闭所有会话"""
        for session in self.sessions.values():
            try:
                if self.async_mode:
                    asyncio.create_task(session.close())
                else:
                    session.close()
            except:
                pass
