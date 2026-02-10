/**
 * MySQL 连接状态管理
 *
 * 职责：
 * - 管理连接列表、活动连接、连接有效性状态
 * - 前端启动时自动拉取连接列表 + 校验默认连接
 * - 切换连接时自动校验连通性
 * - 提供连接 CRUD 操作
 */

import { create } from 'zustand'
import type {
  MySQLConnection,
  MySQLConnectionCreate,
  MySQLConnectionUpdate,
  ConnectionTestRequest,
  ConnectionTestResult,
} from '../types'
import {
  fetchConnectionsApi,
  createConnectionApi,
  updateConnectionApi,
  deleteConnectionApi,
  testConnectionApi,
  testConnectionByIdApi,
} from '../api/client'

interface ConnectionState {
  /** 所有连接配置 */
  connections: MySQLConnection[]
  /** 当前活动连接 ID */
  activeConnectionId: string | null
  /** 当前活动连接是否已通过连通性校验 */
  connectionValid: boolean
  /** 正在加载/校验中 */
  loading: boolean
  /** 校验或加载失败的错误信息 */
  error: string | null

  /**
   * 初始化：拉取连接列表 -> 自动选中第一个 -> 校验连通性
   * 应在前端启动时调用
   */
  initConnections: () => Promise<void>

  /** 重新拉取连接列表（不重置活动连接） */
  fetchConnections: () => Promise<void>

  /** 新增连接 */
  addConnection: (config: MySQLConnectionCreate) => Promise<MySQLConnection>

  /** 更新连接 */
  updateConnection: (id: string, config: MySQLConnectionUpdate) => Promise<void>

  /** 删除连接 */
  deleteConnection: (id: string) => Promise<void>

  /** 切换活动连接并自动校验 */
  setActiveConnection: (id: string) => Promise<void>

  /** 测试连接（不保存，仅验证参数） */
  testConnection: (config: ConnectionTestRequest) => Promise<ConnectionTestResult>
}

export const useConnectionStore = create<ConnectionState>((set, get) => ({
  connections: [],
  activeConnectionId: null,
  connectionValid: false,
  loading: false,
  error: null,

  initConnections: async () => {
    set({ loading: true, error: null, connectionValid: false })
    try {
      // 1. 拉取连接列表
      const connections = await fetchConnectionsApi()
      set({ connections })

      if (connections.length === 0) {
        set({ loading: false, error: '暂无数据库连接，请先添加连接配置' })
        return
      }

      // 2. 自动选中第一个连接
      const firstId = connections[0].id
      set({ activeConnectionId: firstId })

      // 3. 校验该连接的连通性
      try {
        const result = await testConnectionByIdApi(firstId)
        if (result.success) {
          set({ connectionValid: true, loading: false, error: null })
        } else {
          set({
            connectionValid: false,
            loading: false,
            error: `默认连接不可用: ${result.message}`,
          })
        }
      } catch {
        set({
          connectionValid: false,
          loading: false,
          error: '默认连接校验失败，请检查配置',
        })
      }
    } catch (err) {
      set({
        loading: false,
        error: `加载连接列表失败: ${err instanceof Error ? err.message : '未知错误'}`,
      })
    }
  },

  fetchConnections: async () => {
    try {
      const connections = await fetchConnectionsApi()
      set({ connections })
    } catch (err) {
      console.error('[ConnectionStore] fetchConnections failed:', err)
    }
  },

  addConnection: async (config) => {
    const connection = await createConnectionApi(config)
    set((state) => ({
      connections: [...state.connections, connection],
    }))

    // 如果是第一个连接，自动选中并校验
    const { connections, activeConnectionId } = get()
    if (connections.length === 1 || !activeConnectionId) {
      await get().setActiveConnection(connection.id)
    }

    return connection
  },

  updateConnection: async (id, config) => {
    const updated = await updateConnectionApi(id, config)
    set((state) => ({
      connections: state.connections.map((c) => (c.id === id ? updated : c)),
    }))

    // 如果更新的是当前活动连接，需要重新校验
    if (get().activeConnectionId === id) {
      set({ connectionValid: false })
      try {
        const result = await testConnectionByIdApi(id)
        set({ connectionValid: result.success })
      } catch {
        set({ connectionValid: false })
      }
    }
  },

  deleteConnection: async (id) => {
    await deleteConnectionApi(id)
    const { connections, activeConnectionId } = get()
    const filtered = connections.filter((c) => c.id !== id)
    set({ connections: filtered })

    // 如果删除的是当前活动连接，切换到第一个
    if (activeConnectionId === id) {
      if (filtered.length > 0) {
        await get().setActiveConnection(filtered[0].id)
      } else {
        set({
          activeConnectionId: null,
          connectionValid: false,
          error: '暂无数据库连接，请先添加连接配置',
        })
      }
    }
  },

  setActiveConnection: async (id) => {
    // 1. 立即更新 ID，置 valid 为 false
    set({ activeConnectionId: id, connectionValid: false, error: null })

    // 2. 校验连通性
    try {
      const result = await testConnectionByIdApi(id)
      // 避免校验结果返回时 activeConnectionId 已切换
      if (get().activeConnectionId !== id) return
      if (result.success) {
        set({ connectionValid: true, error: null })
      } else {
        set({ connectionValid: false, error: `连接不可用: ${result.message}` })
      }
    } catch {
      if (get().activeConnectionId !== id) return
      set({ connectionValid: false, error: '连接校验失败' })
    }
  },

  testConnection: async (config) => {
    return await testConnectionApi(config)
  },
}))
