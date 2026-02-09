"""
Pydantic 数据模型（请求/响应验证）
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


# ===== 会话相关 =====

class SessionCreate(BaseModel):
    """创建会话请求"""
    title: Optional[str] = Field(default=None, description="会话标题，不传则自动生成")


class SessionUpdate(BaseModel):
    """更新会话请求"""
    title: str = Field(..., description="新的会话标题")


class MessageItem(BaseModel):
    """单条消息"""
    role: str = Field(..., description="消息角色: user / assistant")
    content: str = Field(..., description="消息内容")
    timestamp: str = Field(..., description="时间戳")


class SessionResponse(BaseModel):
    """会话响应"""
    id: str = Field(..., description="会话 ID")
    title: str = Field(..., description="会话标题")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    message_count: int = Field(default=0, description="消息数量")


class SessionDetailResponse(SessionResponse):
    """会话详情响应（含消息列表）"""
    messages: list[MessageItem] = Field(default_factory=list, description="消息列表")


# ===== 聊天相关 =====

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, description="用户消息内容")


# ===== 图表相关 =====

class ChartData(BaseModel):
    """图表数据"""
    chart_type: str = Field(..., description="图表类型: bar/line/pie/table")
    echarts_option: Optional[dict[str, Any]] = Field(default=None, description="ECharts 配置项")
    table_data: Optional[dict[str, Any]] = Field(default=None, description="表格数据 {columns, rows}")


# ===== 数据库工具相关 =====

class ColumnInfo(BaseModel):
    """表列信息"""
    name: str = Field(..., description="列名")
    type: str = Field(..., description="列类型")
    primary_key: bool = Field(default=False, description="是否为主键")
    nullable: bool = Field(default=True, description="是否可为空")


class TableSchema(BaseModel):
    """单表结构"""
    name: str = Field(..., description="表名")
    columns: list[ColumnInfo] = Field(default_factory=list, description="列列表")


class SchemaResponse(BaseModel):
    """数据库 schema 响应"""
    tables: list[TableSchema] = Field(default_factory=list, description="所有表")


class SqlQueryRequest(BaseModel):
    """SQL 查询请求"""
    sql: str = Field(..., min_length=1, description="SQL 查询语句（仅允许 SELECT）")
    page: int = Field(default=1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(default=50, ge=1, le=500, description="每页条数")


class SqlQueryResponse(BaseModel):
    """SQL 查询响应（分页）"""
    columns: list[str] = Field(default_factory=list, description="列名列表")
    rows: list[list[Any]] = Field(default_factory=list, description="行数据")
    total_count: int = Field(default=0, description="总行数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=50, description="每页条数")
    total_pages: int = Field(default=0, description="总页数")
    elapsed_ms: int = Field(default=0, description="执行耗时（毫秒）")


# ===== 通用 =====

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(default=None, description="详细错误")
