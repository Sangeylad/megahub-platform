// frontend/src/App.tsx - TanStack Router v1.126 + Auth Context DYNAMIQUE

import { authService } from '@/services/api/authService';
import { useAuthStore } from '@/stores/authStore';
import { tokenManager } from '@/utils/security/tokenManager';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createRouter, RouterProvider } from '@tanstack/react-router';
import React from 'react';
import { routeTree } from './routeTree.gen';

// ==========================================
// INTERFACE TYPES - Context Router
// ==========================================

interface RouterContext {
  queryClient: QueryClient;
  auth: {
    isAuthenticated: boolean;
    user: any | null;
    checkAuth: () => boolean;
  };
}

// ==========================================
// QUERY CLIENT - Configuration TanStack Query v5
// ==========================================

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30, // 30 minutes (v5)
      retry: (failureCount: number, error: any) => {
        // Ne pas retry sur les erreurs d'auth
        if (error?.status === 401 || error?.status === 403) {
          return false;
        }
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
});

// ==========================================
// FONCTION HELPER - Auth Context Dynamique
// ==========================================

function createAuthContext() {
  return {
    // 🎯 FIX : Valeurs dynamiques basées sur l'état réel
    get isAuthenticated() {
      // Triple vérification pour être sûr
      const storeAuth = useAuthStore.getState().isAuthenticated;
      const serviceAuth = authService.isAuthenticated();
      const hasTokens = !!tokenManager.getAccessToken() || !!tokenManager.getRefreshToken();

      const result = storeAuth && serviceAuth && hasTokens;

      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [Router Context] Auth check:', {
          storeAuth,
          serviceAuth,
          hasTokens,
          result
        });
      }

      return result;
    },

    get user() {
      return useAuthStore.getState().user;
    },

    checkAuth: () => {
      // Fonction helper pour vérifications manuelles
      return authService.isAuthenticated() && !!tokenManager.getAccessToken();
    }
  };
}

// ==========================================
// ROUTER COMPONENT - Avec Context Réactif
// ==========================================

function AppRouter() {
  // 🎯 FIX : Hook pour forcer re-render quand auth change
  const { isAuthenticated, user } = useAuthStore();

  // Créer router avec context dynamique à chaque render
  const router = React.useMemo(() => {
    const authContext = createAuthContext();

    if (import.meta.env.MODE === 'development') {
      console.log('🔧 [AppRouter] Creating router with auth context:', {
        isAuthenticated: authContext.isAuthenticated,
        hasUser: !!authContext.user
      });
    }

    return createRouter({
      routeTree,
      context: {
        queryClient,
        auth: authContext,
      } as RouterContext,
    });
  }, [isAuthenticated, user]); // Re-créer quand auth change

  return <RouterProvider router={router} />;
}

// ==========================================
// TYPE DECLARATION - Module augmentation TanStack Router
// ==========================================

declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof createRouter>;
  }
}

// ==========================================
// APP COMPONENT - Avec Auth Context Dynamique
// ==========================================

export default function App(): React.JSX.Element {
  // 🎯 Surveillance des changements d'auth pour debug
  React.useEffect(() => {
    if (import.meta.env.MODE === 'development') {
      const handleAuthChange = (event: Event) => {
        console.log('🔧 [App] Auth event détecté:', event.type);
      };

      window.addEventListener('auth:login', handleAuthChange);
      window.addEventListener('auth:logout', handleAuthChange);
      window.addEventListener('auth:userChanged', handleAuthChange);

      return () => {
        window.removeEventListener('auth:login', handleAuthChange);
        window.removeEventListener('auth:logout', handleAuthChange);
        window.removeEventListener('auth:userChanged', handleAuthChange);
      };
    }
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <AppRouter />
    </QueryClientProvider>
  );
}

// ==========================================
// EXPORT COMPLEMENTAIRE - Pour tests si besoin
// ==========================================

export { queryClient };
