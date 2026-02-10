---
name: NL2SQL 智能数据分析系统 (MySQL 版本)
overview: 基于 FastAPI + LangChain 后端（Qwen3 实现 NL2SQL）和 React 前端（三栏布局）构建全栈智能数据分析系统。使用 MySQL 作为数据存储，支持多连接管理、连接测试，SQL 编辑器和对话区域可切换不同数据库连接。包含 SSE 流式、思考过程、图表、Markdown 渲染、科技主题等完整功能。
todos:
  - id: p1-backend-scaffold
    content: Phase1：后端基础骨架 - 目录结构、requirements.txt、.env 模板、FastAPI 入口 main.py（含 CORS + /api/health）、config.py，nl2sql_vc 环境安装依赖
    status: completed
  - id: p1-backend-run
    content: Phase1：启动后端服务验证 - uvicorn 启动 FastAPI，访问 /api/health 和 /docs 确认正常
    status: completed
  - id: p1-frontend-scaffold
    content: Phase1：前端基础骨架 - Vite + React + TS，安装 Tailwind/zustand/echarts-for-react/axios，配置 proxy
    status: completed
  - id: p1-frontend-run
    content: Phase1：启动前端服务验证 - npm run dev，确认页面可访问且 proxy 代理 /api/health 正常
    status: completed
  - id: p2-layout
    content: Phase2：前端三栏布局 - AppLayout 容器（左 250px / 中 flex / 右 520px 上下分割）
    status: completed
  - id: p2-sidebar
    content: Phase2：左侧边栏 UI - SessionList + SessionItem，新建/删除/高亮（mock 数据驱动）
    status: completed
  - id: p2-chat-ui
    content: Phase2：中间聊天面板 UI - ChatPanel + MessageList + MessageItem + ChatInput（mock 数据驱动）
    status: completed
  - id: p2-chart-ui
    content: Phase2：右侧图表面板 UI - ChartPanel + DynamicChart + DataTable，ECharts 渲染 + 空状态占位
    status: completed
  - id: p2-stores
    content: Phase2：Zustand 状态管理 - sessionStore + chatStore + TypeScript 类型定义（snake_case 对齐后端）
    status: completed
  - id: p3-llm-service
    content: Phase3：后端 LLM 服务 - Qwen3 via DashScope，ChatOpenAI 初始化 + 连通性测试
    status: completed
  - id: p3-mysql-connection
    content: Phase3：MySQL 连接管理 - config.py MYSQL_* 参数、connection.py MySQL 连接工厂、connection_service CRUD+缓存+测试、connection 路由
    status: completed
  - id: p3-agent-service
    content: Phase3：后端 SQL Agent - create_agent + SQLDatabaseToolkit + InMemorySaver，按 connection_id 管理 Agent 缓存
    status: completed
  - id: p3-session-api
    content: Phase3：后端会话接口 - 会话 CRUD REST API（POST/GET/PUT/DELETE）
    status: completed
  - id: p3-chart-service
    content: Phase3：后端图表服务 - AI 图表类型决策 + ECharts option JSON 生成
    status: completed
  - id: p3-chat-stream-api
    content: Phase3：后端聊天流式接口 - SSE（token/sql/chart/thinking/done/error），ChatRequest 含 connection_id
    status: completed
  - id: p4-api-client
    content: Phase4：前端 API 对接 - api/client.ts（Axios REST + Fetch SSE 流式封装），含连接管理 API
    status: completed
  - id: p4-session-integration
    content: Phase4：会话联调 - 左侧边栏对接后端会话 CRUD，切换会话加载历史消息
    status: completed
  - id: p4-chat-integration
    content: Phase4：聊天联调 - 中间面板对接 SSE 流式接口 + 实时渲染 token/sql + 上下文记忆，传入 connectionId
    status: completed
  - id: p4-chart-integration
    content: Phase4：图表联调 - 右侧面板接收 SSE chart 事件，动态渲染 ECharts + 图表/表格切换
    status: completed
  - id: p4-e2e-test
    content: Phase4：端到端验证 - 自动化测试全部通过
    status: completed
  - id: p5-db-backend-api
    content: Phase5：后端数据库工具 API - GET /api/database/schema + POST /api/database/query（分页），必填 connection_id
    status: completed
  - id: p5-db-frontend-types
    content: Phase5：前端类型 + API - ColumnInfo/TableSchema/SqlQueryResult、MySQLConnection/ConnectionTestResult、fetchSchemaApi/executeSqlApi 含 connectionId
    status: completed
  - id: p5-connection-ui
    content: Phase5：连接管理 UI - connectionStore、ConnectionManager、ConnectionDialog、ConnectionSelector，DatabasePanel 三 Tab（表结构/SQL查询/连接管理）
    status: completed
  - id: p5-db-schema-explorer
    content: Phase5：SchemaExplorer - 按 connectionId 加载 schema，无效连接占位提示
    status: completed
  - id: p5-db-sql-editor
    content: Phase5：SqlEditor + QueryResult - 按 connectionId 执行 SQL，连接守卫（无效时禁用）
    status: completed
  - id: p5-db-panel-layout
    content: Phase5：DatabasePanel + AppLayout - 右侧栏上下分割，Tab 栏 ConnectionSelector，连接守卫
    status: completed
  - id: p5-app-init
    content: Phase5：App 启动校验 - initConnections 挂载调用，loading/error 横幅，connectionValid 控制
    status: completed
  - id: p5-backend-test
    content: Phase5：后端测试 - test_mysql_connection.py 全流程测试（79 项全部通过）
    status: completed
  - id: p5-e2e-test
    content: Phase5：前端联调测试 - 连接管理/Schema/SQL/对话全流程验证
    status: completed
  - id: p6-markdown
    content: Phase6：AI 回复 Markdown 渲染 - react-markdown + remark-gfm，MessageItem/MessageList 接入
    status: completed
  - id: p6-collapsible
    content: Phase6：中间过程折叠 - CollapsibleProcess 组件，流式时默认展开、完成后默认收缩
    status: completed
  - id: p6-thinking-process
    content: Phase6：思考过程优化 - SSE thinking 事件追加累积，后端持久化 thinking_process，前端 streamingThinking 实时展示 + 历史回显
    status: completed
  - id: p6-chart-ux
    content: Phase6：图表体验优化 - 对话内联图表、右侧查看大图、切换会话清空 chartData、chart_service 去 <think> 修复
    status: completed
  - id: p6-tech-theme
    content: Phase6：科技主题 UI - 全局 CSS 变量、网格背景、青蓝 accent、右侧栏 520px、SQL 编辑器 6 行
    status: completed
isProject: false
---

# NL2SQL 智能数据分析系统 - MySQL 版本

> **运行环境**：conda 虚拟环境 `nl2sql_vc`，Python 3.11
> **数据存储**：MySQL（PyMySQL + SQLAlchemy），支持多连接管理
> **项目路径**：`g:\nl2sql_agent\`

---

## 系统整体架构

```mermaid
graph TB
    subgraph frontend ["前端 - React"]
        ChatList["左侧：会话列表"]
        QAPanel["中间：问答面板 + ConnectionSelector"]
        ChartPanel["右上：可视化面板"]
        DBPanel["右下：数据库工具\n表结构 / SQL 查询 / 连接管理"]
        ConnStore["connectionStore\n连接列表、活动连接、connectionValid"]
    end

    subgraph backend ["后端 - FastAPI"]
        API["FastAPI 路由层"]
        ConnRouter["connection 路由\nCRUD + 测试"]
        ConnService["connection_service\nJSON 持久化 + SQLDatabase 缓存"]
        SessionMgr["会话管理器"]
        Memory["对话记忆"]
        Agent["LangChain SQL Agent\n按 connection_id 缓存"]
        ChartDecider["图表决策器"]
        DBToolAPI["数据库工具 API\nSchema / Query（需 connection_id）"]
    end

    subgraph external ["外部服务"]
        Qwen3["Qwen3 - 阿里云百炼 DashScope"]
        MySQL["MySQL 数据库\n(多连接支持)"]
    end

    ConnStore -->|"initConnections"| ConnRouter
    QAPanel -->|"SSE 流式 + connection_id"| API
    ChatList -->|"REST API"| API
    DBPanel -->|"REST API + connection_id"| DBToolAPI
    ConnRouter --> ConnService
    ConnService -->|"connections.json"| JSON[(JSON)]
    API --> SessionMgr
    SessionMgr --> Memory
    API --> Agent
    Agent --> Qwen3
    Agent --> ConnService
    Agent --> ChartDecider
    ChartDecider -->|"ECharts Option JSON"| API
    DBToolAPI --> ConnService
    ConnService --> MySQL
    API -->|"流式响应"| QAPanel
    API -->|"图表配置"| ChartPanel
    DBToolAPI -->|"Schema / 分页数据"| DBPanel
```



---

## MySQL 连接管理架构

```mermaid
flowchart LR
  subgraph frontend [Frontend React]
    AppInit["App启动 initConnections"]
    ConnStore["connectionStore"]
    ConnMgr["ConnectionManager"]
    ConnSelect["ConnectionSelector"]
    ChatPanel["ChatPanel +连接守卫"]
    SqlEditor["SqlEditor +连接守卫"]
    SchemaExp["SchemaExplorer 按连接加载"]
  end

  subgraph backend [Backend FastAPI]
    ConnRouter["connection router CRUD+测试"]
    ConnService["connection_service JSON持久化"]
    DBRouter["database router 按连接查询"]
    ChatRouter["chat router 按 connection_id 对话"]
    AgentSvc["agent_service 按连接创建Agent"]
    ConnPool["MySQL 连接池 SQLDatabase 实例缓存"]
  end

  subgraph storage [Storage]
    JSON["connections.json"]
    MySQL1["MySQL Server 1"]
    MySQL2["MySQL Server 2"]
  end

  AppInit -->|"1.拉取连接列表"| ConnRouter
  AppInit -->|"2.校验默认连接"| ConnRouter
  AppInit -->|"3.更新状态"| ConnStore
  ConnStore -->|"connectionValid?"| ChatPanel
  ConnStore -->|"connectionValid?"| SqlEditor
  ConnMgr --> ConnRouter
  ConnSelect --> ConnStore
  ChatPanel --> ChatRouter
  SqlEditor --> DBRouter
  SchemaExp --> DBRouter
  ConnRouter --> ConnService
  ConnService --> JSON
  DBRouter --> ConnPool
  ChatRouter --> AgentSvc
  AgentSvc --> ConnPool
  ConnPool --> MySQL1
  ConnPool --> MySQL2
```



**启动校验时序**：

```mermaid
sequenceDiagram
  participant App as App/AppLayout
  participant Store as connectionStore
  participant API as Backend API
  participant MySQL as MySQL Server

  App->>Store: initConnections()
  Store->>API: GET /api/connections
  API-->>Store: connections list
  Store->>Store: 选中第一个连接
  Store->>API: POST /api/connections/{id}/test
  API->>MySQL: 尝试连接
  MySQL-->>API: 连接结果
  API-->>Store: ConnectionTestResult
  alt 校验通过
    Store->>Store: connectionValid = true
    Note over App: 对话和SQL编辑器可用
  else 校验失败
    Store->>Store: connectionValid = false
    Note over App: 对话和SQL编辑器禁用 + 显示提示
  end
```



---

## 项目目录结构

```
g:\nl2sql_agent\
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口，挂载 session/chat/database/connection 路由
│   │   ├── config.py               # MYSQL_* 默认连接参数、CONNECTIONS_FILE
│   │   ├── routers/
│   │   │   ├── chat.py             # 聊天 SSE（请求体含 connection_id）
│   │   │   ├── session.py          # 会话 CRUD
│   │   │   ├── database.py         # Schema + Query（query 参数 connection_id）
│   │   │   └── connection.py       # 连接管理 CRUD + 测试
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── agent_service.py    # 按 connection_id 管理 Agent 缓存
│   │   │   ├── session_service.py
│   │   │   ├── chart_service.py
│   │   │   └── connection_service.py  # 连接 CRUD、SQLDatabase 缓存、连接测试
│   │   ├── models/schemas.py       # 含 MySQLConnectionConfig、ConnectionTestResult、connection_id
│   │   ├── database/
│   │   │   └── connection.py       # MySQL 连接工厂（build_mysql_uri、create_sql_database）
│   │   └── playground/
│   │       ├── test_mysql_connection.py  # Phase5 全流程测试（79 项）
│   │       └── ...
│   ├── data/
│   │   └── connections.json        # 连接配置持久化
│   ├── requirements.txt           # 含 pymysql
│   └── .env                        # MYSQL_HOST、MYSQL_PORT、MYSQL_USER、MYSQL_PASSWORD、MYSQL_DATABASE
├── frontend/
│   ├── src/
│   │   ├── api/client.ts           # 含 fetchConnectionsApi、testConnectionByIdApi 等，现有 API 传 connectionId
│   │   ├── types/index.ts          # 含 MySQLConnection、ConnectionTestResult 等
│   │   ├── stores/
│   │   │   ├── sessionStore.ts
│   │   │   ├── chatStore.ts        # sendMessage(sessionId, content, connectionId)
│   │   │   └── connectionStore.ts # 连接列表、活动连接、connectionValid、initConnections
│   │   └── components/
│   │       ├── AppLayout.tsx       # initConnections、loading/error 横幅、effectiveConnectionId
│   │       ├── Connection/
│   │       │   ├── ConnectionManager.tsx
│   │       │   ├── ConnectionDialog.tsx
│   │       │   └── ConnectionSelector.tsx
│   │       └── Database/
│   │           ├── DatabasePanel.tsx   # 三 Tab：表结构/SQL查询/连接管理 + ConnectionSelector
│   │           ├── SchemaExplorer.tsx # connectionId prop，无效时占位
│   │           └── SqlEditor.tsx      # connectionId prop，连接守卫
│   └── ...
└── ...
```

---

## 任务清单总览


| Phase       | 任务 ID                  | 任务内容                                                                           | 状态          |
| ----------- | ---------------------- | ------------------------------------------------------------------------------ | ----------- |
| **Phase 1** | p1-backend-scaffold    | 后端基础骨架                                                                         | ✅ completed |
| **Phase 1** | p1-backend-run         | 启动后端服务验证                                                                       | ✅ completed |
| **Phase 1** | p1-frontend-scaffold   | 前端基础骨架                                                                         | ✅ completed |
| **Phase 1** | p1-frontend-run        | 启动前端服务验证                                                                       | ✅ completed |
| **Phase 2** | p2-layout              | 前端三栏布局                                                                         | ✅ completed |
| **Phase 2** | p2-sidebar             | 左侧边栏 UI                                                                        | ✅ completed |
| **Phase 2** | p2-chat-ui             | 中间聊天面板 UI                                                                      | ✅ completed |
| **Phase 2** | p2-chart-ui            | 右侧图表面板 UI                                                                      | ✅ completed |
| **Phase 2** | p2-stores              | Zustand 状态管理                                                                   | ✅ completed |
| **Phase 3** | p3-llm-service         | 后端 LLM 服务                                                                      | ✅ completed |
| **Phase 3** | p3-mysql-connection    | MySQL 连接管理（config、connection、connection_service、connection 路由）                 | ✅ completed |
| **Phase 3** | p3-agent-service       | 后端 SQL Agent（按 connection_id 缓存）                                               | ✅ completed |
| **Phase 3** | p3-session-api         | 后端会话接口                                                                         | ✅ completed |
| **Phase 3** | p3-chart-service       | 后端图表服务                                                                         | ✅ completed |
| **Phase 3** | p3-chat-stream-api     | 后端聊天流式接口（含 connection_id）                                                      | ✅ completed |
| **Phase 4** | p4-api-client          | 前端 API 对接（含连接管理 API）                                                           | ✅ completed |
| **Phase 4** | p4-session-integration | 会话联调                                                                           | ✅ completed |
| **Phase 4** | p4-chat-integration    | 聊天联调（传入 connectionId）                                                          | ✅ completed |
| **Phase 4** | p4-chart-integration   | 图表联调                                                                           | ✅ completed |
| **Phase 4** | p4-e2e-test            | 端到端验证                                                                          | ✅ completed |
| **Phase 5** | p5-db-backend-api      | 后端数据库工具 API（connection_id 必填）                                                  | ✅ completed |
| **Phase 5** | p5-db-frontend-types   | 前端类型 + API（含连接类型、connectionId）                                                 | ✅ completed |
| **Phase 5** | p5-connection-ui       | 连接管理 UI（connectionStore、ConnectionManager、ConnectionDialog、ConnectionSelector） | ✅ completed |
| **Phase 5** | p5-db-schema-explorer  | SchemaExplorer（按 connectionId 加载）                                              | ✅ completed |
| **Phase 5** | p5-db-sql-editor       | SqlEditor + QueryResult（连接守卫）                                                  | ✅ completed |
| **Phase 5** | p5-db-panel-layout     | DatabasePanel + AppLayout（连接守卫）                                                | ✅ completed |
| **Phase 5** | p5-app-init            | App 启动校验 initConnections                                                       | ✅ completed |
| **Phase 5** | p5-backend-test        | 后端测试 test_mysql_connection.py                                                  | ✅ completed |
| **Phase 5** | p5-e2e-test            | 前端联调测试                                                                         | ✅ completed |
| **Phase 6** | p6-markdown            | AI 回复 Markdown 渲染                                                              | ✅ completed |
| **Phase 6** | p6-collapsible         | 中间过程折叠                                                                         | ✅ completed |
| **Phase 6** | p6-thinking-process    | 思考过程优化                                                                         | ✅ completed |
| **Phase 6** | p6-chart-ux            | 图表体验优化                                                                         | ✅ completed |
| **Phase 6** | p6-tech-theme          | 科技主题 UI                                                                        | ✅ completed |


---

## 配置与环境

### 后端 config.py（MySQL 版本）

```python
class Settings(BaseSettings):
    DASHSCOPE_API_KEY: str = "sk-xxxxx"
    LLM_MODEL_NAME: str = "qwen3-max"
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_TEMPERATURE: float = 0.7

    # MySQL 默认连接（可通过 .env 覆盖）
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = ""

    # 连接配置持久化路径
    CONNECTIONS_FILE: str = "./data/connections.json"
```

### backend/.env

```
DASHSCOPE_API_KEY=sk-xxxxx
LLM_MODEL_NAME=qwen3-max
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=xxxxx
MYSQL_DATABASE=ai_sales_data
```

---

## 连接管理 API


| 方法     | 路径                           | 描述               |
| ------ | ---------------------------- | ---------------- |
| GET    | `/api/connections`           | 获取所有连接列表         |
| POST   | `/api/connections`           | 新增连接             |
| GET    | `/api/connections/{id}`      | 获取单个连接           |
| PUT    | `/api/connections/{id}`      | 更新连接             |
| DELETE | `/api/connections/{id}`      | 删除连接             |
| POST   | `/api/connections/test`      | 测试连接（不保存，传入完整配置） |
| POST   | `/api/connections/{id}/test` | 测试已保存的连接         |


---

## 数据库与聊天 API（需 connection_id）


| 方法   | 路径                                    | 说明                                            |
| ---- | ------------------------------------- | --------------------------------------------- |
| GET  | `/api/database/schema?connection_id=` | 获取指定连接的表结构                                    |
| POST | `/api/database/query`                 | 请求体含 `connection_id`、`sql`、`page`、`page_size` |
| POST | `/api/chat/{session_id}/stream`       | 请求体含 `message`、`connection_id`                |


---

## Phase 5 测试验证报告

### 后端测试 - test_mysql_connection.py

**运行方式**：`cd backend && python -m app.playground.test_mysql_connection`

**测试结果**：


| 模块                   | 通过     | 失败    | 状态           |
| -------------------- | ------ | ----- | ------------ |
| Part 1: 健康检查         | 2      | 0     | OK           |
| Part 2: 连接测试功能       | 10     | 0     | OK           |
| Part 3: 连接 CRUD      | 22     | 0     | OK           |
| Part 4: Schema 获取    | 10     | 0     | OK           |
| Part 5: SQL 查询执行     | 17     | 0     | OK           |
| Part 6: SSE 聊天流式接口   | 9      | 0     | OK           |
| Part 7: 会话消息持久化      | 6      | 0     | OK           |
| Part 8: 多连接 Agent 隔离 | 3      | 0     | OK           |
| **合计**               | **79** | **0** | **ALL PASS** |


### 前端联调验证


| 检查项                       | 状态   |
| ------------------------- | ---- |
| 启动校验 initConnections      | PASS |
| 连接守卫（无有效连接时禁用）            | PASS |
| 连接管理（新增、测试、删除）            | PASS |
| Schema 按连接加载              | PASS |
| SQL 编辑器按连接执行              | PASS |
| 对话区域选择连接                  | PASS |
| 切换连接重新校验                  | PASS |
| 前端构建 tsc -b && vite build | PASS |


---

## 涉及文件变更清单（MySQL 版本）

### 后端 - 修改


| 文件                        | 变更描述                                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| config.py                 | 移除 DB_PATH，新增 MYSQL_* 和 CONNECTIONS_FILE                                                  |
| models/schemas.py         | 新增 MySQLConnectionConfig、ConnectionTestResult，ChatRequest/SqlQueryRequest 含 connection_id |
| database/connection.py    | 重写为 MySQL 连接工厂                                                                            |
| routers/database.py       | 移除 sqlite3，使用 SQLAlchemy inspect + connection_id                                          |
| services/agent_service.py | 按 connection_id 管理 Agent 缓存                                                               |
| routers/chat.py           | ChatRequest 含 connection_id                                                               |
| main.py                   | 移除 SQLite 初始化，挂载 connection 路由                                                            |


### 后端 - 新增


| 文件                                  | 描述                          |
| ----------------------------------- | --------------------------- |
| services/connection_service.py      | 连接 CRUD、SQLDatabase 缓存、连接测试 |
| routers/connection.py               | 连接管理 REST API               |
| playground/test_mysql_connection.py | 全流程测试脚本                     |


### 前端 - 修改


| 文件                  | 变更描述                                                                    |
| ------------------- | ----------------------------------------------------------------------- |
| types/index.ts      | 新增 MySQLConnection、ConnectionTestResult 等                               |
| api/client.ts       | 新增连接 API，fetchSchemaApi/executeSqlApi/sendChatMessageApi 含 connectionId |
| stores/chatStore.ts | sendMessage(sessionId, content, connectionId)                           |
| AppLayout.tsx       | initConnections、loading/error 横幅、effectiveConnectionId                  |
| ChatPanel.tsx       | ConnectionSelector、connectionId 透传                                      |
| ChatInput.tsx       | connectionId、连接守卫                                                       |
| DatabasePanel.tsx   | 三 Tab、ConnectionSelector、connectionId 透传                                |
| SchemaExplorer.tsx  | connectionId、无效占位                                                       |
| SqlEditor.tsx       | connectionId、连接守卫                                                       |


### 前端 - 新增


| 文件                                           | 描述      |
| -------------------------------------------- | ------- |
| stores/connectionStore.ts                    | 连接状态管理  |
| components/Connection/ConnectionManager.tsx  | 连接管理面板  |
| components/Connection/ConnectionDialog.tsx   | 连接编辑弹窗  |
| components/Connection/ConnectionSelector.tsx | 连接下拉选择器 |


---

## 核心依赖

### 后端（requirements.txt）

- `fastapi` + `uvicorn[standard]`
- `langchain` + `langchain-openai` + `langchain-community`
- `python-dotenv` + `pydantic` + `pydantic-settings`
- `sse-starlette`
- `pymysql`  # MySQL 驱动

### 前端（package.json）

- `react` + `react-dom` + `vite` + `typescript`
- `tailwindcss` + `@tailwindcss/vite`
- `zustand` + `axios` + `uuid`
- `echarts` + `echarts-for-react`
- `react-markdown` + `remark-gfm`

