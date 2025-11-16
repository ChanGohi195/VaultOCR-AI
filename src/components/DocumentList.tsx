import React, { useState, useEffect } from 'react'
import { FileText, Tag, Calendar, FileStack, ChevronDown, ChevronRight } from 'lucide-react'

interface Document {
  id: string
  title: string
  file_path?: string
  created_at: string
  page_count?: number
  tags: string[]
}

interface DocumentListProps {
  onDocumentSelect: (docId: string) => void
  onLoadDocuments: (limit?: number, offset?: number) => Promise<Document[]>
  onLoadTags: () => Promise<string[]>
}

export default function DocumentList({
  onDocumentSelect,
  onLoadDocuments,
  onLoadTags
}: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [allTags, setAllTags] = useState<string[]>([])
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set())
  const [isLoading, setIsLoading] = useState(false)
  const [showTagFilter, setShowTagFilter] = useState(false)

  // Load documents and tags on mount
  useEffect(() => {
    loadDocuments()
    loadTags()
  }, [])

  const loadDocuments = async () => {
    setIsLoading(true)
    try {
      const docs = await onLoadDocuments(100, 0)
      setDocuments(docs)
    } catch (error) {
      console.error('Failed to load documents:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadTags = async () => {
    try {
      const tags = await onLoadTags()
      setAllTags(tags)
    } catch (error) {
      console.error('Failed to load tags:', error)
    }
  }

  const toggleTag = (tag: string) => {
    const newSelectedTags = new Set(selectedTags)
    if (newSelectedTags.has(tag)) {
      newSelectedTags.delete(tag)
    } else {
      newSelectedTags.add(tag)
    }
    setSelectedTags(newSelectedTags)
  }

  const clearTagFilter = () => {
    setSelectedTags(new Set())
  }

  // Filter documents by selected tags
  const filteredDocuments = selectedTags.size === 0
    ? documents
    : documents.filter(doc =>
        doc.tags.some(tag => selectedTags.has(tag))
      )

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    } catch {
      return dateString
    }
  }

  return (
    <div className="h-full flex flex-col bg-obsidian-sidebar border-r border-obsidian-border">
      {/* Header */}
      <div className="p-4 border-b border-obsidian-border">
        <h2 className="text-obsidian-text font-semibold mb-2 flex items-center gap-2">
          <FileStack className="w-4 h-4" />
          Documents ({filteredDocuments.length})
        </h2>

        {/* Tag Filter Toggle */}
        <button
          onClick={() => setShowTagFilter(!showTagFilter)}
          className="flex items-center gap-2 text-sm text-obsidian-text-muted hover:text-obsidian-text transition-colors"
        >
          {showTagFilter ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
          <Tag className="w-3 h-3" />
          Filter by tags
          {selectedTags.size > 0 && (
            <span className="ml-1 px-2 py-0.5 bg-obsidian-accent text-obsidian-bg rounded-full text-xs">
              {selectedTags.size}
            </span>
          )}
        </button>

        {/* Tag Filter Panel */}
        {showTagFilter && (
          <div className="mt-2 p-2 bg-obsidian-bg-secondary rounded-md max-h-32 overflow-y-auto">
            <div className="flex flex-wrap gap-1">
              {allTags.length === 0 ? (
                <p className="text-xs text-obsidian-text-muted">No tags available</p>
              ) : (
                <>
                  {allTags.map(tag => (
                    <button
                      key={tag}
                      onClick={() => toggleTag(tag)}
                      className={`px-2 py-1 text-xs rounded transition-colors ${
                        selectedTags.has(tag)
                          ? 'bg-obsidian-accent text-obsidian-bg'
                          : 'bg-obsidian-bg-hover text-obsidian-text-muted hover:text-obsidian-text'
                      }`}
                    >
                      #{tag}
                    </button>
                  ))}
                  {selectedTags.size > 0 && (
                    <button
                      onClick={clearTagFilter}
                      className="px-2 py-1 text-xs rounded bg-red-500/20 text-red-400 hover:bg-red-500/30"
                    >
                      Clear
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-obsidian-text-muted">
            Loading documents...
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="p-4 text-center text-obsidian-text-muted">
            {selectedTags.size > 0 ? 'No documents with selected tags' : 'No documents yet'}
          </div>
        ) : (
          <div className="divide-y divide-obsidian-border">
            {filteredDocuments.map(doc => (
              <button
                key={doc.id}
                onClick={() => onDocumentSelect(doc.id)}
                className="w-full text-left p-3 hover:bg-obsidian-bg-hover transition-colors"
              >
                <div className="flex items-start gap-2">
                  <FileText className="w-4 h-4 mt-0.5 text-obsidian-text-muted flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-obsidian-text truncate">
                      {doc.title}
                    </h3>

                    <div className="flex items-center gap-3 mt-1 text-xs text-obsidian-text-muted">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(doc.created_at)}
                      </span>
                      {doc.page_count && doc.page_count > 0 && (
                        <span className="flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          {doc.page_count}p
                        </span>
                      )}
                    </div>

                    {doc.tags && doc.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {doc.tags.slice(0, 3).map(tag => (
                          <span
                            key={tag}
                            className="px-1.5 py-0.5 bg-obsidian-bg-secondary text-obsidian-text-muted text-xs rounded"
                          >
                            #{tag}
                          </span>
                        ))}
                        {doc.tags.length > 3 && (
                          <span className="px-1.5 py-0.5 text-obsidian-text-muted text-xs">
                            +{doc.tags.length - 3}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
