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

interface ChatState {
  messages: Message[]
  isStreaming: boolean
  streamingContent: string
  streamingSql: string | null
  chartData: ChartData | null

  sendMessage: (sessionId: string, content: string) => Promise<void>
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
  }
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isStreaming: false,
  streamingContent: '',
  streamingSql: null,
  chartData: null,

  sendMessage: async (sessionId, content) => {
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
    }))

    let finalContent = ''
    let finalSql: string | null = null
    let finalChart: ChartData | null = null

    try {
      await sendChatMessageApi(sessionId, content, {
        onToken: (text) => {
          finalContent += text
          set({ streamingContent: finalContent })
        },
        onSql: (sql) => {
          finalSql = sql
          set({ streamingSql: sql })
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
            chart_data: finalChart,
          }
          set((state) => ({
            messages: [...state.messages, assistantMsg],
            isStreaming: false,
            streamingContent: '',
            streamingSql: null,
          }))
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
          }))
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
      }))
    }
  },

  setChartData: (data) => set({ chartData: data }),

  clearMessages: () => set({ messages: [], chartData: null, streamingContent: '', streamingSql: null }),

  loadSessionMessages: async (sessionId) => {
    try {
      const detail = await getSessionDetailApi(sessionId)
      const messages = detail.messages.map((msg, i) => toFrontendMessage(msg, sessionId, i))
      set({ messages, chartData: null, streamingContent: '', streamingSql: null })
    } catch (err) {
      console.error('[ChatStore] loadSessionMessages failed:', err)
      set({ messages: [], chartData: null })
    }
  },
}))
