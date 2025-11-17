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

ipcMain.handle('run-ocr', async (event, filePath: string) => {
  try {
    const result = await runPythonOCR(filePath)
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
function runPythonOCR(filePath: string): Promise<any> {
  const ext = path.extname(filePath).toLowerCase()
  const command = ext === '.pdf' ? 'ocr_pdf' : 'ocr'
  const requestKey = ext === '.pdf' ? 'pdf_path' : 'image_path'

  return runPythonCommand({
    command,
    [requestKey]: filePath
  })
})
