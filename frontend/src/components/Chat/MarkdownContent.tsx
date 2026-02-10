import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface Props {
  content: string
  className?: string
}

/** AI 回复的 Markdown 渲染，深色主题样式 */
export function MarkdownContent({ content, className = '' }: Props) {
  return (
    <div
      className={`markdown-body text-sm leading-relaxed ${className}`}
      data-color-mode="dark"
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          ul: ({ children }) => <ul className="list-disc pl-5 mb-2 space-y-0.5">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal pl-5 mb-2 space-y-0.5">{children}</ol>,
          li: ({ children }) => <li className="text-gray-200">{children}</li>,
          strong: ({ children }) => <strong className="font-semibold text-gray-100">{children}</strong>,
          code: ({ className, children, ...props }) => {
            const isBlock = className?.includes('language-')
            if (isBlock) {
              return (
                <pre className="my-2 p-3 rounded-lg overflow-x-auto text-xs" style={{ backgroundColor: 'var(--tech-bg-elevated)' }}>
                  <code className={className} {...props}>{children}</code>
                </pre>
              )
            }
            return (
              <code className="px-1.5 py-0.5 rounded font-mono text-xs" style={{ backgroundColor: 'var(--tech-bg-elevated)', color: 'var(--tech-text)' }} {...props}>
                {children}
              </code>
            )
          },
          pre: ({ children }) => <>{children}</>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="hover:underline" style={{ color: 'var(--tech-accent)' }}>
              {children}
            </a>
          ),
          h1: ({ children }) => <h1 className="text-base font-bold mt-2 mb-1 text-gray-100">{children}</h1>,
          h2: ({ children }) => <h2 className="text-sm font-bold mt-2 mb-1 text-gray-100">{children}</h2>,
          h3: ({ children }) => <h3 className="text-sm font-semibold mt-1 mb-0.5 text-gray-100">{children}</h3>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-gray-500 pl-3 my-2 text-gray-400">{children}</blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-2">
              <table className="min-w-full border border-gray-600 rounded-lg overflow-hidden">{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-gray-700/80">{children}</thead>,
          tbody: ({ children }) => <tbody className="text-gray-200">{children}</tbody>,
          tr: ({ children }) => <tr className="border-b border-gray-600">{children}</tr>,
          th: ({ children }) => <th className="px-3 py-2 text-left text-xs font-semibold text-gray-300">{children}</th>,
          td: ({ children }) => <td className="px-3 py-2 text-xs">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
