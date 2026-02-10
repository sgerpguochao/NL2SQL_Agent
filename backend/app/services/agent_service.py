"""
SQL Agent 服务层（MySQL 版本 - Phase2）
基于 LangChain create_agent + SQLDatabaseToolkit + InMemorySaver
按 connection_id 管理独立的 Agent 实例和 Checkpointer
"""

from typing import Any

from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver

from app.services.llm_service import get_llm
from app.services import connection_service

# 按 connection_id 缓存 Agent 和 Checkpointer
_agents: dict[str, Any] = {}
_checkpointers: dict[str, InMemorySaver] = {}

SYSTEM_PROMPT = """你是一个专业的 SQL 数据库查询助手，负责帮助用户通过自然语言查询数据库。

规则：
1. 首先使用 sql_db_list_tables 查看数据库有哪些表
2. 使用 sql_db_schema 查看相关表的结构和示例数据
3. 根据用户问题生成正确的 MySQL SQL 查询
4. 使用 sql_db_query_checker 校验 SQL 语法
5. 使用 sql_db_query 执行查询
6. 用中文总结查询结果，回答要清晰、有条理
7. 在回答末尾附上执行的 SQL 语句（用 ```sql 代码块包裹）

限制：
- 查询最多返回 {top_k} 条结果
- 绝对不允许执行 INSERT、UPDATE、DELETE、DROP 等修改操作
- 如果查询出错，分析错误原因并重写查询重试
- 不确定时，先查表结构再生成查询"""


def get_agent(connection_id: str):
    """
    获取指定连接的 SQL Agent（带缓存）

    Args:
        connection_id: MySQL 连接 ID

    Returns:
        create_agent 创建的 CompiledStateGraph 实例

    Raises:
        ValueError: 连接 ID 不存在或无法连接
    """
    if connection_id in _agents:
        return _agents[connection_id]

    # 获取 SQLDatabase 实例
    db = connection_service.get_sql_database(connection_id)
    if db is None:
        raise ValueError(f"连接 '{connection_id}' 不存在或无法获取数据库实例")

    llm = get_llm()

    # 创建工具集
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    # 创建 checkpointer（用于多轮对话记忆）
    checkpointer = InMemorySaver()

    # 构建 system prompt
    prompt = SYSTEM_PROMPT.format(top_k=10)

    # 创建 Agent
    agent = create_agent(
        llm,
        tools,
        system_prompt=prompt,
        checkpointer=checkpointer,
    )

    _agents[connection_id] = agent
    _checkpointers[connection_id] = checkpointer

    return agent


def get_checkpointer(connection_id: str) -> InMemorySaver:
    """
    获取指定连接的 checkpointer 实例

    Args:
        connection_id: MySQL 连接 ID
    """
    if connection_id not in _checkpointers:
        get_agent(connection_id)  # 确保初始化
    return _checkpointers[connection_id]


def clear_agent_cache(connection_id: str = None) -> None:
    """
    清除 Agent 缓存（连接配置变更时应调用）

    Args:
        connection_id: 指定连接 ID，为 None 时清除所有缓存
    """
    if connection_id:
        _agents.pop(connection_id, None)
        _checkpointers.pop(connection_id, None)
    else:
        _agents.clear()
        _checkpointers.clear()
