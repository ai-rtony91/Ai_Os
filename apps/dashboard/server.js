import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'
import crypto from 'node:crypto'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const port = Number(process.env.PORT || 8080)
const repoRootDir = path.basename(rootDir) === 'dist'
  ? path.resolve(rootDir, '..', '..', '..')
  : path.resolve(rootDir, '..', '..')
const liveAutonomyBridgeStatePath = path.resolve(
  repoRootDir,
  process.env.AIOS_AUTONOMY_BRIDGE_STATE_PATH
    || 'telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json',
)
const dashboardProjectionPath = path.resolve(repoRootDir, '.aios/runtime/dashboard_measurement/AIOS_DASHBOARD_PROJECTION_V1.json')
const projectionLimit = 250 * 1024

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

function isLiveAutonomyBridgeStateRequest(requestUrl) {
  const parsedUrl = new URL(requestUrl, 'http://localhost')
  return parsedUrl.pathname === '/live-data/autonomy_bridge_state.json'
}

function isDashboardProjectionRequest(requestUrl) { return new URL(requestUrl, 'http://localhost').pathname === '/aios-dashboard-projection' }

function serveDashboardProjection(request, response) {
  if (!dashboardProjectionPath.startsWith(path.resolve(repoRootDir) + path.sep)) return sendText(response, 403, 'Forbidden')
  fs.readFile(dashboardProjectionPath, (error, raw) => {
    if (error || raw.length > projectionLimit) return sendText(response, error?.code === 'ENOENT' ? 404 : 503, 'Projection unavailable')
    let projection
    try { projection = JSON.parse(raw) } catch { return sendText(response, 503, 'Projection unavailable') }
    if (projection.schema_version !== 'AIOS_DASHBOARD_PROJECTION_V1' || !projection.dimensions || !projection.receipts) return sendText(response, 503, 'Projection unavailable')
    const etag = `"${crypto.createHash('sha256').update(raw).digest('hex')}"`
    if (request.headers['if-none-match'] === etag) { response.writeHead(304, { etag }); response.end(); return }
    response.writeHead(200, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', etag, 'x-aios-projection-state': projection.projection_state || 'UNAVAILABLE' })
    response.end(request.method === 'HEAD' ? undefined : raw)
  })
}

const server = http.createServer((request, response) => {
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    sendText(response, 405, 'Method not allowed')
    return
  }

  if (isLiveAutonomyBridgeStateRequest(request.url)) {
    fs.stat(liveAutonomyBridgeStatePath, (statError, stats) => {
      if (statError || !stats.isFile()) {
        sendText(response, 404, 'Not found')
        return
      }

      response.writeHead(200, {
        'content-type': 'application/json; charset=utf-8',
        'cache-control': 'no-store',
      })

      if (request.method === 'HEAD') {
        response.end()
        return
      }

      fs.createReadStream(liveAutonomyBridgeStatePath).pipe(response)
    })
    return
  }

  if (isDashboardProjectionRequest(request.url)) { serveDashboardProjection(request, response); return }

  let filePath

  try {
    filePath = getFilePath(request.url)
  } catch {
    sendText(response, 400, 'Bad request')
    return
  }

  if (!filePath) {
    sendText(response, 403, 'Forbidden')
    return
  }

  fs.stat(filePath, (statError, stats) => {
    if (statError || !stats.isFile()) {
      sendText(response, 404, 'Not found')
      return
    }

    const contentType = contentTypes.get(path.extname(filePath).toLowerCase())
      || 'application/octet-stream'

    response.writeHead(200, {
      'content-type': contentType,
      'cache-control': 'no-store',
    })

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
