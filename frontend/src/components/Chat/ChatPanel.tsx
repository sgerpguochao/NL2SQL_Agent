import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'
import { useSessionStore } from '../../stores/sessionStore'

export function ChatPanel() {
  const activeSessionId = useSessionStore((s) => s.activeSessionId)

  if (!activeSessionId) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500">
        <div className="text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p className="text-lg text-gray-400">选择或创建一个会话开始对话</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* 顶部标题栏 */}
      <div className="px-6 py-3 border-b border-gray-700/50 bg-gray-900">
        <h2 className="text-sm font-medium text-gray-300">
          {useSessionStore.getState().sessions.find((s) => s.id === activeSessionId)?.title || '对话'}
        </h2>
      </div>

      {/* 消息列表 */}
      <MessageList />

      {/* 输入区域 */}
      <ChatInput />
    </div>
  )
}
