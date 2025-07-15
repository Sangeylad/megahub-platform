// frontend/src/services/api/authService.ts - Fix Final Undefined Data + Boucle

import type {
  AuthTokens,
  LoginFormData,
  LoginResponse,
  LogoutResponse,
  PasswordChangeData,
  PasswordChangeResponse,
  RefreshTokenResponse,
  User,
  UserUpdateData,
} from '@/types/auth';
import { tokenManager } from '@/utils/security/tokenManager';
import { authValidation } from '@/utils/validation/authValidation';
import { apiClient } from './apiClient';

// ==========================================
// QUERY KEYS FACTORY - TanStack Query v5
// ==========================================

export const authQueryKeys = {
  all: ['auth'] as const,
  user: () => [...authQueryKeys.all, 'user'] as const,
  profile: () => [...authQueryKeys.all, 'profile'] as const,
  loginHistory: () => [...authQueryKeys.all, 'loginHistory'] as const,
} as const;

// ==========================================
// AUTH SERVICE CLASS - FIX FINAL BOUCLE + UNDEFINED
// ==========================================

class AuthService {
  private readonly basePath = '/auth';
  private readonly baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // ===== CACHE OPTIMISÉ POUR ÉVITER BOUCLE =====
  private authCheckCache: {
    lastCheck: number;
    result: boolean;
    ttl: number;
  } = {
      lastCheck: 0,
      result: false,
      ttl: 2000, // 🔧 FIX : Augmenté à 2 secondes
    };

  // ===== THROTTLING LOGS =====
  private lastAuthLog = 0;
  private lastSessionLog = 0;
  private readonly logThrottle = 10000; // 10 secondes

  // ==========================================
  // AUTHENTIFICATION - ENHANCED SYNC
  // ==========================================

  async login(credentials: LoginFormData): Promise<LoginResponse> {
    // Validation côté client
    authValidation.validateLoginForm(credentials);

    try {
      // 🔧 DEBUG : Log début login
      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [AuthService] Starting login for:', credentials.username);
      }

      // 🔧 FIX : Utiliser apiClient.postPublic au lieu d'axios direct
      const loginData = await apiClient.postPublic<LoginResponse>(
        `${this.basePath}/login/`,
        {
          username: credentials.username.trim(),
          password: credentials.password,
          remember_me: credentials.remember_me || false,
        }
      );

      // 🔧 DEBUG : Log réponse login
      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [AuthService] Login response received:', {
          hasAccess: !!loginData.access,
          hasRefresh: !!loginData.refresh,
          hasUser: !!loginData.user,
          expiresIn: loginData.expires_in
        });
      }

      // 🔧 FIX : Créer tokens avec toutes les informations disponibles
      const tokens: AuthTokens = {
        access: loginData.access,
        refresh: loginData.refresh,
        token_type: 'Bearer' as const,
        expires_in: typeof loginData.expires_in === 'number' ? loginData.expires_in : undefined,
        access_expires_in: typeof loginData.expires_in === 'number' ? loginData.expires_in : undefined,
      };

      // 🔧 FIX : Synchronisation atomique AMÉLIORÉE
      await this.setTokensWithEnhancedSync(tokens);

      // 🔧 FIX : Vérifier que le token est bien disponible ET accessible par l'intercepteur
      const accessToken = tokenManager.getAccessToken();
      if (!accessToken) {
        throw new Error('Token non disponible après setTokens');
      }

      // 🔧 FIX : Tester que l'intercepteur peut voir le token
      const syncCheck = await apiClient.ensureTokenSync();
      if (!syncCheck) {
        console.warn('⚠️ [AuthService] Token sync check failed, but continuing...');
      }

      // 🔧 FIX : Invalider le cache d'authentification
      this.invalidateAuthCache();

      // 🔧 DEBUG : Log synchronisation complète
      if (import.meta.env.MODE === 'development') {
        console.log('✅ [AuthService] Token synchronization complete:', {
          tokenAvailable: !!accessToken,
          syncCheckPassed: syncCheck,
          tokenManagerDebug: tokenManager.getDebugInfo()
        });
      }

      // Dispatcher event pour les composants
      window.dispatchEvent(new CustomEvent('auth:login', {
        detail: { user: loginData.user }
      }));

      return loginData;

    } catch (error) {
      // Logger la tentative échouée
      console.error('Login failed:', error);

      // 🔧 FIX : Invalider le cache d'authentification
      this.invalidateAuthCache();

      // Dispatcher event d'échec
      window.dispatchEvent(new CustomEvent('auth:loginError', {
        detail: { error }
      }));

      throw error;
    }
  }

  // ==========================================
  // ENHANCED SYNCHRONISATION ATOMIQUE
  // ==========================================

  private async setTokensWithEnhancedSync(tokens: AuthTokens): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // 🔧 DEBUG : Log avant setTokens
        if (import.meta.env.MODE === 'development') {
          console.log('🔧 [AuthService] Setting tokens...');
        }

        // Set tokens synchronously
        tokenManager.setTokens(tokens);

        // 🔧 FIX : Vérification immédiate AMÉLIORÉE avec retry
        const verifyToken = (attempt: number = 1) => {
          const accessToken = tokenManager.getAccessToken();

          if (import.meta.env.MODE === 'development') {
            console.log(`🔧 [AuthService] Token verification attempt ${attempt}:`, {
              hasToken: !!accessToken,
              tokenLength: accessToken?.length || 0
            });
          }

          if (accessToken) {
            if (import.meta.env.MODE === 'development') {
              console.log('✅ [AuthService] Token verification successful');
            }
            resolve();
          } else if (attempt < 5) {
            // Retry jusqu'à 5 fois avec délai croissant
            setTimeout(() => {
              verifyToken(attempt + 1);
            }, attempt * 10); // 10ms, 20ms, 30ms, 40ms
          } else {
            console.error('❌ [AuthService] Token synchronization failed after 5 attempts');
            reject(new Error('Token synchronization failed'));
          }
        };

        verifyToken();
      } catch (error) {
        console.error('❌ [AuthService] setTokensWithEnhancedSync error:', error);
        reject(error);
      }
    });
  }

  async logout(): Promise<LogoutResponse> {
    try {
      const refreshToken = tokenManager.getRefreshToken();

      // Appel API de déconnexion avec token actuel
      const response = await apiClient.post<LogoutResponse>(
        `${this.basePath}/logout/`,
        refreshToken ? { refresh: refreshToken } : {}
      );

      // Nettoyer les tokens localement
      tokenManager.clearTokens();

      // 🔧 FIX : Invalider le cache d'authentification
      this.invalidateAuthCache();

      // Dispatcher event de déconnexion
      window.dispatchEvent(new CustomEvent('auth:logout'));

      return response.data;

    } catch (error) {
      // Même en cas d'erreur, nettoyer localement
      tokenManager.clearTokens();
      this.invalidateAuthCache();
      window.dispatchEvent(new CustomEvent('auth:logout'));

      throw error;
    }
  }

  async refreshToken(): Promise<string> {
    const refreshToken = tokenManager.getRefreshToken();

    if (!refreshToken) {
      throw new Error('Aucun refresh token disponible');
    }

    try {
      // 🔧 FIX : Utiliser apiClient.postPublic pour éviter loops
      const refreshResponse = await apiClient.postPublic<RefreshTokenResponse>(
        `${this.basePath}/refresh/`,
        { refresh: refreshToken }
      );

      const { access, access_expires_in, expires_in } = refreshResponse;

      // 🔧 FIX : Mise à jour atomique du token AMÉLIORÉE
      const expiresInSeconds = access_expires_in || expires_in;

      await new Promise<void>((resolve) => {
        tokenManager.setAccessToken(access, expiresInSeconds);

        // Vérification avec retry
        const verifyRefresh = (attempt: number = 1) => {
          const newToken = tokenManager.getAccessToken();
          if (newToken === access) {
            if (import.meta.env.MODE === 'development') {
              console.log('✅ [AuthService] Token refresh sync successful');
            }
            resolve();
          } else if (attempt < 3) {
            setTimeout(() => {
              verifyRefresh(attempt + 1);
            }, attempt * 10);
          } else {
            console.error('❌ [AuthService] Token refresh sync failed');
            resolve(); // Ne pas bloquer, mais log l'erreur
          }
        };

        verifyRefresh();
      });

      // 🔧 FIX : Invalider le cache d'authentification après refresh
      this.invalidateAuthCache();

      return access;

    } catch (error) {
      // Refresh failed - nettoyer et déconnecter
      tokenManager.clearTokens();
      this.invalidateAuthCache();
      window.dispatchEvent(new CustomEvent('auth:logout'));

      throw error;
    }
  }

  // ==========================================
  // GESTION UTILISATEUR - FIX UNDEFINED DATA
  // ==========================================

  async getCurrentUser(): Promise<User> {
    // 🔧 FIX : Vérifier que le token est accessible avant la requête
    const hasToken = await tokenManager.waitForToken(1000);

    if (!hasToken) {
      if (import.meta.env.MODE === 'development') {
        console.warn('⚠️ [AuthService] No token available for getCurrentUser');
      }
      throw new Error('No access token available');
    }

    if (import.meta.env.MODE === 'development') {
      console.log('🔧 [AuthService] Getting current user with token available');
    }

    try {
      // 🔧 FIX CRITIQUE : apiClient.get retourne déjà response.data
      // Pas besoin d'accéder à .data à nouveau !
      const userData = await apiClient.get<User>(`${this.basePath}/me/`);

      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [AuthService] User data received:', {
          hasData: !!userData,
          hasDataData: !!(userData as any)?.data,
          keys: userData ? Object.keys(userData) : 'no data'
        });
      }

      // 🔧 FIX : Si apiClient retourne une structure ApiResponse<User>
      // alors userData.data contient le User, sinon userData EST le User
      const user = (userData as any)?.data || userData;

      if (!user) {
        throw new Error('No user data received from API');
      }

      return user as User;

    } catch (error) {
      console.error('❌ [AuthService] getCurrentUser error:', error);
      throw error;
    }
  }

  async updateProfile(data: UserUpdateData): Promise<User> {
    // Validation des données
    authValidation.validateProfileUpdate(data);

    const response = await apiClient.patch<User>(
      `${this.basePath}/me/`,
      data
    );

    // 🔧 FIX : Même correction pour updateProfile
    const user = (response as any)?.data || response;

    // Dispatcher event de mise à jour profil
    window.dispatchEvent(new CustomEvent('auth:profileUpdated', {
      detail: { user }
    }));

    return user as User;
  }

  async changePassword(data: PasswordChangeData): Promise<PasswordChangeResponse> {
    // Validation des données
    authValidation.validatePasswordChange(data);

    const response = await apiClient.post<PasswordChangeResponse>(
      `${this.basePath}/change-password/`,
      data
    );

    // Dispatcher event de changement mot de passe
    window.dispatchEvent(new CustomEvent('auth:passwordChanged'));

    // 🔧 FIX : Correction structure response
    return (response as any)?.data || response;
  }

  // ==========================================
  // HISTORIQUE & SÉCURITÉ
  // ==========================================

  async getLoginHistory(): Promise<any[]> {
    const response = await apiClient.get<{ login_history: any[] }>(
      `${this.basePath}/login-history/`
    );

    // 🔧 FIX : Correction structure response
    const data = (response as any)?.data || response;
    return data.login_history || [];
  }

  // ==========================================
  // UTILITAIRES D'AUTHENTIFICATION - FIX BOUCLE FINALE
  // ==========================================

  isAuthenticated(): boolean {
    // 🔧 FIX : Cache plus long et strict pour éviter les appels répétés
    const now = Date.now();

    // Utiliser le cache si encore valide (2 secondes)
    if (now - this.authCheckCache.lastCheck < this.authCheckCache.ttl) {
      return this.authCheckCache.result;
    }

    const hasValidToken = tokenManager.hasValidAccessToken();
    const hasRefreshToken = tokenManager.hasRefreshToken();
    const result = hasValidToken || hasRefreshToken;

    // Mettre à jour le cache
    this.authCheckCache = {
      lastCheck: now,
      result,
      ttl: 2000, // 2 secondes de cache
    };

    // 🔧 FIX : Logs TRÈS throttlés (1 fois toutes les 10 secondes MAX)
    if (import.meta.env.MODE === 'development') {
      const shouldLog = (now - this.lastAuthLog) > this.logThrottle;

      if (shouldLog) {
        console.log('🔧 [AuthService] Authentication check:', {
          hasValidToken,
          hasRefreshToken,
          result,
          cached: false,
          nextLogIn: Math.round((this.logThrottle - (now - this.lastAuthLog)) / 1000) + 's'
        });
        this.lastAuthLog = now;
      }
    }

    return result;
  }

  private invalidateAuthCache(): void {
    this.authCheckCache.lastCheck = 0;
    this.lastAuthLog = 0; // Reset log throttle aussi
  }

  getUser(): User | null {
    // Cette méthode sera complétée par le store Zustand
    return null;
  }

  hasValidSession(): boolean {
    return tokenManager.hasRefreshToken();
  }

  needsAuthentication(): boolean {
    return !this.isAuthenticated();
  }

  // ==========================================
  // PERMISSIONS & RÔLES
  // ==========================================

  async checkPermission(permission: string): Promise<boolean> {
    try {
      const user = await this.getCurrentUser();
      return this.userHasPermission(user, permission);
    } catch {
      return false;
    }
  }

  userHasPermission(user: User, permission: string): boolean {
    const userPermissions = this.getUserPermissions(user);
    return userPermissions.includes(permission);
  }

  getUserPermissions(user: User): string[] {
    const permissions: Set<string> = new Set();

    // Permissions basées sur le type d'utilisateur
    if (user.user_type === 'agency_admin') {
      permissions.add('company.admin');
      permissions.add('users.write');
      permissions.add('brands.write');
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

    return Array.from(permissions);
  }

  // ==========================================
  // HELPERS DE RÔLE
  // ==========================================

  isCompanyAdmin(user?: User): boolean {
    if (!user) return false;
    return user.user_type === 'agency_admin' ||
      user.permissions_summary?.is_company_admin === true;
  }

  isBrandAdmin(user?: User): boolean {
    if (!user) return false;
    return user.user_type === 'brand_admin' ||
      user.permissions_summary?.is_brand_admin === true;
  }

  canAccessAnalytics(user?: User): boolean {
    if (!user) return false;
    return user.can_access_analytics ||
      this.isCompanyAdmin(user) ||
      this.isBrandAdmin(user);
  }

  canAccessReports(user?: User): boolean {
    if (!user) return false;
    return user.can_access_reports ||
      this.isCompanyAdmin(user) ||
      this.isBrandAdmin(user);
  }

  // ==========================================
  // GESTION DE SESSION - LOGS THROTTLÉS
  // ==========================================

  getSessionInfo() {
    const info = {
      isAuthenticated: this.isAuthenticated(),
      hasValidSession: this.hasValidSession(),
      tokenExpiry: tokenManager.getTokenExpiry(),
      timeUntilExpiry: tokenManager.getTimeUntilExpiry(),
      sessionId: tokenManager.getSessionId(),
      debugInfo: tokenManager.getDebugInfo(),
      authCacheAge: Date.now() - this.authCheckCache.lastCheck,
    };

    // 🔧 FIX : Logs TRÈS throttlés pour session info (1 fois toutes les 10 secondes)
    if (import.meta.env.MODE === 'development') {
      const now = Date.now();
      const shouldLog = (now - this.lastSessionLog) > this.logThrottle;
      if (shouldLog) {
        console.log('🔧 [AuthService] Session info:', info);
        this.lastSessionLog = now;
      }
    }

    return info;
  }

  // ==========================================
  // QUERY OPTIONS FACTORY - TanStack Query v5
  // ==========================================

  createQueryOptions = {
    user: () => ({
      queryKey: authQueryKeys.user(),
      queryFn: () => this.getCurrentUser(),
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (v5)
      retry: (failureCount: number, error: any) => {
        // Ne pas retry sur les erreurs 401/403
        if (error?.status_code === 401 || error?.status_code === 403) {
          return false;
        }
        return failureCount < 3;
      },
    }),

    loginHistory: () => ({
      queryKey: authQueryKeys.loginHistory(),
      queryFn: () => this.getLoginHistory(),
      staleTime: 10 * 60 * 1000, // 10 minutes
      gcTime: 30 * 60 * 1000, // 30 minutes (v5)
    }),
  } as const;
}

// ==========================================
// EXPORT SINGLETON
// ==========================================

export const authService = new AuthService();
export default authService;

// Export pour tests et hooks
export { AuthService };

// 🔧 DEBUG : Exposer sur window pour tests
if (typeof window !== 'undefined') {
  (window as any).authService = authService;
}