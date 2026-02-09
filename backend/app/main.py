from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import session, chat, database
from app.database.sample_data import init_sample_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化示例数据库"""
    initialized = init_sample_database()
    if initialized:
        print("[启动] 示例数据库初始化完成")
    else:
        print("[启动] 示例数据库已存在，跳过初始化")
    yield


app = FastAPI(
    title="NL2SQL 智能数据分析系统",
    description="基于自然语言查询数据库并自动生成可视化图表",
    version="0.2.0",
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
app.include_router(session.router)
app.include_router(chat.router)
app.include_router(database.router)


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "nl2sql-backend", "version": "0.2.0"}
