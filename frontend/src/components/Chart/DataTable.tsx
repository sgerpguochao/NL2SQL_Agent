import type { TableData } from '../../types'

interface Props {
  data: TableData
}

export function DataTable({ data }: Props) {
  if (!data.columns.length || !data.rows.length) {
    return <p className="text-sm text-gray-500 text-center py-4">暂无数据</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            {data.columns.map((col, i) => (
              <th
                key={i}
                className="px-4 py-2.5 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider bg-gray-700 border-b border-gray-600 first:rounded-tl-lg last:rounded-tr-lg"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.rows.map((row, ri) => (
            <tr
              key={ri}
              className={`border-b border-gray-700/50 transition-colors hover:bg-gray-700/40 ${
                ri % 2 === 0 ? 'bg-gray-800' : 'bg-gray-800/60'
              }`}
            >
              {row.map((cell, ci) => (
                <td key={ci} className="px-4 py-2.5 text-gray-300 whitespace-nowrap">
                  {typeof cell === 'number' ? cell.toLocaleString('zh-CN') : cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-2 text-xs text-gray-500 text-right">
        共 {data.rows.length} 条记录
      </div>
    </div>
  )
}
