// frontend/vite.config.ts
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { TanStackRouterVite } from '@tanstack/router-plugin/vite';
import tailwindcss from '@tailwindcss/vite'; // ✅ AJOUTER
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [
      TanStackRouterVite({
        routesDirectory: './src/pages',
        generatedRouteTree: './src/routeTree.gen.ts',
        routeFileIgnorePrefix: '-',
        quoteStyle: 'single',
        semicolons: true,
        autoCodeSplitting: true,
      }),
      
      tailwindcss(), // ✅ AJOUTER CETTE LIGNE
      
      react({
        babel: {
          plugins: env['VITE_ENABLE_REACT_COMPILER'] === 'true' 
            ? [['babel-plugin-react-compiler']] 
            : [],
        },
      }),
    ],
    // ... reste de ta config identique
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    
    build: {
      target: 'ES2022',
      sourcemap: env['GENERATE_SOURCEMAP'] === 'true',
      cssCodeSplit: true,
      minify: 'esbuild',
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor-react': ['react', 'react-dom'],
            'vendor-tanstack': ['@tanstack/react-query', '@tanstack/react-router'],
            'vendor-utils': ['clsx', 'tailwind-merge', 'zod'],
          },
        },
      },
    },

    server: {
      port: 3000,
      host: '0.0.0.0',
      strictPort: true,
      hmr: {
        port: 3001,
      },
    },

    define: {
      __APP_VERSION__: JSON.stringify(process.env['npm_package_version']),
      __REACT_VERSION__: JSON.stringify('19.1.0'),
      __TANSTACK_QUERY_VERSION__: JSON.stringify('5.82.0'),
      __TANSTACK_ROUTER_VERSION__: JSON.stringify('1.127.3'),
    },

    esbuild: {
      target: 'ES2022',
      keepNames: true,
    },
  };
});