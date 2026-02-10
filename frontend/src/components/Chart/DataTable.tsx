import type { TableData } from '../../types'

interface Props {
  data: TableData
}

export function DataTable({ data }: Props) {
  if (!data.columns.length || !data.rows.length) {
    return <p className="text-sm text-center py-4" style={{ color: 'var(--tech-text-muted)' }}>暂无数据</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            {data.columns.map((col, i) => (
              <th
                key={i}
                className="px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wider first:rounded-tl-lg last:rounded-tr-lg"
                style={{ color: 'var(--tech-text-muted)', backgroundColor: 'var(--tech-bg-elevated)', borderBottom: '1px solid var(--tech-border)' }}
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
              className="border-b transition-colors"
              style={{
                borderColor: 'var(--tech-border)',
                backgroundColor: ri % 2 === 0 ? 'var(--tech-bg-card)' : 'var(--tech-bg-elevated)',
              }}
            >
              {row.map((cell, ci) => (
                <td key={ci} className="px-4 py-2.5 whitespace-nowrap" style={{ color: 'var(--tech-text)' }}>
                  {typeof cell === 'number' ? cell.toLocaleString('zh-CN') : cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-2 text-xs text-right" style={{ color: 'var(--tech-text-muted)' }}>
        共 {data.rows.length} 条记录
      </div>
    </div>
  )
}
