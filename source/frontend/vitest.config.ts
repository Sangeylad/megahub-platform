// frontend/vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [
    react({
      jsxRuntime: 'automatic',
      jsxImportSource: 'react',
    }),
  ],
  
  test: {
    // ==========================================
    // ENVIRONMENT & SETUP - React 19
    // ==========================================
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    css: true,
    
    // ==========================================
    // COVERAGE CONFIGURATION - React 19 + TanStack v5
    // ==========================================
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov', 'json-summary'],
      reportOnFailure: true,
      
      // Exclusions justifiées
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/index.ts',          // Barrel exports
        '**/*.stories.*',       // Storybook
        'dist/',
        'coverage/',
      ],
      
      // Seuils qualité selon standards MegaHub
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 85,
          statements: 85,
        },
      },
    },
    
    // ==========================================
    // REPORTERS CONFIGURATION
    // ==========================================
    reporters: process.env.CI 
      ? ['default', 'junit', 'github-actions']
      : ['default', 'html'],
    
    outputFile: {
      junit: './test-results/junit.xml',
      html: './test-results/index.html',
    },
  },
  
  // ==========================================
  // RÉSOLUTION PATHS
  // ==========================================
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@/components': resolve(__dirname, './src/components'),
      '@/features': resolve(__dirname, './src/features'),
      '@/hooks': resolve(__dirname, './src/hooks'),
      '@/services': resolve(__dirname, './src/services'),
      '@/stores': resolve(__dirname, './src/stores'),
      '@/types': resolve(__dirname, './src/types'),
      '@/utils': resolve(__dirname, './src/utils'),
      '@/test': resolve(__dirname, './src/test'),
    },
  },
  
  // ==========================================
  // DÉFINITIONS GLOBALES TESTS
  // ==========================================
  define: {
    __DEV__: JSON.stringify(true),
    __PROD__: JSON.stringify(false),
    __VERSION__: JSON.stringify('3.0.0-test'),
    __REACT_VERSION__: JSON.stringify('19.1.0'),
    __TANSTACK_QUERY_VERSION__: JSON.stringify('5.83.0'),
  },
});