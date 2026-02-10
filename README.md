# NL2SQL 智能数据分析系统

> **版本**：sqlite3v0.0.1

基于自然语言查询数据库并自动生成可视化图表的全栈 AI 应用。

用户只需输入中文自然语言问题（如"各部门的销售总额是多少"），系统会自动将其转换为 SQL 查询、执行并返回结构化数据，同时生成 ECharts 图表进行可视化展示。

---

## 功能特性

- **自然语言转 SQL（NL2SQL）**：基于 LangChain SQL Agent，自动解析用户意图、生成并执行 SQL
- **流式对话**：通过 SSE（Server-Sent Events）实时推送 AI 思考过程、SQL 语句和最终回答
- **思考过程展示**：完整展示「用户问题 + AI 推理步骤 + 最终回答」，流式时默认展开、完成后自动收缩；思考过程持久化，切换会话后可回显
- **Markdown 渲染**：AI 回复支持 Markdown 格式（段落、列表、加粗、代码块、表格等）
- **智能图表生成**：AI 自动选择最佳图表类型（柱状图/折线图/饼图/表格），生成 ECharts 配置，支持对话内联展示及「在右侧查看大图」
- **多轮对话记忆**：基于 LangGraph InMemorySaver，支持上下文关联的连续提问
- **会话管理**：支持创建、切换、重命名、删除多个独立会话
- **数据库浏览器**：可折叠的表结构展示，直观查看所有表和字段信息，点击表名可预填 SQL
- **SQL 编辑器**：手动编写并执行 SQL 查询，支持分页浏览大数据集（突破 100 条限制）
- **科技主题 UI**：深色网格背景、青蓝 accent、统一的暗色调界面

## 技术栈

### 后端

| 技术 | 用途 |
|---|---|
| **FastAPI** | Web 框架，提供 REST API 和 SSE 流式接口 |
| **LangChain** | AI Agent 框架，NL2SQL 核心实现 |
| **Qwen3-max** | 阿里云百炼大模型（通过 DashScope OpenAI 兼容端点） |
| **SQLite3** | 轻量级关系数据库 |
| **LangGraph** | Agent 执行引擎 + 多轮对话记忆（InMemorySaver） |
| **Pydantic** | 数据模型验证 |
| **Uvicorn** | ASGI 服务器 |

### 前端

| 技术 | 用途 |
|---|---|
| **React 19** | UI 框架 |
| **TypeScript** | 类型安全 |
| **Tailwind CSS 4** | 样式系统 |
| **Vite 7** | 构建工具与开发服务器 |
| **ECharts** | 数据可视化图表 |
| **Zustand** | 轻量状态管理 |
| **Axios** | HTTP 请求客户端 |
| **react-markdown** + **remark-gfm** | AI 回复 Markdown 渲染 |

## 项目结构

```
nl2sql_agent/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口，路由挂载与生命周期
│   │   ├── config.py               # 配置管理（API Key、模型、数据库路径）
│   │   ├── database/
│   │   │   ├── connection.py       # SQLite + LangChain SQLDatabase 连接
│   │   │   └── sample_data.py      # 示例数据初始化（4 张业务表）
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic 请求/响应模型（含 thinking_process）
│   │   ├── routers/
│   │   │   ├── session.py          # 会话 CRUD REST API
│   │   │   ├── chat.py             # SSE 流式聊天接口（含 thinking 事件）
│   │   │   └── database.py         # 数据库 Schema 查询 + SQL 执行接口
│   │   ├── services/
│   │   │   ├── llm_service.py      # Qwen3 LLM 实例管理
│   │   │   ├── agent_service.py    # SQL Agent 创建与单例管理
│   │   │   ├── session_service.py  # 会话内存存储（含 thinking_process 持久化）
│   │   │   └── chart_service.py    # AI 图表类型决策 + ECharts 配置生成
│   │   └── playground/             # 测试脚本（Qwen3、NL2SQL、E2E、thinking）
│   ├── requirements.txt
│   └── .env                        # 环境变量（API Key，不提交到 Git）
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts           # API 客户端（REST + SSE，含 onThinking）
│   │   ├── stores/
│   │   │   ├── sessionStore.ts     # 会话状态管理
│   │   │   └── chatStore.ts        # 聊天 + 流式状态（streamingThinking）
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript 类型定义（含 thinking_process）
│   │   ├── components/
│   │   │   ├── AppLayout.tsx        # 三栏布局容器
│   │   │   ├── Sidebar/            # 左栏：会话列表
│   │   │   ├── Chat/               # 中栏：聊天问答（CollapsibleProcess、MarkdownContent）
│   │   │   ├── Chart/              # 右栏上：数据可视化
│   │   │   └── Database/           # 右栏下：数据库工具
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── sql_repo/                       # SQLite3 测试库
│   ├── init_db.py                  # 初始化脚本，支持 --force 重建
│   ├── README.md
│   └── data/
│       └── test.db                 # 测试数据库（每表 100+ 行 mock）
├── nl2sql_analysis_system_sqlit3.md  # 完整开发计划文档
└── README.md
```

## 快速开始

### 环境要求

- Python 3.11+（推荐使用 Conda）
- Node.js 18+
- 阿里云百炼平台 API Key

### 1. 克隆项目

```bash
git clone https://github.com/sgerpguochao/NL2SQL_Agent.git
cd NL2SQL_Agent
```

### 2. 后端配置与启动

```bash
# 创建并激活虚拟环境（可选，推荐使用 Conda）
conda create -n nl2sql_vc python=3.11
conda activate nl2sql_vc

# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境变量
# 创建 .env 文件并填入你的 API Key
echo DASHSCOPE_API_KEY=你的API_Key > .env
echo LLM_MODEL_NAME=qwen3-max >> .env
echo LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1 >> .env
echo DB_PATH=./data/business.db >> .env
# 可选：使用 sql_repo 测试库（每表 100+ 行数据）
# 运行 python sql_repo/init_db.py 后，将 DB_PATH 改为 sql_repo/data/test.db 的绝对路径

# 启动后端（首次启动会自动创建示例数据库）
python -m uvicorn app.main:app --port 8000
```

### 3. 前端配置与启动

```bash
# 新开一个终端
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

打开浏览器访问 `http://localhost:5173`

## 界面布局

```
┌──────────┬────────────────────┬──────────────┐
│          │                    │  数据可视化    │
│  会话列表  │     聊天问答区域     │  (图表/表格)   │
│          │                    ├──────────────┤
│  新建会话  │  用户输入自然语言     │  数据库工具    │
│  历史会话  │  AI 流式回复        │  表结构浏览    │
│          │  中间过程折叠（流式展开/完成后收缩） │  SQL 编辑器    │
│          │                    │  分页查询结果   │
└──────────┴────────────────────┴──────────────┘
```

## API 接口

### 会话管理

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/sessions` | 创建会话 |
| GET | `/api/sessions` | 会话列表 |
| GET | `/api/sessions/:id` | 会话详情（含消息） |
| PUT | `/api/sessions/:id` | 更新标题 |
| DELETE | `/api/sessions/:id` | 删除会话 |

### 聊天

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/chat/:sessionId/stream` | SSE 流式聊天 |

**SSE 事件类型**：`thinking`（累积思考过程）、`token`（文本片段）、`sql`（SQL 语句）、`chart`（图表配置）、`done`（结束）、`error`（错误）

### 数据库工具

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/database/schema` | 获取所有表结构 |
| POST | `/api/database/query` | 执行 SQL 查询（分页） |

## 示例数据库

系统支持两种数据源：

1. **backend/data/business.db**：首次启动时由 `sample_data.py` 自动创建  
2. **sql_repo/data/test.db**：独立测试库，每表 100+ 行 mock 数据，运行 `python sql_repo/init_db.py` 初始化，支持 `--force` 重建

销售业务示例数据库包含以下 4 张表：

| 表名 | 说明 | 主要字段 |
|---|---|---|
| `departments` | 部门 | id, name, manager, budget |
| `employees` | 员工 | id, name, department_id, position, salary, hire_date |
| `products` | 产品 | id, name, category, price, stock |
| `sales` | 销售记录 | id, employee_id, product_id, amount, quantity, sale_date |

**示例查询**：
- "各部门的销售总额是多少？"
- "哪个产品的销售量最高？"
- "上个月的销售趋势如何？"
- "薪资最高的 5 位员工是谁？"

## 开发说明

- 后端使用 `--reload` 参数启动可实现热更新：`python -m uvicorn app.main:app --reload --port 8000`
- 前端 Vite 开发服务器自带 HMR 热更新
- 前端通过 Vite proxy 将 `/api` 请求代理到后端 `127.0.0.1:8000`，开发时无需处理跨域

## License

MIT
