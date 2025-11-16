import React, { useState } from 'react'
import { X, Download, FileText, Code, FileJson, Boxes, FolderOpen } from 'lucide-react'

interface ExportDialogProps {
  isOpen: boolean
  onClose: () => void
  onExport: (format: string, vaultPath?: string) => Promise<void>
  content: string
  metadata?: any
  toc?: any[]
}

type ExportFormat = 'markdown' | 'obsidian' | 'json' | 'notion'

const formatOptions: Array<{
  value: ExportFormat
  label: string
  description: string
  icon: React.ReactNode
  needsVaultPath?: boolean
}> = [
  {
    value: 'markdown',
    label: 'Markdown',
    description: 'Standard Markdown format with metadata comments',
    icon: <FileText className="w-5 h-5" />
  },
  {
    value: 'obsidian',
    label: 'Obsidian',
    description: 'Obsidian vault format with frontmatter and Wiki links',
    icon: <Code className="w-5 h-5" />,
    needsVaultPath: true
  },
  {
    value: 'json',
    label: 'JSON',
    description: 'Structured JSON with paragraphs, sections, and metadata',
    icon: <FileJson className="w-5 h-5" />
  },
  {
    value: 'notion',
    label: 'Notion',
    description: 'Notion-compatible import format',
    icon: <Boxes className="w-5 h-5" />
  }
]

export default function ExportDialog({
  isOpen,
  onClose,
  onExport,
  content,
  metadata,
  toc
}: ExportDialogProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('markdown')
  const [vaultPath, setVaultPath] = useState('')
  const [isExporting, setIsExporting] = useState(false)

  if (!isOpen) return null

  const selectedOption = formatOptions.find(opt => opt.value === selectedFormat)

  const handleExport = async () => {
    setIsExporting(true)
    try {
      await onExport(
        selectedFormat,
        selectedOption?.needsVaultPath ? vaultPath : undefined
      )
      onClose()
    } catch (error) {
      console.error('Export error:', error)
      alert('Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  const handleSelectVaultPath = async () => {
    // Electron API to select directory
    if (window.electronAPI?.selectDirectory) {
      const path = await window.electronAPI.selectDirectory()
      if (path) {
        setVaultPath(path)
      }
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-obsidian-bg border border-obsidian-border rounded-lg shadow-xl w-full max-w-2xl mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-obsidian-border">
          <h2 className="text-lg font-semibold text-obsidian-text flex items-center gap-2">
            <Download className="w-5 h-5" />
            Export Document
          </h2>
          <button
            onClick={onClose}
            className="text-obsidian-text-muted hover:text-obsidian-text transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Format Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-obsidian-text mb-3">
              Export Format
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {formatOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => setSelectedFormat(option.value)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selectedFormat === option.value
                      ? 'border-obsidian-accent bg-obsidian-accent/10'
                      : 'border-obsidian-border bg-obsidian-bg-secondary hover:border-obsidian-accent/50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`${
                      selectedFormat === option.value
                        ? 'text-obsidian-accent'
                        : 'text-obsidian-text-muted'
                    }`}>
                      {option.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-obsidian-text mb-1">
                        {option.label}
                      </h3>
                      <p className="text-xs text-obsidian-text-muted">
                        {option.description}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Vault Path Input (for Obsidian) */}
          {selectedOption?.needsVaultPath && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-obsidian-text mb-2">
                Obsidian Vault Path
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={vaultPath}
                  onChange={(e) => setVaultPath(e.target.value)}
                  placeholder="/path/to/obsidian/vault"
                  className="flex-1 px-3 py-2 bg-obsidian-bg-secondary border border-obsidian-border rounded text-obsidian-text focus:outline-none focus:ring-2 focus:ring-obsidian-accent"
                />
                <button
                  onClick={handleSelectVaultPath}
                  className="px-3 py-2 bg-obsidian-bg-secondary border border-obsidian-border rounded text-obsidian-text hover:bg-obsidian-bg-hover transition-colors"
                >
                  <FolderOpen className="w-5 h-5" />
                </button>
              </div>
              <p className="text-xs text-obsidian-text-muted mt-1">
                Select the root directory of your Obsidian vault
              </p>
            </div>
          )}

          {/* Preview Info */}
          <div className="mb-6 p-4 bg-obsidian-bg-secondary rounded border border-obsidian-border">
            <h4 className="text-sm font-medium text-obsidian-text mb-2">
              Document Info
            </h4>
            <div className="grid grid-cols-2 gap-2 text-xs text-obsidian-text-muted">
              <div>
                <span className="opacity-60">Title:</span>{' '}
                <span>{metadata?.title || 'Untitled'}</span>
              </div>
              <div>
                <span className="opacity-60">Pages:</span>{' '}
                <span>{metadata?.page_count || 1}</span>
              </div>
              {toc && toc.length > 0 && (
                <div>
                  <span className="opacity-60">Sections:</span>{' '}
                  <span>{toc.length}</span>
                </div>
              )}
              <div>
                <span className="opacity-60">Length:</span>{' '}
                <span>{content.length} chars</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-4 border-t border-obsidian-border">
          <button
            onClick={onClose}
            className="px-4 py-2 text-obsidian-text-muted hover:text-obsidian-text transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleExport}
            disabled={isExporting || (selectedOption?.needsVaultPath && !vaultPath)}
            className="px-4 py-2 bg-obsidian-accent text-obsidian-bg rounded hover:bg-obsidian-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            {isExporting ? 'Exporting...' : 'Export'}
          </button>
        </div>
      </div>
    </div>
  )
}
