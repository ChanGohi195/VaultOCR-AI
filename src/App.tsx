import { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar'
import Editor from './components/Editor'
import Preview from './components/Preview'
import Toolbar from './components/Toolbar'
import DocumentInfo from './components/DocumentInfo'
import SearchBar from './components/SearchBar'
import DocumentList from './components/DocumentList'
import ExportDialog from './components/ExportDialog'
import BatchProcessDialog from './components/BatchProcessDialog'

type SidebarMode = 'files' | 'documents'

function App() {
  const [currentFile, setCurrentFile] = useState<string | null>(null)
  const [content, setContent] = useState<string>('# Welcome to VaultOCR-AI\n\nStart by opening a file or running OCR on a PDF/image.')
  const [showPreview, setShowPreview] = useState(true)
  const [documentMetadata, setDocumentMetadata] = useState<any>(null)
  const [documentToc, setDocumentToc] = useState<any[]>([])
  const [documentSections, setDocumentSections] = useState<any[]>([])
  const [sidebarMode, setSidebarMode] = useState<SidebarMode>('files')
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [showBatchDialog, setShowBatchDialog] = useState(false)
  const [currentDocId, setCurrentDocId] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleFileSelect = async (filePath: string) => {
    setCurrentFile(filePath)
    const result = await window.electronAPI.readFile(filePath)
    if (result.success && result.content) {
      setContent(result.content)
    }
  }

  const handleContentChange = (newContent: string) => {
    setContent(newContent)
  }

  const handleSave = async () => {
    if (!currentFile) return
    await window.electronAPI.writeFile(currentFile, content)
  }

  const handleOCRComplete = (text: string, metadata?: any, toc?: any[], sections?: any[]) => {
    setContent(text)
    setCurrentFile(null) // New unsaved content
    setDocumentMetadata(metadata || null)
    setDocumentToc(toc || [])
    setDocumentSections(sections || [])
  }

  // Phase 4 handlers
  const handleSearch = async (query: string) => {
    const result = await window.electronAPI.searchDocuments(query, 20)
    if (result.success) {
      return result.result.results || []
    }
    return []
  }

  const handleSearchResultClick = async (docId: string) => {
    setCurrentDocId(docId)
    // Load document content - would need to implement document retrieval
    // For now, just switch to documents mode
    setSidebarMode('documents')
  }

  const handleDocumentSelect = async (docId: string) => {
    await handleLoadDocument(docId)
  }

  const handleLoadDocuments = async (limit?: number, offset?: number) => {
    const result = await window.electronAPI.listDocuments(limit, offset)
    if (result.success) {
      return result.result.documents || []
    }
    return []
  }

  const handleLoadTags = async () => {
    const result = await window.electronAPI.getTags()
    if (result.success) {
      return result.result.tags || []
    }
    return []
  }

  const handleExport = async (format: string, vaultPath?: string) => {
    const result = await window.electronAPI.exportDocument({
      format,
      content,
      metadata: documentMetadata,
      toc: documentToc,
      vault_path: vaultPath
    })

    if (result.success) {
      alert(`Export successful! ${result.result.message || ''}`)
    } else {
      throw new Error(result.error || 'Export failed')
    }
  }

  const handleBatchOCR = async (filePaths: string[], autoSave: boolean, tags: string[]) => {
    const result = await window.electronAPI.batchOCR(filePaths, autoSave, tags)
    if (result.success && result.result) {
      return result.result
    } else {
      throw new Error(result.error || 'Batch OCR failed')
    }
  }

  const handleLoadDocument = async (docId: string) => {
    const result = await window.electronAPI.getDocument(docId)
    if (result.success && result.result) {
      const doc = result.result.document
      setContent(doc.content)
      setDocumentMetadata(doc.metadata || { title: doc.title, page_count: doc.page_count })
      setCurrentDocId(doc.id)
      setCurrentFile(null)
    }
  }

  // Drag and drop handler
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    const supportedExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']

    const validFiles = files.filter(file => {
      const ext = file.name.toLowerCase().match(/\.[^.]+$/)?.[0]
      return ext && supportedExtensions.includes(ext)
    })

    if (validFiles.length === 0) {
      alert('Please drop PDF or image files (jpg, png, pdf, etc.)')
      return
    }

    if (validFiles.length === 1) {
      // Single file: run OCR directly
      const file = validFiles[0]
      const filePath = (file as any).path || file.name

      try {
        const result = await window.electronAPI.runOCR(filePath)
        if (result.success && result.result) {
          handleOCRComplete(
            result.result.text,
            result.result.metadata,
            result.result.toc,
            result.result.sections
          )
        } else {
          alert(`OCR failed: ${result.error}`)
        }
      } catch (error) {
        alert(`Error: ${(error as Error).message}`)
      }
    } else {
      // Multiple files: open batch dialog
      setShowBatchDialog(true)
      // Note: Batch dialog would need to be enhanced to accept dropped files
    }
  }

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0
      const ctrlOrCmd = isMac ? e.metaKey : e.ctrlKey

      // Cmd/Ctrl + S: Save
      if (ctrlOrCmd && e.key === 's') {
        e.preventDefault()
        if (currentFile) {
          handleSave()
        }
      }

      // Cmd/Ctrl + K: Focus search
      if (ctrlOrCmd && e.key === 'k') {
        e.preventDefault()
        const searchInput = document.querySelector('input[placeholder*="Search"]') as HTMLInputElement
        searchInput?.focus()
      }

      // Cmd/Ctrl + B: Open batch dialog
      if (ctrlOrCmd && e.key === 'b') {
        e.preventDefault()
        setShowBatchDialog(true)
      }

      // Cmd/Ctrl + E: Open export dialog
      if (ctrlOrCmd && e.key === 'e') {
        e.preventDefault()
        setShowExportDialog(true)
      }

      // Cmd/Ctrl + P: Toggle preview
      if (ctrlOrCmd && e.key === 'p') {
        e.preventDefault()
        setShowPreview(prev => !prev)
      }

      // Cmd/Ctrl + D: Toggle documents/files sidebar
      if (ctrlOrCmd && e.key === 'd') {
        e.preventDefault()
        setSidebarMode(mode => mode === 'files' ? 'documents' : 'files')
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentFile, handleSave])

  return (
    <div
      className="flex flex-col h-screen bg-obsidian-bg text-obsidian-text relative"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {isDragging && (
        <div className="absolute inset-0 z-50 bg-obsidian-accent/20 backdrop-blur-sm flex items-center justify-center border-4 border-dashed border-obsidian-accent">
          <div className="bg-obsidian-bg p-8 rounded-lg shadow-2xl text-center">
            <p className="text-2xl font-bold text-obsidian-accent mb-2">Drop files here</p>
            <p className="text-obsidian-text-muted">PDF, JPG, PNG supported</p>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="border-b border-obsidian-border p-3 flex items-center justify-center bg-obsidian-bg-secondary">
        <SearchBar
          onSearch={handleSearch}
          onResultClick={handleSearchResultClick}
        />
      </div>

      <Toolbar
        onSave={handleSave}
        onTogglePreview={() => setShowPreview(!showPreview)}
        showPreview={showPreview}
        currentFile={currentFile}
        onOCRComplete={handleOCRComplete}
        onExport={() => setShowExportDialog(true)}
        onBatch={() => setShowBatchDialog(true)}
        onToggleSidebarMode={() => setSidebarMode(mode => mode === 'files' ? 'documents' : 'files')}
        sidebarMode={sidebarMode}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - Files or Documents */}
        {sidebarMode === 'files' ? (
          <Sidebar onFileSelect={handleFileSelect} />
        ) : (
          <DocumentList
            onDocumentSelect={handleDocumentSelect}
            onLoadDocuments={handleLoadDocuments}
            onLoadTags={handleLoadTags}
          />
        )}

        <div className="flex flex-1 overflow-hidden">
          <Editor
            content={content}
            onChange={handleContentChange}
            className={showPreview ? 'w-1/2' : 'w-full'}
          />

          {showPreview && (
            <Preview content={content} className="w-1/2" />
          )}
        </div>

        <DocumentInfo
          metadata={documentMetadata}
          toc={documentToc}
          sections={documentSections}
        />
      </div>

      {/* Export Dialog */}
      <ExportDialog
        isOpen={showExportDialog}
        onClose={() => setShowExportDialog(false)}
        onExport={handleExport}
        content={content}
        metadata={documentMetadata}
        toc={documentToc}
      />

      {/* Batch Process Dialog */}
      <BatchProcessDialog
        isOpen={showBatchDialog}
        onClose={() => setShowBatchDialog(false)}
        onBatchOCR={handleBatchOCR}
      />
    </div>
  )
}

export default App
