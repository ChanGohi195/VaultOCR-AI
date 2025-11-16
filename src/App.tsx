import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Editor from './components/Editor'
import Preview from './components/Preview'
import Toolbar from './components/Toolbar'

function App() {
  const [currentFile, setCurrentFile] = useState<string | null>(null)
  const [content, setContent] = useState<string>('# Welcome to VaultOCR-AI\n\nStart by opening a file or running OCR on a PDF/image.')
  const [showPreview, setShowPreview] = useState(true)

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

  const handleOCRComplete = (text: string) => {
    setContent(text)
    setCurrentFile(null) // New unsaved content
  }

  return (
    <div className="flex flex-col h-screen bg-obsidian-bg text-obsidian-text">
      <Toolbar
        onSave={handleSave}
        onTogglePreview={() => setShowPreview(!showPreview)}
        showPreview={showPreview}
        currentFile={currentFile}
        onOCRComplete={handleOCRComplete}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar onFileSelect={handleFileSelect} />

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
      </div>
    </div>
  )
}

export default App
