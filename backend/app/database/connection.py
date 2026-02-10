"""
MySQL 数据库连接工厂 + LangChain SQLDatabase 封装
替代原 SQLite 连接，支持多 MySQL 实例动态创建
"""

from urllib.parse import quote_plus
from langchain_community.utilities import SQLDatabase
from app.config import get_settings

# 兼容旧代码的默认 SQLDatabase 单例（Phase 2 中将被 connection_service 完全替代）
_default_db: SQLDatabase | None = None


def build_mysql_uri(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> str:
    """
    构建 MySQL 连接 URI（pymysql 驱动）

    Args:
        host: MySQL 主机地址
        port: MySQL 端口
        user: 用户名
        password: 密码（自动 URL 编码特殊字符）
        database: 数据库名

    Returns:
        SQLAlchemy 格式连接串，如：
        mysql+pymysql://root:pwd@localhost:3306/mydb?charset=utf8mb4
    """
    encoded_password = quote_plus(password) if password else ""
    return f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}?charset=utf8mb4"


def create_sql_database(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> SQLDatabase:
    """
    创建 LangChain SQLDatabase 实例（MySQL）

    Args:
        host: MySQL 主机地址
        port: MySQL 端口
        user: 用户名
        password: 密码
        database: 数据库名

    Returns:
        SQLDatabase 实例，已连接到指定 MySQL 数据库
    """
    uri = build_mysql_uri(host, port, user, password, database)
    return SQLDatabase.from_uri(uri)


def test_mysql_connection(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> dict:
    """
    测试 MySQL 连接，返回版本和表数量

    Args:
        host: MySQL 主机地址
        port: MySQL 端口
        user: 用户名
        password: 密码
        database: 数据库名

    Returns:
        dict: {"success": bool, "message": str, "mysql_version": str|None, "tables_count": int|None}
    """
    import pymysql

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset="utf8mb4",
            connect_timeout=5,
        )
        try:
            cursor = conn.cursor()

            # 获取 MySQL 版本
            cursor.execute("SELECT VERSION()")
            version_row = cursor.fetchone()
            mysql_version = version_row[0] if version_row else "unknown"

            # 获取表数量
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            tables_count = len(tables)

            return {
                "success": True,
                "message": f"连接成功 - MySQL {mysql_version}，共 {tables_count} 张表",
                "mysql_version": mysql_version,
                "tables_count": tables_count,
            }
        finally:
            conn.close()

    except pymysql.err.OperationalError as e:
        code, msg = e.args if len(e.args) == 2 else (0, str(e))
        if code == 1045:
            return {"success": False, "message": f"认证失败：用户名或密码错误 ({msg})", "mysql_version": None, "tables_count": None}
        elif code == 2003:
            return {"success": False, "message": f"无法连接到 {host}:{port}，请检查地址和端口 ({msg})", "mysql_version": None, "tables_count": None}
        elif code == 1049:
            return {"success": False, "message": f"数据库 '{database}' 不存在 ({msg})", "mysql_version": None, "tables_count": None}
        else:
            return {"success": False, "message": f"连接失败：{msg}", "mysql_version": None, "tables_count": None}
    except Exception as e:
        return {"success": False, "message": f"连接异常：{str(e)}", "mysql_version": None, "tables_count": None}


# ==================== 兼容旧代码 ====================

def get_db() -> SQLDatabase:
    """
    获取默认 MySQL SQLDatabase 单例（兼容旧代码，Phase 2 将移除）

    使用 .env 中的 MYSQL_* 配置创建连接

    Returns:
        SQLDatabase 实例
    """
    global _default_db
    if _default_db is None:
        settings = get_settings()
        _default_db = create_sql_database(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
        )
    return _default_db
