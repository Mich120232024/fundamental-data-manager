import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@services': path.resolve(__dirname, './src/services'),
      '@store': path.resolve(__dirname, './src/store'),
      '@modules': path.resolve(__dirname, './src/modules'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@types': path.resolve(__dirname, './src/types'),
      '@context': path.resolve(__dirname, './src/context'),
      '@gzc/ui': path.resolve(__dirname, './src/shared/gzc-ui'),
    }
  },
  server: {
    port: 3200,
    host: true, // This binds to all network interfaces
    strictPort: false,
    open: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    // Enable modular architecture with code splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['framer-motion', 'react-grid-layout', 'clsx'],
          'data-vendor': ['@tanstack/react-query', 'axios', 'zustand'],
          'azure-vendor': ['@azure/msal-browser', '@azure/msal-react'],
          
          // Feature chunks - for future microservice separation
          'analytics': [
            './src/components/analytics/AnalyticsDashboardExample.tsx',
            './src/components/analytics/CompoundAnalyticsPanel.tsx',
            './src/components/analytics/FilterAwareAnalyticsContainer.tsx',
          ],
          'trading': [
            './src/modules/trading/TradingOperationsView.tsx',
            './src/components/OrderManagement.tsx',
            './src/components/TradeExecutions_Styled.tsx',
          ],
          'admin': [
            './src/components/GZCPortfolioComponent.tsx',
            './src/components/FXPositionsComponent.tsx',
          ],
        }
      }
    },
    // Prepare for future microservice deployment
    cssCodeSplit: true,
    sourcemap: true,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  // Prepare for module federation alternative
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      '@azure/msal-browser',
      '@tanstack/react-query'
    ]
  }
})