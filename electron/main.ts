import { app, BrowserWindow, ipcMain, dialog } from 'electron'
import path from 'path'
import { fileURLToPath } from 'url'
import { spawn, ChildProcess } from 'child_process'

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

  return { success: true, filePath: result.filePaths[0] }
})

ipcMain.handle('run-ocr', async (event, filePath: string) => {
  try {
    const result = await runPythonOCR(filePath)
    return { success: true, result }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
})

// Python OCR integration
function runPythonOCR(filePath: string): Promise<any> {
  return new Promise((resolve, reject) => {
    // Determine Python script path
    const pythonScriptPath = path.join(__dirname, '../../python/ocr_server.py')

    // Spawn Python process if not already running
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

    // Determine command based on file extension
    const ext = path.extname(filePath).toLowerCase()
    const command = ext === '.pdf' ? 'ocr_pdf' : 'ocr'
    const requestKey = ext === '.pdf' ? 'pdf_path' : 'image_path'

    // Send request to Python
    const request = {
      command,
      [requestKey]: filePath
    }

    if (pythonProcess?.stdin) {
      pythonProcess.stdin.write(JSON.stringify(request) + '\n')
    }

    // Read response from Python
    let responseData = ''

    const onData = (data: Buffer) => {
      responseData += data.toString()

      // Try to parse JSON response
      try {
        const response = JSON.parse(responseData)

        // Remove listener
        pythonProcess?.stdout?.removeListener('data', onData)

        if (response.status === 'ok') {
          resolve(response.result)
        } else {
          reject(new Error(response.message || 'OCR failed'))
        }
      } catch (e) {
        // Not complete JSON yet, continue accumulating
      }
    }

    if (pythonProcess?.stdout) {
      pythonProcess.stdout.on('data', onData)
    }

    // Timeout after 60 seconds
    setTimeout(() => {
      pythonProcess?.stdout?.removeListener('data', onData)
      reject(new Error('OCR timeout'))
    }, 60000)
  })
})
