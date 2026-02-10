/**
 * API 客户端 —— REST (Axios) + SSE 流式 (Fetch + ReadableStream)
 *
 * 后端接口一览：
 *  REST:
 *    POST   /api/sessions              创建会话
 *    GET    /api/sessions              会话列表
 *    GET    /api/sessions/:id          会话详情（含消息）
 *    PUT    /api/sessions/:id          更新标题
 *    DELETE /api/sessions/:id          删除会话
 *    GET    /api/database/schema       数据库表结构
 *    POST   /api/database/query        SQL 查询（分页）
 *  SSE:
 *    POST   /api/chat/:sessionId/stream  聊天流式接口
 */

import axios from 'axios'
import type { Session, ChartData, TableSchema, SqlQueryResult } from '../types'

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

/** 获取数据库 schema（所有表结构） */
export async function fetchSchemaApi(): Promise<{ tables: TableSchema[] }> {
  const { data } = await api.get<{ tables: TableSchema[] }>('/database/schema')
  return data
}

/** 执行 SQL 查询（仅 SELECT，带分页） */
export async function executeSqlApi(
  sql: string,
  page: number = 1,
  pageSize: number = 50,
): Promise<SqlQueryResult> {
  const { data } = await api.post<SqlQueryResult>('/database/query', {
    sql,
    page,
    page_size: pageSize,
  })
  return data
}

// ======================== SSE 聊天流式接口 ========================

/** SSE 事件回调 */
export interface SSECallbacks {
  /** 收到文本片段 */
  onToken: (content: string) => void
  /** 收到 SQL 语句 */
  onSql: (sql: string) => void
  /** 收到图表配置 */
  onChart: (chartData: ChartData) => void
  /** 流结束 */
  onDone: () => void
  /** 发生错误 */
  onError: (message: string) => void
}

/**
 * 发送聊天消息并通过 SSE 接收流式响应
 */
export async function sendChatMessageApi(
  sessionId: string,
  message: string,
  callbacks: SSECallbacks,
): Promise<void> {
  const response = await fetch(`/api/chat/${sessionId}/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
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
