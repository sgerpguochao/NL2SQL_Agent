import { useState, useRef, type KeyboardEvent } from 'react'
import { useChatStore } from '../../stores/chatStore'
import { useSessionStore } from '../../stores/sessionStore'

interface Props {
  /** 当前活动的 MySQL 连接 ID */
  connectionId?: string
}

export function ChatInput({ connectionId }: Props) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const activeSessionId = useSessionStore((s) => s.activeSessionId)
  const { isStreaming, sendMessage } = useChatStore()

  const canSend = !!input.trim() && !!activeSessionId && !isStreaming && !!connectionId

  const handleSend = async () => {
    const text = input.trim()
    if (!text || !activeSessionId || isStreaming || !connectionId) return

    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    await sendMessage(activeSessionId, text, connectionId)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    const el = e.target
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 150) + 'px'
  }

  return (
    <div
      className="px-6 py-4 border-t rounded-xl"
      style={{ borderColor: 'var(--tech-border)', backgroundColor: 'var(--tech-bg-panel)' }}
    >
      <div
        className="flex items-end gap-3 rounded-xl px-4 py-3"
        style={{ backgroundColor: 'var(--tech-bg-card)', border: '1px solid var(--tech-border)' }}
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={connectionId ? '输入自然语言查询，如：上个月的销售总额是多少？' : '请先选择数据库连接...'}
          rows={1}
          className="flex-1 bg-transparent resize-none outline-none text-sm text-gray-100 placeholder-gray-500 max-h-[150px]"
          disabled={isStreaming || !connectionId}
        />
        <button
          onClick={handleSend}
          disabled={!canSend}
          className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center transition-colors ${
            canSend
              ? 'text-white'
              : 'cursor-not-allowed'
          }`}
          style={
            canSend
              ? { backgroundColor: 'var(--tech-accent)' }
              : { backgroundColor: 'var(--tech-bg-elevated)', color: 'var(--tech-text-muted)' }
          }
        >
          {isStreaming ? (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19V5m0 0l-7 7m7-7l7 7" />
            </svg>
          )}
        </button>
      </div>
      <p className="text-xs text-gray-600 mt-2 text-center">
        Enter 发送 / Shift + Enter 换行
      </p>
    </div>
  )
}
