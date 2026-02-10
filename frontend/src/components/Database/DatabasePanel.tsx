import { useState, useCallback } from 'react'
import { SchemaExplorer } from './SchemaExplorer'
import { SqlEditor } from './SqlEditor'
import { ConnectionManager } from '../Connection/ConnectionManager'
import { ConnectionSelector } from '../Connection/ConnectionSelector'

type TabId = 'schema' | 'sql' | 'connections'

interface Props {
  /** 当前活动的 MySQL 连接 ID */
  connectionId?: string
}

export function DatabasePanel({ connectionId }: Props) {
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
    { id: 'connections', label: '连接管理' },
  ]

  return (
    <div className="flex flex-col h-full">
      {/* Tab 栏 + 连接选择器 */}
      <div
        className="flex-shrink-0 px-3 pt-2 pb-1 border-b"
        style={{ backgroundColor: 'var(--tech-bg-panel)', borderColor: 'var(--tech-border)' }}
      >
        <div className="flex items-center gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 text-xs rounded-md transition-colors ${
                activeTab === tab.id ? 'font-medium' : ''
              }`}
              style={
                activeTab === tab.id
                  ? { backgroundColor: 'var(--tech-accent)', color: '#fff' }
                  : { color: 'var(--tech-text-muted)' }
              }
            >
              {tab.label}
            </button>
          ))}
          {/* 连接选择器靠右 */}
          <div className="ml-auto">
            <ConnectionSelector compact />
          </div>
        </div>
      </div>

      {/* Tab 内容 */}
      <div className="flex-1 min-h-0">
        {activeTab === 'schema' && (
          <SchemaExplorer onFillSql={handleFillSql} connectionId={connectionId} />
        )}
        {activeTab === 'sql' && (
          <SqlEditor prefillSql={prefillSql} onPrefillConsumed={handlePrefillConsumed} connectionId={connectionId} />
        )}
        {activeTab === 'connections' && (
          <ConnectionManager />
        )}
      </div>
    </div>
  )
}
