import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    // Proxy API and audio requests to the FastAPI backend
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        // Don't fail on ECONNREFUSED - let the app handle it gracefully
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.log(`[vite-proxy] Backend connection error: ${err.message}. Make sure the backend is running on port 8000.`)
          })
        },
      },
      '/audio': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.log(`[vite-proxy] Backend connection error: ${err.message}.`)
          })
        },
      },
    },
  },
})
</write_to_file>