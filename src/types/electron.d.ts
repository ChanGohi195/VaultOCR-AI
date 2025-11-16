export interface ElectronAPI {
  readFile: (filePath: string) => Promise<{ success: boolean; content?: string; error?: string }>
  writeFile: (filePath: string, content: string) => Promise<{ success: boolean; error?: string }>
  listFiles: (dirPath: string) => Promise<{
    success: boolean
    files?: Array<{ name: string; isDirectory: boolean; path: string }>
    error?: string
  }>
  runOCR: (imagePath: string) => Promise<{
    success: boolean
    result?: { text: string; chunks: any[] }
    error?: string
  }>
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
