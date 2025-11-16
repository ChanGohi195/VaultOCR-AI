import { useState, useEffect } from 'react'
import { Folder, File, ChevronRight, ChevronDown } from 'lucide-react'

interface SidebarProps {
  onFileSelect: (filePath: string) => void
}

export default function Sidebar({ onFileSelect }: SidebarProps) {
  const [files, setFiles] = useState<any[]>([])
  const [currentDir, setCurrentDir] = useState<string>('')

  // Mock file tree for now
  useEffect(() => {
    setFiles([
      { name: 'Documents', isDirectory: true, path: '/documents' },
      { name: 'sample.md', isDirectory: false, path: '/sample.md' },
      { name: 'OCR Results', isDirectory: true, path: '/ocr-results' },
    ])
  }, [])

  return (
    <div className="w-64 bg-obsidian-sidebar border-r border-obsidian-border flex flex-col">
      <div className="p-4 border-b border-obsidian-border">
        <h2 className="text-sm font-semibold text-obsidian-text/80">FILES</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {files.map((file, idx) => (
          <div
            key={idx}
            className="flex items-center space-x-2 px-2 py-1.5 rounded hover:bg-obsidian-hover cursor-pointer text-sm"
            onClick={() => !file.isDirectory && onFileSelect(file.path)}
          >
            {file.isDirectory ? (
              <>
                <ChevronRight className="w-4 h-4 text-obsidian-text/60" />
                <Folder className="w-4 h-4 text-obsidian-accent" />
              </>
            ) : (
              <>
                <div className="w-4" />
                <File className="w-4 h-4 text-obsidian-text/60" />
              </>
            )}
            <span className="truncate">{file.name}</span>
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-obsidian-border text-xs text-obsidian-text/50">
        Phase 1: MVP
      </div>
    </div>
  )
}
