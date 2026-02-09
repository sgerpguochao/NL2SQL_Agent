/**
 * 会话状态管理 —— 对接后端 REST API
 */

import { create } from 'zustand'
import type { Session } from '../types'
import {
  createSessionApi,
  fetchSessionsApi,
  deleteSessionApi,
  updateSessionTitleApi,
} from '../api/client'

interface SessionState {
  sessions: Session[]
  activeSessionId: string | null
  loading: boolean

  fetchSessions: () => Promise<void>
  createSession: () => Promise<string>
  deleteSession: (id: string) => Promise<void>
  setActiveSession: (id: string) => void
  updateSessionTitle: (id: string, title: string) => Promise<void>
}

export const useSessionStore = create<SessionState>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  loading: false,

  fetchSessions: async () => {
    set({ loading: true })
    try {
      const sessions = await fetchSessionsApi()
      set({ sessions, loading: false })
      const { activeSessionId } = get()
      if (!activeSessionId && sessions.length > 0) {
        set({ activeSessionId: sessions[0].id })
      }
    } catch (err) {
      console.error('[SessionStore] fetchSessions failed:', err)
      set({ loading: false })
    }
  },

  createSession: async () => {
    try {
      const session = await createSessionApi()
      set((state) => ({
        sessions: [session, ...state.sessions],
        activeSessionId: session.id,
      }))
      return session.id
    } catch (err) {
      console.error('[SessionStore] createSession failed:', err)
      throw err
    }
  },

  deleteSession: async (id) => {
    try {
      await deleteSessionApi(id)
      const { sessions, activeSessionId } = get()
      const filtered = sessions.filter((s) => s.id !== id)
      set({
        sessions: filtered,
        activeSessionId:
          activeSessionId === id
            ? filtered.length > 0
              ? filtered[0].id
              : null
            : activeSessionId,
      })
    } catch (err) {
      console.error('[SessionStore] deleteSession failed:', err)
    }
  },

  setActiveSession: (id) => {
    set({ activeSessionId: id })
  },

  updateSessionTitle: async (id, title) => {
    try {
      const updated = await updateSessionTitleApi(id, title)
      set((state) => ({
        sessions: state.sessions.map((s) =>
          s.id === id ? { ...s, title: updated.title, updated_at: updated.updated_at } : s
        ),
      }))
    } catch (err) {
      console.error('[SessionStore] updateSessionTitle failed:', err)
    }
  },
}))
