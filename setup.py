from setuptools import setup, find_packages

setup(
    name="nacos-tools",  # 包名
    version="0.1.6",  # 版本号
    packages=find_packages(),  # 自动发现所有包和子包
    install_requires=[
        "sqlalchemy>=1.4.0",
        "pymysql>=1.1.1",  # 同步 MySQL 驱动
        "psycopg2-binary>=2.9.5",  # 同步 PostgreSQL 驱动
        "aiomysql>=0.2.0",  # 异步 MySQL 驱动
        "asyncpg>=0.27.0",  # 异步 PostgreSQL 驱动
        "redis>=4.0.0",
        "nacos-sdk-python>=0.1.9",
        "oss2>=2.17.0"  # 阿里云 OSS SDK
    ],
    author="Oscar Ou",
    author_email="oscar.ou@tamaredge.ai",
    description="A Python library for Nacos integration with virtual database (async/sync), cache, and storage systems",
    long_description=open("docs/README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/oscarou1992/nacos_tools",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
