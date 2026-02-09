import { useState, useCallback } from 'react'
import { SchemaExplorer } from './SchemaExplorer'
import { SqlEditor } from './SqlEditor'

type TabId = 'schema' | 'sql'

export function DatabasePanel() {
  const [activeTab, setActiveTab] = useState<TabId>('schema')
  const [prefillSql, setPrefillSql] = useState('')

  /** SchemaExplorer 点击表名 -> 自动切换到 SQL Tab 并预填 SQL */
  const handleFillSql = useCallback((sql: string) => {
    setPrefillSql(sql)
    setActiveTab('sql')
  }, [])

  const handlePrefillConsumed = useCallback(() => {
    setPrefillSql('')
  }, [])

  const tabs: { id: TabId; label: string }[] = [
    { id: 'schema', label: '表结构' },
    { id: 'sql', label: 'SQL 查询' },
  ]

  return (
    <div className="flex flex-col h-full">
      {/* Tab 栏 */}
      <div className="flex-shrink-0 px-3 pt-2 pb-1 bg-gray-900 border-b border-gray-700/50">
        <div className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                activeTab === tab.id
                  ? 'bg-gray-700 text-gray-100 font-medium'
                  : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab 内容 */}
      <div className="flex-1 min-h-0">
        {activeTab === 'schema' && (
          <SchemaExplorer onFillSql={handleFillSql} />
        )}
        {activeTab === 'sql' && (
          <SqlEditor prefillSql={prefillSql} onPrefillConsumed={handlePrefillConsumed} />
        )}
      </div>
    </div>
  )
}
