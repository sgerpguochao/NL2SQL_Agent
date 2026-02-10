import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'
import { useSessionStore } from '../../stores/sessionStore'
import { ConnectionSelector } from '../Connection/ConnectionSelector'

interface Props {
  /** 当前活动的 MySQL 连接 ID */
  connectionId?: string
}

export function ChatPanel({ connectionId }: Props) {
  const activeSessionId = useSessionStore((s) => s.activeSessionId)
  const activeTitle = useSessionStore((s) =>
    s.activeSessionId ? s.sessions.find((sess) => sess.id === s.activeSessionId)?.title ?? '对话' : ''
  )

  if (!activeSessionId) {
    return (
      <div className="flex-1 flex items-center justify-center" style={{ color: 'var(--tech-text-muted)' }}>
        <div className="text-center">
          <svg className="w-16 h-16 mx-auto mb-4 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p className="text-lg" style={{ color: 'var(--tech-text-muted)' }}>选择或创建一个会话开始对话</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* 顶部标题栏 */}
      <div
        className="px-6 py-3 border-b flex items-center justify-between"
        style={{ borderColor: 'var(--tech-border)', backgroundColor: 'var(--tech-bg-panel)' }}
      >
        <h2 className="text-sm font-medium" style={{ color: 'var(--tech-text)' }}>
          {activeTitle}
        </h2>
        {/* 连接选择器 */}
        <ConnectionSelector compact />
      </div>

      {/* 消息列表 */}
      <MessageList />

      {/* 输入区域 */}
      <ChatInput connectionId={connectionId} />
    </div>
  )
}
