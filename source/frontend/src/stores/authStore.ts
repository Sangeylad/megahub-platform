// frontend/src/stores/authStore.ts

import { create } from 'zustand';
import { persist, devtools, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { 
  User, 
  AuthTokens, 
  AuthState,
  UserType 
} from '@/types/auth';

interface AuthStoreState extends AuthState {
  setUser: (user: User | null) => void;
  setTokens: (tokens: AuthTokens | null) => void;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  setIsLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  updateLastActivity: () => void;
  updateUserProfile: (updates: Partial<User>) => void;
  clearAuth: () => void;
  clearError: () => void;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (permissions: string[]) => boolean;
  hasAllPermissions: (permissions: string[]) => boolean;
  isCompanyAdmin: () => boolean;
  isBrandAdmin: () => boolean;
  canAccessAnalytics: () => boolean;
  canAccessReports: () => boolean;
  canAccessBrand: (brandId: number) => boolean;
  canAdminBrand: (brandId: number) => boolean;
  isSessionValid: () => boolean;
  getSessionInfo: () => AuthSessionInfo;
}

interface AuthSessionInfo {
  isAuthenticated: boolean;
  hasValidSession: boolean;
  userType: UserType | null;
  lastActivity: number;
  timeToExpiry: number | null;
  sessionId: string | null;
}

const initialAuthState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  lastActivity: Date.now(),
};

export const useAuthStore = create<AuthStoreState>()(
  devtools(
    subscribeWithSelector(
      immer(
        persist(
          (set, get) => ({
            ...initialAuthState,

            setUser: (user: User | null) => {
              set((state) => {
                state.user = user;
                state.isAuthenticated = !!user;
                state.lastActivity = Date.now();
                
                if (typeof window !== 'undefined') {
                  window.dispatchEvent(new CustomEvent('auth:userChanged', {
                    detail: { user }
                  }));
                }
              });
            },

            setTokens: (tokens: AuthTokens | null) => {
              set((state) => {
                state.tokens = tokens;
                state.lastActivity = Date.now();
              });
            },

            setIsAuthenticated: (isAuthenticated: boolean) => {
              set((state) => {
                state.isAuthenticated = isAuthenticated;
                state.lastActivity = Date.now();
              });
            },

            setIsLoading: (isLoading: boolean) => {
              set((state) => {
                state.isLoading = isLoading;
              });
            },

            setError: (error: string | null) => {
              set((state) => {
                state.error = error;
              });
            },

            updateLastActivity: () => {
              set((state) => {
                state.lastActivity = Date.now();
              });
            },

            updateUserProfile: (updates: Partial<User>) => {
              set((state) => {
                if (state.user) {
                  state.user = { ...state.user, ...updates };
                  state.lastActivity = Date.now();
                  
                  if (typeof window !== 'undefined') {
                    window.dispatchEvent(new CustomEvent('auth:profileUpdated', {
                      detail: { user: state.user }
                    }));
                  }
                }
              });
            },

            clearAuth: () => {
              set((state) => {
                state.user = null;
                state.tokens = null;
                state.isAuthenticated = false;
                state.error = null;
                state.isLoading = false;
                state.lastActivity = Date.now();
                
                if (typeof window !== 'undefined') {
                  window.dispatchEvent(new CustomEvent('auth:cleared'));
                }
              });
            },

            clearError: () => {
              set((state) => {
                state.error = null;
              });
            },

            hasPermission: (permission: string): boolean => {
              const { user } = get();
              if (!user) return false;
              const permissions = getUserPermissions(user);
              return permissions.includes(permission);
            },

            hasAnyPermission: (permissions: string[]): boolean => {
              const { hasPermission } = get();
              return permissions.some(permission => hasPermission(permission));
            },

            hasAllPermissions: (permissions: string[]): boolean => {
              const { hasPermission } = get();
              return permissions.every(permission => hasPermission(permission));
            },

            isCompanyAdmin: (): boolean => {
              const { user } = get();
              if (!user) return false;
              return user.user_type === 'agency_admin' || 
                     user.permissions_summary?.is_company_admin === true;
            },

            isBrandAdmin: (): boolean => {
              const { user } = get();
              if (!user) return false;
              return user.user_type === 'brand_admin' || 
                     user.permissions_summary?.is_brand_admin === true;
            },

            canAccessAnalytics: (): boolean => {
              const { user, isCompanyAdmin, isBrandAdmin } = get();
              if (!user) return false;
              return user.can_access_analytics || isCompanyAdmin() || isBrandAdmin();
            },

            canAccessReports: (): boolean => {
              const { user, isCompanyAdmin, isBrandAdmin } = get();
              if (!user) return false;
              return user.can_access_reports || isCompanyAdmin() || isBrandAdmin();
            },

            canAccessBrand: (brandId: number): boolean => {
              const { user } = get();
              if (!user) return false;
              
              if (user.user_type === 'agency_admin') return true;
              
              return user.brands?.some(brand => 
                (typeof brand === 'object' ? brand.id : brand) === brandId
              ) || false;
            },

            canAdminBrand: (brandId: number): boolean => {
              const { user } = get();
              if (!user) return false;
              
              if (user.user_type === 'agency_admin') return true;
              
              return user.administered_brands_list?.some(brand => 
                brand.id === brandId
              ) || false;
            },

            isSessionValid: (): boolean => {
              const { tokens, lastActivity } = get();
              if (!tokens) return false;
              
              const SESSION_TIMEOUT = 2 * 60 * 60 * 1000;
              const timeSinceActivity = Date.now() - lastActivity;
              
              return timeSinceActivity < SESSION_TIMEOUT;
            },

            getSessionInfo: (): AuthSessionInfo => {
              const { user, tokens, isAuthenticated, lastActivity } = get();
              
              return {
                isAuthenticated,
                hasValidSession: !!tokens,
                userType: user?.user_type || null,
                lastActivity,
                timeToExpiry: tokens ? getTokenTimeToExpiry() : null,
                sessionId: getSessionId(),
              };
            },
          }),
          {
            name: 'megahub-auth-store',
            version: 1,
            partialize: (state) => ({
              user: state.user,
              isAuthenticated: state.isAuthenticated,
              lastActivity: state.lastActivity,
            }),
            migrate: (persistedState: any, version: number) => {
              if (version === 0) {
                return {
                  ...persistedState,
                  lastActivity: Date.now(),
                };
              }
              return persistedState as AuthStoreState;
            },
          }
        )
      )
    ),
    { name: 'AuthStore' }
  )
);

function getUserPermissions(user: User): string[] {
  const permissions: Set<string> = new Set();

  if (user.user_type === 'agency_admin') {
    permissions.add('company.admin');
    permissions.add('users.write');
    permissions.add('brands.write');
    permissions.add('analytics.read');
    permissions.add('reports.read');
  }

  if (user.user_type === 'brand_admin') {
    permissions.add('brand.admin');
    permissions.add('pages.write');
    permissions.add('analytics.read');
  }

  if (user.can_access_analytics) {
    permissions.add('analytics.read');
  }

  if (user.can_access_reports) {
    permissions.add('reports.read');
  }

  permissions.add('profile.read');
  permissions.add('profile.write');

  return Array.from(permissions);
}

function getTokenTimeToExpiry(): number | null {
  return null;
}

function getSessionId(): string | null {
  if (typeof window !== 'undefined') {
    return sessionStorage.getItem('megahub_session_id');
  }
  return null;
}

export const useAuthUser = () => useAuthStore((state) => state.user);
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated);
export const useAuthTokens = () => useAuthStore((state) => state.tokens);
export const useAuthLoading = () => useAuthStore((state) => state.isLoading);
export const useAuthError = () => useAuthStore((state) => state.error);
export const useLastActivity = () => useAuthStore((state) => state.lastActivity);

export const useUserDisplayName = () => useAuthStore((state) => {
  if (!state.user) return '';
  return `${state.user.first_name} ${state.user.last_name}`.trim() || state.user.username;
});

export const useUserInitials = () => useAuthStore((state) => {
  if (!state.user) return '';
  const firstName = state.user.first_name?.charAt(0) || '';
  const lastName = state.user.last_name?.charAt(0) || '';
  return (firstName + lastName).toUpperCase() || state.user.username.charAt(0).toUpperCase();
});

export const useUserPermissions = () => useAuthStore((state) => {
  if (!state.user) return [];
  return getUserPermissions(state.user);
});

export const useAuthActions = () => useAuthStore((state) => ({
  setUser: state.setUser,
  setTokens: state.setTokens,
  setIsAuthenticated: state.setIsAuthenticated,
  setIsLoading: state.setIsLoading,
  setError: state.setError,
  updateLastActivity: state.updateLastActivity,
  updateUserProfile: state.updateUserProfile,
  clearAuth: state.clearAuth,
  clearError: state.clearError,
}));

export const usePermissionActions = () => useAuthStore((state) => ({
  hasPermission: state.hasPermission,
  hasAnyPermission: state.hasAnyPermission,
  hasAllPermissions: state.hasAllPermissions,
}));

export const useRoleActions = () => useAuthStore((state) => ({
  isCompanyAdmin: state.isCompanyAdmin,
  isBrandAdmin: state.isBrandAdmin,
  canAccessAnalytics: state.canAccessAnalytics,
  canAccessReports: state.canAccessReports,
  canAccessBrand: state.canAccessBrand,
  canAdminBrand: state.canAdminBrand,
}));

export default useAuthStore;
