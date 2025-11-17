import { app, BrowserWindow, ipcMain, dialog, shell } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import { spawn, ChildProcess } from 'child_process'
import fs from 'fs'
import os from 'os'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

let mainWindow: BrowserWindow | null = null
let pythonProcess: ChildProcess | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 600,
    backgroundColor: '#1e1e1e',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
    titleBarStyle: 'hiddenInset',
    frame: true,
  })

  // Development mode
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL)
    mainWindow.webContents.openDevTools()
  } else {
    // Production mode
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  // Clean up Python process
  if (pythonProcess) {
    pythonProcess.kill()
    pythonProcess = null
  }

  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// IPC Handlers
ipcMain.handle('read-file', async (event, filePath: string) => {
  const fs = await import('fs/promises')
  try {
    const content = await fs.readFile(filePath, 'utf-8')
    return { success: true, content }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('write-file', async (event, filePath: string, content: string) => {
  const fs = await import('fs/promises')
  try {
    await fs.writeFile(filePath, content, 'utf-8')
    return { success: true }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('list-files', async (event, dirPath: string) => {
  const fs = await import('fs/promises')
  try {
    const entries = await fs.readdir(dirPath, { withFileTypes: true })
    const files = entries.map(entry => ({
      name: entry.name,
      isDirectory: entry.isDirectory(),
      path: path.join(dirPath, entry.name)
    }))
    return { success: true, files }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('select-file', async (event, options?: any) => {
  const result = await dialog.showOpenDialog(mainWindow!, {
    properties: ['openFile'],
    filters: [
      { name: 'Images & PDF', extensions: ['jpg', 'jpeg', 'png', 'pdf'] },
      { name: 'All Files', extensions: ['*'] }
    ],
    ...options
  })

  if (result.canceled) {
    return { success: false, canceled: true }
  }

  return {
    success: true,
    filePath: result.filePaths[0],
    filePaths: result.filePaths
  }
})

ipcMain.handle('select-directory', async (event) => {
  const result = await dialog.showOpenDialog(mainWindow!, {
    properties: ['openDirectory']
  })

  if (result.canceled) {
    return null
  }

  return result.filePaths[0]
})

ipcMain.handle('run-ocr', async (event, filePath: string, lang?: string, autoDetect?: boolean) => {
  try {
    const result = await runPythonOCR(filePath, lang, autoDetect)
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

// Phase 7: Get supported languages
ipcMain.handle('get-supported-languages', async (event) => {
  try {
    const result = await runPythonCommand({
      command: 'get_supported_languages'
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

// Phase 4 IPC Handlers
ipcMain.handle('search-documents', async (event, query: string, limit?: number) => {
  try {
    const result = await runPythonCommand({
      command: 'search',
      query,
      limit: limit || 20
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('save-document', async (event, docData: any) => {
  try {
    const result = await runPythonCommand({
      command: 'save_document',
      ...docData
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('export-document', async (event, exportData: any) => {
  try {
    const result = await runPythonCommand({
      command: 'export',
      ...exportData
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('list-documents', async (event, limit?: number, offset?: number) => {
  try {
    const result = await runPythonCommand({
      command: 'list_documents',
      limit: limit || 100,
      offset: offset || 0
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('get-tags', async (event) => {
  try {
    const result = await runPythonCommand({
      command: 'get_tags'
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('get-document', async (event, docId: string) => {
  try {
    const result = await runPythonCommand({
      command: 'get_document',
      doc_id: docId
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('batch-ocr', async (event, filePaths: string[], autoSave: boolean, tags: string[]) => {
  try {
    const result = await runPythonCommand({
      command: 'batch_ocr',
      file_paths: filePaths,
      auto_save: autoSave,
      tags: tags || []
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

// Phase 8: Vector Search IPC Handlers
ipcMain.handle('semantic-search', async (event, query: string, topK?: number, threshold?: number) => {
  try {
    const result = await runPythonCommand({
      command: 'semantic_search',
      query,
      top_k: topK || 10,
      threshold: threshold || 0.0
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('hybrid-search', async (event, query: string, topK?: number, keywordWeight?: number, semanticWeight?: number) => {
  try {
    const result = await runPythonCommand({
      command: 'hybrid_search',
      query,
      top_k: topK || 10,
      keyword_weight: keywordWeight || 0.5,
      semantic_weight: semanticWeight || 0.5
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('find-similar', async (event, docId: string, topK?: number) => {
  try {
    const result = await runPythonCommand({
      command: 'find_similar',
      doc_id: docId,
      top_k: topK || 5
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

// Phase 9: AI feature IPC Handlers
ipcMain.handle('summarize', async (event, text: string, options?: any) => {
  try {
    const result = await runPythonCommand({
      command: 'summarize',
      text,
      max_length: options?.maxLength || 150,
      min_length: options?.minLength || 40,
      language: options?.language || 'en',
      ratio: options?.ratio
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('translate', async (event, text: string, sourceLang: string, targetLang: string) => {
  try {
    const result = await runPythonCommand({
      command: 'translate',
      text,
      source_lang: sourceLang,
      target_lang: targetLang
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('extract-template', async (event, text: string, templateName?: string) => {
  try {
    const result = await runPythonCommand({
      command: 'extract_template',
      text,
      template: templateName
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('generate-searchable-pdf', async (event, options: any) => {
  try {
    const result = await runPythonCommand({
      command: 'generate_searchable_pdf',
      mode: options.mode || 'text',
      text: options.text,
      images: options.images,
      ocr_results: options.ocrResults,
      output_path: options.outputPath,
      metadata: options.metadata,
      font_size: options.fontSize || 12,
      line_spacing: options.lineSpacing || 14
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('get-templates', async (event) => {
  try {
    const result = await runPythonCommand({
      command: 'get_templates'
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

ipcMain.handle('get-translation-pairs', async (event) => {
  try {
    const result = await runPythonCommand({
      command: 'get_translation_pairs'
    })
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

// Generic Python command runner
function runPythonCommand(request: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonScriptPath = path.join(__dirname, '../../python/ocr_server.py')

    if (!pythonProcess) {
      pythonProcess = spawn('python3', [pythonScriptPath], {
        stdio: ['pipe', 'pipe', 'pipe']
      })

      pythonProcess.on('error', (error) => {
        console.error('Failed to start Python process:', error)
        pythonProcess = null
      })

      pythonProcess.on('exit', (code) => {
        console.log(`Python process exited with code ${code}`)
        pythonProcess = null
      })

      if (pythonProcess.stderr) {
        pythonProcess.stderr.on('data', (data) => {
          console.error('Python stderr:', data.toString())
        })
      }
    }

    if (pythonProcess?.stdin) {
      pythonProcess.stdin.write(JSON.stringify(request) + '\n')
    }

    let responseData = ''

    const onData = (data: Buffer) => {
      responseData += data.toString()

      try {
        const response = JSON.parse(responseData)
        pythonProcess?.stdout?.removeListener('data', onData)

        if (response.status === 'ok') {
          resolve(response.result || response)
        } else {
          reject(new Error(response.message || 'Command failed'))
        }
      } catch (e) {
        // Not complete JSON yet, continue accumulating
      }
    }

    if (pythonProcess?.stdout) {
      pythonProcess.stdout.on('data', onData)
    }

    setTimeout(() => {
      pythonProcess?.stdout?.removeListener('data', onData)
      reject(new Error('Command timeout'))
    }, 60000)
  })
}

// Python OCR integration (uses generic runner)
// Phase 7: Added multi-language support
function runPythonOCR(filePath: string, lang?: string, autoDetect: boolean = true): Promise<any> {
  const ext = path.extname(filePath).toLowerCase()
  const command = ext === '.pdf' ? 'ocr_pdf' : 'ocr'
  const requestKey = ext === '.pdf' ? 'pdf_path' : 'image_path'

  const request: any = {
    command,
    [requestKey]: filePath
  }

  // Phase 7: Add language parameters
  if (lang) {
    request.lang = lang
  }
  if (autoDetect !== undefined) {
    request.auto_detect = autoDetect
  }

  return runPythonCommand(request)
})
