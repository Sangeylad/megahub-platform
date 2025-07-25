// frontend/src/pages/__root.tsx - Root Route compatible Auth Context Dynamique

import { createRootRoute, Outlet } from '@tanstack/react-router';
import React from 'react';

// ==========================================
// ROOT ROUTE - Configuration avec Context Typé
// ==========================================

export const Route = createRootRoute({
  // 🎯 FIX : Pas besoin de définir context ici, il vient d'App.tsx
  component: RootComponent,
});

// ==========================================
// ROOT COMPONENT - Layout global
// ==========================================

function RootComponent(): React.JSX.Element {
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

      {/* Debug Auth Context en développement */}
      {import.meta.env.MODE === 'development' && (
        <AuthContextDebugger />
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

// ==========================================
// DEBUG COMPONENT - Auth Context Monitoring
// ==========================================

function AuthContextDebugger(): React.JSX.Element | null {
  const [debugInfo, setDebugInfo] = React.useState({
    contextAuth: false,
    timestamp: Date.now()
  });

  React.useEffect(() => {
    const updateDebug = () => {
      // Accéder au context du router pour debug
      setDebugInfo({
        contextAuth: false, // Sera mis à jour par le context
        timestamp: Date.now()
      });
    };

    // Update périodique moins fréquent
    const interval = setInterval(updateDebug, 10000); // 10 secondes

    // Update sur événements auth
    const handleAuthEvent = () => {
      setTimeout(updateDebug, 100);
    };

    window.addEventListener('auth:login', handleAuthEvent);
    window.addEventListener('auth:logout', handleAuthEvent);

    return () => {
      clearInterval(interval);
      window.removeEventListener('auth:login', handleAuthEvent);
      window.removeEventListener('auth:logout', handleAuthEvent);
    };
  }, []);

  if (import.meta.env.MODE !== 'development') {
    return null;
  }

  return (
    <div className="fixed top-8 left-0 z-40 bg-purple-50 border border-purple-200 text-purple-800 px-2 py-1 text-xs font-mono shadow-lg max-w-xs">
      <div className="font-bold">🔧 Root Context Debug</div>
      <div className="text-xs">
        Last: {new Date(debugInfo.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
}