"""
MySQL 连接管理服务
- 连接配置 CRUD（JSON 文件持久化）
- SQLDatabase 实例缓存（按 connection_id）
- 连接测试（pymysql 直连校验）
"""

import json
import os
import uuid
from typing import Optional

from langchain_community.utilities import SQLDatabase

from app.config import get_settings
from app.database.connection import build_mysql_uri, create_sql_database, test_mysql_connection
from app.models.schemas import (
    MySQLConnectionConfig,
    MySQLConnectionCreate,
    MySQLConnectionUpdate,
    ConnectionTestResult,
    ConnectionTestRequest,
)

# ==================== 内部状态 ====================

# 连接配置列表（内存副本，定期与 JSON 文件同步）
_connections: list[dict] = []

# SQLDatabase 实例缓存：connection_id -> SQLDatabase
_db_cache: dict[str, SQLDatabase] = {}

# 是否已初始化
_initialized: bool = False


# ==================== 持久化 ====================

def _get_connections_file() -> str:
    """获取连接配置 JSON 文件路径"""
    settings = get_settings()
    file_path = settings.CONNECTIONS_FILE
    # 相对路径基于 backend 目录
    if not os.path.isabs(file_path):
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        file_path = os.path.join(backend_dir, file_path)
    return file_path


def _load_connections() -> list[dict]:
    """从 JSON 文件加载连接配置"""
    file_path = _get_connections_file()
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def _save_connections(connections: list[dict]) -> None:
    """将连接配置保存到 JSON 文件"""
    file_path = _get_connections_file()
    # 确保目录存在
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(connections, f, ensure_ascii=False, indent=2)


def _ensure_initialized() -> None:
    """确保连接配置已从磁盘加载"""
    global _connections, _initialized
    if not _initialized:
        _connections = _load_connections()
        _initialized = True


# ==================== 初始化默认连接 ====================

def init_default_connection() -> Optional[MySQLConnectionConfig]:
    """
    从 .env 配置初始化默认连接（如果尚未存在）。
    应在应用启动时调用。

    Returns:
        新创建的默认连接配置，如果已有连接则返回 None
    """
    _ensure_initialized()

    # 如果已有连接，不再自动创建
    if _connections:
        return None

    settings = get_settings()
    # 只有 host 和 database 都配置了才创建默认连接
    if not settings.MYSQL_HOST or not settings.MYSQL_DATABASE:
        return None

    config = MySQLConnectionCreate(
        name=f"默认连接 - {settings.MYSQL_DATABASE}",
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
    )
    return add_connection(config)


# ==================== CRUD ====================

def list_connections() -> list[MySQLConnectionConfig]:
    """获取所有连接配置"""
    _ensure_initialized()
    return [MySQLConnectionConfig(**conn) for conn in _connections]


def get_connection(conn_id: str) -> Optional[MySQLConnectionConfig]:
    """
    根据 ID 获取连接配置

    Args:
        conn_id: 连接 ID

    Returns:
        连接配置，不存在时返回 None
    """
    _ensure_initialized()
    for conn in _connections:
        if conn["id"] == conn_id:
            return MySQLConnectionConfig(**conn)
    return None


def add_connection(config: MySQLConnectionCreate) -> MySQLConnectionConfig:
    """
    新增连接配置

    Args:
        config: 连接创建请求

    Returns:
        带 ID 的完整连接配置
    """
    _ensure_initialized()

    conn_id = uuid.uuid4().hex[:12]
    conn_dict = {
        "id": conn_id,
        "name": config.name,
        "host": config.host,
        "port": config.port,
        "user": config.user,
        "password": config.password,
        "database": config.database,
    }
    _connections.append(conn_dict)
    _save_connections(_connections)

    return MySQLConnectionConfig(**conn_dict)


def update_connection(conn_id: str, update: MySQLConnectionUpdate) -> Optional[MySQLConnectionConfig]:
    """
    更新连接配置

    Args:
        conn_id: 连接 ID
        update: 部分更新字段

    Returns:
        更新后的连接配置，不存在时返回 None
    """
    _ensure_initialized()

    for i, conn in enumerate(_connections):
        if conn["id"] == conn_id:
            update_data = update.model_dump(exclude_unset=True)
            _connections[i].update(update_data)
            _save_connections(_connections)

            # 清除该连接的 SQLDatabase 缓存（配置已变更）
            _db_cache.pop(conn_id, None)

            return MySQLConnectionConfig(**_connections[i])

    return None


def delete_connection(conn_id: str) -> bool:
    """
    删除连接配置

    Args:
        conn_id: 连接 ID

    Returns:
        是否删除成功
    """
    _ensure_initialized()

    for i, conn in enumerate(_connections):
        if conn["id"] == conn_id:
            _connections.pop(i)
            _save_connections(_connections)

            # 清除该连接的 SQLDatabase 缓存
            _db_cache.pop(conn_id, None)

            return True

    return False


# ==================== SQLDatabase 缓存 ====================

def get_sql_database(conn_id: str) -> Optional[SQLDatabase]:
    """
    获取指定连接的 LangChain SQLDatabase 实例（带缓存）

    Args:
        conn_id: 连接 ID

    Returns:
        SQLDatabase 实例，连接不存在时返回 None
    """
    if conn_id in _db_cache:
        return _db_cache[conn_id]

    config = get_connection(conn_id)
    if config is None:
        return None

    db = create_sql_database(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
    )
    _db_cache[conn_id] = db
    return db


def clear_db_cache(conn_id: Optional[str] = None) -> None:
    """
    清除 SQLDatabase 缓存

    Args:
        conn_id: 指定连接 ID，为 None 时清除所有缓存
    """
    if conn_id:
        _db_cache.pop(conn_id, None)
    else:
        _db_cache.clear()


# ==================== 连接测试 ====================

def test_connection_by_config(config: ConnectionTestRequest) -> ConnectionTestResult:
    """
    测试连接（传入配置，不保存）

    Args:
        config: 连接测试请求

    Returns:
        ConnectionTestResult
    """
    result = test_mysql_connection(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
    )
    return ConnectionTestResult(**result)


def test_connection_by_id(conn_id: str) -> Optional[ConnectionTestResult]:
    """
    测试已保存的连接

    Args:
        conn_id: 连接 ID

    Returns:
        ConnectionTestResult，连接不存在时返回 None
    """
    config = get_connection(conn_id)
    if config is None:
        return None

    result = test_mysql_connection(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
    )
    return ConnectionTestResult(**result)
