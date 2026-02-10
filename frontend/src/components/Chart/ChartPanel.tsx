import { useState, useEffect } from 'react'
import { useChatStore } from '../../stores/chatStore'
import { DynamicChart } from './DynamicChart'
import { DataTable } from './DataTable'

type ViewMode = 'chart' | 'table'

export function ChartPanel() {
  const chartData = useChatStore((s) => s.chartData)
  const [viewMode, setViewMode] = useState<ViewMode>('chart')

  // chartData 变化时自动切回图表视图（如点击"在右侧查看大图"）
  useEffect(() => {
    if (chartData && chartData.chart_type !== 'table') {
      setViewMode('chart')
    }
  }, [chartData])

  const effectiveMode =
    chartData?.chart_type === 'table' ? 'table' : viewMode

  const hasChart = chartData && chartData.chart_type !== 'table'
  const hasTable = chartData?.table_data

  return (
    <div className="flex flex-col h-full">
      {/* 标题栏 */}
      <div
        className="px-5 py-3 border-b"
        style={{ borderColor: 'var(--tech-border)', backgroundColor: 'var(--tech-bg-panel)' }}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium flex items-center gap-2" style={{ color: 'var(--tech-text)' }}>
            <svg className="w-4 h-4" style={{ color: 'var(--tech-accent)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            数据可视化
          </h2>

          {chartData && hasChart && hasTable && (
            <div
              className="flex rounded-lg p-0.5"
              style={{ backgroundColor: 'var(--tech-bg-card)' }}
            >
              <button
                onClick={() => setViewMode('chart')}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  effectiveMode === 'chart'
                    ? 'shadow-sm font-medium'
                    : ''
                }`}
                style={
                  effectiveMode === 'chart'
                    ? { backgroundColor: 'var(--tech-accent)', color: '#fff' }
                    : { color: 'var(--tech-text-muted)' }
                }
              >
                图表
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  effectiveMode === 'table'
                    ? 'shadow-sm font-medium'
                    : ''
                }`}
                style={
                  effectiveMode === 'table'
                    ? { backgroundColor: 'var(--tech-accent)', color: '#fff' }
                    : { color: 'var(--tech-text-muted)' }
                }
              >
                表格
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-y-auto p-5">
        {chartData ? (
          <div>
            {effectiveMode === 'chart' && hasChart && chartData.echarts_option && (
              <div
                className="rounded-xl p-4"
                style={{ backgroundColor: 'var(--tech-bg-card)', border: '1px solid var(--tech-border)' }}
              >
                <DynamicChart option={chartData.echarts_option} />
              </div>
            )}

            {effectiveMode === 'table' && hasTable && (
              <div
                className="rounded-xl p-4"
                style={{ backgroundColor: 'var(--tech-bg-card)', border: '1px solid var(--tech-border)' }}
              >
                <DataTable data={chartData.table_data!} />
              </div>
            )}

            {chartData.chart_type === 'table' && !hasTable && (
              <div
                className="rounded-xl p-8 text-center"
                style={{ backgroundColor: 'var(--tech-bg-card)', border: '1px solid var(--tech-border)', color: 'var(--tech-text-muted)' }}
              >
                <p className="text-sm">表格数据加载中...</p>
              </div>
            )}

            <div className="mt-3 flex items-center gap-2 text-xs" style={{ color: 'var(--tech-text-muted)' }}>
              <span
                className="px-2 py-0.5 rounded-full"
                style={{ backgroundColor: 'var(--tech-bg-elevated)', color: 'var(--tech-accent)' }}
              >
                {chartData.chart_type}
              </span>
              <span>由 AI 自动选择展示方式</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full" style={{ color: 'var(--tech-text-muted)' }}>
            <div className="text-center">
              <svg className="w-20 h-20 mx-auto mb-4 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
              </svg>
              <p className="text-sm">查询数据后将在此展示图表</p>
              <p className="text-xs mt-1 opacity-80">支持柱状图、折线图、饼图、表格等</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
