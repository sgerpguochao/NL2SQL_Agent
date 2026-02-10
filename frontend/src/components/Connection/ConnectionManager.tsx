/**
 * 连接管理面板 —— 展示在 DatabasePanel 的 "连接管理" Tab 中
 *
 * 功能：
 * - 连接列表展示（名称、host:port/db、状态指示）
 * - 新增/编辑/删除操作
 * - 点击切换当前活动连接
 * - 测试已保存的连接
 */

import { useState } from 'react'
import type { MySQLConnection } from '../../types'
import { useConnectionStore } from '../../stores/connectionStore'
import { ConnectionDialog } from './ConnectionDialog'
import { testConnectionByIdApi } from '../../api/client'

export function ConnectionManager() {
  const connections = useConnectionStore((s) => s.connections)
  const activeConnectionId = useConnectionStore((s) => s.activeConnectionId)
  const connectionValid = useConnectionStore((s) => s.connectionValid)
  const setActiveConnection = useConnectionStore((s) => s.setActiveConnection)
  const deleteConnection = useConnectionStore((s) => s.deleteConnection)

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingConn, setEditingConn] = useState<MySQLConnection | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [testingId, setTestingId] = useState<string | null>(null)
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({})

  /** 打开新增对话框 */
  const handleAdd = () => {
    setEditingConn(null)
    setDialogOpen(true)
  }

  /** 打开编辑对话框 */
  const handleEdit = (conn: MySQLConnection) => {
    setEditingConn(conn)
    setDialogOpen(true)
  }

  /** 删除连接 */
  const handleDelete = async (id: string) => {
    setDeletingId(id)
    try {
      await deleteConnection(id)
      // 清除该连接的测试结果
      setTestResults((prev) => {
        const next = { ...prev }
        delete next[id]
        return next
      })
    } catch (err) {
      console.error('删除连接失败:', err)
    } finally {
      setDeletingId(null)
    }
  }

  /** 测试已保存的连接 */
  const handleTestSaved = async (id: string) => {
    setTestingId(id)
    try {
      const result = await testConnectionByIdApi(id)
      setTestResults((prev) => ({
        ...prev,
        [id]: { success: result.success, message: result.message },
      }))
    } catch (err) {
      setTestResults((prev) => ({
        ...prev,
        [id]: { success: false, message: err instanceof Error ? err.message : '测试失败' },
      }))
    } finally {
      setTestingId(null)
    }
  }

  /** 切换活动连接 */
  const handleSelect = async (id: string) => {
    if (id !== activeConnectionId) {
      await setActiveConnection(id)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* 顶部操作栏 */}
      <div className="flex items-center justify-between px-3 py-2 flex-shrink-0">
        <span className="text-xs" style={{ color: 'var(--tech-text-muted)' }}>
          {connections.length} 个连接
        </span>
        <button
          onClick={handleAdd}
          className="flex items-center gap-1 px-2.5 py-1 text-xs rounded-md transition-colors text-white"
          style={{ backgroundColor: 'var(--tech-accent)' }}
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          新增
        </button>
      </div>

      {/* 连接列表 */}
      <div className="flex-1 overflow-y-auto px-3 pb-2 space-y-1.5">
        {connections.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2" style={{ color: 'var(--tech-text-muted)' }}>
            <svg className="w-10 h-10 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
            </svg>
            <p className="text-xs">暂无连接配置</p>
            <button onClick={handleAdd} className="text-xs underline" style={{ color: 'var(--tech-accent)' }}>
              添加第一个连接
            </button>
          </div>
        ) : (
          connections.map((conn) => {
            const isActive = conn.id === activeConnectionId
            const isDeleting = deletingId === conn.id
            const isTesting = testingId === conn.id
            const testRes = testResults[conn.id]

            return (
              <div
                key={conn.id}
                className={`rounded-lg px-3 py-2.5 transition-colors cursor-pointer group ${
                  isActive ? 'ring-1' : ''
                }`}
                style={{
                  backgroundColor: isActive ? 'var(--tech-bg-elevated)' : 'var(--tech-bg-card)',
                  border: '1px solid var(--tech-border)',
                  ...(isActive ? { ringColor: 'var(--tech-accent)' } : {}),
                }}
                onClick={() => handleSelect(conn.id)}
              >
                {/* 第一行：名称 + 状态 */}
                <div className="flex items-center gap-2">
                  {/* 状态指示点 */}
                  <span
                    className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{
                      backgroundColor: isActive
                        ? connectionValid
                          ? '#22c55e'
                          : '#ef4444'
                        : '#6b7280',
                    }}
                  />
                  <span className="text-sm font-medium truncate" style={{ color: 'var(--tech-text)' }}>
                    {conn.name}
                  </span>
                  {isActive && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ backgroundColor: 'var(--tech-accent)', color: '#fff' }}>
                      当前
                    </span>
                  )}
                </div>

                {/* 第二行：连接信息 */}
                <div className="text-[11px] mt-1 ml-4" style={{ color: 'var(--tech-text-muted)' }}>
                  {conn.host}:{conn.port} / {conn.database}
                </div>

                {/* 测试结果行 */}
                {testRes && (
                  <div className={`text-[11px] mt-1 ml-4 ${testRes.success ? 'text-green-400' : 'text-red-400'}`}>
                    {testRes.success ? 'OK' : '失败'}: {testRes.message}
                  </div>
                )}

                {/* 操作按钮行 */}
                <div className="flex items-center gap-1.5 mt-2 ml-4 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleTestSaved(conn.id) }}
                    disabled={isTesting}
                    className="px-2 py-0.5 text-[11px] rounded transition-colors"
                    style={{
                      backgroundColor: 'var(--tech-bg-elevated)',
                      color: 'var(--tech-text-muted)',
                      border: '1px solid var(--tech-border)',
                    }}
                  >
                    {isTesting ? '测试中...' : '测试'}
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleEdit(conn) }}
                    className="px-2 py-0.5 text-[11px] rounded transition-colors"
                    style={{
                      backgroundColor: 'var(--tech-bg-elevated)',
                      color: 'var(--tech-text-muted)',
                      border: '1px solid var(--tech-border)',
                    }}
                  >
                    编辑
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(conn.id) }}
                    disabled={isDeleting}
                    className="px-2 py-0.5 text-[11px] rounded transition-colors text-red-400"
                    style={{
                      backgroundColor: 'var(--tech-bg-elevated)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                    }}
                  >
                    {isDeleting ? '删除中...' : '删除'}
                  </button>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* 连接编辑对话框 */}
      <ConnectionDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        editConnection={editingConn}
      />
    </div>
  )
}
