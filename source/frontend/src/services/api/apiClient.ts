// frontend/src/services/api/apiClient.ts - Fix CORS + Performance

import type { ApiError, ApiResponse } from '@/types/global/api.types';
import { tokenManager } from '@/utils/security/tokenManager';
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios';

// ==========================================
// CONFIGURATION AXIOS FIXED
// ==========================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://backoffice.humari.fr';

interface ApiClientConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

const defaultConfig: ApiClientConfig = {
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
};

// ==========================================
// AXIOS INSTANCES - Instance unique
// ==========================================

// Instance principale avec auth
export const api: AxiosInstance = axios.create(defaultConfig);

// Instance publique sans auth (pour login/refresh)
const publicApiInstance: AxiosInstance = axios.create(defaultConfig);

// ==========================================
// INTERCEPTEUR REQUEST - JWT ROBUSTE OPTIMISÉ
// ==========================================

api.interceptors.request.use(
  async (config) => {
    if (import.meta.env.MODE === 'development') {
      console.log('🔧 [Interceptor] Request:', config.method?.toUpperCase(), config.url);
    }

    // ===== ÉTAPE 1 : Récupération token avec retry =====
    let accessToken: string | null = null;
    let tokenAttempts = 0;
    const maxTokenAttempts = 3;

    while (tokenAttempts < maxTokenAttempts && !accessToken) {
      accessToken = tokenManager.getAccessToken();

      if (!accessToken) {
        if (import.meta.env.MODE === 'development') {
          console.log(`🔄 [Interceptor] Token attempt ${tokenAttempts + 1}/${maxTokenAttempts}`);
        }

        // Attendre un peu et retry
        await new Promise(resolve => setTimeout(resolve, 50));
        tokenAttempts++;
      }
    }

    // ===== ÉTAPE 2 : Application du token =====
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;

      if (import.meta.env.MODE === 'development') {
        console.log('✅ [Interceptor] Token appliqué:', {
          tokenLength: accessToken.length,
          tokenPreview: `${accessToken.substring(0, 20)}...`
        });
      }
    } else {
      if (import.meta.env.MODE === 'development') {
        console.warn('⚠️ [Interceptor] Aucun token disponible après', maxTokenAttempts, 'tentatives');
        console.log('🔧 [Interceptor] TokenManager debug:', tokenManager.getDebugInfo());
      }
    }

    // ===== ÉTAPE 3 : Headers de sécurité FIXES =====
    config.headers['X-Requested-With'] = 'XMLHttpRequest';

    // CSRF token si disponible
    const csrfToken = tokenManager.getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }

    // 🔧 FIX CORS : Supprimer X-Request-ID temporairement
    // Le backend doit d'abord autoriser ce header dans CORS_ALLOW_HEADERS
    // config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    return config;
  },
  (error) => {
    console.error('❌ [Interceptor] Request error:', error);
    return Promise.reject(error);
  }
);

// ==========================================
// INTERCEPTEUR RESPONSE - REFRESH AUTOMATIQUE OPTIMISÉ
// ==========================================

api.interceptors.response.use(
  (response: AxiosResponse) => {
    // ===== LOG SUCCÈS =====
    if (import.meta.env.MODE === 'development') {
      console.log('✅ [Interceptor] Success:', {
        method: response.config.method?.toUpperCase(),
        url: response.config.url,
        status: response.status
      });
    }

    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (import.meta.env.MODE === 'development') {
      console.log('🔧 [Interceptor] Response error:', {
        status: error.response?.status,
        url: originalRequest?.url,
        hasRetried: !!originalRequest._retry,
        errorCode: error.code
      });
    }

    // ===== GESTION 401 - REFRESH TOKEN =====
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (import.meta.env.MODE === 'development') {
        console.log('🔄 [Interceptor] Tentative refresh token...');
      }

      try {
        const refreshToken = tokenManager.getRefreshToken();

        if (!refreshToken) {
          if (import.meta.env.MODE === 'development') {
            console.log('❌ [Interceptor] Pas de refresh token disponible');
          }
          throw new Error('No refresh token available');
        }

        // ===== REFRESH AVEC API PUBLIQUE =====
        const refreshResponse = await publicApiInstance.post('/auth/refresh/', {
          refresh: refreshToken,
        });

        const { access, access_expires_in, expires_in } = refreshResponse.data;

        if (!access) {
          throw new Error('No access token in refresh response');
        }

        // ===== SYNCHRONISATION ROBUSTE =====
        const expiresInSeconds = access_expires_in || expires_in;

        // Mise à jour synchrone
        tokenManager.setAccessToken(access, expiresInSeconds);

        // Vérification que le token est disponible
        let syncVerified = false;
        let syncAttempts = 0;
        const maxSyncAttempts = 10; // 1 seconde max

        while (syncAttempts < maxSyncAttempts && !syncVerified) {
          const verifyToken = tokenManager.getAccessToken();

          if (verifyToken === access) {
            syncVerified = true;

            if (import.meta.env.MODE === 'development') {
              console.log('✅ [Interceptor] Token refresh sync vérifié');
            }
          } else {
            await new Promise(resolve => setTimeout(resolve, 100));
            syncAttempts++;
          }
        }

        if (!syncVerified) {
          console.warn('⚠️ [Interceptor] Token sync timeout après refresh');
        }

        // ===== RETRY REQUÊTE ORIGINALE =====
        originalRequest.headers.Authorization = `Bearer ${access}`;

        if (import.meta.env.MODE === 'development') {
          console.log('🔄 [Interceptor] Retry requête originale avec nouveau token');
        }

        return api(originalRequest);

      } catch (refreshError) {
        if (import.meta.env.MODE === 'development') {
          console.error('❌ [Interceptor] Refresh token failed:', refreshError);
        }

        // ===== ÉCHEC REFRESH - DÉCONNEXION =====
        tokenManager.clearTokens();

        // Dispatcher événement de déconnexion forcée
        window.dispatchEvent(new CustomEvent('auth:logout', {
          detail: { reason: 'refresh_failed', originalError: refreshError }
        }));

        // Redirection vers login si pas déjà sur une page auth
        if (!window.location.pathname.includes('/auth/')) {
          const currentUrl = window.location.href;
          window.location.href = `/auth/login?redirect=${encodeURIComponent(currentUrl)}`;
        }

        return Promise.reject(refreshError);
      }
    }

    // ===== FORMATAGE ERREUR API =====
    const apiError: ApiError = {
      message: error.response?.data?.message ||
        error.message ||
        'Une erreur est survenue',
      code: error.response?.data?.code ||
        error.code ||
        'UNKNOWN_ERROR',
      details: error.response?.data?.details || {},
      non_field_errors: error.response?.data?.non_field_errors || [],
      timestamp: new Date().toISOString(),
      status_code: error.response?.status,
      // Pas de request_id pour éviter les références
    };

    // ===== GESTION ERREURS SPÉCIALES =====

    // Erreur réseau
    if (!error.response && error.code === 'NETWORK_ERROR') {
      const networkError: ApiError = {
        ...apiError,
        code: 'NETWORK_ERROR',
        message: 'Erreur de connexion réseau'
      };
      return Promise.reject(networkError);
    }

    // Timeout
    if (error.code === 'TIMEOUT' || error.code === 'ECONNABORTED') {
      const timeoutError: ApiError = {
        ...apiError,
        code: 'TIMEOUT_ERROR',
        message: 'La requête a expiré'
      };
      return Promise.reject(timeoutError);
    }

    // ===== LOGGING ERREUR SPÉCIALISÉ =====
    if (import.meta.env.MODE === 'development') {
      console.error('❌ [Interceptor] API Error:', {
        ...apiError,
        originalError: error,
        requestConfig: {
          method: originalRequest?.method,
          url: originalRequest?.url,
          data: originalRequest?.data
        }
      });
    }

    // Erreur 403 - Permissions
    if (error.response?.status === 403) {
      window.dispatchEvent(new CustomEvent('auth:forbidden', {
        detail: { error: apiError }
      }));
    }

    // Erreur 500+ - Serveur
    if (error.response?.status && error.response.status >= 500) {
      window.dispatchEvent(new CustomEvent('api:serverError', {
        detail: { error: apiError }
      }));
    }

    return Promise.reject(apiError);
  }
);

// ==========================================
// API CLIENT CLASS - METHODS TYPÉES ENHANCED
// ==========================================

interface RequestOptions extends AxiosRequestConfig {
  skipAuth?: boolean;
  skipRefresh?: boolean;
  retries?: number;
  retryDelay?: number;
}

class ApiClient {
  private instance: AxiosInstance;
  private publicInstance: AxiosInstance;

  constructor() {
    this.instance = api;
    this.publicInstance = publicApiInstance;
  }

  // ===== MÉTHODES HTTP TYPÉES =====

  async get<T = unknown>(url: string, options: RequestOptions = {}): Promise<ApiResponse<T>> {
    const response = await this.instance.get<ApiResponse<T>>(url, options);
    return response.data;
  }

  async post<T = unknown, D = unknown>(
    url: string,
    data?: D,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.post<ApiResponse<T>>(url, data, options);
    return response.data;
  }

  async put<T = unknown, D = unknown>(
    url: string,
    data?: D,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.put<ApiResponse<T>>(url, data, options);
    return response.data;
  }

  async patch<T = unknown, D = unknown>(
    url: string,
    data?: D,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const response = await this.instance.patch<ApiResponse<T>>(url, data, options);
    return response.data;
  }

  async delete<T = unknown>(url: string, options: RequestOptions = {}): Promise<ApiResponse<T>> {
    const response = await this.instance.delete<ApiResponse<T>>(url, options);
    return response.data;
  }

  // ===== MÉTHODES PUBLIQUES (sans auth) =====

  async postPublic<T = unknown, D = unknown>(
    url: string,
    data?: D
  ): Promise<T> {
    if (import.meta.env.MODE === 'development') {
      console.log('🔧 [Public Request] POST:', url);
    }

    const response = await this.publicInstance.post<T>(url, data);
    return response.data;
  }

  async getPublic<T = unknown>(url: string): Promise<T> {
    if (import.meta.env.MODE === 'development') {
      console.log('🔧 [Public Request] GET:', url);
    }

    const response = await this.publicInstance.get<T>(url);
    return response.data;
  }

  // ===== UTILITAIRES DIAGNOTIC & SYNC =====

  async ensureTokenSync(maxWaitMs: number = 2000): Promise<boolean> {
    if (import.meta.env.MODE === 'development') {
      console.log('🔧 [ApiClient] Vérification sync token...');
    }

    try {
      const token = await tokenManager.waitForToken(maxWaitMs);

      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [ApiClient] Token sync result:', {
          hasToken: !!token,
          tokenManagerDebug: tokenManager.getDebugInfo()
        });
      }

      return !!token;
    } catch (error) {
      console.error('❌ [ApiClient] Token sync error:', error);
      return false;
    }
  }

  getDebugInfo() {
    return {
      baseURL: API_BASE_URL,
      hasToken: !!tokenManager.getAccessToken(),
      hasRefreshToken: !!tokenManager.hasRefreshToken(),
      tokenExpiry: tokenManager.getTokenExpiry(),
      sessionId: tokenManager.getSessionId(),
      tokenManagerDebug: tokenManager.getDebugInfo(),
      timestamp: Date.now()
    };
  }
}

// ==========================================
// EXPORT INSTANCE & TYPES
// ==========================================

export const apiClient = new ApiClient();
export default api;

// Export instances
export { api as authenticatedApi, publicApiInstance as publicApi };

// Export types
export type { ApiClientConfig, RequestOptions };
