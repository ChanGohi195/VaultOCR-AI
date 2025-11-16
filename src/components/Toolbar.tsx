import { useState } from 'react'
import { Save, Eye, EyeOff, FileText, Camera, Loader2 } from 'lucide-react'

interface ToolbarProps {
  onSave: () => void
  onTogglePreview: () => void
  showPreview: boolean
  currentFile: string | null
  onOCRComplete: (text: string, metadata?: any, toc?: any[], sections?: any[]) => void
}

export default function Toolbar({ onSave, onTogglePreview, showPreview, currentFile, onOCRComplete }: ToolbarProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [status, setStatus] = useState<string>('')

  const handleOCR = async () => {
    try {
      setIsProcessing(true)
      setStatus('Selecting file...')

      // Open file dialog
      const fileResult = await window.electronAPI.selectFile()

      if (!fileResult.success || fileResult.canceled) {
        setIsProcessing(false)
        setStatus('')
        return
      }

      const filePath = fileResult.filePath!
      const fileName = filePath.split(/[\\/]/).pop() || 'file'
      const isP DF = filePath.toLowerCase().endsWith('.pdf')

      setStatus(isP DF ? `Processing PDF: ${fileName}...` : `Processing image: ${fileName}...`)

      // Run OCR
      const ocrResult = await window.electronAPI.runOCR(filePath)

      if (!ocrResult.success) {
        setStatus(`Error: ${ocrResult.error}`)
        setTimeout(() => setStatus(''), 3000)
        return
      }

      // Update editor with result
      const result = ocrResult.result!
      onOCRComplete(
        result.text,
        result.metadata,
        result.toc,
        result.sections
      )

      // Show success message
      const metadata = result.metadata
      const details = [
        `Pages: ${metadata?.page_count || 1}`,
        `Layout: ${metadata?.layout_type || 'unknown'}`,
        metadata?.section_count ? `Sections: ${metadata.section_count}` : null,
        metadata?.total_tables ? `Tables: ${metadata.total_tables}` : null
      ].filter(Boolean).join(', ')

      setStatus(`Success! ${details}`)
      setTimeout(() => setStatus(''), 5000)

    } catch (error) {
      setStatus(`Error: ${(error as Error).message}`)
      setTimeout(() => setStatus(''), 3000)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="flex flex-col border-b border-obsidian-border bg-obsidian-sidebar">
      <div className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-obsidian-accent" />
          <span className="text-sm font-medium">VaultOCR-AI</span>
          <span className="text-xs text-obsidian-text/50">Phase 2</span>
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
            onClick={handleOCR}
            disabled={isProcessing}
            className="px-3 py-1.5 text-sm rounded hover:bg-obsidian-hover bg-obsidian-accent/20 flex items-center space-x-1 disabled:opacity-50"
            title="Run OCR on PDF/Image"
          >
            {isProcessing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Camera className="w-4 h-4" />
            )}
            <span>OCR</span>
          </button>
        </div>
      </div>

      {status && (
        <div className="px-4 py-1 text-xs bg-obsidian-bg text-obsidian-text/70 border-t border-obsidian-border">
          {status}
        </div>
      )}
    </div>
  )
}
