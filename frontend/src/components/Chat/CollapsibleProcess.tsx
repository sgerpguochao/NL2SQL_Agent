import { useState } from 'react'

interface Props {
  /** 折叠块标题 */
  title?: string
  /** 中间过程内容（如 SQL、思考状态） */
  children: React.ReactNode
  /** 是否默认展开 */
  defaultExpanded?: boolean
  className?: string
}

/** 中间过程折叠块：小图标收缩，点击展开，主回答在下方单独展示 */
export function CollapsibleProcess({
  title = '中间过程',
  children,
  defaultExpanded = false,
  className = '',
}: Props) {
  const [expanded, setExpanded] = useState(defaultExpanded)

  return (
    <div
      className={`rounded-lg overflow-hidden ${className}`}
      style={{ border: '1px solid var(--tech-border)' }}
    >
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center gap-2 px-3 py-1.5 text-left text-xs transition-colors"
        style={{ color: 'var(--tech-text-muted)' }}
      >
        <span className="flex-shrink-0 text-gray-500 transition-transform" style={{ transform: expanded ? 'rotate(180deg)' : 'none' }}>
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </span>
        <span>{title}</span>
      </button>
      {expanded && (
        <div
          className="px-3 pb-2 pt-0 text-xs border-t"
          style={{ borderColor: 'var(--tech-border)', backgroundColor: 'rgba(6, 182, 212, 0.05)' }}
        >
          {children}
        </div>
      )}
    </div>
  )
}
