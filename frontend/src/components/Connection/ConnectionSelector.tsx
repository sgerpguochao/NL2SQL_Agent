/**
 * 连接选择器 —— 轻量下拉组件
 *
 * 复用于 ChatPanel 标题栏和 DatabasePanel 顶部
 * 显示当前连接名称 + 数据库名，下拉切换连接
 */

import { useState, useRef, useEffect } from 'react'
import { useConnectionStore } from '../../stores/connectionStore'

interface Props {
  /** 额外 CSS 类名 */
  className?: string
  /** 是否紧凑模式（用于标题栏内嵌） */
  compact?: boolean
}

export function ConnectionSelector({ className = '', compact = false }: Props) {
  const connections = useConnectionStore((s) => s.connections)
  const activeConnectionId = useConnectionStore((s) => s.activeConnectionId)
  const connectionValid = useConnectionStore((s) => s.connectionValid)
  const setActiveConnection = useConnectionStore((s) => s.setActiveConnection)
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  // 当前活动连接
  const activeConn = connections.find((c) => c.id === activeConnectionId)

  // 点击外部关闭
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleSelect = async (id: string) => {
    setOpen(false)
    if (id !== activeConnectionId) {
      await setActiveConnection(id)
    }
  }

  // 状态指示颜色
  const statusColor = connectionValid ? '#22c55e' : '#ef4444'

  return (
    <div ref={ref} className={`relative ${className}`}>
      {/* 触发按钮 */}
      <button
        onClick={() => setOpen(!open)}
        className={`flex items-center gap-2 rounded-lg transition-colors ${
          compact ? 'px-2 py-1 text-xs' : 'px-3 py-1.5 text-xs'
        }`}
        style={{
          backgroundColor: 'var(--tech-bg-card)',
          border: '1px solid var(--tech-border)',
          color: 'var(--tech-text)',
        }}
      >
        {/* 状态指示点 */}
        <span
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: statusColor }}
        />

        {activeConn ? (
          <>
            <span className="truncate max-w-[120px]">{activeConn.name}</span>
            {!compact && (
              <span className="text-gray-500 truncate max-w-[80px]">
                {activeConn.database}
              </span>
            )}
          </>
        ) : (
          <span className="text-gray-500">选择连接...</span>
        )}

        {/* 下拉箭头 */}
        <svg
          className={`w-3 h-3 text-gray-500 transition-transform flex-shrink-0 ${open ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* 下拉列表 */}
      {open && connections.length > 0 && (
        <div
          className="absolute top-full left-0 mt-1 w-64 rounded-lg shadow-lg z-50 py-1 overflow-y-auto max-h-[240px]"
          style={{
            backgroundColor: 'var(--tech-bg-card)',
            border: '1px solid var(--tech-border)',
          }}
        >
          {connections.map((conn) => {
            const isActive = conn.id === activeConnectionId
            return (
              <button
                key={conn.id}
                onClick={() => handleSelect(conn.id)}
                className={`w-full text-left px-3 py-2 text-xs transition-colors flex items-center gap-2 ${
                  isActive ? 'font-medium' : ''
                }`}
                style={{
                  backgroundColor: isActive ? 'var(--tech-bg-elevated)' : 'transparent',
                  color: 'var(--tech-text)',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) e.currentTarget.style.backgroundColor = 'var(--tech-bg-elevated)'
                }}
                onMouseLeave={(e) => {
                  if (!isActive) e.currentTarget.style.backgroundColor = 'transparent'
                }}
              >
                {/* 选中标记 */}
                {isActive && (
                  <svg className="w-3 h-3 flex-shrink-0" style={{ color: 'var(--tech-accent)' }} fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                <div className={`flex-1 min-w-0 ${!isActive ? 'ml-5' : ''}`}>
                  <div className="truncate">{conn.name}</div>
                  <div className="text-gray-500 truncate text-[10px]">
                    {conn.host}:{conn.port}/{conn.database}
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
