// frontend/src/pages/_authenticated.tsx - Fix TypeScript selon Standards TanStack Router v1.126.1

import { authService } from '@/services/api/authService';
import { tokenManager } from '@/utils/security/tokenManager';
import {
  createFileRoute,
  Outlet
} from '@tanstack/react-router';
import React from 'react';

// ==========================================
// TYPES TANSTACK ROUTER - TypeScript 5.8.3 Strict
// ==========================================

interface AuthContext {
  auth: {
    isAuthenticated: boolean;
    user?: any;
  }
  queryClient: any;
}

interface RouteBeforeLoadContext {
  context: AuthContext;
  location: {
    href: string;
    pathname: string;
    search: string;
    hash: string;
  };
}

// ==========================================
// AUTHENTICATED LAYOUT ROUTE - FIX TYPESCRIPT COMPLET
// ==========================================

export const Route = createFileRoute('/_authenticated')({
  // 🔒 BEFORELOAD - Protection authentification TypeScript strict
  beforeLoad: async ({ context, location }: RouteBeforeLoadContext) => {
    if (import.meta.env.MODE === 'development') {
      console.log('🔒 [Auth Check] Vérification authentification pour:', location.href);
    }

    // ===== VÉRIFICATION SIMPLE ET DIRECTE - Selon standards TanStack =====

    // 1. Vérifier context auth (source de vérité principale)
    const contextAuth = context?.auth?.isAuthenticated ?? false;

    // 2. Vérifier tokens directs
    const hasValidTokens = !!tokenManager.getAccessToken() || !!tokenManager.getRefreshToken();

    // 3. Vérifier AuthService (backup)
    const authServiceCheck = authService.isAuthenticated();

    if (import.meta.env.MODE === 'development') {
      console.log('🔧 [Auth Check] États:', {
        contextAuth,
        hasValidTokens,
        authServiceCheck
      });
    }

    // ===== DÉCISION SIMPLE - PAS DE MULTI-VÉRIFICATIONS =====

    const isAuthenticated = contextAuth && hasValidTokens && authServiceCheck;

    if (!isAuthenticated) {
      if (import.meta.env.MODE === 'development') {
        console.log('❌ [Auth Check] Non authentifié - Redirection vers login');
      }

      // 🎯 FIX : Redirection simple avec URL params
      const redirectUrl = `/auth/login?redirect=${encodeURIComponent(location.href)}`;

      // Option 1: Redirection immédiate
      if (typeof window !== 'undefined') {
        window.location.href = redirectUrl;
      }

      // Option 2 : Lancer une erreur pour stopper l'exécution
      throw new Error(`REDIRECT_TO_LOGIN:${redirectUrl}`);
    }

    if (import.meta.env.MODE === 'development') {
      console.log('✅ [Auth Check] Utilisateur authentifié - Accès autorisé');
    }

    // Context enrichi pour routes enfants
    return {
      auth: {
        isAuthenticated: true,
        sessionInfo: authService.getSessionInfo(),
        timestamp: Date.now(),
      }
    };
  },

  // 🎯 COMPONENT - Layout pour routes protégées
  component: AuthenticatedLayout,

  // 🚨 ERROR COMPONENT - Gestion erreurs TypeScript strict
  errorComponent: ({ error, reset }: { error: Error; reset: () => void }) => {
    // 🎯 FIX : Gérer la redirection personnalisée
    if (error.message?.startsWith('REDIRECT_TO_LOGIN:')) {
      const redirectUrl = error.message.split('REDIRECT_TO_LOGIN:')[1];

      if (redirectUrl && typeof window !== 'undefined') {
        // Redirection différée pour éviter les erreurs React
        setTimeout(() => {
          window.location.href = redirectUrl;
        }, 100);
      }

      // Afficher un loader pendant la redirection
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Redirection vers la connexion...</p>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow p-6 max-w-md w-full">
          <div className="flex items-center mb-4">
            <svg className="w-6 h-6 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-lg font-semibold text-gray-900">
              Erreur d'authentification
            </h2>
          </div>

          <p className="text-sm text-gray-600 mb-4">
            Une erreur est survenue lors de la vérification de votre authentification.
          </p>

          <div className="flex space-x-3">
            <button
              onClick={() => {
                // Clear tokens et reset
                tokenManager.clearTokens();
                reset();
              }}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Réessayer
            </button>
            <button
              onClick={() => {
                // Clear et redirection
                tokenManager.clearTokens();
                window.location.href = '/auth/login';
              }}
              className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Se reconnecter
            </button>
          </div>

          {/* Debug info en développement */}
          {import.meta.env.MODE === 'development' && (
            <details className="mt-4">
              <summary className="text-xs text-gray-500 cursor-pointer">
                🔧 Debug Error Info
              </summary>
              <pre className="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded overflow-auto max-h-32">
                {JSON.stringify({
                  errorMessage: error.message,
                  tokenDebug: tokenManager.getDebugInfo(),
                  authDebug: authService.getSessionInfo(),
                }, null, 2)}
              </pre>
            </details>
          )}
        </div>
      </div>
    );
  }
});

// ==========================================
// AUTHENTICATED LAYOUT COMPONENT - TypeScript Strict
// ==========================================

function AuthenticatedLayout(): React.JSX.Element {
  return (
    <div className="authenticated-layout min-h-screen bg-gray-50">

      {/* Header Navigation */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">

            {/* Logo & Title */}
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h1 className="text-xl font-semibold text-gray-900">
                MegaHub
              </h1>
            </div>

            {/* User Menu Placeholder */}
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Development Indicators */}
      {import.meta.env.MODE === 'development' && (
        <>
          {/* Auth Status Indicator */}
          <div className="fixed bottom-4 right-4 bg-green-100 border border-green-300 text-green-800 px-3 py-2 rounded-lg text-sm font-mono shadow-lg z-50">
            🔒 Layout Authentifié
          </div>

          {/* Token Sync Monitor */}
          <TokenSyncMonitor />
        </>
      )}
    </div>
  );
}

// ==========================================
// DEVELOPMENT TOKEN SYNC MONITOR - TypeScript Strict
// ==========================================

interface SyncStatus {
  hasAccessToken: boolean;
  hasRefreshToken: boolean;
  isAuthenticated: boolean;
  lastCheck: number;
}

function TokenSyncMonitor(): React.JSX.Element | null {
  const [syncStatus, setSyncStatus] = React.useState<SyncStatus>({
    hasAccessToken: false,
    hasRefreshToken: false,
    isAuthenticated: false,
    lastCheck: Date.now()
  });

  React.useEffect(() => {
    if (import.meta.env.MODE !== 'development') {
      return;
    }

    const checkSync = (): void => {
      try {
        const status: SyncStatus = {
          hasAccessToken: !!tokenManager.getAccessToken(),
          hasRefreshToken: !!tokenManager.hasRefreshToken(),
          isAuthenticated: authService.isAuthenticated(),
          lastCheck: Date.now()
        };
        setSyncStatus(status);
      } catch (error) {
        console.error('❌ [TokenSyncMonitor] Erreur check sync:', error);
      }
    };

    // Check initial
    checkSync();

    // Check périodique moins fréquent
    const interval = setInterval(checkSync, 5000); // 5 secondes

    // Écouter événements auth avec cleanup
    const handleAuthEvent = (): void => {
      setTimeout(checkSync, 200);
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
    <div className="fixed bottom-4 left-4 bg-blue-50 border border-blue-200 text-blue-800 px-3 py-2 rounded-lg text-xs font-mono shadow-lg z-50 max-w-xs">
      <div className="font-bold mb-1">🔧 Token Sync Status</div>
      <div className="space-y-1">
        <div className={`${syncStatus.hasAccessToken ? 'text-green-600' : 'text-red-600'}`}>
          Access: {syncStatus.hasAccessToken ? '✅' : '❌'}
        </div>
        <div className={`${syncStatus.hasRefreshToken ? 'text-green-600' : 'text-red-600'}`}>
          Refresh: {syncStatus.hasRefreshToken ? '✅' : '❌'}
        </div>
        <div className={`${syncStatus.isAuthenticated ? 'text-green-600' : 'text-red-600'}`}>
          Auth: {syncStatus.isAuthenticated ? '✅' : '❌'}
        </div>
        <div className="text-gray-500 text-xs">
          Last: {new Date(syncStatus.lastCheck).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}