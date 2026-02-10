"""
数据库工具 API（MySQL 版本 - Phase2）
- GET  /api/database/schema?connection_id=xxx  — 获取指定连接的所有表结构
- POST /api/database/query                     — 在指定连接上执行 SQL 查询（仅 SELECT，带分页）
"""

import math
import re
import time

import pymysql
from fastapi import APIRouter, HTTPException, Query

from app.services import connection_service
from app.models.schemas import (
    ColumnInfo,
    TableSchema,
    SchemaResponse,
    SqlQueryRequest,
    SqlQueryResponse,
)

router = APIRouter(prefix="/api/database", tags=["数据库工具"])

# 禁止的 SQL 关键词（仅允许 SELECT）
_FORBIDDEN_KEYWORDS = re.compile(
    r"^\s*(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE)\b",
    re.IGNORECASE,
)


def _get_mysql_connection_by_id(connection_id: str) -> pymysql.Connection:
    """
    根据 connection_id 获取原生 pymysql 连接
    """
    config = connection_service.get_connection(connection_id)
    if config is None:
        raise HTTPException(status_code=404, detail=f"连接 '{connection_id}' 不存在")

    try:
        return pymysql.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
            charset="utf8mb4",
            connect_timeout=10,
        )
    except pymysql.Error as e:
        raise HTTPException(status_code=503, detail=f"无法连接到数据库: {str(e)}")


@router.get("/schema", response_model=SchemaResponse)
async def get_schema(connection_id: str = Query(..., description="MySQL 连接 ID")):
    """
    获取指定连接的数据库所有表结构信息（表名 + 列定义）
    """
    conn = _get_mysql_connection_by_id(connection_id)
    try:
        cursor = conn.cursor()

        # 获取所有用户表
        cursor.execute("SHOW TABLES")
        table_names = [row[0] for row in cursor.fetchall()]

        tables: list[TableSchema] = []
        for table_name in table_names:
            cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")
            columns: list[ColumnInfo] = []
            for col_row in cursor.fetchall():
                # SHOW FULL COLUMNS 返回:
                # (Field, Type, Collation, Null, Key, Default, Extra, Privileges, Comment)
                columns.append(ColumnInfo(
                    name=col_row[0],
                    type=col_row[1] or "VARCHAR(255)",
                    primary_key=(col_row[4] == "PRI"),
                    nullable=(col_row[3] == "YES"),
                ))
            tables.append(TableSchema(name=table_name, columns=columns))

        return SchemaResponse(tables=tables)
    finally:
        conn.close()


@router.post("/query", response_model=SqlQueryResponse)
async def execute_query(body: SqlQueryRequest):
    """
    在指定连接上执行用户 SQL 查询（仅允许 SELECT），返回分页结果。
    """
    sql = body.sql.strip()

    # 安全校验：仅允许 SELECT
    if not sql.upper().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="仅允许 SELECT 查询语句")

    if _FORBIDDEN_KEYWORDS.match(sql):
        raise HTTPException(status_code=400, detail="不允许执行写操作语句")

    conn = _get_mysql_connection_by_id(body.connection_id)
    try:
        cursor = conn.cursor()
        start_time = time.time()

        # 1. 获取总行数
        count_sql = f"SELECT COUNT(*) FROM ({sql}) AS _count_subquery"
        try:
            cursor.execute(count_sql)
            total_count = cursor.fetchone()[0]
        except pymysql.Error as e:
            raise HTTPException(status_code=400, detail=f"SQL 执行错误: {str(e)}")

        # 2. 计算分页
        total_pages = max(1, math.ceil(total_count / body.page_size))
        offset = (body.page - 1) * body.page_size

        # 3. 获取分页数据
        paged_sql = f"SELECT * FROM ({sql}) AS _paged_subquery LIMIT {body.page_size} OFFSET {offset}"
        try:
            cursor.execute(paged_sql)
            rows_raw = cursor.fetchall()
            # 获取列名
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
        except pymysql.Error as e:
            raise HTTPException(status_code=400, detail=f"SQL 执行错误: {str(e)}")

        elapsed_ms = int((time.time() - start_time) * 1000)

        # 转换行数据为可序列化列表
        rows = [list(row) for row in rows_raw]

        return SqlQueryResponse(
            columns=columns,
            rows=rows,
            total_count=total_count,
            page=body.page,
            page_size=body.page_size,
            total_pages=total_pages,
            elapsed_ms=elapsed_ms,
        )
    finally:
        conn.close()
