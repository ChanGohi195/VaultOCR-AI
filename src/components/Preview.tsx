import ReactMarkdown from 'react-markdown'

interface PreviewProps {
  content: string
  className?: string
}

export default function Preview({ content, className = '' }: PreviewProps) {
  return (
    <div className={`overflow-y-auto bg-obsidian-bg ${className}`}>
      <div className="prose prose-invert max-w-none p-8">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  )
}
