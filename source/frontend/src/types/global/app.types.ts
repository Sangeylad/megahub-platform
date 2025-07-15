// frontend/src/types/global/app.types.ts

// 🎯 Types application globaux - React 19 + TanStack v5 selon architecture MegaHub

// ==========================================
// USER TYPES (Re-export from auth pour compatibilité)
// ==========================================

export interface User {
  readonly id: number;
  readonly username: string;
  readonly email: string;
  readonly first_name: string;
  readonly last_name: string;
  readonly user_type: 'agency_admin' | 'brand_admin' | 'brand_member' | 'client_readonly';
  readonly company?: {
    readonly id: number;
    readonly name: string;
  } | null;
  readonly permissions: string[];
  readonly avatar?: string;
  readonly phone: string;
  readonly position: string;
  readonly can_access_analytics: boolean;
  readonly can_access_reports: boolean;
  readonly is_active: boolean;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface AuthTokens {
  readonly access: string;
  readonly refresh: string;
  readonly access_expires_in?: number;
  readonly refresh_expires_in?: number;
  readonly token_type: 'Bearer';
}

// ==========================================
// APPLICATION CONFIGURATION
// ==========================================

export type Environment = 'development' | 'staging' | 'production' | 'test';

export interface AppConfig {
  readonly api: {
    readonly baseUrl: string;
    readonly timeout: number;
    readonly retries: number;
  };
  readonly app: {
    readonly name: string;
    readonly version: string;
    readonly environment: Environment;
    readonly debug: boolean;
  };
  readonly features: {
    readonly enableReactCompiler: boolean;
    readonly enableLightningCSS: boolean;
    readonly enableMockApi: boolean;
    readonly enableServiceWorker: boolean;
    readonly enableAnalytics: boolean;
    readonly enableErrorTracking: boolean;
  };
  readonly ui: {
    readonly theme: 'light' | 'dark' | 'auto';
    readonly language: string;
    readonly timezone: string;
    readonly currency: string;
  };
  readonly security: {
    readonly enableCSP: boolean;
    readonly enableSRI: boolean;
    readonly sessionTimeout: number;
    readonly maxLoginAttempts: number;
  };
}

// ==========================================
// NAVIGATION & ROUTING
// ==========================================

export interface NavigationItem {
  readonly id: string;
  readonly label: string;
  readonly href: string;
  readonly icon?: string;
  readonly badge?: {
    readonly text: string;
    readonly variant: 'default' | 'secondary' | 'destructive' | 'outline';
  };
  readonly isActive?: boolean;
  readonly isDisabled?: boolean;
  readonly children?: NavigationItem[];
  readonly permissions?: string[]; // Permissions requises pour afficher
  readonly roles?: string[]; // Rôles requis pour afficher
}

export interface Breadcrumb {
  readonly id: string;
  readonly label: string;
  readonly href?: string;
  readonly isActive?: boolean;
}

export interface RouteMetadata {
  readonly title: string;
  readonly description?: string;
  readonly keywords?: string[];
  readonly breadcrumbs?: Breadcrumb[];
  readonly permissions?: string[];
  readonly roles?: string[];
  readonly layout?: 'default' | 'auth' | 'minimal' | 'dashboard';
}

// ==========================================
// ERROR HANDLING - React 19
// ==========================================

export interface ErrorInfo {
  readonly componentStack: string;
  readonly errorBoundary?: string;
  readonly errorBoundaryStack?: string;
}

export interface AppError extends Error {
  readonly code?: string;
  readonly statusCode?: number;
  readonly context?: Record<string, unknown>;
  readonly timestamp?: string;
  readonly user_id?: number;
  readonly session_id?: string;
  readonly request_id?: string;
  readonly component?: string;
  readonly severity?: 'low' | 'medium' | 'high' | 'critical';
}

export interface ErrorBoundaryState {
  readonly hasError: boolean;
  readonly error?: AppError;
  readonly errorInfo?: ErrorInfo;
  readonly fallbackComponent?: React.ComponentType<ErrorFallbackProps>;
}

export interface ErrorFallbackProps {
  readonly error: AppError;
  readonly resetError: () => void;
  readonly errorInfo?: ErrorInfo;
}

// ==========================================
// LOADING & UI STATES
// ==========================================

export type LoadingState = 'idle' | 'pending' | 'success' | 'error';

export interface AsyncState<T = unknown> {
  readonly data: T | null;
  readonly loading: boolean;
  readonly error: string | null;
  readonly lastUpdated?: string;
}

export interface PaginationState {
  readonly page: number;
  readonly pageSize: number;
  readonly total: number;
  readonly totalPages: number;
  readonly hasNext: boolean;
  readonly hasPrev: boolean;
}

export interface SortState {
  readonly field: string;
  readonly direction: 'asc' | 'desc';
}

export interface FilterState {
  readonly [key: string]: string | number | boolean | string[] | number[] | null;
}

export interface TableState {
  readonly pagination: PaginationState;
  readonly sorting: SortState[];
  readonly filters: FilterState;
  readonly selection: Set<string | number>;
  readonly columnVisibility: Record<string, boolean>;
  readonly columnOrder: string[];
}

// ==========================================
// NOTIFICATIONS & TOASTS
// ==========================================

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Notification {
  readonly id: string;
  readonly type: NotificationType;
  readonly title: string;
  readonly message?: string;
  readonly duration?: number; // ms, 0 = persistant
  readonly actions?: Array<{
    readonly label: string;
    readonly action: () => void;
    readonly variant?: 'default' | 'secondary';
  }>;
  readonly dismissible?: boolean;
  readonly timestamp: string;
}

export interface ToastOptions {
  readonly type?: NotificationType;
  readonly duration?: number;
  readonly position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
  readonly dismissible?: boolean;
}

// ==========================================
// MODALS & DIALOGS
// ==========================================

export interface ModalState {
  readonly isOpen: boolean;
  readonly title?: string;
  readonly content?: React.ReactNode;
  readonly size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  readonly closable?: boolean;
  readonly onClose?: () => void;
  readonly onConfirm?: () => void;
  readonly loading?: boolean;
}

export interface ConfirmDialogOptions {
  readonly title: string;
  readonly message: string;
  readonly confirmText?: string;
  readonly cancelText?: string;
  readonly variant?: 'default' | 'destructive';
  readonly onConfirm: () => void | Promise<void>;
  readonly onCancel?: () => void;
}

// ==========================================
// THEME & STYLING
// ==========================================

export type ThemeMode = 'light' | 'dark' | 'system';

export interface Theme {
  readonly mode: ThemeMode;
  readonly colors: {
    readonly primary: string;
    readonly secondary: string;
    readonly accent: string;
    readonly background: string;
    readonly foreground: string;
    readonly muted: string;
    readonly border: string;
    readonly success: string;
    readonly warning: string;
    readonly error: string;
  };
  readonly typography: {
    readonly fontFamily: string;
    readonly fontSize: Record<string, string>;
    readonly fontWeight: Record<string, number>;
    readonly lineHeight: Record<string, number>;
  };
  readonly spacing: Record<string, string>;
  readonly borderRadius: Record<string, string>;
  readonly shadows: Record<string, string>;
}

// ==========================================
// FORMS & VALIDATION
// ==========================================

export interface FormField<T = unknown> {
  readonly name: string;
  readonly label: string;
  readonly type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea' | 'checkbox' | 'radio' | 'file' | 'date';
  readonly value: T;
  readonly placeholder?: string;
  readonly required?: boolean;
  readonly disabled?: boolean;
  readonly readonly?: boolean;
  readonly options?: Array<{ label: string; value: string | number }>;
  readonly validation?: {
    readonly min?: number;
    readonly max?: number;
    readonly pattern?: RegExp;
    readonly custom?: (value: T) => string | null;
  };
  readonly error?: string;
  readonly touched?: boolean;
}

export interface FormState<T = Record<string, unknown>> {
  readonly values: T;
  readonly errors: Partial<Record<keyof T, string>>;
  readonly touched: Partial<Record<keyof T, boolean>>;
  readonly isValid: boolean;
  readonly isSubmitting: boolean;
  readonly isDirty: boolean;
}

// ==========================================
// SEARCH & FILTERS
// ==========================================

export interface SearchState {
  readonly query: string;
  readonly filters: FilterState;
  readonly sorting: SortState[];
  readonly pagination: PaginationState;
  readonly facets?: Record<string, Array<{ value: string; count: number }>>;
}

export interface SearchResult<T = unknown> {
  readonly items: T[];
  readonly total: number;
  readonly facets?: Record<string, Array<{ value: string; count: number }>>;
  readonly suggestions?: string[];
  readonly query: string;
  readonly executionTime: number;
}

// ==========================================
// FEATURE FLAGS
// ==========================================

export interface FeatureFlag {
  readonly name: string;
  readonly enabled: boolean;
  readonly description?: string;
  readonly rollout?: {
    readonly percentage: number;
    readonly userSegments?: string[];
    readonly conditions?: Record<string, unknown>;
  };
}

export interface FeatureFlagsState {
  readonly flags: Record<string, FeatureFlag>;
  readonly loading: boolean;
  readonly error?: string;
  readonly lastUpdated?: string;
}

// ==========================================
// ANALYTICS & TRACKING
// ==========================================

export interface AnalyticsEvent {
  readonly name: string;
  readonly properties?: Record<string, string | number | boolean>;
  readonly timestamp?: string;
  readonly userId?: number;
  readonly sessionId?: string;
}

export interface PageViewEvent extends AnalyticsEvent {
  readonly name: 'page_view';
  readonly properties: {
    readonly path: string;
    readonly title: string;
    readonly referrer?: string;
    readonly duration?: number;
  };
}

// ==========================================
// PERFORMANCE MONITORING
// ==========================================

export interface PerformanceMetric {
  readonly name: string;
  readonly value: number;
  readonly unit: 'ms' | 'bytes' | 'count' | 'percentage';
  readonly timestamp: string;
  readonly tags?: Record<string, string>;
}

export interface WebVitals {
  readonly FCP?: number; // First Contentful Paint
  readonly LCP?: number; // Largest Contentful Paint
  readonly FID?: number; // First Input Delay
  readonly CLS?: number; // Cumulative Layout Shift
  readonly TTFB?: number; // Time to First Byte
}

// ==========================================
// ACCESSIBILITY
// ==========================================

export interface A11yState {
  readonly highContrast: boolean;
  readonly reducedMotion: boolean;
  readonly fontSize: 'small' | 'medium' | 'large' | 'xl';
  readonly screenReader: boolean;
  readonly focusVisible: boolean;
}

// ==========================================
// DEVICE & BROWSER INFO
// ==========================================

export interface DeviceInfo {
  readonly type: 'desktop' | 'tablet' | 'mobile';
  readonly os: string;
  readonly browser: string;
  readonly version: string;
  readonly viewport: {
    readonly width: number;
    readonly height: number;
  };
  readonly touchSupport: boolean;
  readonly orientation: 'portrait' | 'landscape';
}

// ==========================================
// SESSION & STORAGE
// ==========================================

export interface SessionInfo {
  readonly id: string;
  readonly userId?: number;
  readonly startTime: string;
  readonly lastActivity: string;
  readonly duration: number;
  readonly pageViews: number;
  readonly device: DeviceInfo;
}

export interface StorageState<T = unknown> {
  readonly data: T;
  readonly timestamp: string;
  readonly version: string;
  readonly encrypted?: boolean;
}

// ==========================================
// WEBSOCKET & REAL-TIME
// ==========================================

export interface WebSocketState {
  readonly connected: boolean;
  readonly connecting: boolean;
  readonly lastConnected?: string;
  readonly reconnectAttempts: number;
  readonly error?: string;
}

export interface RealtimeEvent<T = unknown> {
  readonly type: string;
  readonly data: T;
  readonly timestamp: string;
  readonly source: string;
  readonly id?: string;
}