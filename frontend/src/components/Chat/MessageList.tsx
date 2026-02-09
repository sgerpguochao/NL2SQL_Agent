import { useEffect, useRef } from 'react'
import { useChatStore } from '../../stores/chatStore'
import { MessageItem } from './MessageItem'

export function MessageList() {
  const messages = useChatStore((s) => s.messages)
  const isStreaming = useChatStore((s) => s.isStreaming)
  const streamingContent = useChatStore((s) => s.streamingContent)
  const streamingSql = useChatStore((s) => s.streamingSql)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
      {messages.length === 0 && !isStreaming ? (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <p className="text-lg mb-2 text-gray-400">开始提问吧</p>
            <p className="text-sm text-gray-600">输入自然语言查询数据库，AI 会为你生成结果和图表</p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <MessageItem key={msg.id} message={msg} />
          ))}

          {isStreaming && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
                <span className="text-gray-300 text-sm font-medium">AI</span>
              </div>
              <div className="max-w-[75%] rounded-2xl rounded-tl-sm px-4 py-3 bg-gray-800 text-gray-200">
                {streamingContent ? (
                  <div>
                    {streamingSql && (
                      <div className="mb-2 text-xs bg-gray-700 rounded-lg px-3 py-2 font-mono text-gray-300 overflow-x-auto">
                        <span className="text-gray-500">SQL: </span>
                        {streamingSql}
                      </div>
                    )}
                    <div className="text-sm leading-relaxed whitespace-pre-wrap">
                      {streamingContent}
                      <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-0.5 align-text-bottom" />
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    <span className="text-xs text-gray-500">AI 正在思考中...</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      <div ref={bottomRef} />
    </div>
  )
}
