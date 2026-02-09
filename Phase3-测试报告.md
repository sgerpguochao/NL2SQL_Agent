# Phase 3 测试报告 —— 后端接口开发

> 测试时间：2026-02-09
> 测试环境：Windows 10 / conda nl2sql_vc (Python 3.11) / FastAPI + Uvicorn
> 测试端口：http://127.0.0.1:8001
> 测试脚本：`backend/app/playground/test_phase3_api.py`

---

## 一、Phase 3 任务完成情况

| 任务 ID | 任务内容 | 状态 |
|---|---|---|
| p3-llm-service | LLM 服务 - `llm_service.py`（ChatOpenAI + Qwen3-max） | 已完成 |
| p3-db-setup | 数据库搭建 - `connection.py` + `sample_data.py`（SQLite + SQLDatabase） | 已完成 |
| p3-agent-service | SQL Agent - `agent_service.py`（create_agent + SQLDatabaseToolkit + InMemorySaver） | 已完成 |
| p3-session-api | 会话接口 - `session_service.py` + `session.py`（CRUD REST API） | 已完成 |
| p3-chart-service | 图表服务 - `chart_service.py`（AI 图表决策 + ECharts JSON） | 已完成 |
| p3-chat-stream-api | 聊天流式接口 - `chat.py`（SSE token/sql/chart/done/error） | 已完成 |

---

## 二、新增/修改文件清单

| 文件路径 | 操作 | 说明 |
|---|---|---|
| `backend/.env` | 修改 | API Key 填入实际值，模型名更新为 `qwen3-max` |
| `backend/app/config.py` | 修改 | 新增 `LLM_TEMPERATURE` 配置项，默认模型名改为 `qwen3-max` |
| `backend/app/main.py` | 修改 | 挂载 session/chat 路由，添加 lifespan 启动时初始化数据库 |
| `backend/app/services/llm_service.py` | 新建 | `get_llm()` 工厂函数，ChatOpenAI 对接 DashScope |
| `backend/app/database/connection.py` | 新建 | `get_db()` 工厂函数，SQLDatabase 单例封装 |
| `backend/app/database/sample_data.py` | 新建 | 示例数据库初始化（5 表、15 员工、24 条销售记录） |
| `backend/app/services/agent_service.py` | 新建 | SQL Agent 单例，create_agent + SQLDatabaseToolkit + InMemorySaver |
| `backend/app/services/session_service.py` | 新建 | 会话内存存储，CRUD + 消息管理 |
| `backend/app/services/chart_service.py` | 新建 | AI 图表决策，Qwen3 生成 ECharts option JSON，含降级方案 |
| `backend/app/models/schemas.py` | 新建 | Pydantic 数据模型定义 |
| `backend/app/routers/session.py` | 新建 | 会话 REST API 路由 |
| `backend/app/routers/chat.py` | 新建 | SSE 流式聊天路由 |
| `backend/app/playground/test_phase3_api.py` | 新建 | Phase 3 全接口自动化测试脚本 |

---

## 三、API 接口清单

### 3.1 健康检查

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查，返回服务状态和版本号 |

### 3.2 会话管理

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/sessions` | 创建新会话 |
| GET | `/api/sessions` | 获取会话列表（按更新时间倒序） |
| GET | `/api/sessions/{session_id}` | 获取会话详情（含消息列表） |
| PUT | `/api/sessions/{session_id}` | 更新会话标题 |
| DELETE | `/api/sessions/{session_id}` | 删除会话 |

### 3.3 聊天接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/chat/{session_id}/stream` | SSE 流式聊天（NL2SQL） |

SSE 事件类型：

| 事件 | 数据格式 | 说明 |
|---|---|---|
| `token` | `{"content": "文本片段"}` | 流式文本回复 |
| `sql` | `{"sql": "SELECT..."}` | Agent 执行的 SQL 语句 |
| `chart` | `{"chart_type": "bar", "echarts_option": {...}, "table_data": {...}}` | 图表配置 |
| `done` | `{}` | 流结束标记 |
| `error` | `{"message": "错误描述"}` | 错误信息 |

---

## 四、测试用例及结果

### 测试 1：健康检查

- **请求**：`GET /api/health`
- **期望**：200，返回 `{status, service, version}`
- **实际**：

```json
{
  "status": "ok",
  "service": "nl2sql-backend",
  "version": "0.2.0"
}
```

- **结果**：PASS

### 测试 2：路由注册

- **请求**：`GET /openapi.json`
- **期望**：所有 Phase 3 路由均注册
- **实际**：

```
Routes: ['/api/sessions', '/api/sessions/{session_id}', '/api/chat/{session_id}/stream', '/api/health']
```

- **结果**：PASS

### 测试 3：会话 CRUD

| 操作 | 请求 | 状态码 | 验证点 | 结果 |
|---|---|---|---|---|
| 创建会话 | `POST /api/sessions {"title":"CRUD 测试会话"}` | 201 | 返回 id、title、timestamps | PASS |
| 获取列表 | `GET /api/sessions` | 200 | count >= 1 | PASS |
| 获取详情 | `GET /api/sessions/{id}` | 200 | 包含 messages 字段，message_count=0 | PASS |
| 更新标题 | `PUT /api/sessions/{id} {"title":"Updated Title"}` | 200 | title 已更新 | PASS |
| 删除会话 | `DELETE /api/sessions/{id}` | 204 | 无返回体 | PASS |
| 404 测试 | `GET /api/sessions/nonexistent` | 404 | 错误提示 | PASS |

- **结果**：全部 PASS

### 测试 4：NL2SQL 流式接口

- **问题**：`各部门的员工人数分别是多少？`
- **请求**：`POST /api/chat/{session_id}/stream {"message": "..."}`
- **SSE 事件统计**：

| 事件类型 | 数量 | 说明 |
|---|---|---|
| `token` | 5 | Agent 思考过程 + 最终回答 |
| `sql` | 1 | 生成并执行的 SQL |
| `chart` | 1 | ECharts 柱状图配置 |
| `done` | 1 | 流结束标记 |

- **Agent 生成的 SQL**：

```sql
SELECT d.name AS department_name, COUNT(e.id) AS employee_count
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY employee_count DESC;
```

- **文本回复**（摘要）：

> 各部门的员工人数如下：
> 1. 销售部：4人
> 2. 技术部：4人
> 3. 市场部：3人
> 4. 人事部：2人
> 5. 财务部：2人

- **图表数据**：
  - 类型：`bar`（柱状图）
  - ECharts option keys：`backgroundColor, textStyle, tooltip, xAxis, yAxis, series`
  - 表格列：`['department_name', 'employee_count']`
  - 表格行数：5

- **结果**：PASS

### 测试 5：上下文追问

- **追问**：`其中人数最多的部门，平均工资是多少？`（同一 session_id）
- **期望**：Agent 能理解"其中"指代上轮提到的部门
- **实际回复**（摘要）：

> 人数最多的两个部门（销售部和技术部，各有4名员工）的平均工资分别是：
> - 技术部：25,500元（平均工资最高）
> - 销售部：17,250元

- **验证**：Agent 正确关联上文语境，识别"人数最多"指销售部和技术部
- **结果**：PASS

### 测试 6：会话消息持久化

- **请求**：`GET /api/sessions/{id}`
- **期望**：2 轮问答共 4 条消息
- **实际**：

| 索引 | 角色 | 内容摘要 |
|---|---|---|
| 0 | user | 各部门的员工人数分别是多少？ |
| 1 | assistant | 各部门的员工人数如下：1.销售部：4人 2.技术部：4人... |
| 2 | user | 其中人数最多的部门，平均工资是多少？ |
| 3 | assistant | 人数最多的两个部门的平均工资分别是：技术部 25,500元... |

- **消息数量**：4（符合预期）
- **结果**：PASS

---

## 五、技术栈及关键实现

### 5.1 核心组件版本

| 组件 | 版本 | 说明 |
|---|---|---|
| langchain | 1.2.9 | Agent 框架 |
| langchain-openai | -- | ChatOpenAI 对接 DashScope |
| langchain-community | -- | SQLDatabaseToolkit |
| langgraph | -- | create_agent + InMemorySaver |
| fastapi | -- | Web 框架 |
| uvicorn | -- | ASGI 服务器 |

### 5.2 NL2SQL 技术方案

| 层次 | 技术选型 | 说明 |
|---|---|---|
| LLM | Qwen3-max via DashScope OpenAI 兼容端点 | ChatOpenAI 封装 |
| Agent | `langchain.agents.create_agent` (v1) | LangChain 最新标准 API |
| 工具集 | `SQLDatabaseToolkit` (4 个工具) | list_tables / schema / query_checker / query |
| 数据库 | `SQLDatabase.from_uri("sqlite:///...")` | LangChain 封装 |
| 记忆 | `InMemorySaver` + thread_id | LangGraph checkpointer |
| 图表 | `chart_service` + Qwen3-max | AI 决策图表类型 + 生成 ECharts JSON |
| 流式 | SSE (StreamingResponse) | stream_mode="updates" 事件驱动 |

### 5.3 Agent 工具调用链（实测）

```
用户提问
  ↓
sql_db_list_tables → 获取表名列表
  ↓
sql_db_schema → 获取相关表结构
  ↓
sql_db_query_checker → LLM 校验 SQL 语法
  ↓
sql_db_query → 执行 SQL 查询
  ↓
Qwen3 格式化中文回答
  ↓
chart_service → AI 生成图表配置
  ↓
SSE 推送 token + sql + chart + done
```

---

## 六、示例数据库结构

| 表名 | 记录数 | 字段 |
|---|---|---|
| `departments` | 5 | id, name, manager, budget, created_at |
| `employees` | 15 | id, name, department_id, position, salary, hire_date |
| `products` | 5 | id, name, category, price, stock |
| `sales` | 24 | id, employee_id, product_id, amount, quantity, sale_date |

数据覆盖 2024 年 1-6 月，包含 5 个部门、15 名员工、5 种产品、24 条销售记录，可支持部门统计、员工排名、月度趋势、产品分析等多类查询场景。

---

## 七、测试结论

| 项目 | 结果 |
|---|---|
| 测试总数 | 6 |
| 通过 | 6 |
| 失败 | 0 |
| 通过率 | 100% |

**Phase 3 后端接口开发全部完成。** 所有 API 接口通过测试：
- 会话 CRUD 5 个端点正常工作
- NL2SQL 完整链路畅通：自然语言 → SQL 生成 → 查询执行 → 中文回答 → 图表配置
- SSE 流式推送 4 种事件类型正确输出
- 上下文记忆通过 InMemorySaver + thread_id 实现，追问功能验证通过
- 消息持久化到内存会话存储，支持历史查询

**可进入 Phase 4：前后端联调。**
