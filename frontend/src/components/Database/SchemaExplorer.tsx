import { useState, useEffect } from 'react'
import type { TableSchema } from '../../types'
import { fetchSchemaApi } from '../../api/client'

interface Props {
  /** 点击表名时回调，传递预填 SQL */
  onFillSql?: (sql: string) => void
}

export function SchemaExplorer({ onFillSql }: Props) {
  const [tables, setTables] = useState<TableSchema[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedTable, setExpandedTable] = useState<string | null>(null)

  useEffect(() => {
    loadSchema()
  }, [])

  const loadSchema = async () => {
    setLoading(true)
    setError(null)
    try {
      const { tables } = await fetchSchemaApi()
      setTables(tables)
      // 默认展开第一张表
      if (tables.length > 0) {
        setExpandedTable(tables[0].name)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const toggleTable = (name: string) => {
    setExpandedTable((prev) => (prev === name ? null : name))
  }

  const handleQueryTable = (tableName: string, e: React.MouseEvent) => {
    e.stopPropagation()
    onFillSql?.(`SELECT * FROM ${tableName} LIMIT 50`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full" style={{ color: 'var(--tech-text-muted)' }}>
        <p className="text-sm">加载表结构中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-2" style={{ color: 'var(--tech-text-muted)' }}>
        <p className="text-sm text-red-400">{error}</p>
        <button onClick={loadSchema} className="text-xs underline" style={{ color: 'var(--tech-accent)' }}>
          重试
        </button>
      </div>
    )
  }

  return (
    <div className="overflow-y-auto h-full px-3 py-2 space-y-1">
      {tables.map((table) => {
        const isExpanded = expandedTable === table.name
        return (
          <div key={table.name} className="rounded-lg overflow-hidden">
            {/* 表名行 */}
            <div
              onClick={() => toggleTable(table.name)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') toggleTable(table.name) }}
              className="w-full flex items-center gap-2 px-3 py-2 text-left rounded-lg transition-colors group cursor-pointer"
              style={{ border: '1px solid transparent' }}
            >
              {/* 展开箭头 */}
              <svg
                className={`w-3 h-3 text-gray-500 transition-transform flex-shrink-0 ${isExpanded ? 'rotate-90' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>

              {/* 表图标 */}
              <svg className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>

              <span className="text-sm font-medium truncate" style={{ color: 'var(--tech-text)' }}>{table.name}</span>
              <span className="text-xs flex-shrink-0" style={{ color: 'var(--tech-text-muted)' }}>({table.columns.length}列)</span>

              {/* 查询按钮 */}
              <button
                onClick={(e) => handleQueryTable(table.name, e)}
                className="ml-auto opacity-0 group-hover:opacity-100 text-xs px-1.5 py-0.5 rounded transition-all flex-shrink-0"
                style={{ color: 'var(--tech-accent)' }}
                title={`查询 ${table.name}`}
              >
                SELECT
              </button>
            </div>

            {/* 列列表 */}
            {isExpanded && (
              <div className="ml-5 mr-2 mb-1">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-gray-500">
                      <th className="text-left py-1 px-2 font-normal">列名</th>
                      <th className="text-left py-1 px-2 font-normal">类型</th>
                      <th className="text-left py-1 px-2 font-normal">约束</th>
                    </tr>
                  </thead>
                  <tbody>
                    {table.columns.map((col) => (
                      <tr key={col.name} data-schema-row className="text-gray-300">
                        <td className="py-1 px-2 font-mono">
                          {col.primary_key && (
                            <span className="text-yellow-500 mr-1" title="主键">PK</span>
                          )}
                          {col.name}
                        </td>
                        <td className="py-1 px-2 text-gray-400">{col.type}</td>
                        <td className="py-1 px-2 text-gray-500">
                          {!col.nullable && <span className="text-orange-400">NOT NULL</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
