import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5176,
    proxy: {
      '/api/bloomberg': {
        target: 'http://20.172.249.92:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/bloomberg/, '/api'),
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('Bloomberg API proxy error:', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Bloomberg API proxy request:', req.method, req.url);
          });
        },
      },
    },
  },
})
