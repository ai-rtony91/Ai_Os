import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { cpSync, existsSync } from 'node:fs'
import path from 'node:path'

const staticDashboardOutputs = [
  'AIOS_STATIC_PREVIEW.html',
  'manifest.webmanifest',
  'css',
  'js',
  'icons',
  'assets',
  'mock-data',
  'package.json',
  'server.js',
]

function copyStaticDashboardRuntime() {
  let rootDir = process.cwd()
  let outDir = 'dist'

  return {
    name: 'copy-static-dashboard-runtime',
    apply: 'build',
    configResolved(config) {
      rootDir = config.root
      outDir = path.resolve(config.root, config.build.outDir)
    },
    writeBundle() {
      const missingSources = staticDashboardOutputs.filter((entry) => {
        return !existsSync(path.resolve(rootDir, entry))
      })

      if (missingSources.length > 0) {
        throw new Error(
          `Static dashboard source missing: ${missingSources.join(', ')}`,
        )
      }

      for (const entry of staticDashboardOutputs) {
        cpSync(path.resolve(rootDir, entry), path.join(outDir, entry), {
          recursive: true,
          force: true,
        })
      }
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), copyStaticDashboardRuntime()],
  server: {
    proxy: {
      '/api': 'http://localhost:5050',
    },
  },
})
