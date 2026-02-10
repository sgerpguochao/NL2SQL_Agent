import type { Message } from '../../types'
import { useChatStore } from '../../stores/chatStore'
import { MarkdownContent } from './MarkdownContent'
import { CollapsibleProcess } from './CollapsibleProcess'
import { DynamicChart } from '../Chart/DynamicChart'
import { DataTable } from '../Chart/DataTable'

interface Props {
  message: Message
}

export function MessageItem({ message }: Props) {
  const setChartData = useChatStore((s) => s.setChartData)
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: isUser ? 'rgba(59, 130, 246, 0.8)' : 'var(--tech-accent)' }}
      >
        {isUser ? (
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        ) : (
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
          </svg>
        )}
      </div>

      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 ${isUser ? 'rounded-tr-sm' : 'rounded-tl-sm'}`}
        style={{
          backgroundColor: isUser ? 'var(--tech-bg-elevated)' : 'var(--tech-bg-card)',
          color: 'var(--tech-text)',
          border: '1px solid var(--tech-border)',
        }}
      >
        {!isUser && (message.thinking_process || message.sql) && (
          <div className="mb-2">
            <CollapsibleProcess title="中间过程" defaultExpanded={false}>
              {message.thinking_process ? (
                <div className="text-sm whitespace-pre-wrap" style={{ color: 'var(--tech-text-muted)' }}>
                  <MarkdownContent content={message.thinking_process} />
                </div>
              ) : (
                <div className="font-mono text-gray-300 overflow-x-auto whitespace-pre">
                  <span className="text-gray-500">SQL: </span>
                  {message.sql}
                </div>
              )}
            </CollapsibleProcess>
          </div>
        )}

        {isUser ? (
          <div className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</div>
        ) : (
          <MarkdownContent content={message.content} />
        )}

        {message.chart_data && !isUser && (
          <div
            className="mt-3 rounded-xl overflow-hidden"
            style={{ border: '1px solid var(--tech-border)', backgroundColor: 'rgba(6, 182, 212, 0.05)' }}
          >
            <div
              className="px-3 py-2 flex items-center justify-between"
              style={{ borderBottom: '1px solid var(--tech-border)' }}
            >
              <span className="text-xs font-medium text-gray-400">图表展示</span>
              <button
                onClick={() => setChartData(message.chart_data!)}
                className="text-xs text-sky-400 hover:text-sky-300"
              >
                <span style={{ color: 'var(--tech-accent)' }}>在右侧查看大图</span>
              </button>
            </div>
            <div className="p-3 min-h-[200px]">
              {message.chart_data.chart_type !== 'table' && message.chart_data.echarts_option && (
                <DynamicChart option={message.chart_data.echarts_option} height={260} />
              )}
              {(message.chart_data.chart_type === 'table' || message.chart_data.table_data) && message.chart_data.table_data && (
                <DataTable data={message.chart_data.table_data} />
              )}
              {message.chart_data.chart_type !== 'table' && !message.chart_data.echarts_option && message.chart_data.table_data && (
                <DataTable data={message.chart_data.table_data} />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
