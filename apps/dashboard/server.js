import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const port = Number(process.env.PORT || 8080)

const contentTypes = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
  ['.jpg', 'image/jpeg'],
  ['.jpeg', 'image/jpeg'],
  ['.webmanifest', 'application/manifest+json; charset=utf-8'],
])

function logRequest(request, message) {
  console.log(`[request] ${request.method} ${request.url} ${message}`)
}

function sendText(response, statusCode, message) {
  response.writeHead(statusCode, {
    'content-type': 'text/plain; charset=utf-8',
    'cache-control': 'no-store',
  })
  response.end(message)
}

function getFilePath(requestUrl) {
  const parsedUrl = new URL(requestUrl, 'http://localhost')
  const pathname = parsedUrl.pathname === '/' ? '/index.html' : parsedUrl.pathname
  const decodedPath = decodeURIComponent(pathname)
  const requestedPath = path.resolve(rootDir, `.${decodedPath}`)

  if (!requestedPath.startsWith(rootDir + path.sep) && requestedPath !== rootDir) {
    return null
  }

  return requestedPath
}

const server = http.createServer((request, response) => {
  logRequest(request, 'received')

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    logRequest(request, 'status=405')
    sendText(response, 405, 'Method not allowed')
    return
  }

  let filePath

  try {
    filePath = getFilePath(request.url)
  } catch {
    logRequest(request, 'status=400')
    sendText(response, 400, 'Bad request')
    return
  }

  if (!filePath) {
    logRequest(request, 'resolved=BLOCKED status=403')
    sendText(response, 403, 'Forbidden')
    return
  }

  logRequest(request, `resolved=${filePath}`)

  fs.stat(filePath, (statError, stats) => {
    if (statError || !stats.isFile()) {
      logRequest(request, 'status=404')
      sendText(response, 404, 'Not found')
      return
    }

    const contentType = contentTypes.get(path.extname(filePath).toLowerCase())
      || 'application/octet-stream'

    response.writeHead(200, {
      'content-type': contentType,
      'cache-control': 'no-store',
    })

    logRequest(request, 'status=200')

    if (request.method === 'HEAD') {
      response.end()
      return
    }

    fs.createReadStream(filePath).pipe(response)
  })
})

server.listen(port, '0.0.0.0', () => {
  console.log(`AI_OS dashboard static server listening on port ${port}`)
})
