import { useEffect } from 'react'
import { Sidebar } from './Sidebar/SessionList'
import { ChatPanel } from './Chat/ChatPanel'
import { ChartPanel } from './Chart/ChartPanel'
import { DatabasePanel } from './Database/DatabasePanel'
import { useConnectionStore } from '../stores/connectionStore'

export function AppLayout() {
  const initConnections = useConnectionStore((s) => s.initConnections)
  const loading = useConnectionStore((s) => s.loading)
  const error = useConnectionStore((s) => s.error)
  const connectionValid = useConnectionStore((s) => s.connectionValid)
  const activeConnectionId = useConnectionStore((s) => s.activeConnectionId)

  // 启动时自动初始化连接
  useEffect(() => {
    initConnections()
  }, [initConnections])

  // 仅当连接有效时传递 connectionId
  const effectiveConnectionId = connectionValid ? activeConnectionId ?? undefined : undefined

  return (
    <div className="flex h-screen" style={{ backgroundColor: 'var(--tech-bg-base)' }}>
      {/* 左侧：会话列表（最深层） */}
      <aside
        className="w-[250px] flex-shrink-0 flex flex-col border-r"
        style={{ backgroundColor: 'var(--tech-bg-panel)', borderColor: 'var(--tech-border)' }}
      >
        <Sidebar />
      </aside>

      {/* 中间：聊天问答 */}
      <main className="flex-1 flex flex-col min-w-0" style={{ backgroundColor: 'var(--tech-bg-base)' }}>
        {/* 连接状态横幅 */}
        {loading && (
          <div
            className="flex-shrink-0 px-4 py-2 text-xs text-center"
            style={{ backgroundColor: 'rgba(6, 182, 212, 0.1)', color: 'var(--tech-accent)', borderBottom: '1px solid var(--tech-border)' }}
          >
            正在检测数据库连接...
          </div>
        )}
        {!loading && error && (
          <div
            className="flex-shrink-0 px-4 py-2 text-xs text-center text-amber-300"
            style={{ backgroundColor: 'rgba(245, 158, 11, 0.1)', borderBottom: '1px solid var(--tech-border)' }}
          >
            {error}
          </div>
        )}
        <ChatPanel connectionId={effectiveConnectionId} />
      </main>

      {/* 右侧：上下分割 — 图表 + 数据库工具 */}
      <aside
        className="w-[520px] flex-shrink-0 flex flex-col min-h-0 border-l"
        style={{ backgroundColor: 'var(--tech-bg-panel)', borderColor: 'var(--tech-border)' }}
      >
        {/* 上半区：数据可视化（与下半区等分，保证图表可见） */}
        <div
          className="flex-1 min-h-[240px] flex flex-col min-w-0 overflow-hidden"
          style={{ borderBottom: '1px solid var(--tech-border)' }}
        >
          <ChartPanel />
        </div>
        {/* 下半区：数据库工具 */}
        <div className="flex-1 min-h-[200px] flex flex-col min-w-0 overflow-hidden">
          <DatabasePanel connectionId={effectiveConnectionId} />
        </div>
      </aside>
    </div>
  )
}
