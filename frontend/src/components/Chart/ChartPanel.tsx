import { useState } from 'react'
import { useChatStore } from '../../stores/chatStore'
import { DynamicChart } from './DynamicChart'
import { DataTable } from './DataTable'

type ViewMode = 'chart' | 'table'

export function ChartPanel() {
  const chartData = useChatStore((s) => s.chartData)
  const [viewMode, setViewMode] = useState<ViewMode>('chart')

  const effectiveMode =
    chartData?.chart_type === 'table' ? 'table' : viewMode

  const hasChart = chartData && chartData.chart_type !== 'table'
  const hasTable = chartData?.table_data

  return (
    <div className="flex flex-col h-full">
      {/* 标题栏 */}
      <div className="px-5 py-3 border-b border-gray-700/50 bg-gray-900">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            数据可视化
          </h2>

          {chartData && hasChart && hasTable && (
            <div className="flex bg-gray-800 rounded-lg p-0.5">
              <button
                onClick={() => setViewMode('chart')}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  effectiveMode === 'chart'
                    ? 'bg-gray-700 text-gray-100 shadow-sm font-medium'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
              >
                图表
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  effectiveMode === 'table'
                    ? 'bg-gray-700 text-gray-100 shadow-sm font-medium'
                    : 'text-gray-500 hover:text-gray-300'
                }`}
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
              <div className="bg-gray-800 rounded-xl border border-gray-700/50 p-4">
                <DynamicChart option={chartData.echarts_option} />
              </div>
            )}

            {effectiveMode === 'table' && hasTable && (
              <div className="bg-gray-800 rounded-xl border border-gray-700/50 p-4">
                <DataTable data={chartData.table_data!} />
              </div>
            )}

            {chartData.chart_type === 'table' && !hasTable && (
              <div className="bg-gray-800 rounded-xl border border-gray-700/50 p-8 text-center text-gray-500">
                <p className="text-sm">表格数据加载中...</p>
              </div>
            )}

            <div className="mt-3 flex items-center gap-2 text-xs text-gray-500">
              <span className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded-full">
                {chartData.chart_type}
              </span>
              <span>由 AI 自动选择展示方式</span>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <svg className="w-20 h-20 mx-auto mb-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
              </svg>
              <p className="text-sm text-gray-400">查询数据后将在此展示图表</p>
              <p className="text-xs text-gray-600 mt-1">支持柱状图、折线图、饼图、表格等</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
