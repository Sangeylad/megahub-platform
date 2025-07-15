// frontend/src/App.tsx

// 🚀 App Root - TanStack Router v1.126 + TanStack Query v5 avec Auth Context

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createRouter, RouterProvider } from '@tanstack/react-router';
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
// ROUTER - Configuration simple selon standards
// ==========================================

const router = createRouter({
  routeTree,
  context: {
    queryClient,
    auth: {
      isAuthenticated: false,
      user: null,
      checkAuth: () => false,
    },
  } as RouterContext,
});

// ==========================================
// TYPE DECLARATION - Module augmentation TanStack Router
// ==========================================

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

// ==========================================
// APP COMPONENT - Simple selon exemple official
// ==========================================

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}