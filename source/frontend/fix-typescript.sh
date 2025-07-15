#!/bin/bash
set -euo pipefail

# ==========================================
# FIX CRITIQUE TYPESCRIPT + REACT 19 - STANDARDS LEADERS 2025
# Configuration TypeScript 5.8.3 + React 19 + Vite 6 + TanStack v5
# ==========================================

cd /var/www/megahub/frontend/react-app

echo "🔥 FIX CRITIQUE: TypeScript + React 19 selon standards leaders..."

# ==========================================
# 1. CORRIGER TSCONFIG.JSON - STANDARDS LEADERS
# ==========================================

echo "📝 Configuration TypeScript 5.8.3 + React 19 selon standards leaders..."

cat > tsconfig.json << 'EOF'
{
  "$schema": "https://json.schemastore.org/tsconfig",
  "compilerOptions": {
    /* === BASE CONFIG TypeScript 5.8.3 === */
    "target": "ES2022",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleDetection": "force",

    /* === BUNDLER MODE VITE 6 === */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "jsxImportSource": "react",

    /* === ENHANCED STRICT MODE 5.8.3 === */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,

    /* === TYPESCRIPT 5.8.3 ENHANCED FEATURES === */
    "verbatimModuleSyntax": true,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,

    /* === PATH MAPPING === */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/features/*": ["./src/features/*"],
      "@/hooks/*": ["./src/hooks/*"],
      "@/services/*": ["./src/services/*"],
      "@/stores/*": ["./src/stores/*"],
      "@/types/*": ["./src/types/*"],
      "@/utils/*": ["./src/utils/*"],
      "@/styles/*": ["./src/styles/*"],
      "@/assets/*": ["./src/assets/*"],
      "@/pages/*": ["./src/pages/*"]
    },

    /* === REACT 19 + VITE 6 TYPES === */
    "types": ["vite/client", "@types/react", "@types/react-dom", "@types/node"],
    "typeRoots": ["./node_modules/@types"],
    "resolveJsonModule": true
  },

  "include": [
    "src/**/*.ts",
    "src/**/*.tsx",
    "src/**/*.d.ts",
    "vite.config.ts",
    "vitest.config.ts"
  ],

  "exclude": [
    "node_modules",
    "dist",
    "build",
    "coverage",
    "**/*.test.ts",
    "**/*.test.tsx",
    "**/*.spec.ts",
    "**/*.spec.tsx"
  ]
}
EOF

# ==========================================
# 2. CORRIGER VITE-ENV.D.TS - REACT 19 TYPES
# ==========================================

echo "🔧 Types Vite + React 19 avec variables d'environnement..."

cat > src/vite-env.d.ts << 'EOF'
/// <reference types="vite/client" />
/// <reference types="@types/react" />
/// <reference types="@types/react-dom" />

// Types environnement Vite + React 19
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_NODE_ENV: string;
  readonly VITE_ENABLE_REACT_COMPILER: string;
  readonly VITE_ENABLE_LIGHTNING_CSS: string;
  readonly VITE_ENABLE_DEVTOOLS: string;
  readonly VITE_DEBUG: string;
  readonly VITE_ENABLE_MOCK_API: string;
  readonly GENERATE_SOURCEMAP: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Types React 19 augmentations - Server Components ready
declare module 'react' {
  interface CSSProperties {
    [key: `--${string}`]: string | number | undefined;
  }
  
  // React 19 - ref comme prop normale (plus de forwardRef)
  interface ComponentProps<T extends keyof JSX.IntrinsicElements | React.JSXElementConstructor<any>> {
    ref?: React.Ref<T extends keyof JSX.IntrinsicElements ? JSX.IntrinsicElements[T] extends React.DetailedHTMLProps<React.HTMLAttributes<infer U>, any> ? U : any : any>;
  }
}

// Process.env types pour Node.js
declare namespace NodeJS {
  interface ProcessEnv {
    readonly npm_package_version: string;
    readonly GENERATE_SOURCEMAP: string;
  }
}

// Types pour assets
declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.jpeg' {
  const content: string;
  export default content;
}

declare module '*.gif' {
  const content: string;
  export default content;
}

declare module '*.webp' {
  const content: string;
  export default content;
}

// Types TanStack Router v5
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
EOF

# ==========================================
# 3. INSTALLER TYPES MANQUANTS
# ==========================================

echo "📦 Installation types React 19 + Node.js..."

# Installer les types React 19 et Node.js si manquants
npm install --save-dev @types/react@latest @types/react-dom@latest

# ==========================================
# 4. CORRIGER VITE.CONFIG.TS - VARIABLES ENV
# ==========================================

echo "⚙️ Configuration Vite + TypeScript strict..."

cat > vite.config.ts << 'EOF'
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { TanStackRouterVite } from '@tanstack/router-plugin/vite';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [
      // TanStack Router Plugin v1.126.1 - File-based routing
      TanStackRouterVite({
        routesDirectory: './src/pages',
        generatedRouteTree: './src/routeTree.gen.ts',
        routeFileIgnorePrefix: '-',
        quoteStyle: 'single',
        semicolons: true,
        autoCodeSplitting: true,
      }),
      
      // React 19 + React Compiler support
      react({
        babel: {
          plugins: env['VITE_ENABLE_REACT_COMPILER'] === 'true' 
            ? [['babel-plugin-react-compiler']] 
            : [],
        },
      }),
      
      // Tailwind v4 avec @tailwindcss/vite
      tailwindcss(),
    ],

    // Résolution des chemins
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@/components': path.resolve(__dirname, './src/components'),
        '@/features': path.resolve(__dirname, './src/features'),
        '@/hooks': path.resolve(__dirname, './src/hooks'),
        '@/services': path.resolve(__dirname, './src/services'),
        '@/stores': path.resolve(__dirname, './src/stores'),
        '@/types': path.resolve(__dirname, './src/types'),
        '@/utils': path.resolve(__dirname, './src/utils'),
        '@/styles': path.resolve(__dirname, './src/styles'),
        '@/assets': path.resolve(__dirname, './src/assets'),
        '@/pages': path.resolve(__dirname, './src/pages'),
      },
    },

    // Configuration CSS avec Lightning CSS
    css: {
      transformer: 'lightningcss',
      lightningcss: {
        targets: {
          chrome: 100,
          firefox: 100,
          safari: 15,
        },
        drafts: {
          customMedia: true,
          nesting: true,
        },
      },
    },

    // Configuration build optimisée
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
            'vendor-radix': [
              '@radix-ui/react-dialog',
              '@radix-ui/react-dropdown-menu',
              '@radix-ui/react-select',
              '@radix-ui/react-toast',
            ],
            'vendor-utils': ['clsx', 'tailwind-merge', 'zod'],
          },
        },
      },
    },

    // Configuration serveur de développement
    server: {
      port: 3000,
      host: '0.0.0.0',
      strictPort: true,
      hmr: {
        port: 3001,
      },
    },

    // Variables d'environnement
    define: {
      __APP_VERSION__: JSON.stringify(process.env['npm_package_version']),
      __REACT_VERSION__: JSON.stringify('19.1.0'),
      __TANSTACK_QUERY_VERSION__: JSON.stringify('5.82.0'),
      __TANSTACK_ROUTER_VERSION__: JSON.stringify('1.126.1'),
    },

    // Configuration esbuild pour TypeScript
    esbuild: {
      target: 'ES2022',
      keepNames: true,
    },
  };
});
EOF

# ==========================================
# 5. CORRIGER VITEST.CONFIG.TS - COMPATIBILITÉ
# ==========================================

echo "🧪 Configuration Vitest compatible TypeScript strict..."

cat > vitest.config.ts << 'EOF'
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/features': path.resolve(__dirname, './src/features'),
      '@/hooks': path.resolve(__dirname, './src/hooks'),
      '@/services': path.resolve(__dirname, './src/services'),
      '@/stores': path.resolve(__dirname, './src/stores'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/utils': path.resolve(__dirname, './src/utils'),
      '@/styles': path.resolve(__dirname, './src/styles'),
      '@/assets': path.resolve(__dirname, './src/assets'),
      '@/pages': path.resolve(__dirname, './src/pages'),
    },
  },
});
EOF

# ==========================================
# 6. CORRIGER COMPONENTS REACT 19
# ==========================================

echo "🧩 Correction composants React 19 - suppression imports inutiles..."

# Corriger App.tsx - React 19 n'a plus besoin d'import React explicite
cat > src/App.tsx << 'EOF'
import { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { routeTree } from './routeTree.gen';
import { useAuthStore } from '@/stores/global/authStore';
import './styles/globals.css';

// QueryClient configuration pour TanStack Query v5
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30, // 30 minutes (v5: gcTime remplace cacheTime)
      retry: (failureCount, error: any) => {
        if (error?.status === 404) return false;
        return failureCount < 3;
      },
    },
  },
});

// Router configuration TanStack Router v1.126.1
const router = createRouter({
  routeTree,
  context: {
    queryClient,
  },
});

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

export default function App() {
  const { initializeAuth } = useAuthStore();

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      {import.meta.env.DEV && (
        <ReactQueryDevtools
          initialIsOpen={false}
          buttonPosition="bottom-right"
        />
      )}
    </QueryClientProvider>
  );
}
EOF

# ==========================================
# 7. CORRIGER MAIN.TSX - REACT 19
# ==========================================

echo "🚀 Correction main.tsx React 19..."

cat > src/main.tsx << 'EOF'
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { ErrorBoundary } from '@/components/global/ErrorBoundary';

const container = document.getElementById('root');
if (!container) throw new Error('Root container not found');

const root = createRoot(container);

root.render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>
);
EOF

# ==========================================
# 8. CORRIGER ERRORBOUNDARY - REACT 19
# ==========================================

echo "🛡️ Correction ErrorBoundary React 19..."

cat > src/components/global/ErrorBoundary.tsx << 'EOF'
import { Component, type ErrorInfo, type ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
    
    this.setState({
      hasError: true,
      error,
      errorInfo,
    });
  }

  resetError = (): void => {
    this.setState({
      hasError: false,
      error: undefined,
      errorInfo: undefined,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Fallback UI personnalisé
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // UI d'erreur par défaut
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center space-x-2 text-red-600 mb-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <h2 className="text-lg font-semibold">Erreur Application</h2>
            </div>
            
            <p className="text-gray-600 mb-4">
              Une erreur inattendue s'est produite. Veuillez recharger la page ou contacter le support.
            </p>
            
            {import.meta.env.DEV && this.state.error && (
              <details className="mb-4 p-2 bg-gray-100 rounded text-xs">
                <summary className="cursor-pointer font-medium">Détails de l'erreur (dev)</summary>
                <pre className="mt-2 whitespace-pre-wrap text-red-600">
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
            
            <button
              onClick={this.resetError}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
            >
              Réessayer
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
EOF

# ==========================================
# 9. GÉNÉRER ROUTE TREE TANSTACK
# ==========================================

echo "🛣️ Génération du routeTree TanStack Router v5..."

# Créer le fichier de route tree de base si manquant
mkdir -p src/pages
cat > src/routeTree.gen.ts << 'EOF'
/* eslint-disable */

// TanStack Router route tree generation
// This file is auto-generated by @tanstack/router-plugin/vite

import { Route, RootRoute, Router } from '@tanstack/react-router';

// Import des composants de pages
const IndexLazy = () => import('./pages/index').then((d) => d.default);
const NotFoundLazy = () => import('./pages/404').then((d) => d.default);

// Route racine
const rootRoute = new RootRoute({
  component: () => import('./pages/__root').then((d) => d.default),
});

// Routes définies
const indexRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/',
  component: IndexLazy,
});

const notFoundRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/404',
  component: NotFoundLazy,
});

// Arbre des routes
export const routeTree = rootRoute.addChildren([
  indexRoute,
  notFoundRoute,
]);

// Export pour TypeScript
export type RouteTree = typeof routeTree;
EOF

# ==========================================
# 10. VÉRIFICATION ET TEST
# ==========================================

echo "🔍 Vérification configuration TypeScript + React 19..."

# Installer les dépendances si nécessaire
npm install

# Test du type checking
echo "📝 Test TypeScript strict..."
npm run type-check:strict

if [ $? -eq 0 ]; then
    echo "✅ Configuration TypeScript + React 19 corrigée selon standards leaders"
else
    echo "❌ Erreurs TypeScript persistantes - vérification nécessaire"
    exit 1
fi

# ==========================================
# 11. COMMIT DES CORRECTIONS
# ==========================================

echo "📤 Commit des corrections TypeScript + React 19..."

git add .
git commit -m "fix: TypeScript 5.8.3 + React 19 configuration selon standards leaders

- Configuration tsconfig.json avec types React 19 + Vite
- Types environnement variables TypeScript strict  
- Composants React 19 sans imports inutiles
- ErrorBoundary avec types corrects React 19
- Vite config avec variables d'environnement strict
- Vitest config compatible TypeScript
- TanStack Router route tree génération

Standards leaders 2025: TypeScript 5.8.3 + React 19 + TanStack v5"

git push origin main

echo "🎉 FIX CRITIQUE TERMINÉ - TypeScript + React 19 selon standards leaders!"
