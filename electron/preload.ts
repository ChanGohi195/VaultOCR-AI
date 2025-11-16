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
  runOCR: (filePath: string) => ipcRenderer.invoke('run-ocr', filePath),
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
})
