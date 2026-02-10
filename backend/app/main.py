from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import session, chat, database, connection
from app.services.connection_service import init_default_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化默认 MySQL 连接"""
    default_conn = init_default_connection()
    if default_conn:
        print(f"[启动] 已创建默认 MySQL 连接: {default_conn.name} ({default_conn.host}:{default_conn.port}/{default_conn.database})")
    else:
        print("[启动] 已有连接配置或未配置 MySQL 默认参数，跳过默认连接创建")
    yield


app = FastAPI(
    title="NL2SQL 智能数据分析系统",
    description="基于自然语言查询 MySQL 数据库并自动生成可视化图表",
    version="1.0.0-mysql",
    lifespan=lifespan,
)

# CORS 配置 - 允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(connection.router)
app.include_router(session.router)
app.include_router(chat.router)
app.include_router(database.router)


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "nl2sql-backend", "version": "1.0.0-mysql"}
