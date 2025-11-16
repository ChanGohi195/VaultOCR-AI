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
    canceled?: boolean
  }>
  runOCR: (filePath: string) => Promise<{
    success: boolean
    result?: {
      text: string
      chunks: any[]
      paragraphs?: any[]
      metadata?: {
        page_count: number
        layout_type: string
      }
    }
    error?: string
  }>
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
