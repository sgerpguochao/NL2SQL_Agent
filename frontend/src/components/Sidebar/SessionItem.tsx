import { useState } from 'react'
import type { Session } from '../../types'

interface Props {
  session: Session
  isActive: boolean
  onSelect: () => void
  onDelete: () => void
}

export function SessionItem({ session, isActive, onSelect, onDelete }: Props) {
  const [hovering, setHovering] = useState(false)

  const timeStr = new Date(session.updated_at).toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div
      className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
        !isActive ? 'hover:bg-[var(--tech-bg-elevated)]/50' : ''
      }`}
      style={{
        backgroundColor: isActive ? 'var(--tech-bg-elevated)' : 'transparent',
        color: isActive ? 'var(--tech-text)' : 'var(--tech-text-muted)',
        border: isActive ? '1px solid var(--tech-border)' : '1px solid transparent',
      }}
      onClick={onSelect}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      {/* 会话图标 */}
      <svg className="w-4 h-4 flex-shrink-0 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>

      {/* 标题 + 时间 */}
      <div className="flex-1 min-w-0">
        <p className="text-sm truncate">{session.title}</p>
        <p className="text-xs mt-0.5" style={{ color: 'var(--tech-text-muted)' }}>{timeStr}</p>
      </div>

      {/* 删除按钮 */}
      {hovering && (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete()
          }}
          className="flex-shrink-0 p-1 rounded hover:bg-gray-700 transition-colors"
          title="删除会话"
        >
          <svg className="w-3.5 h-3.5 text-gray-500 hover:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      )}
    </div>
  )
}
