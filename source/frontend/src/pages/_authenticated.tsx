// frontend/src/pages/_authenticated.tsx - Fix Compatible avec TokenManager Actuel

import { authService } from '@/services/api/authService';
import { tokenManager } from '@/utils/security/tokenManager';
import { createFileRoute, Outlet } from '@tanstack/react-router';
import React from 'react';

// ==========================================
// AUTHENTICATED LAYOUT ROUTE - FIX BOUCLE COMPATIBLE
// ==========================================

export const Route = createFileRoute('/_authenticated')({
  // 🔒 BEFORELOAD - Protection authentification ENHANCED ANTI-BOUCLE
  beforeLoad: async ({ location }: { location: { href: string } }) => {
    if (import.meta.env.MODE === 'development') {
      console.log('🔒 [Auth Check] Début vérification authentification pour:', location.href);
    }

    // ===== ÉTAPE 1 : Vérification tokens directs SANS cache =====
    let hasValidTokens = false;

    try {
      // Check direct des tokens sans passer par authService.isAuthenticated()
      const accessToken = tokenManager.getAccessToken();
      const refreshToken = tokenManager.getRefreshToken();

      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [Auth Check] Tokens directs:', {
          hasAccess: !!accessToken,
          hasRefresh: !!refreshToken
        });
      }

      // Si on a au moins un token valide
      hasValidTokens = !!accessToken || !!refreshToken;

    } catch (error) {
      console.error('❌ [Auth Check] Erreur vérification tokens:', error);
      hasValidTokens = false;
    }

    // ===== ÉTAPE 2 : Si pas de tokens, redirection immédiate =====
    if (!hasValidTokens) {
      if (import.meta.env.MODE === 'development') {
        console.log('❌ [Auth Check] Aucun token - Redirection immédiate vers login');
      }

      // Redirection avec URL preservation
      const redirectUrl = encodeURIComponent(location.href);
      const loginUrl = `/auth/login?redirect=${redirectUrl}`;

      if (import.meta.env.MODE === 'development') {
        console.log('🔄 [Auth Check] Redirection vers:', loginUrl);
      }

      throw new Error(`REDIRECT:${loginUrl}`);
    }

    // ===== ÉTAPE 3 : Si refresh token seulement, essayer refresh =====
    const accessToken = tokenManager.getAccessToken();
    if (!accessToken && tokenManager.getRefreshToken()) {
      if (import.meta.env.MODE === 'development') {
        console.log('🔄 [Auth Check] Pas d\'access token, tentative refresh...');
      }

      try {
        const newAccessToken = await authService.refreshToken();
        if (newAccessToken) {
          if (import.meta.env.MODE === 'development') {
            console.log('✅ [Auth Check] Refresh token réussi');
          }
        } else {
          throw new Error('Refresh failed');
        }
      } catch (refreshError) {
        console.error('❌ [Auth Check] Échec refresh token:', refreshError);

        // Clear tokens et redirection
        tokenManager.clearTokens();
        const redirectUrl = encodeURIComponent(location.href);
        throw new Error(`REDIRECT:/auth/login?redirect=${redirectUrl}`);
      }
    }

    // ===== ÉTAPE 4 : Validation finale avec AuthService =====
    let finalAuthCheck = false;
    try {
      // Force une vérification fresh (pas de cache)
      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [Auth Check] Validation finale AuthService...');
      }

      // 🔧 FIX COMPATIBLE : Invalider le cache si la méthode existe
      try {
        const authServiceInstance = (window as any).authService;
        if (authServiceInstance && typeof authServiceInstance.invalidateAuthCachePublic === 'function') {
          authServiceInstance.invalidateAuthCachePublic();
        }
      } catch (cacheError) {
        // Ignore si méthode pas disponible
        if (import.meta.env.MODE === 'development') {
          console.log('🔧 [Auth Check] Cache invalidation non disponible');
        }
      }

      finalAuthCheck = authService.isAuthenticated();

    } catch (error) {
      console.error('❌ [Auth Check] Erreur validation finale:', error);
      finalAuthCheck = false;
    }

    // ===== ÉTAPE 5 : Décision finale =====
    if (!finalAuthCheck) {
      if (import.meta.env.MODE === 'development') {
        console.log('❌ [Auth Check] Validation finale échouée - Redirection vers login');
        console.log('🔧 [Auth Check] Debug final:', {
          hasAccessToken: !!tokenManager.getAccessToken(),
          hasRefreshToken: !!tokenManager.getRefreshToken(),
          authServiceResult: finalAuthCheck,
          sessionInfo: authService.getSessionInfo(),
          tokenDebug: tokenManager.getDebugInfo()
        });
      }

      // Clear complet et redirection
      tokenManager.clearTokens();
      const redirectUrl = encodeURIComponent(location.href);
      throw new Error(`REDIRECT:/auth/login?redirect=${redirectUrl}`);
    }

    if (import.meta.env.MODE === 'development') {
      console.log('✅ [Auth Check] Utilisateur authentifié - Accès autorisé');
    }

    // ===== ÉTAPE 6 : Context enrichi pour les pages protégées =====
    return {
      auth: {
        isAuthenticated: true,
        sessionInfo: authService.getSessionInfo(),
        timestamp: Date.now(),
      }
    };
  },

  // 🎯 COMPONENT - Layout pour routes protégées ENHANCED
  component: AuthenticatedLayout,

  // 🚨 ERROR COMPONENT - Gestion erreurs authentification COMPATIBLE
  errorComponent: ({ error, reset }: { error: Error; reset: () => void }) => {
    // 🔧 FIX : Si erreur de redirection, effectuer la redirection
    if (error.message?.includes('REDIRECT:')) {
      const redirectUrl = error.message.split('REDIRECT:')[1];
      if (redirectUrl) {
        if (import.meta.env.MODE === 'development') {
          console.log('🔄 [Auth Error] Redirection automatique vers:', redirectUrl);
        }

        // Redirection immédiate
        window.location.href = redirectUrl;

        // Afficher un loading pendant la redirection
        return (
          <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Redirection vers la connexion...</p>
            </div>
          </div>
        );
      }
    }

    // Autres erreurs d'authentification
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
                // 🔧 FIX COMPATIBLE : Clear avec méthode disponible
                tokenManager.clearTokens();

                // Clear additional storage si besoin
                try {
                  localStorage.clear();
                  sessionStorage.clear();
                } catch (storageError) {
                  console.warn('⚠️ Erreur clear storage:', storageError);
                }

                reset();
              }}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Réessayer
            </button>
            <button
              onClick={() => {
                // 🔧 FIX COMPATIBLE : Clear avant redirection
                tokenManager.clearTokens();
                try {
                  localStorage.clear();
                  sessionStorage.clear();
                } catch (storageError) {
                  console.warn('⚠️ Erreur clear storage:', storageError);
                }
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
// AUTHENTICATED LAYOUT COMPONENT - ENHANCED
// ==========================================

function AuthenticatedLayout() {
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
// DEVELOPMENT TOKEN SYNC MONITOR OPTIMISÉ
// ==========================================

function TokenSyncMonitor() {
  interface SyncStatus {
    hasAccessToken: boolean;
    hasRefreshToken: boolean;
    isAuthenticated: boolean;
    lastCheck: number;
  }

  const [syncStatus, setSyncStatus] = React.useState<SyncStatus>({
    hasAccessToken: false,
    hasRefreshToken: false,
    isAuthenticated: false,
    lastCheck: Date.now()
  });

  React.useEffect(() => {
    const checkSync = () => {
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

    // Check périodique (moins fréquent)
    const interval = setInterval(checkSync, 3000); // 3 secondes au lieu de 1

    // Écouter les événements auth avec throttling
    let eventTimeout: NodeJS.Timeout;
    const handleAuthEvent = () => {
      clearTimeout(eventTimeout);
      eventTimeout = setTimeout(checkSync, 200);
    };

    window.addEventListener('auth:login', handleAuthEvent);
    window.addEventListener('auth:logout', handleAuthEvent);

    return () => {
      clearInterval(interval);
      clearTimeout(eventTimeout);
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