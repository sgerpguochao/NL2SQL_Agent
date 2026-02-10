import { useEffect, useRef } from 'react'
import { useChatStore } from '../../stores/chatStore'
import { MessageItem } from './MessageItem'
import { MarkdownContent } from './MarkdownContent'
import { CollapsibleProcess } from './CollapsibleProcess'
import { DynamicChart } from '../Chart/DynamicChart'
import { DataTable } from '../Chart/DataTable'

export function MessageList() {
  const messages = useChatStore((s) => s.messages)
  const isStreaming = useChatStore((s) => s.isStreaming)
  const streamingContent = useChatStore((s) => s.streamingContent)
  const streamingSql = useChatStore((s) => s.streamingSql)
  const chartData = useChatStore((s) => s.chartData)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent, chartData])

  return (
    <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
      {messages.length === 0 && !isStreaming ? (
        <div className="flex items-center justify-center h-full" style={{ color: 'var(--tech-text-muted)' }}>
          <div className="text-center">
            <p className="text-lg mb-2">开始提问吧</p>
            <p className="text-sm opacity-80">输入自然语言查询数据库，AI 会为你生成结果和图表</p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <MessageItem key={msg.id} message={msg} />
          ))}

          {isStreaming && (
            <div className="flex gap-3">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: 'var(--tech-accent)' }}
              >
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                </svg>
              </div>
              <div
                className="max-w-[75%] rounded-2xl rounded-tl-sm px-4 py-3 space-y-2"
                style={{ backgroundColor: 'var(--tech-bg-card)', color: 'var(--tech-text)', border: '1px solid var(--tech-border)' }}
              >
                {(streamingSql || !streamingContent) && (
                  <CollapsibleProcess title="中间过程">
                    {!streamingContent && (
                      <div className="flex items-center gap-2 text-gray-500">
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                          <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                          <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                        <span className="text-xs">AI 正在思考中...</span>
                      </div>
                    )}
                    {streamingSql && (
                      <div className="font-mono text-gray-300 overflow-x-auto whitespace-pre mt-1">
                        <span className="text-gray-500">SQL: </span>
                        {streamingSql}
                      </div>
                    )}
                  </CollapsibleProcess>
                )}
                {streamingContent && (
                  <div className="relative">
                    <MarkdownContent content={streamingContent} />
                    <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-0.5 align-text-bottom" />
                  </div>
                )}
                {chartData && (
                  <div
                    className="mt-3 rounded-xl overflow-hidden"
                    style={{ border: '1px solid var(--tech-border)', backgroundColor: 'rgba(6, 182, 212, 0.05)' }}
                  >
                    <div
                      className="px-3 py-2 text-xs font-medium"
                      style={{ borderBottom: '1px solid var(--tech-border)', color: 'var(--tech-text-muted)' }}
                    >
                      图表展示
                    </div>
                    <div className="p-3 min-h-[200px]">
                      {chartData.chart_type !== 'table' && chartData.echarts_option && (
                        <DynamicChart option={chartData.echarts_option} height={260} />
                      )}
                      {(chartData.chart_type === 'table' || chartData.table_data) && chartData.table_data && (
                        <DataTable data={chartData.table_data} />
                      )}
                      {chartData.chart_type !== 'table' && !chartData.echarts_option && chartData.table_data && (
                        <DataTable data={chartData.table_data} />
                      )}
                    </div>
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
