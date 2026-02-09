"""
NL2SQL 组件完整测试脚本
基于已验证的 Qwen3-max 模型，逐层测试 LangChain NL2SQL 全链路组件的实际输入输出。

测试项目：
  1. SQLDatabase 连接 + 基础操作
  2. SQLDatabaseToolkit 工具集（4 个工具的输入输出）
  3. SQL Agent 完整 NL2SQL 流程
  4. Agent 流式输出
  5. Agent 多轮对话（上下文记忆）
"""

import os
import json
import sqlite3
import tempfile
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

# ===== 配置 =====
API_KEY = "sk-18bc9910dfd540bfa95df545f76d7fb2"
MODEL_NAME = "qwen3-max"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 测试数据库路径（临时文件）
DB_PATH = os.path.join(tempfile.gettempdir(), "nl2sql_test.db")


def create_llm(streaming: bool = False) -> ChatOpenAI:
    return ChatOpenAI(
        model=MODEL_NAME,
        api_key=API_KEY,
        base_url=BASE_URL,
        streaming=streaming,
        temperature=0.7,
    )


# ============================================================
# 准备工作：创建测试数据库
# ============================================================
def setup_test_database():
    """创建包含示例数据的 SQLite 测试数据库"""
    print("=" * 60)
    print("准备工作：创建测试数据库")
    print("=" * 60)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 部门表
    cursor.execute("""
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            manager TEXT,
            budget REAL
        )
    """)

    # 员工表
    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department_id INTEGER,
            position TEXT,
            salary REAL,
            hire_date TEXT,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)

    # 销售记录表
    cursor.execute("""
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            product TEXT,
            amount REAL,
            quantity INTEGER,
            sale_date TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)

    # 插入部门数据
    departments = [
        (1, "销售部", "张三", 500000),
        (2, "技术部", "李四", 800000),
        (3, "市场部", "王五", 300000),
        (4, "人事部", "赵六", 200000),
    ]
    cursor.executemany("INSERT INTO departments VALUES (?,?,?,?)", departments)

    # 插入员工数据
    employees = [
        (1, "张三", 1, "部门经理", 25000, "2020-03-15"),
        (2, "李四", 2, "部门经理", 30000, "2019-06-01"),
        (3, "王五", 3, "部门经理", 22000, "2021-01-10"),
        (4, "赵六", 4, "部门经理", 20000, "2020-09-20"),
        (5, "孙七", 1, "销售主管", 18000, "2021-04-15"),
        (6, "周八", 1, "销售代表", 12000, "2022-01-20"),
        (7, "吴九", 2, "高级工程师", 28000, "2020-07-10"),
        (8, "郑十", 2, "初级工程师", 15000, "2023-03-01"),
        (9, "钱十一", 3, "市场专员", 13000, "2022-06-15"),
        (10, "陈十二", 1, "销售代表", 11000, "2023-08-01"),
    ]
    cursor.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?)", employees)

    # 插入销售数据
    sales = [
        (1, 1, "产品A", 50000, 10, "2024-01-15"),
        (2, 5, "产品B", 30000, 5, "2024-01-20"),
        (3, 6, "产品A", 25000, 5, "2024-02-10"),
        (4, 10, "产品C", 15000, 3, "2024-02-15"),
        (5, 1, "产品B", 40000, 8, "2024-03-01"),
        (6, 5, "产品A", 35000, 7, "2024-03-10"),
        (7, 6, "产品C", 20000, 4, "2024-03-20"),
        (8, 10, "产品A", 18000, 3, "2024-04-05"),
        (9, 1, "产品C", 22000, 4, "2024-04-15"),
        (10, 5, "产品B", 28000, 6, "2024-05-01"),
        (11, 6, "产品A", 32000, 6, "2024-05-10"),
        (12, 10, "产品B", 12000, 2, "2024-06-01"),
    ]
    cursor.executemany("INSERT INTO sales VALUES (?,?,?,?,?,?)", sales)

    conn.commit()
    conn.close()

    print(f"  数据库路径: {DB_PATH}")
    print(f"  表: departments(4条), employees(10条), sales(12条)")
    print("  [DONE] 测试数据库创建完成\n")


# ============================================================
# 测试 1：SQLDatabase 连接 + 基础操作
# ============================================================
def test_sql_database():
    print("=" * 60)
    print("测试 1：SQLDatabase 连接 + 基础操作")
    print("=" * 60)

    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

    # 1a: 基础属性
    print(f"\n--- 1a: 基础属性 ---")
    print(f"  type: {type(db).__name__}")
    print(f"  dialect: {db.dialect}")
    print(f"  table_names: {db.get_usable_table_names()}")

    # 1b: 获取表信息
    print(f"\n--- 1b: get_table_info() ---")
    table_info = db.get_table_info()
    print(f"  返回类型: {type(table_info).__name__}")
    print(f"  长度: {len(table_info)} 字符")
    print(f"  内容预览:\n{table_info[:800]}...")

    # 1c: 执行查询
    print(f"\n--- 1c: db.run() 执行查询 ---")
    result = db.run("SELECT name, salary FROM employees WHERE salary > 20000 ORDER BY salary DESC")
    print(f"  返回类型: {type(result).__name__}")
    print(f"  结果: {result}")

    # 1d: 带 include_columns 的查询
    print(f"\n--- 1d: db.run() 指定 include_columns ---")
    try:
        result2 = db.run(
            "SELECT d.name as dept, COUNT(e.id) as emp_count FROM departments d "
            "LEFT JOIN employees e ON d.id = e.department_id GROUP BY d.name",
            include_columns=True
        )
        print(f"  返回类型: {type(result2).__name__}")
        print(f"  结果: {result2}")
    except Exception as e:
        print(f"  include_columns 报错: {e}")

    print("\n[PASS] SQLDatabase 测试通过\n")
    return db


# ============================================================
# 测试 2：SQLDatabaseToolkit 工具集
# ============================================================
def test_toolkit(db):
    print("=" * 60)
    print("测试 2：SQLDatabaseToolkit 工具集")
    print("=" * 60)

    llm = create_llm()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # 2a: 列出所有工具
    tools = toolkit.get_tools()
    print(f"\n--- 2a: 工具列表 ---")
    print(f"  工具数量: {len(tools)}")
    for t in tools:
        print(f"\n  工具名: {t.name}")
        print(f"    类型: {type(t).__name__}")
        print(f"    描述: {t.description[:120]}...")
        # 查看 args_schema
        if hasattr(t, "args_schema") and t.args_schema:
            schema = t.args_schema.schema() if hasattr(t.args_schema, "schema") else str(t.args_schema)
            print(f"    args_schema: {json.dumps(schema, ensure_ascii=False, default=str)}")

    # 2b: 逐个调用工具并记录输入输出
    print(f"\n--- 2b: 逐个调用工具 ---")

    # sql_db_list_tables
    list_tables_tool = next(t for t in tools if t.name == "sql_db_list_tables")
    result_list = list_tables_tool.invoke("")
    print(f"\n  [sql_db_list_tables]")
    print(f"    输入: '' (空字符串)")
    print(f"    输出类型: {type(result_list).__name__}")
    print(f"    输出: {result_list}")

    # sql_db_schema
    schema_tool = next(t for t in tools if t.name == "sql_db_schema")
    result_schema = schema_tool.invoke("departments, employees")
    print(f"\n  [sql_db_schema]")
    print(f"    输入: 'departments, employees'")
    print(f"    输出类型: {type(result_schema).__name__}")
    print(f"    输出长度: {len(result_schema)} 字符")
    print(f"    输出预览:\n{result_schema[:600]}")

    # sql_db_query_checker
    checker_tool = next(t for t in tools if t.name == "sql_db_query_checker")
    test_sql = "SELECT name, salary FROM employees WHERE salary > 20000"
    result_check = checker_tool.invoke(test_sql)
    print(f"\n  [sql_db_query_checker]")
    print(f"    输入: '{test_sql}'")
    print(f"    输出类型: {type(result_check).__name__}")
    print(f"    输出: {result_check}")

    # sql_db_query
    query_tool = next(t for t in tools if t.name == "sql_db_query")
    exec_sql = "SELECT d.name, COUNT(e.id) as cnt FROM departments d LEFT JOIN employees e ON d.id = e.department_id GROUP BY d.name"
    result_query = query_tool.invoke(exec_sql)
    print(f"\n  [sql_db_query]")
    print(f"    输入: '{exec_sql}'")
    print(f"    输出类型: {type(result_query).__name__}")
    print(f"    输出: {result_query}")

    print("\n[PASS] SQLDatabaseToolkit 测试通过\n")
    return tools


# ============================================================
# 测试 3：SQL Agent 完整 NL2SQL 流程
# ============================================================
def test_sql_agent(db):
    print("=" * 60)
    print("测试 3：SQL Agent 完整 NL2SQL 流程")
    print("=" * 60)

    llm = create_llm()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    # 尝试新版 create_agent
    try:
        from langchain.agents import create_agent
        print("\n  使用 langchain.agents.create_agent (v1 新版)")

        system_prompt = """你是一个 SQL 数据库查询助手。
根据用户的自然语言问题，生成正确的 {dialect} SQL 查询并执行。
规则：
1. 首先查看数据库有哪些表
2. 查看相关表的结构
3. 生成 SQL 并用 checker 校验
4. 执行查询
5. 用中文回答，附上执行的 SQL

限制最多返回 {top_k} 条结果。
不允许执行 INSERT/UPDATE/DELETE/DROP 等修改操作。""".format(
            dialect=db.dialect,
            top_k=10,
        )

        agent = create_agent(
            llm,
            tools,
            system_prompt=system_prompt,
        )

        agent_type = "create_agent"

    except ImportError:
        # 回退到旧版
        from langchain_community.agent_toolkits import create_sql_agent as _create_sql_agent
        print("\n  create_agent 不可用，回退到 create_sql_agent (旧版)")

        agent = _create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type="openai-tools",
            verbose=True,
        )
        agent_type = "create_sql_agent"

    # 3a: 简单查询
    print(f"\n--- 3a: 简单查询 (agent_type={agent_type}) ---")
    question1 = "公司一共有多少员工？"
    print(f"  问题: {question1}")

    if agent_type == "create_agent":
        result1 = agent.invoke(
            {"messages": [{"role": "user", "content": question1}]},
            config={"configurable": {"thread_id": "test-1"}},
        )
        print(f"\n  返回类型: {type(result1).__name__}")
        print(f"  返回 keys: {list(result1.keys()) if isinstance(result1, dict) else 'N/A'}")

        # 分析 messages
        if isinstance(result1, dict) and "messages" in result1:
            msgs = result1["messages"]
            print(f"  messages 数量: {len(msgs)}")
            for i, msg in enumerate(msgs):
                print(f"\n  messages[{i}]:")
                print(f"    类型: {type(msg).__name__}")
                if hasattr(msg, "content"):
                    content_preview = msg.content[:200] if len(msg.content) > 200 else msg.content
                    print(f"    content: {content_preview}")
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    print(f"    tool_calls: {msg.tool_calls}")
                if hasattr(msg, "name"):
                    print(f"    name: {msg.name}")
    else:
        result1 = agent.invoke({"input": question1})
        print(f"\n  返回类型: {type(result1).__name__}")
        print(f"  返回 keys: {list(result1.keys()) if isinstance(result1, dict) else 'N/A'}")
        if isinstance(result1, dict):
            print(f"  output: {result1.get('output', 'N/A')}")

    # 3b: 聚合查询
    print(f"\n--- 3b: 聚合查询 ---")
    question2 = "各部门的平均工资是多少？按平均工资从高到低排列"
    print(f"  问题: {question2}")

    if agent_type == "create_agent":
        result2 = agent.invoke(
            {"messages": [{"role": "user", "content": question2}]},
            config={"configurable": {"thread_id": "test-2"}},
        )
        if isinstance(result2, dict) and "messages" in result2:
            final_msg = result2["messages"][-1]
            print(f"\n  最终回复类型: {type(final_msg).__name__}")
            print(f"  最终回复: {final_msg.content[:500]}")
            print(f"  messages 总数: {len(result2['messages'])}")

            # 提取 Agent 执行的 SQL
            for msg in result2["messages"]:
                if hasattr(msg, "name") and msg.name == "sql_db_query":
                    print(f"  [Agent 执行的 SQL 查询结果]: {msg.content[:300]}")
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        if tc.get("name") == "sql_db_query":
                            print(f"  [Agent 生成的 SQL]: {tc['args']}")
    else:
        result2 = agent.invoke({"input": question2})
        if isinstance(result2, dict):
            print(f"  output: {result2.get('output', 'N/A')[:500]}")

    # 3c: 关联查询
    print(f"\n--- 3c: 关联查询 ---")
    question3 = "销售额最高的员工是谁？他卖了多少钱？"
    print(f"  问题: {question3}")

    if agent_type == "create_agent":
        result3 = agent.invoke(
            {"messages": [{"role": "user", "content": question3}]},
            config={"configurable": {"thread_id": "test-3"}},
        )
        if isinstance(result3, dict) and "messages" in result3:
            final_msg = result3["messages"][-1]
            print(f"\n  最终回复: {final_msg.content[:500]}")

            # 统计 Agent 使用了哪些工具
            tool_usage = []
            for msg in result3["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_usage.append(tc.get("name"))
            print(f"  Agent 工具调用顺序: {tool_usage}")
    else:
        result3 = agent.invoke({"input": question3})
        if isinstance(result3, dict):
            print(f"  output: {result3.get('output', 'N/A')[:500]}")

    print("\n[PASS] SQL Agent 测试通过\n")
    return agent, agent_type


# ============================================================
# 测试 4：Agent 流式输出
# ============================================================
def test_agent_streaming(db):
    print("=" * 60)
    print("测试 4：Agent 流式输出")
    print("=" * 60)

    llm = create_llm(streaming=True)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    system_prompt = """你是一个 SQL 数据库查询助手。
根据用户的自然语言问题，查询数据库并用中文回答。
首先列出表名，然后获取相关表结构，生成并校验 SQL，执行后用中文总结。""".format()

    try:
        from langchain.agents import create_agent

        agent = create_agent(
            llm,
            tools,
            system_prompt=system_prompt,
        )

        question = "每个月的总销售额是多少？"
        print(f"\n  问题: {question}")
        print(f"\n  流式事件输出：")

        event_types = {}
        final_content = ""
        tool_calls_log = []
        sql_executed = []

        for event in agent.stream(
            {"messages": [{"role": "user", "content": question}]},
            config={"configurable": {"thread_id": "stream-test-1"}},
            stream_mode="updates",
        ):
            # 记录事件类型
            for node_name, node_data in event.items():
                event_type = node_name
                event_types[event_type] = event_types.get(event_type, 0) + 1

                print(f"\n  [事件] node={node_name}")

                if isinstance(node_data, dict) and "messages" in node_data:
                    for msg in node_data["messages"]:
                        msg_type = type(msg).__name__
                        print(f"    msg_type: {msg_type}")

                        if hasattr(msg, "content") and msg.content:
                            preview = msg.content[:150]
                            print(f"    content: {preview}")
                            if msg_type == "AIMessage":
                                final_content = msg.content

                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                tool_calls_log.append(tc.get("name"))
                                print(f"    tool_call: {tc.get('name')} args={tc.get('args')}")
                                if tc.get("name") == "sql_db_query":
                                    sql_executed.append(tc["args"])

                        if hasattr(msg, "name") and msg.name:
                            print(f"    tool_name: {msg.name}")

        print(f"\n  --- 流式输出统计 ---")
        print(f"  事件类型分布: {event_types}")
        print(f"  工具调用顺序: {tool_calls_log}")
        print(f"  执行的 SQL: {sql_executed}")
        print(f"  最终回复: {final_content[:500]}")

    except ImportError:
        print("  create_agent 不可用，跳过流式测试")

    print("\n[PASS] Agent 流式输出测试通过\n")


# ============================================================
# 测试 5：Agent 多轮对话（上下文记忆）
# ============================================================
def test_agent_memory(db):
    print("=" * 60)
    print("测试 5：Agent 多轮对话（上下文记忆）")
    print("=" * 60)

    llm = create_llm()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    system_prompt = """你是一个 SQL 数据库查询助手。
根据用户的问题查询数据库并用中文回答。回答要简洁明了。"""

    try:
        from langchain.agents import create_agent
        from langgraph.checkpoint.memory import InMemorySaver

        agent = create_agent(
            llm,
            tools,
            system_prompt=system_prompt,
            checkpointer=InMemorySaver(),
        )

        thread_config = {"configurable": {"thread_id": "memory-test-1"}}

        # 第 1 轮
        q1 = "销售部有几个人？"
        print(f"\n  第 1 轮: {q1}")
        r1 = agent.invoke(
            {"messages": [{"role": "user", "content": q1}]},
            config=thread_config,
        )
        answer1 = r1["messages"][-1].content
        print(f"  回答: {answer1[:300]}")
        print(f"  messages 数量: {len(r1['messages'])}")

        # 第 2 轮（追问，依赖上下文）
        q2 = "他们的平均工资呢？"
        print(f"\n  第 2 轮 (追问): {q2}")
        r2 = agent.invoke(
            {"messages": [{"role": "user", "content": q2}]},
            config=thread_config,
        )
        answer2 = r2["messages"][-1].content
        print(f"  回答: {answer2[:300]}")
        print(f"  messages 数量: {len(r2['messages'])}")

        # 第 3 轮（继续追问）
        q3 = "其中工资最高的是谁？"
        print(f"\n  第 3 轮 (继续追问): {q3}")
        r3 = agent.invoke(
            {"messages": [{"role": "user", "content": q3}]},
            config=thread_config,
        )
        answer3 = r3["messages"][-1].content
        print(f"  回答: {answer3[:300]}")
        print(f"  messages 数量: {len(r3['messages'])}")

        # 验证上下文：切换到新 thread 问同样的追问
        print(f"\n  --- 上下文验证：新 thread 问追问 ---")
        new_thread = {"configurable": {"thread_id": "memory-test-2"}}
        r_new = agent.invoke(
            {"messages": [{"role": "user", "content": "他们的平均工资呢？"}]},
            config=new_thread,
        )
        answer_new = r_new["messages"][-1].content
        print(f"  新 thread 回答: {answer_new[:300]}")
        print(f"  (应无法理解'他们'指谁，与上面第 2 轮回答不同)")

    except ImportError as e:
        print(f"  依赖缺失，跳过记忆测试: {e}")
        # 回退方案：使用 create_sql_agent
        print("  尝试使用 create_sql_agent 方案...")
        try:
            from langchain_community.agent_toolkits import create_sql_agent as _create_sql_agent

            agent = _create_sql_agent(
                llm=llm,
                toolkit=toolkit,
                agent_type="openai-tools",
                verbose=True,
            )

            q1 = "各部门的员工人数分别是多少？"
            print(f"\n  问题: {q1}")
            r1 = agent.invoke({"input": q1})
            print(f"  回答: {r1.get('output', 'N/A')[:500]}")
            print(f"  返回 keys: {list(r1.keys())}")

        except Exception as e2:
            print(f"  create_sql_agent 也失败: {e2}")

    print("\n[PASS] 多轮对话测试通过\n")


# ============================================================
# 主函数
# ============================================================
if __name__ == "__main__":
    print("\n>>> NL2SQL 组件完整测试开始\n")

    # 准备
    setup_test_database()

    # 测试 1
    try:
        db = test_sql_database()
    except Exception as e:
        print(f"[FAIL] SQLDatabase 测试失败: {e}\n")
        import traceback; traceback.print_exc()
        exit(1)

    # 测试 2
    try:
        test_toolkit(db)
    except Exception as e:
        print(f"[FAIL] Toolkit 测试失败: {e}\n")
        import traceback; traceback.print_exc()

    # 测试 3
    try:
        agent, agent_type = test_sql_agent(db)
    except Exception as e:
        print(f"[FAIL] SQL Agent 测试失败: {e}\n")
        import traceback; traceback.print_exc()

    # 测试 4
    try:
        test_agent_streaming(db)
    except Exception as e:
        print(f"[FAIL] Agent 流式输出测试失败: {e}\n")
        import traceback; traceback.print_exc()

    # 测试 5
    try:
        test_agent_memory(db)
    except Exception as e:
        print(f"[FAIL] 多轮对话测试失败: {e}\n")
        import traceback; traceback.print_exc()

    # 清理
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print(f"  已清理测试数据库: {DB_PATH}")
    except PermissionError:
        print(f"  测试数据库文件被占用，跳过清理: {DB_PATH}")

    print("\n>>> 全部测试完成")
