export interface ElectronAPI {
  readFile: (filePath: string) => Promise<{ success: boolean; content?: string; error?: string }>
  writeFile: (filePath: string, content: string) => Promise<{ success: boolean; error?: string }>
  listFiles: (dirPath: string) => Promise<{
    success: boolean
    files?: Array<{ name: string; isDirectory: boolean; path: string }>
    error?: string
  }>
  selectFile: (options?: any) => Promise<{
    success: boolean
    filePath?: string
    filePaths?: string[]
    canceled?: boolean
  }>
  selectDirectory: () => Promise<string | null>
  runOCR: (filePath: string) => Promise<{
    success: boolean
    result?: {
      text: string
      chunks: any[]
      paragraphs?: any[]
      metadata?: {
        page_count: number
        layout_type: string
        section_count?: number
        total_tables?: number
      }
      toc?: any[]
      sections?: any[]
    }
    error?: string
  }>
  // Phase 4 APIs
  searchDocuments: (query: string, limit?: number) => Promise<{
    success: boolean
    result?: {
      results: Array<{
        doc_id: string
        title: string
        snippet: string
        path?: string
        score: number
      }>
    }
    error?: string
  }>
  saveDocument: (docData: {
    title: string
    content: string
    tags?: string[]
    metadata?: any
    page_count?: number
  }) => Promise<{
    success: boolean
    result?: { doc_id: string }
    error?: string
  }>
  exportDocument: (exportData: {
    format: string
    content: string
    metadata?: any
    toc?: any[]
    vault_path?: string
  }) => Promise<{
    success: boolean
    result?: { message?: string; path?: string }
    error?: string
  }>
  listDocuments: (limit?: number, offset?: number) => Promise<{
    success: boolean
    result?: {
      documents: Array<{
        id: string
        title: string
        file_path?: string
        created_at: string
        page_count?: number
        tags: string[]
      }>
    }
    error?: string
  }>
  getTags: () => Promise<{
    success: boolean
    result?: { tags: string[] }
    error?: string
  }>
  getDocument: (docId: string) => Promise<{
    success: boolean
    result?: {
      document: {
        id: string
        title: string
        content: string
        file_path?: string
        created_at: string
        page_count?: number
        tags: string[]
        metadata?: any
      }
    }
    error?: string
  }>
  // Phase 5 APIs
  batchOCR: (filePaths: string[], autoSave: boolean, tags: string[]) => Promise<{
    success: boolean
    result?: {
      total: number
      success: number
      failed: number
      files: Array<{
        path: string
        filename: string
        status: string
        error?: string
        doc_id?: string
      }>
    }
    error?: string
  }>
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
