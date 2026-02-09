"""
SQL Agent 服务层
基于 LangChain v1 create_agent + SQLDatabaseToolkit + InMemorySaver
基于 playground/test_nl2sql.py 实测验证
"""

from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver

from app.services.llm_service import get_llm
from app.database.connection import get_db

# 全局单例
_agent = None
_checkpointer = None

SYSTEM_PROMPT = """你是一个专业的 SQL 数据库查询助手，负责帮助用户通过自然语言查询数据库。

规则：
1. 首先使用 sql_db_list_tables 查看数据库有哪些表
2. 使用 sql_db_schema 查看相关表的结构和示例数据
3. 根据用户问题生成正确的 {dialect} SQL 查询
4. 使用 sql_db_query_checker 校验 SQL 语法
5. 使用 sql_db_query 执行查询
6. 用中文总结查询结果，回答要清晰、有条理
7. 在回答末尾附上执行的 SQL 语句（用 ```sql 代码块包裹）

限制：
- 查询最多返回 {top_k} 条结果
- 绝对不允许执行 INSERT、UPDATE、DELETE、DROP 等修改操作
- 如果查询出错，分析错误原因并重写查询重试
- 不确定时，先查表结构再生成查询"""


def get_agent():
    """
    获取 SQL Agent 单例

    Returns:
        create_agent 创建的 CompiledStateGraph 实例
    """
    global _agent, _checkpointer

    if _agent is None:
        llm = get_llm()
        db = get_db()

        # 创建工具集
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()

        # 创建 checkpointer（用于多轮对话记忆）
        _checkpointer = InMemorySaver()

        # 构建 system prompt
        prompt = SYSTEM_PROMPT.format(
            dialect=db.dialect,
            top_k=10,
        )

        # 创建 Agent
        _agent = create_agent(
            llm,
            tools,
            system_prompt=prompt,
            checkpointer=_checkpointer,
        )

    return _agent


def get_checkpointer():
    """获取 checkpointer 实例"""
    global _checkpointer
    if _checkpointer is None:
        get_agent()  # 确保初始化
    return _checkpointer
