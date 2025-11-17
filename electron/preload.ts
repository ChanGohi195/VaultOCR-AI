import { contextBridge, ipcRenderer } from 'electron'

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  readFile: (filePath: string) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath: string, content: string) =>
    ipcRenderer.invoke('write-file', filePath, content),
  listFiles: (dirPath: string) => ipcRenderer.invoke('list-files', dirPath),
  selectFile: (options?: any) => ipcRenderer.invoke('select-file', options),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  runOCR: (filePath: string, lang?: string, autoDetect?: boolean) =>
    ipcRenderer.invoke('run-ocr', filePath, lang, autoDetect),
  // Phase 4 APIs
  searchDocuments: (query: string, limit?: number) =>
    ipcRenderer.invoke('search-documents', query, limit),
  saveDocument: (docData: any) => ipcRenderer.invoke('save-document', docData),
  exportDocument: (exportData: any) =>
    ipcRenderer.invoke('export-document', exportData),
  listDocuments: (limit?: number, offset?: number) =>
    ipcRenderer.invoke('list-documents', limit, offset),
  getTags: () => ipcRenderer.invoke('get-tags'),
  getDocument: (docId: string) => ipcRenderer.invoke('get-document', docId),
  // Phase 5 APIs
  batchOCR: (filePaths: string[], autoSave: boolean, tags: string[]) =>
    ipcRenderer.invoke('batch-ocr', filePaths, autoSave, tags),
  // Phase 7 APIs
  getSupportedLanguages: () => ipcRenderer.invoke('get-supported-languages'),
  // Phase 8 APIs
  semanticSearch: (query: string, topK?: number, threshold?: number) =>
    ipcRenderer.invoke('semantic-search', query, topK, threshold),
  hybridSearch: (query: string, topK?: number, keywordWeight?: number, semanticWeight?: number) =>
    ipcRenderer.invoke('hybrid-search', query, topK, keywordWeight, semanticWeight),
  findSimilar: (docId: string, topK?: number) =>
    ipcRenderer.invoke('find-similar', docId, topK),
  // Phase 9 APIs
  summarize: (text: string, options?: any) =>
    ipcRenderer.invoke('summarize', text, options),
  translate: (text: string, sourceLang: string, targetLang: string) =>
    ipcRenderer.invoke('translate', text, sourceLang, targetLang),
  extractTemplate: (text: string, templateName?: string) =>
    ipcRenderer.invoke('extract-template', text, templateName),
  generateSearchablePDF: (options: any) =>
    ipcRenderer.invoke('generate-searchable-pdf', options),
  getTemplates: () =>
    ipcRenderer.invoke('get-templates'),
  getTranslationPairs: () =>
    ipcRenderer.invoke('get-translation-pairs'),
})
