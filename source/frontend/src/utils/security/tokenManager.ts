// frontend/src/utils/security/tokenManager.ts - Fix Final Session Save Loop

import type { AuthTokens } from '@/types/auth';

// ==========================================
// INTERFACES TOKEN MANAGER
// ==========================================

interface TokenData {
  access: string;
  refresh: string;
  timestamp: number;
  expiresAt?: number;
}

interface StoredTokenData {
  refresh: string;
  timestamp: number;
  version: string;
}

interface SessionTokenData {
  access: string;
  expiresAt: number;
  timestamp: number;
  version: string;
}

interface TokenChangeListener {
  id: string;
  callback: () => void;
}

// ==========================================
// CONSTANTES SÉCURITÉ & CONFIGURATION
// ==========================================

const STORAGE_KEYS = {
  TOKENS: 'megahub_auth_tokens',
  SESSION: 'megahub_session_id',
  CSRF: 'megahub_csrf_token',
  ACCESS_SESSION: 'megahub_access_session',
} as const;

const TOKEN_VERSION = '1.1';
const ACCESS_TOKEN_BUFFER = 30 * 1000; // 30 secondes avant expiration
const MAX_STORAGE_AGE = 7 * 24 * 60 * 60 * 1000; // 7 jours
const SESSION_TOKEN_TTL = 60 * 60 * 1000; // 1 heure max en session
const SYNC_VERIFICATION_TIMEOUT = 5000; // 5 secondes max pour sync
const MAX_SYNC_RETRIES = 10;

// ==========================================
// CLASSE TOKEN MANAGER OPTIMISÉE ANTI-BOUCLE
// ==========================================

class TokenManager {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiry: number | null = null;
  private sessionId: string | null = null;

  // ===== SYSTÈME LISTENERS OPTIMISÉ =====
  private listeners: Map<string, TokenChangeListener> = new Map();
  private listenerIdCounter = 0;

  // ===== ÉTAT SYNCHRONISATION =====
  private isInitialized = false;
  private syncQueue: Array<() => void> = [];
  private lastSyncTime = 0;
  private syncInProgress = false;

  // ===== FIX BOUCLE : SESSION SAVE THROTTLING =====
  private lastSessionSave = 0;
  private sessionSaveThrottle = 1000; // 1 seconde entre saves
  private isNavigationEvent = false;

  constructor() {
    this.initializeAsync();
  }

  // ==========================================
  // INITIALISATION ASYNCHRONE
  // ==========================================

  private async initializeAsync(): Promise<void> {
    try {
      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [TokenManager] Début initialisation asynchrone...');
      }

      // Initialiser dans l'ordre optimal
      await this.initializeFromStorage();
      this.setupStorageListener();
      this.setupBeforeUnloadHandler();
      this.setupNavigationPersistence();
      this.setupPeriodicCleanup();

      this.isInitialized = true;
      this.processSyncQueue();

      if (import.meta.env.MODE === 'development') {
        console.log('✅ [TokenManager] Initialisation terminée:', this.getDebugInfo());
      }
    } catch (error) {
      console.error('❌ [TokenManager] Erreur initialisation:', error);
      this.clearStoredTokens();
    }
  }

  // ==========================================
  // SYSTÈME DE LISTENERS ROBUSTE
  // ==========================================

  addTokenChangeListener(callback: () => void): () => void {
    const id = `listener_${++this.listenerIdCounter}`;
    this.listeners.set(id, { id, callback });

    if (import.meta.env.MODE === 'development') {
      console.log('🔧 [TokenManager] Listener ajouté:', { id, totalListeners: this.listeners.size });
    }

    return () => {
      this.listeners.delete(id);
      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [TokenManager] Listener supprimé:', { id, totalListeners: this.listeners.size });
      }
    };
  }

  private notifyListeners(): void {
    if (this.listeners.size === 0) return;

    const notifications: Promise<void>[] = [];

    this.listeners.forEach(({ id, callback }) => {
      notifications.push(
        new Promise<void>((resolve) => {
          try {
            callback();
            resolve();
          } catch (error) {
            console.error(`❌ [TokenManager] Erreur listener ${id}:`, error);
            resolve(); // Continue malgré l'erreur
          }
        })
      );
    });

    // Exécuter notifications en parallèle avec timeout
    Promise.allSettled(notifications).then(() => {
      if (import.meta.env.MODE === 'development') {
        console.log('✅ [TokenManager] Notifications listeners terminées');
      }
    });
  }

  // ==========================================
  // NAVIGATION PERSISTENCE FIX BOUCLE
  // ==========================================

  private setupNavigationPersistence(): void {
    // Restaurer au démarrage
    this.restoreAccessTokenFromSession();

    // 🔧 FIX : Sauvegarder seulement sur événements navigation réels
    window.addEventListener('beforeunload', () => {
      this.isNavigationEvent = true;
      this.saveAccessTokenToSession();
      // Reset après délai
      setTimeout(() => {
        this.isNavigationEvent = false;
      }, 1000);
    });

    // 🔧 FIX : Gérer visibilité sans spam
    let visibilityTimeout: NodeJS.Timeout;
    document.addEventListener('visibilitychange', () => {
      clearTimeout(visibilityTimeout);

      visibilityTimeout = setTimeout(() => {
        if (document.hidden) {
          this.isNavigationEvent = true;
          this.saveAccessTokenToSession();
        } else {
          this.restoreAccessTokenFromSession();
        }
        // Reset après délai
        setTimeout(() => {
          this.isNavigationEvent = false;
        }, 500);
      }, 100); // Débounce 100ms
    });

    // 🔧 FIX : Gérer focus/blur sans spam
    let focusTimeout: NodeJS.Timeout;
    window.addEventListener('focus', () => {
      clearTimeout(focusTimeout);
      focusTimeout = setTimeout(() => {
        this.restoreAccessTokenFromSession();
      }, 100);
    });

    window.addEventListener('blur', () => {
      clearTimeout(focusTimeout);
      focusTimeout = setTimeout(() => {
        this.isNavigationEvent = true;
        this.saveAccessTokenToSession();
        setTimeout(() => {
          this.isNavigationEvent = false;
        }, 500);
      }, 100);
    });

    // Nettoyage périodique session storage
    setInterval(() => {
      this.cleanupExpiredSessionTokens();
    }, 60000); // Chaque minute
  }

  private saveAccessTokenToSession(): void {
    if (!this.accessToken || !this.tokenExpiry) return;

    // 🔧 FIX : Throttling pour éviter saves répétitifs
    const now = Date.now();
    if (now - this.lastSessionSave < this.sessionSaveThrottle && !this.isNavigationEvent) {
      return; // Skip si trop récent et pas navigation
    }

    try {
      const sessionData: SessionTokenData = {
        access: this.accessToken,
        expiresAt: this.tokenExpiry,
        timestamp: Date.now(),
        version: TOKEN_VERSION,
      };

      sessionStorage.setItem(STORAGE_KEYS.ACCESS_SESSION, JSON.stringify(sessionData));
      this.lastSessionSave = now;

      if (import.meta.env.MODE === 'development') {
        console.log('🔧 [TokenManager] Token sauvé en session pour navigation');
      }
    } catch (error) {
      console.error('❌ [TokenManager] Erreur sauvegarde session:', error);
    }
  }

  private restoreAccessTokenFromSession(): void {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEYS.ACCESS_SESSION);
      if (!stored) return;

      const sessionData: SessionTokenData = JSON.parse(stored);

      // Vérifications de validité
      if (sessionData.version !== TOKEN_VERSION) {
        sessionStorage.removeItem(STORAGE_KEYS.ACCESS_SESSION);
        return;
      }

      const age = Date.now() - sessionData.timestamp;
      if (age > SESSION_TOKEN_TTL) {
        sessionStorage.removeItem(STORAGE_KEYS.ACCESS_SESSION);
        return;
      }

      if (Date.now() >= sessionData.expiresAt - ACCESS_TOKEN_BUFFER) {
        sessionStorage.removeItem(STORAGE_KEYS.ACCESS_SESSION);
        return;
      }

      // Restaurer seulement si pas déjà présent ou différent
      if (!this.accessToken || this.accessToken !== sessionData.access) {
        this.accessToken = sessionData.access;
        this.tokenExpiry = sessionData.expiresAt;

        if (import.meta.env.MODE === 'development') {
          console.log('✅ [TokenManager] Token restauré depuis session:', {
            hasToken: !!this.accessToken,
            expiresAt: new Date(this.tokenExpiry),
            timeUntilExpiry: this.tokenExpiry - Date.now()
          });
        }

        this.notifyListeners();
      }
    } catch (error) {
      console.error('❌ [TokenManager] Erreur restauration session:', error);
      sessionStorage.removeItem(STORAGE_KEYS.ACCESS_SESSION);
    }
  }

  private cleanupExpiredSessionTokens(): void {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEYS.ACCESS_SESSION);
      if (!stored) return;

      const sessionData: SessionTokenData = JSON.parse(stored);
      const age = Date.now() - sessionData.timestamp;

      if (age > SESSION_TOKEN_TTL || Date.now() >= sessionData.expiresAt) {
        sessionStorage.removeItem(STORAGE_KEYS.ACCESS_SESSION);

        if (import.meta.env.MODE === 'development') {
          console.log('🧹 [TokenManager] Token session expiré nettoyé');
        }
      }
    } catch (error) {
      sessionStorage.removeItem(STORAGE_KEYS.ACCESS_SESSION);
    }
  }

  // ==========================================
  // INITIALISATION STORAGE
  // ==========================================

  private async initializeFromStorage(): Promise<void> {
    try {
      // Récupérer refresh token
      const storedData = localStorage.getItem(STORAGE_KEYS.TOKENS);
      if (storedData) {
        const parsed: StoredTokenData = JSON.parse(storedData);

        if (parsed.version === TOKEN_VERSION) {
          const age = Date.now() - parsed.timestamp;
          if (age < MAX_STORAGE_AGE) {
            this.refreshToken = parsed.refresh;
          } else {
            this.clearStoredTokens();
          }
        } else {
          this.clearStoredTokens();
        }
      }

      // Restaurer access token depuis session
      this.restoreAccessTokenFromSession();

      // Gérer session ID
      this.sessionId = sessionStorage.getItem(STORAGE_KEYS.SESSION);
      if (!this.sessionId) {
        this.sessionId = this.generateSessionId();
        sessionStorage.setItem(STORAGE_KEYS.SESSION, this.sessionId);
      }

    } catch (error) {
      console.error('❌ [TokenManager] Erreur initialisation storage:', error);
      this.clearStoredTokens();
    }
  }

  private setupStorageListener(): void {
    window.addEventListener('storage', (event) => {
      if (event.key === STORAGE_KEYS.TOKENS) {
        if (event.newValue === null) {
          // Refresh token supprimé dans un autre onglet
          this.clearMemoryTokens();
          this.notifyListeners();
          window.dispatchEvent(new CustomEvent('auth:logout', {
            detail: { reason: 'storage_cleared' }
          }));
        }
      }
    });
  }

  private setupBeforeUnloadHandler(): void {
    window.addEventListener('beforeunload', () => {
      this.saveAccessTokenToSession();
    });
  }

  private setupPeriodicCleanup(): void {
    // Nettoyage périodique des tokens expirés
    setInterval(() => {
      this.performCleanup();
    }, 5 * 60 * 1000); // Chaque 5 minutes
  }

  private performCleanup(): void {
    let hasChanges = false;

    // Vérifier expiration access token
    if (this.accessToken && this.tokenExpiry) {
      if (Date.now() >= this.tokenExpiry - ACCESS_TOKEN_BUFFER) {
        this.clearAccessToken();
        hasChanges = true;
      }
    }

    // Nettoyer session storage
    this.cleanupExpiredSessionTokens();

    if (hasChanges) {
      this.notifyListeners();
    }
  }

  // ==========================================
  // GESTION TOKENS AVEC SYNCHRONISATION
  // ==========================================

  setTokens(tokens: AuthTokens): void {
    const oldAccessToken = this.accessToken;

    this.accessToken = tokens.access;
    this.refreshToken = tokens.refresh;

    // Décoder expiration avec priorités
    if (typeof tokens.access_expires_in === 'number') {
      this.tokenExpiry = Date.now() + tokens.access_expires_in * 1000;
    } else if (typeof tokens.expires_in === 'number') {
      this.tokenExpiry = Date.now() + tokens.expires_in * 1000;
    } else {
      this.tokenExpiry = this.decodeTokenExpiration(tokens.access);
    }

    // Stocker refresh token
    this.storeRefreshToken();

    // 🔧 FIX : Sauvegarder access token SEULEMENT si changement
    if (oldAccessToken !== this.accessToken) {
      this.isNavigationEvent = true; // Force save
      this.saveAccessTokenToSession();
      this.isNavigationEvent = false;
    }

    // Mettre à jour sync time
    this.lastSyncTime = Date.now();

    // Notifier changements
    if (oldAccessToken !== this.accessToken) {
      this.notifyListeners();
    }

    if (import.meta.env.MODE === 'development') {
      console.log('✅ [TokenManager] setTokens terminé:', {
        hasAccessToken: !!this.accessToken,
        hasRefreshToken: !!this.refreshToken,
        expiresAt: this.tokenExpiry ? new Date(this.tokenExpiry) : null,
        expiresInHours: this.tokenExpiry ? (this.tokenExpiry - Date.now()) / (1000 * 60 * 60) : null,
        listenersCount: this.listeners.size,
        sessionPersistence: true
      });
    }
  }

  setAccessToken(accessToken: string, expiresIn?: number): void {
    const oldAccessToken = this.accessToken;

    this.accessToken = accessToken;

    if (typeof expiresIn === 'number') {
      this.tokenExpiry = Date.now() + expiresIn * 1000;
    } else {
      this.tokenExpiry = this.decodeTokenExpiration(accessToken);
    }

    // 🔧 FIX : Sauvegarder SEULEMENT si changement
    if (oldAccessToken !== this.accessToken) {
      this.isNavigationEvent = true; // Force save
      this.saveAccessTokenToSession();
      this.isNavigationEvent = false;
    }

    this.lastSyncTime = Date.now();

    if (oldAccessToken !== this.accessToken) {
      this.notifyListeners();
    }
  }

  getAccessToken(): string | null {
    // Restaurer depuis session si pas en mémoire
    if (!this.accessToken) {
      this.restoreAccessTokenFromSession();
    }

    // Vérifier expiration
    if (this.accessToken && this.tokenExpiry) {
      const isExpired = Date.now() >= (this.tokenExpiry - ACCESS_TOKEN_BUFFER);
      if (isExpired) {
        if (import.meta.env.MODE === 'development') {
          console.log('🔧 [TokenManager] Access token expiré, nettoyage');
        }
        this.clearAccessToken();
        return null;
      }
    }

    return this.accessToken;
  }

  getRefreshToken(): string | null {
    return this.refreshToken;
  }

  // ==========================================
  // SYNCHRONISATION ROBUSTE
  // ==========================================

  async waitForToken(maxWaitMs: number = 1000): Promise<string | null> {
    // Si pas encore initialisé, attendre
    if (!this.isInitialized) {
      await this.waitForInitialization(maxWaitMs);
    }

    const startTime = Date.now();
    let attempts = 0;
    const maxAttempts = Math.min(MAX_SYNC_RETRIES, Math.ceil(maxWaitMs / 50));

    while (Date.now() - startTime < maxWaitMs && attempts < maxAttempts) {
      const token = this.getAccessToken();

      if (token) {
        if (import.meta.env.MODE === 'development') {
          console.log(`✅ [TokenManager] Token obtenu après ${attempts + 1} tentatives`);
        }
        return token;
      }

      attempts++;
      await new Promise(resolve => setTimeout(resolve, 50));
    }

    if (import.meta.env.MODE === 'development') {
      console.log(`❌ [TokenManager] Timeout token après ${attempts} tentatives`);
    }

    return null;
  }

  private async waitForInitialization(maxWaitMs: number): Promise<void> {
    const startTime = Date.now();

    while (!this.isInitialized && Date.now() - startTime < maxWaitMs) {
      await new Promise(resolve => setTimeout(resolve, 10));
    }
  }

  private processSyncQueue(): void {
    if (this.syncInProgress) return;

    this.syncInProgress = true;

    try {
      while (this.syncQueue.length > 0) {
        const operation = this.syncQueue.shift();
        if (operation) {
          operation();
        }
      }
    } finally {
      this.syncInProgress = false;
    }
  }

  // ==========================================
  // UTILITAIRES
  // ==========================================

  hasValidAccessToken(): boolean {
    return this.getAccessToken() !== null;
  }

  hasRefreshToken(): boolean {
    return this.refreshToken !== null;
  }

  needsRefresh(): boolean {
    return !this.hasValidAccessToken() && this.hasRefreshToken();
  }

  getTokenExpiry(): Date | null {
    return this.tokenExpiry ? new Date(this.tokenExpiry) : null;
  }

  getTimeUntilExpiry(): number {
    if (!this.tokenExpiry) return 0;
    return Math.max(0, this.tokenExpiry - Date.now());
  }

  // ==========================================
  // SESSION MANAGEMENT
  // ==========================================

  getSessionId(): string | null {
    return this.sessionId;
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // ==========================================
  // CSRF PROTECTION
  // ==========================================

  setCsrfToken(token: string): void {
    sessionStorage.setItem(STORAGE_KEYS.CSRF, token);
  }

  getCsrfToken(): string | null {
    return sessionStorage.getItem(STORAGE_KEYS.CSRF);
  }

  // ==========================================
  // MÉTHODES PRIVÉES
  // ==========================================

  private decodeTokenExpiration(token: string): number | null {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;

      const payload = JSON.parse(atob(parts[1]));
      return payload.exp ? payload.exp * 1000 : null;
    } catch (error) {
      console.error('❌ [TokenManager] Erreur décodage token:', error);
      return null;
    }
  }

  private storeRefreshToken(): void {
    if (!this.refreshToken) return;

    try {
      const tokenData: StoredTokenData = {
        refresh: this.refreshToken,
        timestamp: Date.now(),
        version: TOKEN_VERSION,
      };

      localStorage.setItem(STORAGE_KEYS.TOKENS, JSON.stringify(tokenData));
    } catch (error) {
      console.error('❌ [TokenManager] Erreur stockage refresh token:', error);
    }
  }

  private clearStoredTokens(): void {
    localStorage.removeItem(STORAGE_KEYS.TOKENS);
  }

  private clearMemoryTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpiry = null;
  }

  private clearAccessToken(): void {
    const oldAccessToken = this.accessToken;
    this.accessToken = null;
    this.tokenExpiry = null;

    sessionStorage.removeItem(STORAGE_KEYS.ACCESS_SESSION);

    if (oldAccessToken !== null) {
      this.notifyListeners();
    }
  }

  // ==========================================
  // NETTOYAGE COMPLET
  // ==========================================

  clearTokens(): void {
    this.clearMemoryTokens();
    this.clearStoredTokens();
    sessionStorage.removeItem(STORAGE_KEYS.CSRF);
    sessionStorage.removeItem(STORAGE_KEYS.ACCESS_SESSION);

    this.lastSyncTime = Date.now();
    this.lastSessionSave = 0; // Reset save throttle
    this.notifyListeners();
  }

  // ==========================================
  // DEBUG & MONITORING
  // ==========================================

  getDebugInfo() {
    return {
      hasAccessToken: !!this.accessToken,
      hasRefreshToken: !!this.refreshToken,
      accessTokenExpiry: this.getTokenExpiry(),
      timeUntilExpiry: this.getTimeUntilExpiry(),
      timeUntilExpiryHours: this.tokenExpiry ? (this.tokenExpiry - Date.now()) / (1000 * 60 * 60) : null,
      sessionId: this.sessionId,
      needsRefresh: this.needsRefresh(),
      tokenExpiryTimestamp: this.tokenExpiry,
      listenersCount: this.listeners.size,
      version: TOKEN_VERSION,
      sessionPersistence: !!sessionStorage.getItem(STORAGE_KEYS.ACCESS_SESSION),
      isInitialized: this.isInitialized,
      lastSyncTime: this.lastSyncTime,
      syncInProgress: this.syncInProgress,
      syncQueueLength: this.syncQueue.length,
      lastSessionSave: this.lastSessionSave,
      sessionSaveThrottle: this.sessionSaveThrottle,
    };
  }

  // ==========================================
  // VALIDATION TOKENS
  // ==========================================

  validateTokenFormat(token: string): boolean {
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    try {
      const payload = JSON.parse(atob(parts[1]));
      return !!payload.exp && !!payload.user_id;
    } catch {
      return false;
    }
  }

  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp * 1000;
      return Date.now() >= exp;
    } catch {
      return true;
    }
  }

  // ==========================================
  // HEALTH CHECK ENHANCED
  // ==========================================

  performHealthCheck(): {
    status: 'healthy' | 'warning' | 'error';
    issues: string[];
    recommendations: string[];
    metrics: Record<string, any>;
  } {
    const issues: string[] = [];
    const recommendations: string[] = [];
    const metrics: Record<string, any> = {};

    // Vérifications de base
    if (!this.hasRefreshToken()) {
      issues.push('Aucun refresh token disponible');
      recommendations.push('L\'utilisateur doit se reconnecter');
    }

    if (this.hasValidAccessToken()) {
      const timeUntilExpiry = this.getTimeUntilExpiry();
      metrics.timeUntilExpiryMinutes = Math.floor(timeUntilExpiry / (1000 * 60));

      if (timeUntilExpiry < 5 * 60 * 1000) {
        issues.push('Token d\'accès expire bientôt');
        recommendations.push('Refresh automatique recommandé');
      }
    }

    // Vérifier persistence session
    const hasSessionPersistence = !!sessionStorage.getItem(STORAGE_KEYS.ACCESS_SESSION);
    metrics.hasSessionPersistence = hasSessionPersistence;

    if (this.accessToken && !hasSessionPersistence) {
      issues.push('Session persistence non active');
      recommendations.push('Sauvegarder token pour navigation');
    }

    // Vérifier listeners
    metrics.listenersCount = this.listeners.size;
    if (this.listeners.size === 0) {
      issues.push('Aucun listener actif');
      recommendations.push('Vérifier les hooks d\'authentification');
    }

    // Vérifier storage
    try {
      localStorage.setItem('test', 'test');
      localStorage.removeItem('test');
      metrics.localStorageAvailable = true;
    } catch {
      issues.push('localStorage non disponible');
      recommendations.push('Vérifier paramètres navigateur');
      metrics.localStorageAvailable = false;
    }

    // Métriques de synchronisation
    metrics.isInitialized = this.isInitialized;
    metrics.lastSyncAge = this.lastSyncTime ? Date.now() - this.lastSyncTime : null;
    metrics.syncInProgress = this.syncInProgress;
    metrics.sessionSaveThrottle = this.sessionSaveThrottle;

    const status = issues.length === 0 ? 'healthy' :
      issues.length <= 2 ? 'warning' : 'error';

    return { status, issues, recommendations, metrics };
  }
}

// ==========================================
// EXPORT SINGLETON
// ==========================================

export const tokenManager = new TokenManager();

// Debug global (development)
if (typeof window !== 'undefined' && import.meta.env.MODE === 'development') {
  (window as any).tokenManager = tokenManager;
}

export { TokenManager };
