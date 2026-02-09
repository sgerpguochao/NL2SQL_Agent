import { useEffect } from 'react'
import { useSessionStore } from '../../stores/sessionStore'
import { useChatStore } from '../../stores/chatStore'
import { SessionItem } from './SessionItem'

export function Sidebar() {
  const { sessions, activeSessionId, loading, fetchSessions, createSession, setActiveSession, deleteSession } =
    useSessionStore()
  const { loadSessionMessages, clearMessages } = useChatStore()

  useEffect(() => {
    fetchSessions()
  }, [fetchSessions])

  useEffect(() => {
    if (activeSessionId) {
      loadSessionMessages(activeSessionId)
    } else {
      clearMessages()
    }
  }, [activeSessionId, loadSessionMessages, clearMessages])

  const handleSelect = (id: string) => {
    if (id === activeSessionId) return
    setActiveSession(id)
  }

  const handleCreate = async () => {
    try {
      await createSession()
    } catch {
      // error logged in store
    }
  }

  const handleDelete = async (id: string) => {
    await deleteSession(id)
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-4 border-b border-gray-800">
        <h1 className="text-lg font-semibold tracking-wide text-gray-100">NL2SQL</h1>
        <p className="text-xs text-gray-500 mt-0.5">智能数据分析助手</p>
      </div>

      <div className="px-3 py-3">
        <button
          onClick={handleCreate}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg border border-gray-700 hover:bg-gray-800 transition-colors text-sm text-gray-300"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          新建会话
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 space-y-0.5">
        {loading && sessions.length === 0 ? (
          <p className="text-center text-gray-600 text-sm mt-8">加载中...</p>
        ) : sessions.length === 0 ? (
          <p className="text-center text-gray-600 text-sm mt-8">暂无会话，点击上方按钮创建</p>
        ) : (
          sessions.map((session) => (
            <SessionItem
              key={session.id}
              session={session}
              isActive={session.id === activeSessionId}
              onSelect={() => handleSelect(session.id)}
              onDelete={() => handleDelete(session.id)}
            />
          ))
        )}
      </div>
    </div>
  )
}
