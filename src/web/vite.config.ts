import { defineConfig } from 'vite';  // vite@4.4.5
import react from '@vitejs/plugin-react';  // @vitejs/plugin-react@4.0.0
import tsconfigPaths from 'vite-tsconfig-paths';  // vite-tsconfig-paths@4.2.0
import svgr from 'vite-plugin-svgr';  // vite-plugin-svgr@3.2.0
import path from 'path';  // Node.js path module

/**
 * Vite configuration for the Freight Price Movement Agent web application.
 * This config sets up the development environment and production build process.
 */
export default defineConfig({
  plugins: [
    react(),        // Add React support with Fast Refresh
    tsconfigPaths(), // Resolve imports using tsconfig paths
    svgr()          // Transform SVGs into React components
  ],
  
  // Development server configuration
  server: {
    port: 3000,     // Run dev server on port 3000
    open: true,     // Auto-open browser on server start
    proxy: {
      '/api': {     // Proxy API requests to backend
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    },
    cors: true      // Enable CORS for development
  },
  
  // Build configuration for production
  build: {
    outDir: 'dist',     // Output directory for production build
    sourcemap: true,    // Generate source maps for debugging
    minify: 'terser',   // Use Terser for minification
    terserOptions: {
      compress: {
        drop_console: true, // Remove console logs in production
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor libraries for better caching
          vendor: ['react', 'react-dom', 'react-router-dom'],
          chart: ['chart.js', 'react-chartjs-2'],
        }
      }
    }
  },
  
  // Resolve configuration for import aliases
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src') // Allow '@' to point to src directory
    }
  },
  
  // CSS configuration
  css: {
    devSourcemap: true, // Enable CSS source maps for development
  },
  
  // Environment variables configuration - only expose env vars prefixed with VITE_
  envPrefix: 'VITE_',
  
  // Define global constants available in the application
  define: {
    __APP_VERSION__: JSON.stringify(process.env.VITE_APP_VERSION || '1.0.0'),
  }
});