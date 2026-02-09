"""
数据库工具 API
- GET  /api/database/schema  — 获取所有表结构
- POST /api/database/query   — 执行 SQL 查询（仅 SELECT，带分页）
"""

import math
import re
import sqlite3
import time

from fastapi import APIRouter, HTTPException

from app.database.connection import get_db_path
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
    r"^\s*(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|ATTACH|DETACH|PRAGMA)\b",
    re.IGNORECASE,
)


def _get_raw_connection() -> sqlite3.Connection:
    """获取原生 sqlite3 连接（绕过 LangChain SQLDatabase 的只读限制）"""
    db_path = get_db_path()
    return sqlite3.connect(db_path)


@router.get("/schema", response_model=SchemaResponse)
async def get_schema():
    """
    获取数据库所有表的结构信息（表名 + 列定义）
    """
    conn = _get_raw_connection()
    try:
        cursor = conn.cursor()

        # 获取所有用户表
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        table_names = [row[0] for row in cursor.fetchall()]

        tables: list[TableSchema] = []
        for table_name in table_names:
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns: list[ColumnInfo] = []
            for col_row in cursor.fetchall():
                # PRAGMA table_info 返回: (cid, name, type, notnull, dflt_value, pk)
                columns.append(ColumnInfo(
                    name=col_row[1],
                    type=col_row[2] or "TEXT",
                    primary_key=bool(col_row[5]),
                    nullable=not bool(col_row[3]),
                ))
            tables.append(TableSchema(name=table_name, columns=columns))

        return SchemaResponse(tables=tables)
    finally:
        conn.close()


@router.post("/query", response_model=SqlQueryResponse)
async def execute_query(body: SqlQueryRequest):
    """
    执行用户 SQL 查询（仅允许 SELECT），返回分页结果。
    """
    sql = body.sql.strip()

    # 安全校验：仅允许 SELECT
    if not sql.upper().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="仅允许 SELECT 查询语句")

    if _FORBIDDEN_KEYWORDS.match(sql):
        raise HTTPException(status_code=400, detail="不允许执行写操作语句")

    conn = _get_raw_connection()
    try:
        cursor = conn.cursor()
        start_time = time.time()

        # 1. 获取总行数
        count_sql = f"SELECT COUNT(*) FROM ({sql})"
        try:
            cursor.execute(count_sql)
            total_count = cursor.fetchone()[0]
        except sqlite3.Error as e:
            raise HTTPException(status_code=400, detail=f"SQL 执行错误: {str(e)}")

        # 2. 计算分页
        total_pages = max(1, math.ceil(total_count / body.page_size))
        offset = (body.page - 1) * body.page_size

        # 3. 获取分页数据
        paged_sql = f"SELECT * FROM ({sql}) LIMIT {body.page_size} OFFSET {offset}"
        try:
            cursor.execute(paged_sql)
            rows_raw = cursor.fetchall()
            # 获取列名
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
        except sqlite3.Error as e:
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
