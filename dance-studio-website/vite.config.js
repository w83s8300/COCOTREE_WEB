import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  return {
    server: {
      host: '0.0.0.0',
      port: 5173,
      watch: {
        usePolling: true, // Required for Docker volume mounts
      },
      proxy: {
        '/api': {
          target: process.env.API_PROXY_TARGET || 'http://localhost:8001',
          changeOrigin: true,
        }
      },
      allowedHosts: true
    },
    plugins: [
      vue(),
      ...(mode === 'development' ? [vueDevTools()] : []),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor-vue': ['vue', 'vue-router'],
            'vendor-bootstrap': ['bootstrap'],
            'vendor-axios': ['axios'],
          }
        }
      }
    }
  }
})
