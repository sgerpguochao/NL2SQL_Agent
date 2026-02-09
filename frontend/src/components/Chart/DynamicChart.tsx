import ReactECharts from 'echarts-for-react'

interface Props {
  option: Record<string, unknown>
}

/** 深色主题下的 ECharts 全局默认配置 */
const darkThemeDefaults = {
  backgroundColor: 'transparent',
  textStyle: { color: '#9ca3af' },
  legend: { textStyle: { color: '#9ca3af' } },
  xAxis: { axisLine: { lineStyle: { color: '#4b5563' } }, axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: '#374151' } } },
  yAxis: { axisLine: { lineStyle: { color: '#4b5563' } }, axisLabel: { color: '#9ca3af' }, splitLine: { lineStyle: { color: '#374151' } } },
}

export function DynamicChart({ option }: Props) {
  // 合并深色主题默认配置
  const mergedOption = { ...darkThemeDefaults, ...option }

  return (
    <ReactECharts
      option={mergedOption}
      style={{ height: '350px', width: '100%' }}
      opts={{ renderer: 'canvas' }}
      notMerge={true}
      lazyUpdate={true}
    />
  )
}
