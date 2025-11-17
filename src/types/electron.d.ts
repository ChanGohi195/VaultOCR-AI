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
  runOCR: (filePath: string, lang?: string, autoDetect?: boolean) => Promise<{
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
        detected_language?: string
        language_confidence?: number
        mixed_languages?: Array<{
          lang: string
          percentage: number
          char_count: number
        }>
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
  // Phase 7 APIs
  getSupportedLanguages: () => Promise<{
    success: boolean
    result?: {
      languages: Array<{
        code: string
        name: string
        paddleocr: string
        tesseract: string
      }>
    }
    error?: string
  }>
  // Phase 8 APIs
  semanticSearch: (query: string, topK?: number, threshold?: number) => Promise<{
    success: boolean
    result?: {
      results: Array<{
        doc_id: string
        title: string
        content: string
        score: number
        metadata?: any
      }>
    }
    error?: string
  }>
  hybridSearch: (query: string, topK?: number, keywordWeight?: number, semanticWeight?: number) => Promise<{
    success: boolean
    result?: {
      results: Array<{
        doc_id: string
        title: string
        content: string
        score: number
        keyword_score?: number
        semantic_score?: number
        metadata?: any
      }>
    }
    error?: string
  }>
  findSimilar: (docId: string, topK?: number) => Promise<{
    success: boolean
    result?: {
      results: Array<{
        doc_id: string
        title: string
        content: string
        score: number
        metadata?: any
      }>
    }
    error?: string
  }>
  // Phase 9 APIs
  summarize: (text: string, options?: {
    maxLength?: number
    minLength?: number
    language?: string
    ratio?: number
  }) => Promise<{
    success: boolean
    result?: {
      summary: string
      original_length: number
      summary_length: number
      compression_ratio: number
      model_used: string
      language?: string
      error?: string
    }
    error?: string
  }>
  translate: (text: string, sourceLang: string, targetLang: string) => Promise<{
    success: boolean
    result?: {
      translation: string
      source_lang: string
      target_lang: string
      model_used: string
      original_length: number
      translation_length: number
      error?: string
    }
    error?: string
  }>
  extractTemplate: (text: string, templateName?: string) => Promise<{
    success: boolean
    result?: any
    error?: string
  }>
  generateSearchablePDF: (options: {
    mode: 'text' | 'images'
    text?: string
    images?: string[]
    ocrResults?: any[]
    outputPath: string
    metadata?: {
      title?: string
      author?: string
      subject?: string
      keywords?: string
    }
    fontSize?: number
    lineSpacing?: number
  }) => Promise<{
    success: boolean
    result?: {
      output_path: string
      page_count: number
      file_size: number
    }
    error?: string
  }>
  getTemplates: () => Promise<{
    success: boolean
    result?: {
      templates: Array<{
        name: string
        description: string
      }>
    }
    error?: string
  }>
  getTranslationPairs: () => Promise<{
    success: boolean
    result?: {
      pairs: Array<{
        source: string
        target: string
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
