"""
MySQL 连接管理 API
- GET    /api/connections           获取所有连接列表
- POST   /api/connections           新增连接
- PUT    /api/connections/{id}      更新连接
- DELETE /api/connections/{id}      删除连接
- POST   /api/connections/test      测试连接（不保存）
- POST   /api/connections/{id}/test 测试已保存的连接
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    MySQLConnectionConfig,
    MySQLConnectionCreate,
    MySQLConnectionUpdate,
    ConnectionTestRequest,
    ConnectionTestResult,
    ConnectionListResponse,
)
from app.services import connection_service

router = APIRouter(prefix="/api/connections", tags=["连接管理"])


@router.get("", response_model=ConnectionListResponse)
async def list_connections():
    """
    获取所有 MySQL 连接配置列表
    """
    connections = connection_service.list_connections()
    return ConnectionListResponse(connections=connections)


@router.post("", response_model=MySQLConnectionConfig, status_code=201)
async def create_connection(body: MySQLConnectionCreate):
    """
    新增 MySQL 连接配置
    """
    config = connection_service.add_connection(body)
    return config


@router.get("/{conn_id}", response_model=MySQLConnectionConfig)
async def get_connection(conn_id: str):
    """
    获取指定连接配置详情
    """
    config = connection_service.get_connection(conn_id)
    if config is None:
        raise HTTPException(status_code=404, detail=f"连接 '{conn_id}' 不存在")
    return config


@router.put("/{conn_id}", response_model=MySQLConnectionConfig)
async def update_connection(conn_id: str, body: MySQLConnectionUpdate):
    """
    更新指定连接配置（支持部分更新）
    """
    config = connection_service.update_connection(conn_id, body)
    if config is None:
        raise HTTPException(status_code=404, detail=f"连接 '{conn_id}' 不存在")
    return config


@router.delete("/{conn_id}", status_code=204)
async def delete_connection(conn_id: str):
    """
    删除指定连接配置
    """
    success = connection_service.delete_connection(conn_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"连接 '{conn_id}' 不存在")
    return None


@router.post("/test", response_model=ConnectionTestResult)
async def test_connection(body: ConnectionTestRequest):
    """
    测试 MySQL 连接（不保存，传入完整配置）
    用于新增连接前预先验证连通性
    """
    result = connection_service.test_connection_by_config(body)
    return result


@router.post("/{conn_id}/test", response_model=ConnectionTestResult)
async def test_saved_connection(conn_id: str):
    """
    测试已保存的 MySQL 连接
    用于校验现有连接是否仍然可用
    """
    result = connection_service.test_connection_by_id(conn_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"连接 '{conn_id}' 不存在")
    return result
