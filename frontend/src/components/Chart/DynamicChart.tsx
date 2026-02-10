import ReactECharts from 'echarts-for-react'

interface Props {
  option: Record<string, unknown>
  /** 图表高度，默认 350px */
  height?: number | string
}

/** 科技感深色主题 ECharts 配置 */
const darkThemeDefaults = {
  backgroundColor: 'transparent',
  textStyle: { color: '#94a3b8' },
  legend: { textStyle: { color: '#94a3b8' } },
  xAxis: { axisLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.3)' } }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.08)' } } },
  yAxis: { axisLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.3)' } }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(6, 182, 212, 0.08)' } } },
}

export function DynamicChart({ option, height = '350px' }: Props) {
  // 合并深色主题默认配置
  const mergedOption = { ...darkThemeDefaults, ...option }
  const h = typeof height === 'number' ? `${height}px` : height

  return (
    <ReactECharts
      option={mergedOption}
      style={{ height: h, width: '100%' }}
      opts={{ renderer: 'canvas' }}
      notMerge={true}
      lazyUpdate={true}
    />
  )
}
