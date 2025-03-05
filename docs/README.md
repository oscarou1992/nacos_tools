[English](README.md) | [简体中文](README_zh.md)


# Nacos Tools

A Python library for integrating Nacos configuration management, service discovery, and tool management (virtual
database, cache, storage) with support for both synchronous and asynchronous frameworks.

## Features

- **Nacos Integration**: Dynamically load and listen to configuration changes from Nacos.
- **Service Discovery**: Register and discover services via Nacos.
- **Tool Management**: Manage virtual databases (via SQLAlchemy ORM), cache systems (e.g., Redis), and storage systems (
  e.g., Aliyun OSS) with a unified interface.
- **Async/Sync Support**: Compatible with synchronous frameworks (e.g., Flask) and asynchronous frameworks (e.g., Sanic,
  FastAPI).
- **Dynamic Updates**: Gracefully update tool instances (e.g., database, cache) when Nacos configurations change, without
  disrupting application usage.
- **Extensibility**: Easily extend with new tool types (e.g., Memcached, AWS S3) by registering implementations and updating
  configurations.

## Installation

Install via pip:

```bash
pip install nacos-tools
```

### Requirements

- Python >= 3.6
- Dependencies (automatically installed):
    - sqlalchemy>=1.4.0,
    - pymysql==1.1.1
    - psycopg2-binary>=2.9.5
    - aiomysql>=0.2.0
    - asyncpg>=0.27.0
    - redis>=4.0.0
    - nacos-sdk-python>=0.1.9
    - oss2>=2.17.0

## Usage

### Flask (Synchronous)

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

### Sanic (Asynchronous)

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

### FastAPI (Asynchronous)

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
    nacos.init(service_name="fastapi-service", service_ip="127.0.0.1", service_port=8000)
    db = await nacos.get_db()
    cache = await nacos.get_cache()
    storage = await nacos.get_storage()

@app.get("/test-db")
async def test_db():
    result = await db.execute("SELECT 1").scalar()
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

## Configuration

Set configurations in Nacos (e.g. `app-config-dev`):

```plaintext
# Database (based on DB_TYPE)
DB_TYPE=mysql  # or postgresql
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DB=test_db
MYSQL_PORT=3306
# or
# POSTGRES_HOST=localhost
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=password
# POSTGRES_DB=test_db
# POSTGRES_PORT=5432

# Cache (based on CACHE_TYPE)
CACHE_TYPE=redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Storage (based on STORAGE_TYPE)
STORAGE_TYPE=aliyun
ALIYUN_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_BUCKET_NAME=my-bucket
```

### Configuration Updates

- When Nacos configurations change (e.g., `MYSQL_HOST` updated), the library automatically updates environment variables and reinitializes tool instances (e.g., `db`, `cache`, `storage`).
- Global objects remain the same (e.g., `from app import db`), but their internal instances are refreshed with the new configuration seamlessly.

## Key Concepts

### Tool Management

- **Virtual Database (VDB)**: Supports MySQL and PostgreSQL via SQLAlchemy ORM, with async (`aiomysql`, `asyncpg`) and sync (`pymysql`, `psycopg2`) modes.
- **Cache**: Supports Redis, extensible to other systems (e.g., Memcached).
- **Storage**: Supports Aliyun OSS, extensible to other systems (e.g., AWS S3).

### Dynamic Instance Updates

- Tool instances are wrapped in proxy objects, initialized during app setup (e.g., `create_app` or `init_app`).
- Configuration changes trigger updates to the proxy's internal instances, ensuring global objects (e.g., `db`) always use the latest configuration without changing their reference.

### Extensibility

To add a new tool type (e.g., Memcached cache):

1. Implement the tool class (e.g., `nacos_tools/tools/cache/impl/memcached.py`).
2. Register it in `ToolManager`:
```python
from nacos_tools.tools.cache.impl.memcached import MemcachedCache
nacos.tools.register_tool("cache", "memcached", MemcachedCache)
```
3. Update `nacos_tools/tools/configs.py`:
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
4. Use in Nacos config:
```plaintext
CACHE_TYPE=memcached
MEMCACHED_HOST=localhost
MEMCACHED_PORT=11211
```

## Notes

- **Async Mode**: Set `async_mode=True` for async frameworks (Sanic, FastAPI) to use asynchronous drivers; `False` for sync frameworks (Flask).
- **Resource Cleanup**: Call `nacos.shutdown()` to close all tool connections when the app stops.
- **Thread Safety**: In multi-threaded environments (e.g., Flask with threads), the proxy ensures safe updates, but consider adding locks for critical sections if needed.

## License

MIT License