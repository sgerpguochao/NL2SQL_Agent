/**
 * 聊天状态管理 —— 对接后端 SSE 流式接口 + 会话消息加载
 */

import { create } from 'zustand'
import type { Message, ChartData } from '../types'
import {
  sendChatMessageApi,
  getSessionDetailApi,
  type BackendMessage,
} from '../api/client'
import { useSessionStore } from './sessionStore'

const MAX_TITLE_LENGTH = 24

/** 用首条用户消息生成会话标题（截断、去换行） */
function toSessionTitle(content: string): string {
  const oneLine = content.replace(/\s+/g, ' ').trim()
  if (!oneLine) return '新对话'
  return oneLine.length <= MAX_TITLE_LENGTH ? oneLine : oneLine.slice(0, MAX_TITLE_LENGTH) + '…'
}

interface ChatState {
  messages: Message[]
  isStreaming: boolean
  streamingContent: string
  streamingSql: string | null
  streamingThinking: string
  chartData: ChartData | null

  /** 发送消息，connectionId 为当前活动的 MySQL 连接 ID */
  sendMessage: (sessionId: string, content: string, connectionId: string) => Promise<void>
  setChartData: (data: ChartData | null) => void
  clearMessages: () => void
  loadSessionMessages: (sessionId: string) => Promise<void>
}

const genId = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 8)

function toFrontendMessage(msg: BackendMessage, sessionId: string, index: number): Message {
  return {
    id: `backend-${sessionId}-${index}`,
    session_id: sessionId,
    role: msg.role as 'user' | 'assistant',
    content: msg.content,
    timestamp: msg.timestamp,
    thinking_process: msg.thinking_process ?? null,
  }
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isStreaming: false,
  streamingContent: '',
  streamingSql: null,
  streamingThinking: '',
  chartData: null,

  sendMessage: async (sessionId, content, connectionId) => {
    const isFirstMessage = get().messages.length === 0

    const userMsg: Message = {
      id: genId(),
      session_id: sessionId,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    }
    set((state) => ({
      messages: [...state.messages, userMsg],
      isStreaming: true,
      streamingContent: '',
      streamingSql: null,
      streamingThinking: '',
      chartData: null, // 清空上一次图表，避免残留到新的流式气泡
    }))

    let finalContent = ''
    let finalSql: string | null = null
    let finalThinking = ''
    let finalChart: ChartData | null = null

    const updateTitleIfFirst = () => {
      if (isFirstMessage) {
        useSessionStore.getState().updateSessionTitle(sessionId, toSessionTitle(content))
      }
    }

    try {
      await sendChatMessageApi(sessionId, content, connectionId, {
        onToken: (text) => {
          finalContent += text
          set({ streamingContent: finalContent })
        },
        onSql: (sql) => {
          finalSql = sql
          set({ streamingSql: sql })
        },
        onThinking: (content) => {
          finalThinking = content
          set({ streamingThinking: content })
        },
        onChart: (chartData) => {
          finalChart = chartData
          set({ chartData })
        },
        onDone: () => {
          const assistantMsg: Message = {
            id: genId(),
            session_id: sessionId,
            role: 'assistant',
            content: finalContent || '（未获取到回复）',
            timestamp: new Date().toISOString(),
            sql: finalSql,
            thinking_process: finalThinking || null,
            chart_data: finalChart,
          }
          set((state) => ({
            messages: [...state.messages, assistantMsg],
            isStreaming: false,
            streamingContent: '',
            streamingSql: null,
            streamingThinking: '',
            ...(finalChart != null && { chartData: finalChart }),
          }))
          updateTitleIfFirst()
        },
        onError: (message) => {
          const errorMsg: Message = {
            id: genId(),
            session_id: sessionId,
            role: 'assistant',
            content: `[错误] ${message}`,
            timestamp: new Date().toISOString(),
          }
          set((state) => ({
            messages: [...state.messages, errorMsg],
            isStreaming: false,
            streamingContent: '',
            streamingSql: null,
            streamingThinking: '',
          }))
          updateTitleIfFirst()
        },
      })
    } catch (err) {
      const errorMsg: Message = {
        id: genId(),
        session_id: sessionId,
        role: 'assistant',
        content: `[请求失败] ${err instanceof Error ? err.message : '未知错误'}`,
        timestamp: new Date().toISOString(),
      }
      set((state) => ({
        messages: [...state.messages, errorMsg],
        isStreaming: false,
        streamingContent: '',
        streamingSql: null,
        streamingThinking: '',
      }))
      if (isFirstMessage) {
        useSessionStore.getState().updateSessionTitle(sessionId, toSessionTitle(content))
      }
    }
  },

  setChartData: (data) => set({ chartData: data }),

  clearMessages: () => set({ messages: [], chartData: null, streamingContent: '', streamingSql: null, streamingThinking: '' }),

  loadSessionMessages: async (sessionId) => {
    try {
      const detail = await getSessionDetailApi(sessionId)
      const messages = detail.messages.map((msg, i) => toFrontendMessage(msg, sessionId, i))
      set({ messages, chartData: null, streamingContent: '', streamingSql: null, streamingThinking: '' })
    } catch (err) {
      console.error('[ChatStore] loadSessionMessages failed:', err)
      set({ messages: [], chartData: null })
    }
  },
}))
