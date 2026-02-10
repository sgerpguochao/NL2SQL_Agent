# NL2SQL 智能数据分析系统 - MySQL 版本

> **版本**：v1.0.0-mysql

基于自然语言查询 MySQL 数据库并自动生成可视化图表的全栈 AI 应用。支持多 MySQL 连接管理、连接测试、连接守卫，SQL 编辑器和对话区域可切换不同数据库连接。

用户只需输入中文自然语言问题（如「各部门的销售总额是多少」），系统会自动将其转换为 SQL 查询、执行并返回结构化数据，同时生成 ECharts 图表进行可视化展示。

---

## 功能特性

- **自然语言转 SQL（NL2SQL）**：基于 LangChain SQL Agent，自动解析用户意图、生成并执行 MySQL 语句
- **多连接管理**：支持配置多个 MySQL 连接（不同 host:port），CRUD + 连接测试，连接配置持久化到 `connections.json`
- **连接守卫**：前端启动时自动校验默认连接；无有效连接时禁用对话输入和 SQL 执行，显示提示
- **连接选择器**：ChatPanel 与 DatabasePanel 均可通过下拉选择当前使用的数据库连接，切换时自动校验
- **流式对话**：通过 SSE 实时推送 AI 思考过程、SQL 语句和最终回答
- **思考过程展示**：完整展示「用户问题 + AI 推理步骤 + 最终回答」，流式时默认展开、完成后自动收缩
- **Markdown 渲染**：AI 回复支持 Markdown 格式（段落、列表、加粗、代码块、表格等）
- **智能图表生成**：AI 自动选择最佳图表类型（柱状图/折线图/饼图/表格），支持对话内联展示及「在右侧查看大图」
- **多轮对话记忆**：基于 LangGraph InMemorySaver，按 connection_id 隔离 Agent 缓存
- **会话管理**：支持创建、切换、重命名、删除多个独立会话
- **数据库浏览器**：按连接加载表结构，可折叠展示，点击表名可预填 SQL
- **SQL 编辑器**：按连接执行 SQL 查询，支持分页浏览，连接无效时禁用并提示
- **科技主题 UI**：深色网格背景、青蓝 accent、统一的暗色调界面

---

## 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| **FastAPI** | Web 框架，提供 REST API 和 SSE 流式接口 |
| **LangChain** | AI Agent 框架，NL2SQL 核心实现 |
| **Qwen3-max** | 阿里云百炼大模型（通过 DashScope OpenAI 兼容端点） |
| **MySQL** | 关系数据库（PyMySQL + SQLAlchemy） |
| **LangGraph** | Agent 执行引擎 + 多轮对话记忆（InMemorySaver） |
| **Pydantic** | 数据模型验证 |
| **Uvicorn** | ASGI 服务器 |

### 前端

| 技术 | 用途 |
|------|------|
| **React 19** | UI 框架 |
| **TypeScript** | 类型安全 |
| **Tailwind CSS 4** | 样式系统 |
| **Vite 7** | 构建工具与开发服务器 |
| **ECharts** | 数据可视化图表 |
| **Zustand** | 轻量状态管理（sessionStore、chatStore、connectionStore） |
| **Axios** | HTTP 请求客户端 |
| **react-markdown** + **remark-gfm** | AI 回复 Markdown 渲染 |

---

## 项目结构（MySQL 版本）

```
nl2sql_agent/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口，挂载 session/chat/database/connection 路由
│   │   ├── config.py               # 配置（MYSQL_* 默认连接、CONNECTIONS_FILE）
│   │   ├── database/
│   │   │   └── connection.py      # MySQL 连接工厂（build_mysql_uri、create_sql_database）
│   │   ├── models/
│   │   │   └── schemas.py         # Pydantic 模型（含 MySQLConnectionConfig、connection_id）
│   │   ├── routers/
│   │   │   ├── session.py         # 会话 CRUD
│   │   │   ├── chat.py            # SSE 流式聊天（请求体含 connection_id）
│   │   │   ├── database.py        # Schema + Query（query/body 含 connection_id）
│   │   │   └── connection.py      # 连接管理 CRUD + 测试
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── agent_service.py   # 按 connection_id 管理 Agent 缓存
│   │   │   ├── session_service.py
│   │   │   ├── chart_service.py
│   │   │   └── connection_service.py  # 连接 CRUD、SQLDatabase 缓存、连接测试
│   │   └── playground/
│   │       └── test_mysql_connection.py  # 全流程测试（79 项）
│   ├── data/
│   │   └── connections.json       # 连接配置持久化（自动生成）
│   ├── requirements.txt           # 含 pymysql
│   └── .env                       # MYSQL_HOST、MYSQL_PORT、MYSQL_USER、MYSQL_PASSWORD、MYSQL_DATABASE
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts          # REST + SSE，含连接管理 API、connectionId 参数
│   │   ├── stores/
│   │   │   ├── sessionStore.ts
│   │   │   ├── chatStore.ts       # sendMessage(sessionId, content, connectionId)
│   │   │   └── connectionStore.ts # 连接列表、活动连接、connectionValid、initConnections
│   │   ├── types/
│   │   │   └── index.ts           # 含 MySQLConnection、ConnectionTestResult 等
│   │   ├── components/
│   │   │   ├── AppLayout.tsx      # initConnections、loading/error 横幅、effectiveConnectionId
│   │   │   ├── Connection/       # 连接管理
│   │   │   │   ├── ConnectionManager.tsx
│   │   │   │   ├── ConnectionDialog.tsx
│   │   │   │   └── ConnectionSelector.tsx
│   │   │   ├── Chat/
│   │   │   ├── Chart/
│   │   │   └── Database/         # 三 Tab：表结构 / SQL 查询 / 连接管理
│   │   └── ...
│   └── ...
└── README_MySQL.md
```

---

## 快速开始

### 环境要求

- Python 3.11+（推荐 Conda）
- Node.js 18+
- MySQL 8.0+（本地或远程）
- 阿里云百炼平台 API Key

### 1. 克隆项目

```bash
git clone https://github.com/sgerpguochao/NL2SQL_Agent.git
cd NL2SQL_Agent
# 使用 MySQL 版本
git checkout v1.0.0-mysql
```

### 2. 准备 MySQL 数据库

确保已有可用的 MySQL 实例，并创建目标数据库，例如：

```sql
CREATE DATABASE ai_sales_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- 根据业务需要导入或创建表结构
```

### 3. 后端配置与启动

```bash
conda create -n nl2sql_vc python=3.11
conda activate nl2sql_vc

cd backend
pip install -r requirements.txt

# 创建 .env 文件
cat > .env << EOF
DASHSCOPE_API_KEY=你的API_Key
LLM_MODEL_NAME=qwen3-max
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=ai_sales_data
EOF

# 启动后端（首次启动可自动创建默认连接）
python -m uvicorn app.main:app --reload --port 8000
```

### 4. 前端配置与启动

```bash
cd frontend
npm install
npm run dev
```

### 5. 访问应用

打开浏览器访问 `http://localhost:5173`。  
首次加载时会自动拉取连接列表并校验默认连接；若无有效连接，可通过「连接管理」Tab 新增并测试连接。

---

## 界面布局（MySQL 版本）

```
┌──────────┬────────────────────┬─────────────────────────┐
│          │  ChatPanel          │  数据可视化 (ChartPanel)   │
│  会话列表  │  标题栏 [ConnectionSelector] │                         │
│          ├────────────────────┼─────────────────────────┤
│  新建会话  │  消息列表           │  DatabasePanel           │
│  历史会话  │  中间过程折叠        │  Tab: [表结构][SQL查询][连接管理] │
│          │                    │  右侧 [ConnectionSelector] │
│          │  ChatInput          │  SchemaExplorer / SqlEditor│
│          │  (连接守卫)          │  ConnectionManager       │
└──────────┴────────────────────┴─────────────────────────┘
```

---

## API 接口（MySQL 版本）

### 连接管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/connections` | 获取所有连接列表 |
| POST | `/api/connections` | 新增连接 |
| GET | `/api/connections/:id` | 获取单个连接 |
| PUT | `/api/connections/:id` | 更新连接 |
| DELETE | `/api/connections/:id` | 删除连接 |
| POST | `/api/connections/test` | 测试连接（不保存，传入完整配置） |
| POST | `/api/connections/:id/test` | 测试已保存的连接 |

### 会话管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/sessions` | 创建会话 |
| GET | `/api/sessions` | 会话列表 |
| GET | `/api/sessions/:id` | 会话详情（含消息） |
| PUT | `/api/sessions/:id` | 更新标题 |
| DELETE | `/api/sessions/:id` | 删除会话 |

### 聊天

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat/:sessionId/stream` | SSE 流式聊天 |

**请求体**：`{ "message": "用户问题", "connection_id": "连接ID" }`

**SSE 事件**：`thinking`、`token`、`sql`、`chart`、`done`、`error`

### 数据库工具（需 connection_id）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/database/schema?connection_id=xxx` | 获取指定连接的表结构 |
| POST | `/api/database/query` | 执行 SQL 查询（分页） |

**POST /api/database/query 请求体**：`{ "connection_id": "连接ID", "sql": "SELECT ...", "page": 1, "page_size": 50 }`

---

## 连接管理流程

1. **启动校验**：`AppLayout` 挂载时调用 `initConnections()`，拉取连接列表 → 选中第一个 → 调用测试接口校验
2. **校验通过**：`connectionValid = true`，对话输入和 SQL 执行可用
3. **校验失败**：显示错误横幅，功能禁用，用户可到「连接管理」Tab 新增或编辑连接
4. **切换连接**：通过 ConnectionSelector 切换时，立即置 `connectionValid = false`，再调用测试接口，通过后恢复可用

---

## 测试验证

### 后端全流程测试

```bash
cd backend
# 确保后端已启动在 8000 端口
python -m app.playground.test_mysql_connection
```

**测试覆盖**：健康检查、连接测试（成功/失败）、连接 CRUD、Schema 获取、SQL 执行、SSE 聊天、会话持久化、多连接 Agent 隔离。共 79 项，全部通过。

### 前端构建

```bash
cd frontend
npm run build
```

---

## 与 SQLite 版本的区别

| 特性 | SQLite 版本 | MySQL 版本 |
|------|-------------|------------|
| 数据存储 | 单文件 SQLite3 | MySQL 多连接 |
| 连接管理 | 无，固定 DB_PATH | 多连接 CRUD + 测试 |
| API 参数 | 无 connection_id | Schema/Query/Chat 均需 connection_id |
| 前端 | 无连接选择 | ConnectionSelector + 连接守卫 |
| 配置 | DB_PATH | MYSQL_HOST、MYSQL_PORT 等 |

---

## 开发说明

- 后端 `--reload` 模式：`python -m uvicorn app.main:app --reload --port 8000`
- 前端 Vite 通过 proxy 将 `/api` 代理到 `127.0.0.1:8000`
- 连接配置存储在 `backend/data/connections.json`，可手动编辑（不推荐）

---

## License

MIT
