import { useState, useRef, useEffect, type KeyboardEvent } from 'react'
import type { SqlQueryResult } from '../../types'
import { executeSqlApi } from '../../api/client'
import { QueryResult } from './QueryResult'

interface Props {
  /** 外部传入的预填 SQL（来自 SchemaExplorer 的表名点击） */
  prefillSql: string
  onPrefillConsumed: () => void
}

export function SqlEditor({ prefillSql, onPrefillConsumed }: Props) {
  const [sql, setSql] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SqlQueryResult | null>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // 接收外部预填 SQL
  useEffect(() => {
    if (prefillSql) {
      setSql(prefillSql)
      onPrefillConsumed()
      textareaRef.current?.focus()
    }
  }, [prefillSql, onPrefillConsumed])

  const executeQuery = async (page: number = 1) => {
    const trimmed = sql.trim()
    if (!trimmed || loading) return

    setLoading(true)
    setError(null)

    try {
      const data = await executeSqlApi(trimmed, page, 50)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '查询失败')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+Enter 执行
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      executeQuery()
    }
  }

  const handleClear = () => {
    setSql('')
    setResult(null)
    setError(null)
    textareaRef.current?.focus()
  }

  const handlePageChange = (page: number) => {
    executeQuery(page)
  }

  return (
    <div className="flex flex-col h-full">
      {/* SQL 输入区 */}
      <div className="flex-shrink-0 px-3 pt-2 pb-1">
        <textarea
          ref={textareaRef}
          value={sql}
          onChange={(e) => setSql(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入 SQL 查询语句（仅支持 SELECT）..."
          rows={3}
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-xs font-mono text-gray-200 placeholder-gray-500 resize-none outline-none focus:border-gray-500 transition-colors"
        />
        <div className="flex items-center gap-2 mt-1.5">
          <button
            onClick={() => executeQuery()}
            disabled={!sql.trim() || loading}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              sql.trim() && !loading
                ? 'bg-gray-700 hover:bg-gray-600 text-gray-200'
                : 'bg-gray-800 text-gray-500 cursor-not-allowed'
            }`}
          >
            {loading ? '执行中...' : '执行查询'}
          </button>
          <button
            onClick={handleClear}
            className="px-3 py-1 text-xs rounded-md text-gray-400 hover:text-gray-200 hover:bg-gray-800 transition-colors"
          >
            清空
          </button>
          <span className="ml-auto text-xs text-gray-600">Ctrl+Enter 执行</span>
        </div>
      </div>

      {/* 结果区域 */}
      <div className="flex-1 min-h-0 mt-1">
        {error && (
          <div className="mx-3 mb-2 px-3 py-2 bg-red-900/30 border border-red-800/50 rounded-lg text-xs text-red-300">
            {error}
          </div>
        )}

        {result ? (
          <QueryResult result={result} onPageChange={handlePageChange} />
        ) : (
          !error && (
            <div className="flex items-center justify-center h-full text-gray-600">
              <p className="text-xs">执行 SQL 查询后，结果将在此展示</p>
            </div>
          )
        )}
      </div>
    </div>
  )
}
