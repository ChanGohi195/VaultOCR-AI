import { Save, Eye, EyeOff, FileText, Camera } from 'lucide-react'

interface ToolbarProps {
  onSave: () => void
  onTogglePreview: () => void
  showPreview: boolean
  currentFile: string | null
}

export default function Toolbar({ onSave, onTogglePreview, showPreview, currentFile }: ToolbarProps) {
  return (
    <div className="flex items-center justify-between px-4 py-2 bg-obsidian-sidebar border-b border-obsidian-border">
      <div className="flex items-center space-x-2">
        <FileText className="w-5 h-5 text-obsidian-accent" />
        <span className="text-sm font-medium">VaultOCR-AI</span>
      </div>

      <div className="flex items-center space-x-1">
        <button
          onClick={onSave}
          disabled={!currentFile}
          className="px-3 py-1.5 text-sm rounded hover:bg-obsidian-hover disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
          title="Save (Cmd+S)"
        >
          <Save className="w-4 h-4" />
          <span>Save</span>
        </button>

        <button
          onClick={onTogglePreview}
          className="px-3 py-1.5 text-sm rounded hover:bg-obsidian-hover flex items-center space-x-1"
          title="Toggle Preview"
        >
          {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          <span>{showPreview ? 'Hide' : 'Show'} Preview</span>
        </button>

        <button
          className="px-3 py-1.5 text-sm rounded hover:bg-obsidian-hover bg-obsidian-accent/20 flex items-center space-x-1"
          title="Run OCR"
        >
          <Camera className="w-4 h-4" />
          <span>OCR</span>
        </button>
      </div>
    </div>
  )
}
