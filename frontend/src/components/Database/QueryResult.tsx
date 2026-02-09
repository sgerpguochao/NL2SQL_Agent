import type { SqlQueryResult } from '../../types'

interface Props {
  result: SqlQueryResult
  onPageChange: (page: number) => void
}

export function QueryResult({ result, onPageChange }: Props) {
  if (!result.columns.length) {
    return <p className="text-sm text-gray-500 text-center py-4">查询无返回列</p>
  }

  return (
    <div className="flex flex-col h-full">
      {/* 表格区域 */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-xs border-collapse">
          <thead className="sticky top-0 z-10">
            <tr>
              {result.columns.map((col, i) => (
                <th
                  key={i}
                  className="px-3 py-2 text-left font-semibold text-gray-400 uppercase tracking-wider bg-gray-700 border-b border-gray-600 whitespace-nowrap"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.rows.map((row, ri) => (
              <tr
                key={ri}
                className={`border-b border-gray-700/50 transition-colors hover:bg-gray-700/40 ${
                  ri % 2 === 0 ? 'bg-gray-800' : 'bg-gray-800/60'
                }`}
              >
                {row.map((cell, ci) => (
                  <td key={ci} className="px-3 py-1.5 text-gray-300 whitespace-nowrap">
                    {cell === null ? (
                      <span className="text-gray-600 italic">NULL</span>
                    ) : typeof cell === 'number' ? (
                      cell.toLocaleString('zh-CN')
                    ) : (
                      String(cell)
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 分页栏 */}
      <div className="flex-shrink-0 flex items-center justify-between px-3 py-2 border-t border-gray-700/50 bg-gray-900 text-xs text-gray-400">
        <span>
          共 {result.total_count.toLocaleString()} 条，每页 {result.page_size} 条，耗时 {result.elapsed_ms}ms
        </span>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(result.page - 1)}
            disabled={result.page <= 1}
            className={`px-2 py-1 rounded transition-colors ${
              result.page <= 1
                ? 'text-gray-600 cursor-not-allowed'
                : 'text-gray-300 hover:bg-gray-700'
            }`}
          >
            上一页
          </button>
          <span className="text-gray-300">
            {result.page} / {result.total_pages}
          </span>
          <button
            onClick={() => onPageChange(result.page + 1)}
            disabled={result.page >= result.total_pages}
            className={`px-2 py-1 rounded transition-colors ${
              result.page >= result.total_pages
                ? 'text-gray-600 cursor-not-allowed'
                : 'text-gray-300 hover:bg-gray-700'
            }`}
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  )
}
