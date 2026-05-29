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
    hmr: {
      // Disable HMR overlay to prevent crash loops from proxy errors
      overlay: false,
    },
    // Proxy API and audio requests to the FastAPI backend
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        // Suppress proxy errors to prevent Vite from crashing
        configure: (proxy) => {
          proxy.on('error', () => {
            // Silently ignore proxy errors (backend not running yet)
          })
          proxy.on('proxyReq', () => {})
          proxy.on('proxyRes', () => {})
        },
      },
      '/audio': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy) => {
          proxy.on('error', () => {
            // Silently ignore proxy errors (backend not running yet)
          })
        },
      },
    },
  },
})