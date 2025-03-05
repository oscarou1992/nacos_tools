"""
Default tool configurations for Nacos Tools.

Defines default configurations for various tool categories and types.
"""

import os

# 工具类别和默认配置映射
TOOL_CONFIGS = {
    # 数据库配置
    "vdb": {
        "mysql": {
            "type": os.getenv("DB_CONNECTION", "mysql"),
            "connection": os.getenv("DB_CONNECTION", "mysql"),
            "user": os.getenv("MYSQL_USER", "root"),
            "password": os.getenv("MYSQL_PASSWORD", "password"),
            "database": os.getenv("MYSQL_DB", "test_db"),
            "port": int(os.getenv("MYSQL_PORT", 3306))
        },
        "postgresql": {
            "type": os.getenv("DB_CONNECTION", "postgresql"),
            "connection": os.getenv("DB_CONNECTION", "postgresql"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "password"),
            "database": os.getenv("POSTGRES_DB", "test_db"),
            "port": int(os.getenv("POSTGRES_PORT", 5432))
        }
    },

    # 缓存配置
    "cache": {
        "redis": {
            "type": os.getenv("CACHE_TYPE", "redis"),
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
            "db": int(os.getenv("REDIS_DB", 0))
        }
    },

    # 存储配置
    "storage": {
        "aliyun-oss": {
            "type": os.getenv("STORAGE_TYPE", "redis"),
            "endpoint": os.getenv("ALIYUN_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com"),
            "access_key_id": os.getenv("ALIYUN_ACCESS_KEY_ID"),
            "access_key_secret": os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
            "bucket_name": os.getenv("ALIYUN_BUCKET_NAME", "my-bucket")
        }
    }
}


def get_tool_configs():
    """
    Get the default tool configurations.

    Returns:
        dict: A dictionary of tool configurations.
    """
    return TOOL_CONFIGS
