"""
SQLite 数据库连接 + LangChain SQLDatabase 封装
基于 playground/test_nl2sql.py 实测验证
"""

import os
from langchain_community.utilities import SQLDatabase
from app.config import get_settings

_db_instance: SQLDatabase | None = None


def get_db() -> SQLDatabase:
    """
    获取 SQLDatabase 单例

    Returns:
        SQLDatabase 实例，已连接到 SQLite 数据库
    """
    global _db_instance
    if _db_instance is None:
        settings = get_settings()
        db_path = settings.DB_PATH

        # 确保数据目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        _db_instance = SQLDatabase.from_uri(f"sqlite:///{db_path}")

    return _db_instance


def get_db_path() -> str:
    """获取数据库文件绝对路径"""
    settings = get_settings()
    return os.path.abspath(settings.DB_PATH)
