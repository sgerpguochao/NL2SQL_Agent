import type { Message } from '../../types'
import { useChatStore } from '../../stores/chatStore'

interface Props {
  message: Message
}

export function MessageItem({ message }: Props) {
  const setChartData = useChatStore((s) => s.setChartData)
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-gray-600' : 'bg-gray-700'
        }`}
      >
        <span className="text-sm font-medium text-gray-200">
          {isUser ? 'U' : 'AI'}
        </span>
      </div>

      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-gray-700 text-gray-100 rounded-tr-sm'
            : 'bg-gray-800 text-gray-200 rounded-tl-sm'
        }`}
      >
        {message.sql && !isUser && (
          <div className="mb-2 text-xs bg-gray-700 rounded-lg px-3 py-2 font-mono text-gray-300 overflow-x-auto">
            <span className="text-gray-500">SQL: </span>
            {message.sql}
          </div>
        )}

        <div className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</div>

        {message.chart_data && (
          <button
            onClick={() => setChartData(message.chart_data!)}
            className={`mt-2 flex items-center gap-1 text-xs px-2.5 py-1 rounded-full transition-colors ${
              isUser
                ? 'bg-gray-600 hover:bg-gray-500 text-gray-200'
                : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
            }`}
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            查看图表
          </button>
        )}
      </div>
    </div>
  )
}
