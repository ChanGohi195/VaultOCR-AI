import React, { useState } from 'react'
import { X, Upload, FolderOpen, Play, Check, AlertCircle, Loader2 } from 'lucide-react'

interface BatchProcessDialogProps {
  isOpen: boolean
  onClose: () => void
  onBatchOCR: (filePaths: string[], autoSave: boolean, tags: string[]) => Promise<any>
}

interface FileItem {
  path: string
  name: string
  status: 'pending' | 'processing' | 'success' | 'failed'
  error?: string
}

export default function BatchProcessDialog({
  isOpen,
  onClose,
  onBatchOCR
}: BatchProcessDialogProps) {
  const [files, setFiles] = useState<FileItem[]>([])
  const [autoSave, setAutoSave] = useState(true)
  const [tags, setTags] = useState<string>('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState({ current: 0, total: 0 })

  if (!isOpen) return null

  const handleSelectFiles = async () => {
    // Electron APIで複数ファイル選択
    const result = await window.electronAPI.selectFile({
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: 'Images & PDF', extensions: ['jpg', 'jpeg', 'png', 'pdf'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    })

    if (result.success && result.filePaths) {
      const newFiles: FileItem[] = result.filePaths.map((path: string) => ({
        path,
        name: path.split(/[\\/]/).pop() || path,
        status: 'pending'
      }))
      setFiles(prevFiles => [...prevFiles, ...newFiles])
    }
  }

  const handleRemoveFile = (index: number) => {
    setFiles(files => files.filter((_, i) => i !== index))
  }

  const handleClearAll = () => {
    setFiles([])
    setProgress({ current: 0, total: 0 })
  }

  const handleStartBatch = async () => {
    if (files.length === 0) return

    setIsProcessing(true)
    setProgress({ current: 0, total: files.length })

    try {
      const filePaths = files.map(f => f.path)
      const tagList = tags.split(',').map(t => t.trim()).filter(t => t.length > 0)

      // バッチ処理実行
      const result = await onBatchOCR(filePaths, autoSave, tagList)

      // 結果を反映
      if (result && result.files) {
        const updatedFiles = files.map(file => {
          const resultFile = result.files.find((r: any) => r.path === file.path)
          if (resultFile) {
            return {
              ...file,
              status: resultFile.status,
              error: resultFile.error
            }
          }
          return file
        })
        setFiles(updatedFiles)
        setProgress({ current: result.success + result.failed, total: result.total })
      }

      // 成功メッセージ
      if (result) {
        alert(`Batch processing complete!\nSuccess: ${result.success}\nFailed: ${result.failed}`)
      }
    } catch (error) {
      console.error('Batch processing error:', error)
      alert(`Batch processing failed: ${(error as Error).message}`)
    } finally {
      setIsProcessing(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
      case 'success':
        return <Check className="w-4 h-4 text-green-400" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      default:
        return null
    }
  }

  const successCount = files.filter(f => f.status === 'success').length
  const failedCount = files.filter(f => f.status === 'failed').length

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-obsidian-bg border border-obsidian-border rounded-lg shadow-xl w-full max-w-3xl mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-obsidian-border">
          <h2 className="text-lg font-semibold text-obsidian-text flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Batch OCR Processing
          </h2>
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="text-obsidian-text-muted hover:text-obsidian-text transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Options */}
        <div className="p-4 border-b border-obsidian-border bg-obsidian-bg-secondary">
          <div className="flex items-center gap-6">
            <label className="flex items-center gap-2 text-sm text-obsidian-text cursor-pointer">
              <input
                type="checkbox"
                checked={autoSave}
                onChange={(e) => setAutoSave(e.target.checked)}
                disabled={isProcessing}
                className="w-4 h-4 rounded border-obsidian-border bg-obsidian-bg"
              />
              Auto-save to database
            </label>

            <div className="flex-1">
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="Tags (comma-separated)"
                disabled={isProcessing}
                className="w-full px-3 py-1.5 text-sm bg-obsidian-bg border border-obsidian-border rounded text-obsidian-text focus:outline-none focus:ring-2 focus:ring-obsidian-accent disabled:opacity-50"
              />
            </div>
          </div>
        </div>

        {/* File List */}
        <div className="flex-1 overflow-y-auto p-4">
          {files.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-obsidian-text-muted">
              <Upload className="w-12 h-12 mb-3 opacity-50" />
              <p>No files selected</p>
              <p className="text-xs mt-1">Click "Add Files" to select files for batch processing</p>
            </div>
          ) : (
            <div className="space-y-2">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 bg-obsidian-bg-secondary rounded border border-obsidian-border"
                >
                  <div className="flex-shrink-0">
                    {getStatusIcon(file.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-obsidian-text truncate">
                      {file.name}
                    </p>
                    {file.error && (
                      <p className="text-xs text-red-400 mt-1">{file.error}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveFile(index)}
                    disabled={isProcessing}
                    className="text-obsidian-text-muted hover:text-red-400 transition-colors disabled:opacity-50"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Progress & Stats */}
        {files.length > 0 && (
          <div className="px-4 py-2 border-t border-obsidian-border bg-obsidian-bg-secondary">
            <div className="flex items-center justify-between text-xs text-obsidian-text-muted">
              <span>
                Total: {files.length} files
                {successCount > 0 && ` | Success: ${successCount}`}
                {failedCount > 0 && ` | Failed: ${failedCount}`}
              </span>
              {isProcessing && (
                <span>
                  Processing {progress.current} / {progress.total}...
                </span>
              )}
            </div>
            {isProcessing && (
              <div className="mt-2 h-1 bg-obsidian-bg rounded-full overflow-hidden">
                <div
                  className="h-full bg-obsidian-accent transition-all duration-300"
                  style={{
                    width: `${(progress.current / progress.total) * 100}%`
                  }}
                />
              </div>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between gap-3 p-4 border-t border-obsidian-border">
          <div className="flex gap-2">
            <button
              onClick={handleSelectFiles}
              disabled={isProcessing}
              className="px-4 py-2 text-sm bg-obsidian-bg-secondary border border-obsidian-border rounded hover:bg-obsidian-bg-hover transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              <FolderOpen className="w-4 h-4" />
              Add Files
            </button>
            {files.length > 0 && (
              <button
                onClick={handleClearAll}
                disabled={isProcessing}
                className="px-4 py-2 text-sm text-obsidian-text-muted hover:text-obsidian-text transition-colors disabled:opacity-50"
              >
                Clear All
              </button>
            )}
          </div>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={isProcessing}
              className="px-4 py-2 text-sm text-obsidian-text-muted hover:text-obsidian-text transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleStartBatch}
              disabled={files.length === 0 || isProcessing}
              className="px-4 py-2 text-sm bg-obsidian-accent text-obsidian-bg rounded hover:bg-obsidian-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              {isProcessing ? 'Processing...' : 'Start Processing'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
