// frontend/src/lib/router-context.tsx
// 🚀 Router Context - Context Auth pour TanStack Router v1.126 selon standards

import { queryClient } from '@/lib/tanstack-query';
import { authService } from '@/services/api/authService';
import { useAuthStore } from '@/stores/authStore';
import type { User } from '@/types/auth';
import type { QueryClient } from '@tanstack/react-query';

// ==========================================
// INTERFACE ROUTER CONTEXT - TypeScript 5.8.3 Strict
// ==========================================

export interface RouterContext {
  auth: {
    isAuthenticated: boolean;
    user: User | null;
    hasValidToken: boolean;
    hasRefreshToken: boolean;
  };
  queryClient: QueryClient;
}

// ==========================================
// FACTORY CONTEXT - CRÉATION CONTEXT ROUTER
// ==========================================

export function createRouterContext(): RouterContext {
  // 🔧 FIX : Récupérer l'état auth actuel SANS hooks (car appelé dans beforeLoad)
  const authState = useAuthStore.getState();

  // 🔧 DEBUG : Log création context
  if (import.meta.env.MODE === 'development') {
    console.log('🔧 [RouterContext] Creating context:', {
      hasUser: !!authState.user,
      hasTokens: !!authState.tokens,
      isAuthenticatedFromService: authService.isAuthenticated(),
    });
  }

  return {
    auth: {
      // Combinaison store + service pour robustesse
      isAuthenticated: authService.isAuthenticated() && !!authState.user,
      user: authState.user,
      hasValidToken: !!authState.tokens?.access,
      hasRefreshToken: !!authState.tokens?.refresh,
    },
    queryClient,
  };
}

// ==========================================
// HELPERS CONTEXT - Utilitaires
// ==========================================

/**
 * Vérifie si l'utilisateur peut accéder à une route protégée
 */
export function canAccessProtectedRoute(context: RouterContext): boolean {
  const { auth } = context;

  const canAccess = auth.isAuthenticated &&
    auth.hasValidToken &&
    auth.user !== null;

  if (import.meta.env.MODE === 'development') {
    console.log('🔧 [RouterContext] Access check:', {
      isAuthenticated: auth.isAuthenticated,
      hasValidToken: auth.hasValidToken,
      hasUser: !!auth.user,
      canAccess,
    });
  }

  return canAccess;
}

/**
 * Vérifie si l'utilisateur a des permissions spécifiques
 */
export function hasPermissions(
  context: RouterContext,
  permissions: string[]
): boolean {
  if (!context.auth.user) return false;

  return authService.getUserPermissions(context.auth.user)
    .some(userPerm => permissions.includes(userPerm));
}

/**
 * Vérifie le rôle utilisateur
 */
export function hasRole(context: RouterContext, role: string): boolean {
  if (!context.auth.user) return false;

  switch (role) {
    case 'company_admin':
      return authService.isCompanyAdmin(context.auth.user);
    case 'brand_admin':
      return authService.isBrandAdmin(context.auth.user);
    default:
      return false;
  }
}

// ==========================================
// TYPE GUARDS - Sécurité TypeScript
// ==========================================

export function isAuthenticatedContext(context: RouterContext): context is RouterContext & {
  auth: {
    isAuthenticated: true;
    user: User;
    hasValidToken: true;
    hasRefreshToken: boolean;
  };
} {
  return canAccessProtectedRoute(context);
}

// ==========================================
// CONTEXT REFRESH - Mise à jour context
// ==========================================

/**
 * Rafraîchit le context auth - utile après login/logout
 */
export function refreshRouterContext(): RouterContext {
  if (import.meta.env.MODE === 'development') {
    console.log('🔧 [RouterContext] Refreshing context...');
  }

  return createRouterContext();
}

// ==========================================
// DEBUG HELPERS - Développement uniquement
// ==========================================

export function debugRouterContext(context: RouterContext): void {
  if (import.meta.env.MODE === 'development') {
    console.log('🔧 [RouterContext] Debug Info:', {
      auth: {
        ...context.auth,
        userEmail: context.auth.user?.email,
        userType: context.auth.user?.user_type,
      },
      queryClientInfo: {
        mountedQueries: context.queryClient.getQueryCache().getAll().length,
        isFetching: context.queryClient.isFetching(),
      },
      authServiceInfo: authService.getSessionInfo(),
    });
  }
}