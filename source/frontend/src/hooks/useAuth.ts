// frontend/src/hooks/useAuth.ts - Fix Final Boucle + Performance

import { authQueryKeys, authService } from '@/services/api/authService';
import { useAuthStore } from '@/stores/authStore';
import type {
  LoginFormData,
  LoginResponse,
  PasswordChangeData,
  UseAuthOptions,
  User,
  UserUpdateData
} from '@/types/auth';
import { tokenManager } from '@/utils/security/tokenManager';
import {
  useMutation,
  useQuery,
  useQueryClient
} from '@tanstack/react-query';
import React from 'react';

// ==========================================
// HOOK PRINCIPAL - FIX FINAL ANTI-BOUCLE
// ==========================================

export function useAuth(options: UseAuthOptions = {}) {
  const queryClient = useQueryClient();
  const {
    user,
    setUser,
    clearAuth,
    isAuthenticated,
    setIsAuthenticated
  } = useAuthStore();

  // ===== ÉTAT SYNCHRONISATION =====
  interface SyncStatus {
    isTokenSynced: boolean;
    lastTokenCheck: number;
    syncAttempts: number;
  }

  const [syncStatus, setSyncStatus] = React.useState<SyncStatus>({
    isTokenSynced: false,
    lastTokenCheck: 0,
    syncAttempts: 0
  });

  // 🔧 FIX : Cache stable pour éviter re-calculs
  const authCheckRef = React.useRef({
    lastCheck: 0,
    result: false,
    ttl: 2000, // 2 secondes
  });

  // 🔧 FIX : Fonction de vérification d'auth TRÈS throttlée
  const checkAuthentication = React.useCallback((): boolean => {
    const now = Date.now();

    // Cache de 2 secondes pour éviter les appels répétés
    if (now - authCheckRef.current.lastCheck < authCheckRef.current.ttl) {
      return authCheckRef.current.result;
    }

    // Appel UNIQUE à authService avec cache intégré
    const result = authService.isAuthenticated();

    authCheckRef.current = {
      lastCheck: now,
      result,
      ttl: 2000,
    };

    return result;
  }, []);

  // ===== QUERY USER OPTIMISÉE FINALE =====
  const userQuery = useQuery({
    queryKey: authQueryKeys.user(),
    queryFn: async () => {
      // 🔧 FIX : Vérification d'auth simplifiée
      const isAuth = checkAuthentication();
      if (!isAuth) {
        throw new Error('Not authenticated');
      }

      // Vérifier token disponibilité
      const hasToken = await tokenManager.waitForToken(1000);
      if (!hasToken) {
        if (import.meta.env.MODE === 'development') {
          console.log('🔧 [useAuth] Pas de token pour getCurrentUser');
        }
        throw new Error('No access token available');
      }

      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [useAuth] Récupération utilisateur avec token disponible');
      }

      // 🔧 FIX : getCurrentUser retourne maintenant le bon User
      return authService.getCurrentUser();
    },
    // 🔧 FIX : enabled avec fonction stable
    enabled: React.useMemo(() => {
      const shouldEnable = checkAuthentication() && options.enabled !== false;
      return shouldEnable;
    }, [checkAuthentication, options.enabled]),

    staleTime: options.staleTime || 5 * 60 * 1000,
    gcTime: options.gcTime || 10 * 60 * 1000,
    retry: (failureCount: number, error: unknown) => {
      const retryOption = options.retry;

      if (retryOption !== undefined) {
        if (typeof retryOption === 'boolean') {
          return retryOption;
        }
        if (typeof retryOption === 'number') {
          return failureCount < retryOption;
        }
        if (typeof retryOption === 'function') {
          const retryFn = retryOption as (failureCount: number, error: unknown) => boolean;
          return retryFn(failureCount, error);
        }
      }

      // Retry par défaut
      const status = (error as any)?.status_code;
      if (status === 401 || status === 403) return false;
      return failureCount < 2;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * Math.pow(2, attemptIndex), 5000),
    refetchOnWindowFocus: options.refetchOnWindowFocus ?? false,
    refetchInterval: false, // Pas de refetch automatique
    ...options,
  });

  // ===== SYNCHRONISATION STORE ←→ QUERY AVEC DEBOUNCE =====
  React.useEffect(() => {
    let isMounted = true;

    // 🔧 FIX : Débounce plus long pour éviter spam
    const timeoutId = setTimeout(() => {
      if (!isMounted) return;

      if (userQuery.data && !userQuery.isError) {
        if (import.meta.env.MODE === 'development') {
          console.log('✅ [useAuth] Synchronisation user data vers store');
        }

        setUser(userQuery.data);
        setIsAuthenticated(true);

        setSyncStatus((prev: SyncStatus) => ({
          ...prev,
          isTokenSynced: true,
          lastTokenCheck: Date.now()
        }));
      } else if (userQuery.isError) {
        if (import.meta.env.MODE === 'development') {
          console.log('❌ [useAuth] Erreur user query, clear auth');
        }

        clearAuth();
        setIsAuthenticated(false);

        setSyncStatus((prev: SyncStatus) => ({
          ...prev,
          isTokenSynced: false,
          syncAttempts: prev.syncAttempts + 1
        }));
      }
    }, 200); // Débounce de 200ms

    return () => {
      isMounted = false;
      clearTimeout(timeoutId);
    };
  }, [userQuery.data, userQuery.isError, setUser, clearAuth, setIsAuthenticated]);

  // ===== ÉCOUTE ÉVÉNEMENTS TOKEN AVEC THROTTLING =====
  React.useEffect(() => {
    let isEffectActive = true;
    let tokenChangeTimeout: NodeJS.Timeout;

    const handleTokenChange = () => {
      if (!isEffectActive) return;

      // 🔧 FIX : Throttling plus agressif
      clearTimeout(tokenChangeTimeout);
      tokenChangeTimeout = setTimeout(() => {
        if (!isEffectActive) return;

        if (import.meta.env.MODE === 'development') {
          console.log('🔄 [useAuth] Token change détecté, invalider queries');
        }

        // Invalider cache auth local
        authCheckRef.current.lastCheck = 0;

        // Invalider queries avec délai
        queryClient.invalidateQueries({ queryKey: authQueryKeys.user() });

        setSyncStatus((prev: SyncStatus) => ({
          ...prev,
          lastTokenCheck: Date.now()
        }));
      }, 500); // Délai plus long
    };

    // Écouter changements tokens avec cleanup robuste
    const cleanup = tokenManager.addTokenChangeListener(handleTokenChange);

    // Écouter événements auth globaux avec throttling
    let authEventTimeout: NodeJS.Timeout;
    const handleAuthLogin = () => {
      if (!isEffectActive) return;

      clearTimeout(authEventTimeout);
      authEventTimeout = setTimeout(() => {
        if (isEffectActive) {
          if (import.meta.env.MODE === 'development') {
            console.log('🔄 [useAuth] Événement auth:login reçu');
          }
          handleTokenChange();
        }
      }, 300);
    };

    const handleAuthLogout = () => {
      if (!isEffectActive) return;

      if (import.meta.env.MODE === 'development') {
        console.log('🔄 [useAuth] Événement auth:logout reçu');
      }

      // Clear immédiat pour logout
      clearAuth();
      setIsAuthenticated(false);
      authCheckRef.current.lastCheck = 0;
      queryClient.removeQueries({ queryKey: authQueryKeys.all });
    };

    window.addEventListener('auth:login', handleAuthLogin);
    window.addEventListener('auth:logout', handleAuthLogout);

    return () => {
      isEffectActive = false;
      clearTimeout(tokenChangeTimeout);
      clearTimeout(authEventTimeout);
      cleanup();
      window.removeEventListener('auth:login', handleAuthLogin);
      window.removeEventListener('auth:logout', handleAuthLogout);
    };
  }, [queryClient, clearAuth, setIsAuthenticated]);

  // ==========================================
  // MUTATIONS OPTIMISÉES
  // ==========================================

  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginFormData) => {
      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [useAuth] Début login mutation');
      }
      return authService.login(credentials);
    },
    onMutate: () => {
      setSyncStatus((prev: SyncStatus) => ({
        ...prev,
        syncAttempts: 0,
        isTokenSynced: false
      }));
    },
    onSuccess: async (data: LoginResponse) => {
      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [useAuth] Login mutation onSuccess - début synchronisation');
      }

      try {
        // Mise à jour immédiate
        setUser(data.user);
        setIsAuthenticated(true);

        // Mise à jour cache
        queryClient.setQueryData(authQueryKeys.user(), data.user);

        // Reset cache auth
        authCheckRef.current.lastCheck = 0;

        // Attendre synchronisation tokens
        let syncAttempts = 0;
        const maxSyncAttempts = 10;

        while (syncAttempts < maxSyncAttempts) {
          const hasToken = await tokenManager.waitForToken(100);

          if (hasToken) {
            if (import.meta.env.MODE === 'development') {
              console.log(`✅ [useAuth] Token sync réussi après ${syncAttempts + 1} tentatives`);
            }

            setSyncStatus((prev: SyncStatus) => ({
              ...prev,
              isTokenSynced: true,
              lastTokenCheck: Date.now(),
              syncAttempts: syncAttempts + 1
            }));
            break;
          }

          syncAttempts++;
          await new Promise(resolve => setTimeout(resolve, 100));
        }

        // Invalider queries avec délai
        setTimeout(async () => {
          await queryClient.invalidateQueries({
            queryKey: authQueryKeys.user(),
            refetchType: 'active'
          });
        }, 300);

        if (import.meta.env.MODE === 'development') {
          console.log('✅ [useAuth] Login mutation onSuccess - synchronisation terminée');
        }

      } catch (syncError) {
        console.error('❌ [useAuth] Erreur synchronisation login:', syncError);
      }
    },
    onError: (error) => {
      console.error('❌ [useAuth] Login mutation failed:', error);
      clearAuth();
      setIsAuthenticated(false);
      authCheckRef.current.lastCheck = 0;
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      return authService.logout();
    },
    onMutate: () => {
      // Clear immédiat
      clearAuth();
      setIsAuthenticated(false);
      authCheckRef.current.lastCheck = 0;
    },
    onSettled: () => {
      // Nettoyer tout
      queryClient.removeQueries({ queryKey: authQueryKeys.all });
      setSyncStatus({
        isTokenSynced: false,
        lastTokenCheck: Date.now(),
        syncAttempts: 0
      });
    },
  });

  const updateProfileMutation = useMutation({
    mutationFn: (data: UserUpdateData) => authService.updateProfile(data),
    onSuccess: (updatedUser: User) => {
      setUser(updatedUser);
      queryClient.setQueryData(authQueryKeys.user(), updatedUser);
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: (data: PasswordChangeData) => authService.changePassword(data),
  });

  // ==========================================
  // ACTIONS STABILISÉES
  // ==========================================

  const login = React.useCallback(async (credentials: LoginFormData): Promise<LoginResponse> => {
    try {
      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [useAuth] Début action login');
      }

      const result = await loginMutation.mutateAsync(credentials);

      // Vérification finale avec timeout
      const verifySync = async () => {
        let attempts = 0;
        while (attempts < 5) {
          const isFullySynced = authService.isAuthenticated() &&
            !!tokenManager.getAccessToken() &&
            !!queryClient.getQueryData(authQueryKeys.user());

          if (isFullySynced) {
            if (import.meta.env.MODE === 'development') {
              console.log('✅ [useAuth] Synchronisation finale confirmée');
            }
            return;
          }

          attempts++;
          await new Promise(resolve => setTimeout(resolve, 50));
        }
      };

      await verifySync();
      return result;
    } catch (error) {
      console.error('❌ [useAuth] Action login échouée:', error);
      throw error;
    }
  }, [loginMutation, queryClient]);

  const logout = React.useCallback(async (): Promise<void> => {
    try {
      await logoutMutation.mutateAsync();
    } catch (error) {
      console.error('❌ [useAuth] Logout API error (but client cleared):', error);
    }
  }, [logoutMutation]);

  const updateProfile = React.useCallback((data: UserUpdateData) => {
    return updateProfileMutation.mutateAsync(data);
  }, [updateProfileMutation]);

  const changePassword = React.useCallback((data: PasswordChangeData) => {
    return changePasswordMutation.mutateAsync(data);
  }, [changePasswordMutation]);

  const refetchUser = React.useCallback(() => {
    return userQuery.refetch();
  }, [userQuery]);

  // ==========================================
  // PERMISSIONS HELPERS MEMOIZED
  // ==========================================

  const hasPermission = React.useCallback((permission: string): boolean => {
    if (!user) return false;
    return authService.userHasPermission(user, permission);
  }, [user]);

  const hasAnyPermission = React.useCallback((permissions: string[]): boolean => {
    if (!user) return false;
    return permissions.some(permission => hasPermission(permission));
  }, [user, hasPermission]);

  const hasAllPermissions = React.useCallback((permissions: string[]): boolean => {
    if (!user) return false;
    return permissions.every(permission => hasPermission(permission));
  }, [user, hasPermission]);

  // ==========================================
  // ROLE HELPERS MEMOIZED
  // ==========================================

  const isCompanyAdmin = React.useCallback((): boolean => {
    return authService.isCompanyAdmin(user ?? undefined);
  }, [user]);

  const isBrandAdmin = React.useCallback((): boolean => {
    return authService.isBrandAdmin(user ?? undefined);
  }, [user]);

  const canAccessAnalytics = React.useCallback((): boolean => {
    return authService.canAccessAnalytics(user ?? undefined);
  }, [user]);

  const canAccessReports = React.useCallback((): boolean => {
    return authService.canAccessReports(user ?? undefined);
  }, [user]);

  // ==========================================
  // RETURN STATE OPTIMISÉ
  // ==========================================

  return React.useMemo(() => ({
    // Data
    user,
    isAuthenticated,

    // Loading states
    isLoading: userQuery.isLoading,
    isPending: userQuery.isPending,
    isError: userQuery.isError,
    error: userQuery.error,

    // Mutation states
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    isUpdatingProfile: updateProfileMutation.isPending,
    isChangingPassword: changePasswordMutation.isPending,

    // Actions
    login,
    logout,
    updateProfile,
    changePassword,
    refetchUser,

    // Permissions
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,

    // Roles
    isCompanyAdmin,
    isBrandAdmin,
    canAccessAnalytics,
    canAccessReports,

    // Enhanced info
    sessionInfo: authService.getSessionInfo(),
    syncStatus,

    // Debug helpers (development only)
    ...(import.meta.env.MODE === 'development' && {
      debug: {
        queryState: userQuery,
        syncStatus,
        tokenDebug: tokenManager.getDebugInfo(),
        authServiceDebug: authService.getSessionInfo()
      }
    })
  }), [
    user, isAuthenticated,
    userQuery.isLoading, userQuery.isPending, userQuery.isError, userQuery.error,
    loginMutation.isPending, logoutMutation.isPending,
    updateProfileMutation.isPending, changePasswordMutation.isPending,
    login, logout, updateProfile, changePassword, refetchUser,
    hasPermission, hasAnyPermission, hasAllPermissions,
    isCompanyAdmin, isBrandAdmin, canAccessAnalytics, canAccessReports,
    syncStatus
  ]);
}

// ==========================================
// HOOKS SPÉCIALISÉS OPTIMISÉS
// ==========================================

export function useLoginHistory() {
  return useQuery({
    queryKey: authQueryKeys.loginHistory(),
    queryFn: authService.getLoginHistory,
    staleTime: 10 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
}

export function useAuthPermissions(user?: User) {
  return React.useMemo(() => {
    if (!user) return [];
    return authService.getUserPermissions(user);
  }, [user]);
}

// ==========================================
// HOOK DEBUG OPTIMISÉ
// ==========================================

export function useAuthSyncDebug() {
  const [debugInfo, setDebugInfo] = React.useState({
    authService: authService.getSessionInfo(),
    tokenManager: tokenManager.getDebugInfo(),
    timestamp: Date.now()
  });

  React.useEffect(() => {
    if (import.meta.env.MODE === 'development') {
      const updateDebug = () => {
        setDebugInfo({
          authService: authService.getSessionInfo(),
          tokenManager: tokenManager.getDebugInfo(),
          timestamp: Date.now()
        });
      };

      // Update TRÈS peu fréquent
      const interval = setInterval(updateDebug, 15000); // 15 secondes

      // Update sur événements avec délai important
      let eventTimeout: NodeJS.Timeout;
      const handleAuthEvent = () => {
        clearTimeout(eventTimeout);
        eventTimeout = setTimeout(updateDebug, 1000); // 1 seconde de délai
      };

      window.addEventListener('auth:login', handleAuthEvent);
      window.addEventListener('auth:logout', handleAuthEvent);

      return () => {
        clearInterval(interval);
        clearTimeout(eventTimeout);
        window.removeEventListener('auth:login', handleAuthEvent);
        window.removeEventListener('auth:logout', handleAuthEvent);
      };
    }

    return undefined;
  }, []);

  return debugInfo;
}

// ==========================================
// EXPORT DEFAULT
// ==========================================

export default useAuth;