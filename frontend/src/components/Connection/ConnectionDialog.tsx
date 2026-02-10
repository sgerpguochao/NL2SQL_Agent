/**
 * 连接编辑对话框 —— 新增/编辑 MySQL 连接
 *
 * 功能：
 * - 表单字段：name, host, port, user, password, database
 * - "测试连接" 按钮（显示 MySQL 版本、表数量）
 * - "保存" 按钮
 */

import { useState, useEffect } from 'react'
import type { MySQLConnection, ConnectionTestResult } from '../../types'
import { useConnectionStore } from '../../stores/connectionStore'

interface Props {
  /** 是否显示对话框 */
  open: boolean
  /** 关闭对话框回调 */
  onClose: () => void
  /** 编辑模式时传入连接配置，为 null 则是新增 */
  editConnection?: MySQLConnection | null
}

interface FormData {
  name: string
  host: string
  port: string
  user: string
  password: string
  database: string
}

const defaultForm: FormData = {
  name: '',
  host: 'localhost',
  port: '3306',
  user: 'root',
  password: '',
  database: '',
}

/** 单字段校验结果 */
type FieldErrors = Partial<Record<keyof FormData, string>>

function validateForm(form: FormData, isEdit: boolean): FieldErrors {
  const err: FieldErrors = {}
  if (!form.name.trim()) err.name = '请输入连接名称'
  if (!form.host.trim()) err.host = '请输入主机地址'
  const portNum = parseInt(form.port, 10)
  if (!form.port.trim()) err.port = '请输入端口'
  else if (Number.isNaN(portNum) || portNum < 1 || portNum > 65535) err.port = '端口须为 1–65535'
  if (!form.user.trim()) err.user = '请输入用户名'
  if (!isEdit) {
    if (form.password === undefined || form.password === null) err.password = '请输入密码'
    else if (!String(form.password).trim()) err.password = '请输入密码'
  }
  if (!form.database.trim()) err.database = '请输入数据库名'
  return err
}

export function ConnectionDialog({ open, onClose, editConnection }: Props) {
  const addConnection = useConnectionStore((s) => s.addConnection)
  const updateConnection = useConnectionStore((s) => s.updateConnection)
  const testConnection = useConnectionStore((s) => s.testConnection)

  const [form, setForm] = useState<FormData>(defaultForm)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<ConnectionTestResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  /** 提交过一次后保留各字段校验错误，用于显示红色标识与报错 */
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})

  const isEdit = !!editConnection

  // 初始化表单
  useEffect(() => {
    if (open) {
      if (editConnection) {
        setForm({
          name: editConnection.name,
          host: editConnection.host,
          port: String(editConnection.port),
          user: editConnection.user,
          password: editConnection.password,
          database: editConnection.database,
        })
      } else {
        setForm(defaultForm)
      }
      setTestResult(null)
      setError(null)
      setFieldErrors({})
    }
  }, [open, editConnection])

  const handleChange = (field: keyof FormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    setTestResult(null) // 参数变化后清除上次测试结果
  }

  /** 测试连接 */
  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    setError(null)
    try {
      const result = await testConnection({
        host: form.host,
        port: parseInt(form.port) || 3306,
        user: form.user,
        password: form.password,
        database: form.database,
      })
      setTestResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : '测试失败')
    } finally {
      setTesting(false)
    }
  }

  /** 保存连接 */
  const handleSave = async () => {
    const errors = validateForm(form, isEdit)
    const hasError = Object.keys(errors).length > 0
    setFieldErrors(errors)
    if (hasError) {
      const firstMsg = Object.values(errors)[0]
      setError(firstMsg ?? '请完善必填项后再提交')
      return
    }
    setError(null)

    setSaving(true)
    try {
      const data = {
        name: form.name.trim(),
        host: form.host.trim(),
        port: parseInt(form.port) || 3306,
        user: form.user.trim(),
        password: form.password,
        database: form.database.trim(),
      }

      if (isEdit && editConnection) {
        await updateConnection(editConnection.id, data)
      } else {
        await addConnection(data)
      }
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const inputBase = (field: keyof FormData) => ({
    className: `w-full px-3 py-2 rounded-lg text-sm outline-none transition-colors focus:ring-1 ${
      fieldErrors[field] ? 'focus:ring-red-500/50' : 'focus:ring-cyan-500/50'
    }`,
    style: {
      backgroundColor: 'var(--tech-bg-card)' as const,
      border: `1px solid ${fieldErrors[field] ? 'rgb(239, 68, 68)' : 'var(--tech-border)'}`,
      color: 'var(--tech-text)' as const,
    },
  })
  const RequiredStar = () => (
    <span className="text-red-500 ml-0.5" aria-label="必填">*</span>
  )
  const FieldError = ({ field }: { field: keyof FormData }) =>
    fieldErrors[field] ? (
      <p className="text-xs text-red-400 mt-0.5" role="alert">{fieldErrors[field]}</p>
    ) : null

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* 遮罩 */}
      <div
        className="absolute inset-0 bg-black/60"
        onClick={onClose}
      />

      {/* 对话框 */}
      <div
        className="relative w-[460px] rounded-xl shadow-2xl p-6"
        style={{
          backgroundColor: 'var(--tech-bg-panel)',
          border: '1px solid var(--tech-border)',
        }}
      >
        {/* 标题 */}
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-base font-semibold" style={{ color: 'var(--tech-text)' }}>
            {isEdit ? '编辑连接' : '新增 MySQL 连接'}
          </h3>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-md flex items-center justify-center transition-colors"
            style={{ color: 'var(--tech-text-muted)' }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 表单 */}
        <div className="space-y-3">
          {/* 连接名称 */}
          <div>
            <label className="block text-xs mb-1" style={{ color: 'var(--tech-text-muted)' }}>
              连接名称<RequiredStar />
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="例如：生产库-销售数据"
              aria-invalid={!!fieldErrors.name}
              {...inputBase('name')}
            />
            <FieldError field="name" />
          </div>

          {/* 主机 + 端口 */}
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-xs mb-1" style={{ color: 'var(--tech-text-muted)' }}>
                主机地址<RequiredStar />
              </label>
              <input
                type="text"
                value={form.host}
                onChange={(e) => handleChange('host', e.target.value)}
                placeholder="localhost"
                aria-invalid={!!fieldErrors.host}
                {...inputBase('host')}
              />
              <FieldError field="host" />
            </div>
            <div className="w-24">
              <label className="block text-xs mb-1" style={{ color: 'var(--tech-text-muted)' }}>
                端口<RequiredStar />
              </label>
              <input
                type="text"
                value={form.port}
                onChange={(e) => handleChange('port', e.target.value)}
                placeholder="3306"
                aria-invalid={!!fieldErrors.port}
                {...inputBase('port')}
              />
              <FieldError field="port" />
            </div>
          </div>

          {/* 用户名 + 密码 */}
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="block text-xs mb-1" style={{ color: 'var(--tech-text-muted)' }}>
                用户名<RequiredStar />
              </label>
              <input
                type="text"
                value={form.user}
                onChange={(e) => handleChange('user', e.target.value)}
                placeholder="root"
                aria-invalid={!!fieldErrors.user}
                {...inputBase('user')}
              />
              <FieldError field="user" />
            </div>
            <div className="flex-1">
              <label className="block text-xs mb-1" style={{ color: 'var(--tech-text-muted)' }}>
                密码<RequiredStar />
              </label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => handleChange('password', e.target.value)}
                placeholder="••••••"
                aria-invalid={!!fieldErrors.password}
                {...inputBase('password')}
              />
              <FieldError field="password" />
            </div>
          </div>

          {/* 数据库名 */}
          <div>
            <label className="block text-xs mb-1" style={{ color: 'var(--tech-text-muted)' }}>
              数据库名<RequiredStar />
            </label>
            <input
              type="text"
              value={form.database}
              onChange={(e) => handleChange('database', e.target.value)}
              placeholder="my_database"
              aria-invalid={!!fieldErrors.database}
              {...inputBase('database')}
            />
            <FieldError field="database" />
          </div>
        </div>

        {/* 测试结果 */}
        {testResult && (
          <div
            className={`mt-3 px-3 py-2 rounded-lg text-xs ${
              testResult.success ? 'text-green-300' : 'text-red-300'
            }`}
            style={{
              backgroundColor: testResult.success
                ? 'rgba(34, 197, 94, 0.1)'
                : 'rgba(239, 68, 68, 0.1)',
              border: `1px solid ${testResult.success ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            }}
          >
            <div className="font-medium">{testResult.success ? '连接成功' : '连接失败'}</div>
            <div className="mt-0.5 text-gray-400">{testResult.message}</div>
            {testResult.success && testResult.mysql_version && (
              <div className="mt-0.5">
                MySQL {testResult.mysql_version} | {testResult.tables_count ?? 0} 张表
              </div>
            )}
          </div>
        )}

        {/* 错误提示 */}
        {error && (
          <div
            className="mt-3 px-3 py-2 rounded-lg text-xs text-red-300"
            style={{
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
            }}
          >
            {error}
          </div>
        )}

        {/* 操作按钮 */}
        <div className="flex items-center gap-3 mt-5">
          <button
            onClick={handleTest}
            disabled={testing || !form.host.trim() || !form.database.trim()}
            className="px-4 py-2 text-xs rounded-lg transition-colors"
            style={{
              backgroundColor: testing ? 'var(--tech-bg-elevated)' : 'var(--tech-bg-card)',
              border: '1px solid var(--tech-border)',
              color: testing ? 'var(--tech-text-muted)' : 'var(--tech-text)',
            }}
          >
            {testing ? '测试中...' : '测试连接'}
          </button>

          <div className="flex-1" />

          <button
            onClick={onClose}
            className="px-4 py-2 text-xs rounded-lg transition-colors"
            style={{ color: 'var(--tech-text-muted)' }}
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-xs rounded-lg transition-colors text-white"
            style={{
              backgroundColor: saving ? 'var(--tech-bg-elevated)' : 'var(--tech-accent)',
              color: saving ? 'var(--tech-text-muted)' : '#fff',
            }}
          >
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  )
}
