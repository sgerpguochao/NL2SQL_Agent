import { Sidebar } from './Sidebar/SessionList'
import { ChatPanel } from './Chat/ChatPanel'
import { ChartPanel } from './Chart/ChartPanel'
import { DatabasePanel } from './Database/DatabasePanel'

export function AppLayout() {
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
        <ChatPanel />
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
          <DatabasePanel />
        </div>
      </aside>
    </div>
  )
}
