import { useEffect, useRef } from 'react'
import Editor from '@monaco-editor/react'

interface EditorProps {
  content: string
  onChange: (value: string) => void
  className?: string
}

export default function MarkdownEditor({ content, onChange, className = '' }: EditorProps) {
  const editorRef = useRef<any>(null)

  function handleEditorDidMount(editor: any) {
    editorRef.current = editor
  }

  function handleEditorChange(value: string | undefined) {
    if (value !== undefined) {
      onChange(value)
    }
  }

  return (
    <div className={`border-r border-obsidian-border ${className}`}>
      <Editor
        height="100%"
        defaultLanguage="markdown"
        theme="vs-dark"
        value={content}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'off',
          wordWrap: 'on',
          wrappingIndent: 'same',
          padding: { top: 16, bottom: 16 },
          scrollBeyondLastLine: false,
          renderLineHighlight: 'none',
          overviewRulerBorder: false,
          hideCursorInOverviewRuler: true,
          scrollbar: {
            vertical: 'auto',
            horizontal: 'auto',
          },
        }}
      />
    </div>
  )
}
