"""
Default tool configurations for Nacos Tools.

Defines default configurations for various tool categories and types.
"""

import os


def get_tool_configs():
    """
    Get the default tool configurations.

    Returns:
        dict: A dictionary of tool configurations.
    """
    return {
        # 数据库配置
        "vdb": {
            "mysql": {
                "type": os.getenv("DB_CONNECTION", "mysql"),
                "connection": os.getenv("DB_CONNECTION", "mysql"),
                "host": os.getenv("MYSQL_HOST", "localhost"),
                "user": os.getenv("MYSQL_USER", "root"),
                "password": os.getenv("MYSQL_PASSWORD", "password"),
                "database": os.getenv("MYSQL_DB", "test_db"),
                "port": int(os.getenv("MYSQL_PORT", 3306))
            },
            "postgresql": {
                "type": os.getenv("DB_CONNECTION", "postgresql"),
                "connection": os.getenv("DB_CONNECTION", "mysql"),
                "host": os.getenv("POSTGRES_HOST", "localhost"),
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
                "type": os.getenv("STORAGE_TYPE", "aliyun-oss"),
                "endpoint": os.getenv("ALIYUN_OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com"),
                "access_key_id": os.getenv("ALIYUN_OSS_ACCESS_KEY_ID"),
                "access_key_secret": os.getenv("ALIYUN_OSS_ACCESS_KEY_SECRET"),
                "bucket_name": os.getenv("ALIYUN_OSS_BUCKET_NAME", "my-bucket")
            }
        }
    }
