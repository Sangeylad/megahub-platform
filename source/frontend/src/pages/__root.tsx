// frontend/src/pages/__root.tsx

// 🚀 Root Route - TanStack Router v1.126 selon standards simples

import { createRootRoute, Outlet } from '@tanstack/react-router';
import React from 'react';

// ==========================================
// ROOT ROUTE - Configuration simple
// ==========================================

export const Route = createRootRoute({
  component: RootComponent,
});

// ==========================================
// ROOT COMPONENT - Layout global
// ==========================================

function RootComponent() {
  return (
    <div className="min-h-screen bg-gray-50">

      {/* Development DevTools */}
      {import.meta.env.MODE === 'development' && (
        <div className="fixed top-0 left-0 z-50 bg-yellow-400 text-black px-2 py-1 text-xs font-mono">
          🚧 DEV MODE
        </div>
      )}

      {/* Layout principal */}
      <main className="w-full">
        <Outlet />
      </main>

      {/* TanStack Router DevTools - Development only */}
      {import.meta.env.MODE === 'development' && (
        <React.Suspense fallback={null}>
          <TanStackRouterDevtools position="bottom-right" />
        </React.Suspense>
      )}
    </div>
  );
}

// ==========================================
// DEVTOOLS LAZY IMPORT
// ==========================================

const TanStackRouterDevtools = React.lazy(() =>
  import('@tanstack/router-devtools').then((mod) => ({
    default: mod.TanStackRouterDevtools,
  }))
);