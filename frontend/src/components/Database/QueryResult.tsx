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
                  className="px-3 py-2 text-left font-semibold uppercase tracking-wider whitespace-nowrap"
                style={{ color: 'var(--tech-text-muted)', backgroundColor: 'var(--tech-bg-elevated)', borderBottom: '1px solid var(--tech-border)' }}
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
                className="border-b transition-colors"
                style={{
                  borderColor: 'var(--tech-border)',
                  backgroundColor: ri % 2 === 0 ? 'var(--tech-bg-card)' : 'var(--tech-bg-elevated)',
                }}
              >
                {row.map((cell, ci) => (
                  <td key={ci} className="px-3 py-1.5 whitespace-nowrap" style={{ color: 'var(--tech-text)' }}>
                    {cell === null ? (
                      <span className="italic" style={{ color: 'var(--tech-text-muted)' }}>NULL</span>
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
      <div
        className="flex-shrink-0 flex items-center justify-between px-3 py-2 border-t text-xs"
        style={{ borderColor: 'var(--tech-border)', backgroundColor: 'var(--tech-bg-panel)', color: 'var(--tech-text-muted)' }}
      >
        <span>
          共 {result.total_count.toLocaleString()} 条，每页 {result.page_size} 条，耗时 {result.elapsed_ms}ms
        </span>

        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(result.page - 1)}
            disabled={result.page <= 1}
            className={`px-2 py-1 rounded transition-colors ${
              result.page <= 1 ? 'cursor-not-allowed' : ''
            }`}
            style={
              result.page <= 1
                ? { color: 'var(--tech-text-muted)' }
                : { color: 'var(--tech-text)' }
            }
          >
            上一页
          </button>
          <span style={{ color: 'var(--tech-text)' }}>
            {result.page} / {result.total_pages}
          </span>
          <button
            onClick={() => onPageChange(result.page + 1)}
            disabled={result.page >= result.total_pages}
            className={`px-2 py-1 rounded transition-colors ${
              result.page >= result.total_pages ? 'cursor-not-allowed' : ''
            }`}
            style={
              result.page >= result.total_pages
                ? { color: 'var(--tech-text-muted)' }
                : { color: 'var(--tech-text)' }
            }
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  )
}
