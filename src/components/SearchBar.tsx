import React, { useState, useCallback } from 'react'
import { Search, X, Loader2, Sparkles, Database, Zap } from 'lucide-react'

interface SearchResult {
  doc_id: string
  title: string
  snippet?: string
  content?: string
  path?: string
  score: number
  keyword_score?: number
  semantic_score?: number
}

type SearchMode = 'keyword' | 'semantic' | 'hybrid'

interface SearchBarProps {
  onSearch: (query: string) => Promise<SearchResult[]>
  onResultClick: (docId: string) => void
}

export default function SearchBar({ onSearch, onResultClick }: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [searchMode, setSearchMode] = useState<SearchMode>('hybrid')

  const handleSearch = useCallback(async () => {
    if (!query.trim()) {
      setResults([])
      setShowResults(false)
      return
    }

    setIsSearching(true)
    try {
      let searchResults: SearchResult[] = []

      // Phase 8: Use different search APIs based on mode
      if (searchMode === 'keyword') {
        searchResults = await onSearch(query)
      } else if (searchMode === 'semantic') {
        const response = await window.electronAPI.semanticSearch(query, 20)
        if (response.success && response.result) {
          searchResults = response.result.results.map((r: any) => ({
            doc_id: r.doc_id,
            title: r.title,
            snippet: r.content || '',
            score: r.score,
            metadata: r.metadata
          }))
        }
      } else if (searchMode === 'hybrid') {
        const response = await window.electronAPI.hybridSearch(query, 20, 0.5, 0.5)
        if (response.success && response.result) {
          searchResults = response.result.results.map((r: any) => ({
            doc_id: r.doc_id,
            title: r.title,
            snippet: r.content || '',
            score: r.score,
            keyword_score: r.keyword_score,
            semantic_score: r.semantic_score,
            metadata: r.metadata
          }))
        }
      }

      setResults(searchResults)
      setShowResults(true)
    } catch (error) {
      console.error('Search error:', error)
      setResults([])
    } finally {
      setIsSearching(false)
    }
  }, [query, onSearch, searchMode])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    } else if (e.key === 'Escape') {
      setShowResults(false)
    }
  }

  const handleClear = () => {
    setQuery('')
    setResults([])
    setShowResults(false)
  }

  const handleResultClick = (docId: string) => {
    onResultClick(docId)
    setShowResults(false)
  }

  return (
    <div className="relative w-full max-w-2xl">
      {/* Search Mode Toggle */}
      <div className="flex items-center gap-2 mb-2">
        <button
          onClick={() => setSearchMode('keyword')}
          className={`flex items-center gap-1 px-3 py-1 text-xs rounded transition-colors ${
            searchMode === 'keyword'
              ? 'bg-obsidian-accent text-white'
              : 'bg-obsidian-bg-secondary text-obsidian-text-muted hover:bg-obsidian-bg-hover'
          }`}
          title="Keyword Search - Traditional text matching"
        >
          <Database className="w-3 h-3" />
          <span>Keyword</span>
        </button>
        <button
          onClick={() => setSearchMode('semantic')}
          className={`flex items-center gap-1 px-3 py-1 text-xs rounded transition-colors ${
            searchMode === 'semantic'
              ? 'bg-obsidian-accent text-white'
              : 'bg-obsidian-bg-secondary text-obsidian-text-muted hover:bg-obsidian-bg-hover'
          }`}
          title="Semantic Search - AI-powered meaning-based search"
        >
          <Sparkles className="w-3 h-3" />
          <span>Semantic</span>
        </button>
        <button
          onClick={() => setSearchMode('hybrid')}
          className={`flex items-center gap-1 px-3 py-1 text-xs rounded transition-colors ${
            searchMode === 'hybrid'
              ? 'bg-obsidian-accent text-white'
              : 'bg-obsidian-bg-secondary text-obsidian-text-muted hover:bg-obsidian-bg-hover'
          }`}
          title="Hybrid Search - Combines keyword and semantic search"
        >
          <Zap className="w-3 h-3" />
          <span>Hybrid</span>
        </button>
        <span className="text-xs text-obsidian-text-muted ml-auto">
          {searchMode === 'keyword' && 'Exact text matching'}
          {searchMode === 'semantic' && 'AI meaning-based search'}
          {searchMode === 'hybrid' && 'Best of both worlds'}
        </span>
      </div>

      {/* Search Input */}
      <div className="relative flex items-center">
        <Search className="absolute left-3 w-4 h-4 text-obsidian-text-muted" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setShowResults(true)}
          placeholder="Search documents... (⌘K)"
          className="w-full pl-10 pr-10 py-2 bg-obsidian-bg-secondary border border-obsidian-border rounded-md text-obsidian-text focus:outline-none focus:ring-2 focus:ring-obsidian-accent"
        />
        {isSearching ? (
          <Loader2 className="absolute right-3 w-4 h-4 text-obsidian-text-muted animate-spin" />
        ) : query ? (
          <button
            onClick={handleClear}
            className="absolute right-3 text-obsidian-text-muted hover:text-obsidian-text"
          >
            <X className="w-4 h-4" />
          </button>
        ) : null}
      </div>

      {/* Search Results Dropdown */}
      {showResults && results.length > 0 && (
        <div className="absolute z-50 w-full mt-2 bg-obsidian-bg-secondary border border-obsidian-border rounded-md shadow-lg max-h-96 overflow-y-auto">
          {results.map((result) => (
            <button
              key={result.doc_id}
              onClick={() => handleResultClick(result.doc_id)}
              className="w-full text-left px-4 py-3 hover:bg-obsidian-bg-hover border-b border-obsidian-border last:border-b-0 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-obsidian-text font-medium mb-1">
                    {result.title}
                  </h4>
                  {result.snippet && (
                    <p
                      className="text-sm text-obsidian-text-muted line-clamp-2"
                      dangerouslySetInnerHTML={{ __html: result.snippet }}
                    />
                  )}
                  {result.path && (
                    <p className="text-xs text-obsidian-text-muted mt-1 opacity-60">
                      {result.path}
                    </p>
                  )}
                </div>
                <div className="ml-3 flex flex-col items-end text-xs text-obsidian-text-muted opacity-60">
                  <div>{(result.score * 100).toFixed(0)}%</div>
                  {searchMode === 'hybrid' && result.keyword_score !== undefined && (
                    <div className="text-[10px] mt-0.5">
                      K:{(result.keyword_score * 100).toFixed(0)} S:{((result.semantic_score || 0) * 100).toFixed(0)}
                    </div>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* No Results Message */}
      {showResults && results.length === 0 && !isSearching && query && (
        <div className="absolute z-50 w-full mt-2 bg-obsidian-bg-secondary border border-obsidian-border rounded-md shadow-lg px-4 py-3">
          <p className="text-obsidian-text-muted text-sm">
            No results found for "{query}"
          </p>
        </div>
      )}

      {/* Backdrop to close results */}
      {showResults && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowResults(false)}
        />
      )}
    </div>
  )
}
