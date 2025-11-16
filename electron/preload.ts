import { contextBridge, ipcRenderer } from 'electron'

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  readFile: (filePath: string) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath: string, content: string) =>
    ipcRenderer.invoke('write-file', filePath, content),
  listFiles: (dirPath: string) => ipcRenderer.invoke('list-files', dirPath),
  runOCR: (imagePath: string) => ipcRenderer.invoke('run-ocr', imagePath),
})
