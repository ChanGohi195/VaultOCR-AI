import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Editor from './components/Editor'
import Preview from './components/Preview'
import Toolbar from './components/Toolbar'
import DocumentInfo from './components/DocumentInfo'
import SearchBar from './components/SearchBar'
import DocumentList from './components/DocumentList'
import ExportDialog from './components/ExportDialog'

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
  const [currentDocId, setCurrentDocId] = useState<string | null>(null)

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
    setCurrentDocId(docId)
    // Load document content - would need to implement document retrieval
    console.log('Selected document:', docId)
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

  return (
    <div className="flex flex-col h-screen bg-obsidian-bg text-obsidian-text">
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
    </div>
  )
}

export default App
