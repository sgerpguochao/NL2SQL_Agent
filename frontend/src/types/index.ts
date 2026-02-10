/** 会话 —— 字段与后端 SessionResponse 保持一致（snake_case） */
export interface Session {
  id: string
  title: string
  created_at: string   // ISO-8601 字符串
  updated_at: string   // ISO-8601 字符串
  message_count?: number
}

/** 消息角色 */
export type MessageRole = 'user' | 'assistant'

/** 聊天消息 */
export interface Message {
  id: string
  session_id: string
  role: MessageRole
  content: string
  timestamp: string    // ISO-8601 字符串
  /** Agent 执行的 SQL（来自 SSE sql 事件） */
  sql?: string | null
  /** AI 思考过程：用户问题 + 推理步骤 + 回答（来自 SSE thinking 事件） */
  thinking_process?: string | null
  /** AI 回复可能附带图表数据（来自 SSE chart 事件） */
  chart_data?: ChartData | null
}

/** 图表类型 —— 后端仅支持 bar / line / pie / table */
export type ChartType = 'bar' | 'line' | 'pie' | 'table'

/** 表格数据 */
export interface TableData {
  columns: string[]
  rows: (string | number)[][]
}

/**
 * 图表数据 —— 字段与后端 SSE chart 事件保持一致（snake_case）
 *
 * 后端返回示例：
 * { "chart_type": "bar", "echarts_option": {...}, "table_data": {...} }
 */
export interface ChartData {
  chart_type: ChartType
  /** ECharts option JSON（chart_type 为 table 时可为 null） */
  echarts_option: Record<string, unknown> | null
  /** 表格数据 */
  table_data?: TableData | null
}

// ===== 数据库工具相关 =====

/** 表列信息 */
export interface ColumnInfo {
  name: string
  type: string
  primary_key: boolean
  nullable: boolean
}

/** 单表结构 */
export interface TableSchema {
  name: string
  columns: ColumnInfo[]
}

/** SQL 查询结果（分页） */
export interface SqlQueryResult {
  columns: string[]
  rows: (string | number | null)[][]
  total_count: number
  page: number
  page_size: number
  total_pages: number
  elapsed_ms: number
}
