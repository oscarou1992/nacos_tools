[English](https://github.com/oscarou1992/nacos_tools/blob/main/docs/README.md) | [简体中文](https://github.com/oscarou1992/nacos_tools/blob/main/docs/README_zh.md)


# Nacos Tools

一个用于集成 Nacos 配置管理、服务发现以及工具管理的 Python 库，支持同步和异步框架。

## 功能特性

- **Nacos 集成**： 动态加载和监听 Nacos 配置变更。
- **服务发现**： 通过 Nacos 注册和发现服务。
- **工具管理**： 统一管理虚拟数据库（通过 SQLAlchemy ORM）、缓存系统（如 Redis）和存储系统（如阿里云 OSS）。
- **异步/同步支持**： 兼容同步框架（如 Flask）和异步框架（如 Sanic、FastAPI）。
- **动态更新**： 当 Nacos 配置变更时，优雅地更新工具实例（如数据库、缓存），不影响应用使用。
- **扩展性**：支持通过注册新实现轻松扩展工具类型（如 Memcached、AWS S3）。

## Installation

通过 pip 安装：

```bash
pip install nacos-tools
```

### 依赖要求

- Python >= 3.6
- 自动安装的依赖:
    - sqlalchemy>=1.4.0,
    - pymysql==1.1.1
    - psycopg2-binary>=2.9.5
    - aiomysql>=0.2.0
    - asyncpg>=0.27.0
    - redis>=4.0.0
    - nacos-sdk-python>=0.1.9
    - oss2>=2.17.0

## 使用示例

### Flask (同步)

```python
from flask import Flask, jsonify
from nacos_tools import NacosTools
import asyncio

app = Flask(__name__)
nacos = NacosTools(server_addr="http://localhost:8848", data_id="app-config-dev", async_mode=False)

# Global tool instances
db = None
cache = None
storage = None


def create_app():
    global db, cache, storage
    nacos.init(service_name="flask-service", service_ip="127.0.0.1", service_port=5000)
    db = asyncio.run(nacos.get_db())
    cache = asyncio.run(nacos.get_cache())
    storage = asyncio.run(nacos.get_storage())
    return app


@app.route("/test-db")
def test_db():
    result = db.execute("SELECT 1").scalar()
    return jsonify({"result": result})


@app.route("/test-cache")
def test_cache():
    asyncio.run(cache.set("key", "value"))
    value = asyncio.run(cache.get("key"))
    return jsonify({"value": value.decode("utf-8")})


@app.route("/test-storage")
def test_storage():
    asyncio.run(storage.upload("my-bucket", "test.txt", "Hello Storage"))
    data = asyncio.run(storage.download("my-bucket", "test.txt"))
    return jsonify({"data": data.decode("utf-8")})


@app.route("/shutdown")
def shutdown():
    asyncio.run(nacos.shutdown())
    return jsonify({"status": "shutdown completed"})


if __name__ == "__main__":
    create_app()
    app.run(host="0.0.0.0", port=5000)
```

### Sanic (异步)

```python
from sanic import Sanic, response
from nacos_tools import NacosTools

app = Sanic("SanicApp")
nacos = NacosTools(server_addr="http://localhost:8848", data_id="app-config-dev", async_mode=True)

# Global tool instances
db = None
cache = None
storage = None


async def init_app():
    global db, cache, storage
    nacos.init(service_name="sanic-service", service_ip="127.0.0.1", service_port=8000)
    db = await nacos.get_db()
    cache = await nacos.get_cache()
    storage = await nacos.get_storage()


@app.get("/test-db")
async def test_db(request):
    result = await db.execute("SELECT 1").scalar()
    return response.json({"result": result})


@app.get("/test-cache")
async def test_cache(request):
    await cache.set("key", "value")
    value = await cache.get("key")
    return response.json({"value": value.decode("utf-8")})


@app.get("/test-storage")
async def test_storage(request):
    await storage.upload("my-bucket", "test.txt", "Hello Storage")
    data = await storage.download("my-bucket", "test.txt")
    return response.json({"data": data.decode("utf-8")})


@app.get("/shutdown")
async def shutdown(request):
    await nacos.shutdown()
    return response.json({"status": "shutdown completed"})


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_app())
    app.run(host="0.0.0.0", port=8000)
```

### FastAPI (异步)

```python
from fastapi import FastAPI
from nacos_tools import NacosTools

app = FastAPI()
nacos = NacosTools(server_addr="http://localhost:8848", data_id="app-config-dev", async_mode=True)

# Global tool instances
db = None
cache = None
storage = None


async def init_app():
    global db, cache, storage
    nacos.init(service_name="flask-service", service_ip="127.0.0.1", service_port=5000)
    db = nacos.get_db_sync()
    cache = nacos.get_cache_sync()
    storage = nacos.get_storage_sync()
    return app


@app.get("/test-db")
async def test_db():
    result = await db.execute("SELECT 1").scalar()
    return {"result": result}

@app.get("/test-model-db")
async def test_model_db():
    from sqlalchemy import Column, BigInteger, String, TIMESTAMP
    class XXModel(db.Model):
        __tablename__ = 'xx_table_name'
        __table_args__ = {'schema': 'test_db'}

        id = Column(BigInteger, primary_key=True, autoincrement=True)
        user_id = Column(String(36), nullable=False)


    result = db.session.query(XXModel).filter_by(user_id='xxxx').scalar()
    return {"result": result}

@app.get("/test-cache")
async def test_cache():
    await cache.set("key", "value")
    value = await cache.get("key")
    return {"value": value.decode("utf-8")}


@app.get("/test-storage")
async def test_storage():
    await storage.upload("my-bucket", "test.txt", "Hello Storage")
    data = await storage.download("my-bucket", "test.txt")
    return {"data": data.decode("utf-8")}


@app.get("/shutdown")
async def shutdown():
    await nacos.shutdown()
    return {"status": "shutdown completed"}


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_app())
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 配置说明

在 Nacos 中设置配置（例如 `app-config-dev`）：

```plaintext
# 数据库（根据 DB_TYPE 动态选择）
DB_TYPE=mysql  # or postgresql
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DB=test_db
MYSQL_PORT=3306
# 或
# POSTGRES_HOST=localhost
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=password
# POSTGRES_DB=test_db
# POSTGRES_PORT=5432

# 缓存（根据 CACHE_TYPE 动态选择）
CACHE_TYPE=redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 存储（根据 STORAGE_TYPE 动态选择）
STORAGE_TYPE=aliyun-oss
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_ACCESS_KEY_ID=your_access_key_id
ALIYUN_OSS_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_OSS_BUCKET_NAME=my-bucket
```

### 配置更新

- 当 Nacos 配置发生变更（例如 `MYSQL_HOST` 更新）时，库会自动更新环境变量，并重新初始化工具实例（如 `db`、`cache`、`storage`）。
- 全局对象（例如 ·from app import db·）保持不变，其内部实例会无缝切换到新配置。

## 核心概念

### 工具管理

- **虚拟数据库 (VDB)**：支持 MySQL 和 PostgreSQL，通过 SQLAlchemy ORM 实现，支持异步（`aiomysql`、`asyncpg`）和同步（`pymysql`、`psycopg2`）模式。
- **缓存**： 支持 Redis，可扩展到其他系统（如 Memcached）。
- **存储**： 支持阿里云 OSS，可扩展到其他系统（如 AWS S3）。

### 动态实例更新

- 工具实例在应用初始化时（如 `create_app` 或 `init_app`）被封装为代理对象。
- 配置变更时，代理内部的实例会更新为新配置的实例，而全局对象的引用（如 `db`）保持不变。

### 扩展性

添加新的工具类型（例如 Memcached 缓存）：

1. 实现工具类（例如 `nacos_tools/tools/cache/impl/memcached.py`）。
2. 在 `ToolManager` 中注册：

```python
from nacos_tools.tools.cache.impl.memcached import MemcachedCache

nacos.tools.register_tool("cache", "memcached", MemcachedCache)
```

3. 更新 `nacos_tools/tools/configs.py`：

```python
"cache": {
    "redis": {...},
    "memcached": {
        "type": os.getenv("CACHE_TYPE", "memcached"),
        "host": os.getenv("MEMCACHED_HOST", "localhost"),
        "port": int(os.getenv("MEMCACHED_PORT", 11211))
    }
}
```

4. 在 Nacos 配置中使用：

```plaintext
CACHE_TYPE=memcached
MEMCACHED_HOST=localhost
MEMCACHED_PORT=11211
```

## 注意事项

- **异步模式**： 对于异步框架（Sanic、FastAPI），设置 `async_mode=True` 使用异步驱动；对于同步框架（Flask），设置 `async_mode=False`。
- **资源清理**： 应用停止时调用 `nacos.shutdown()` 以关闭所有工具连接。
- **线程安全**: 在多线程环境（如 Flask 多线程模式）下，代理对象已确保更新安全，但在高并发场景下可考虑加锁优化。

## 许可证

MIT 许可证