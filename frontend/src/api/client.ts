/**
 * API 客户端 —— REST (Axios) + SSE 流式 (Fetch + ReadableStream)
 *
 * 后端接口一览：
 *  REST:
 *    POST   /api/sessions                       创建会话
 *    GET    /api/sessions                       会话列表
 *    GET    /api/sessions/:id                   会话详情（含消息）
 *    PUT    /api/sessions/:id                   更新标题
 *    DELETE /api/sessions/:id                   删除会话
 *    GET    /api/database/schema?connection_id=  数据库表结构（需要 connection_id）
 *    POST   /api/database/query                 SQL 查询（需要 connection_id）
 *    GET    /api/connections                    连接列表
 *    POST   /api/connections                    新增连接
 *    GET    /api/connections/:id                连接详情
 *    PUT    /api/connections/:id                更新连接
 *    DELETE /api/connections/:id                删除连接
 *    POST   /api/connections/test               测试连接（不保存）
 *    POST   /api/connections/:id/test           测试已保存连接
 *  SSE:
 *    POST   /api/chat/:sessionId/stream         聊天流式接口（需要 connection_id）
 */

import axios from 'axios'
import type {
  Session,
  ChartData,
  TableSchema,
  SqlQueryResult,
  MySQLConnection,
  MySQLConnectionCreate,
  MySQLConnectionUpdate,
  ConnectionTestRequest,
  ConnectionTestResult,
} from '../types'

// ======================== Axios 实例 ========================

const api = axios.create({
  baseURL: '/api',
  timeout: 60_000, // 60s，避免冷启动或慢请求（会话/数据库/LLM）触发超时
  headers: { 'Content-Type': 'application/json' },
})

// 统一错误处理
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || '请求失败'
    console.error('[API Error]', msg)
    return Promise.reject(new Error(msg))
  },
)

// ======================== 会话 REST API ========================

/** 后端会话详情响应（含消息列表） */
export interface BackendMessage {
  role: string
  content: string
  timestamp: string
  thinking_process?: string | null
}

export interface SessionDetail extends Session {
  messages: BackendMessage[]
}

/** 创建会话 */
export async function createSessionApi(title?: string): Promise<Session> {
  const { data } = await api.post<Session>('/sessions', title ? { title } : {})
  return data
}

/** 获取会话列表 */
export async function fetchSessionsApi(): Promise<Session[]> {
  const { data } = await api.get<Session[]>('/sessions')
  return data
}

/** 获取会话详情（含消息列表） */
export async function getSessionDetailApi(id: string): Promise<SessionDetail> {
  const { data } = await api.get<SessionDetail>(`/sessions/${id}`)
  return data
}

/** 更新会话标题 */
export async function updateSessionTitleApi(id: string, title: string): Promise<Session> {
  const { data } = await api.put<Session>(`/sessions/${id}`, { title })
  return data
}

/** 删除会话 */
export async function deleteSessionApi(id: string): Promise<void> {
  await api.delete(`/sessions/${id}`)
}

// ======================== 数据库工具 API ========================

/** 获取数据库 schema（所有表结构，需要 connection_id） */
export async function fetchSchemaApi(connectionId: string): Promise<{ tables: TableSchema[] }> {
  const { data } = await api.get<{ tables: TableSchema[] }>('/database/schema', {
    params: { connection_id: connectionId },
  })
  return data
}

/** 执行 SQL 查询（仅 SELECT，带分页，需要 connection_id） */
export async function executeSqlApi(
  connectionId: string,
  sql: string,
  page: number = 1,
  pageSize: number = 50,
): Promise<SqlQueryResult> {
  const { data } = await api.post<SqlQueryResult>('/database/query', {
    connection_id: connectionId,
    sql,
    page,
    page_size: pageSize,
  })
  return data
}

// ======================== SSE 聊天流式接口 ========================

/** SSE 事件回调 */
export interface SSECallbacks {
  /** 收到文本片段（仅最终回答） */
  onToken: (content: string) => void
  /** 收到 SQL 语句 */
  onSql: (sql: string) => void
  /** 收到思考过程（用户问题+推理步骤+回答，追加累积） */
  onThinking: (content: string) => void
  /** 收到图表配置 */
  onChart: (chartData: ChartData) => void
  /** 流结束 */
  onDone: () => void
  /** 发生错误 */
  onError: (message: string) => void
}

/**
 * 发送聊天消息并通过 SSE 接收流式响应
 * @param connectionId MySQL 连接 ID（后端必需字段）
 */
export async function sendChatMessageApi(
  sessionId: string,
  message: string,
  connectionId: string,
  callbacks: SSECallbacks,
): Promise<void> {
  const response = await fetch(`/api/chat/${sessionId}/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, connection_id: connectionId }),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`HTTP ${response.status}: ${text}`)
  }

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    // SSE 协议：每个事件以 \n\n 分隔
    const parts = buffer.split('\n\n')
    buffer = parts.pop() || ''

    for (const part of parts) {
      if (!part.trim()) continue

      let eventType = ''
      let eventData = ''

      for (const line of part.split('\n')) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          eventData = line.slice(6)
        }
      }

      if (!eventType || !eventData) continue

      try {
        const parsed = JSON.parse(eventData)

        switch (eventType) {
          case 'token':
            if (parsed.content) {
              callbacks.onToken(parsed.content)
            }
            break
          case 'sql':
            if (parsed.sql) {
              callbacks.onSql(parsed.sql)
            }
            break
          case 'thinking':
            if (parsed.content) {
              callbacks.onThinking(parsed.content)
            }
            break
          case 'chart':
            callbacks.onChart(parsed as ChartData)
            break
          case 'done':
            callbacks.onDone()
            break
          case 'error':
            callbacks.onError(parsed.message || '未知错误')
            break
        }
      } catch {
        console.warn('[SSE] Failed to parse event data:', eventData)
      }
    }
  }
}

// ======================== MySQL 连接管理 API ========================

/** 连接列表响应（后端返回 { connections: [...] }） */
interface ConnectionListResponse {
  connections: MySQLConnection[]
}

/** 获取所有连接配置 */
export async function fetchConnectionsApi(): Promise<MySQLConnection[]> {
  const { data } = await api.get<ConnectionListResponse>('/connections')
  return data.connections
}

/** 新增连接 */
export async function createConnectionApi(body: MySQLConnectionCreate): Promise<MySQLConnection> {
  const { data } = await api.post<MySQLConnection>('/connections', body)
  return data
}

/** 获取单个连接详情 */
export async function getConnectionApi(connId: string): Promise<MySQLConnection> {
  const { data } = await api.get<MySQLConnection>(`/connections/${connId}`)
  return data
}

/** 更新连接配置 */
export async function updateConnectionApi(connId: string, body: MySQLConnectionUpdate): Promise<MySQLConnection> {
  const { data } = await api.put<MySQLConnection>(`/connections/${connId}`, body)
  return data
}

/** 删除连接 */
export async function deleteConnectionApi(connId: string): Promise<void> {
  await api.delete(`/connections/${connId}`)
}

/** 测试连接（不保存，仅验证参数） */
export async function testConnectionApi(body: ConnectionTestRequest): Promise<ConnectionTestResult> {
  const { data } = await api.post<ConnectionTestResult>('/connections/test', body)
  return data
}

/** 测试已保存的连接 */
export async function testConnectionByIdApi(connId: string): Promise<ConnectionTestResult> {
  const { data } = await api.post<ConnectionTestResult>(`/connections/${connId}/test`)
  return data
}
