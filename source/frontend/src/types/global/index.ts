// frontend/src/types/global/index.ts

// 🎯 Barrel exports types globaux - Standards Leaders TypeScript 5.8.3

// ==========================================
// IMPORTS FROM LOCAL MODULES
// ==========================================

import type {
  ApiResponse,
  ApiError,
  DjangoValidationError,
  PaginatedResponse,
  SimplePaginatedResponse,
  ApiRequestConfig,
  ApiRequestOptions,
  QueryOptions,
  MutationOptions,
  InfiniteQueryOptions,
  QueryKey,
  BaseQueryKeys,
  HttpMethod,
  HttpStatusCode,
  BaseFilters,
  DateRangeFilter,
  BooleanFilters,
  SortDirection,
  SortConfig,
  ApiEndpoint,
  ApiEndpoints,
  FileUploadOptions,
  FileUploadResponse,
  WebSocketMessage,
  WebSocketConfig,
  CacheStrategy,
  CacheConfig,
  ApiClientConfig,
  BulkOperation,
  BulkOperationResponse,
  ApiMetrics,
  PerformanceMetrics,
  HealthCheckResponse,
  FeatureFlag as ApiFeatureFlag,
  FeatureFlagsResponse,
} from './api.types';

import { HTTP_STATUS } from './api.types';

import type {
  User,
  AuthTokens,
  AppConfig,
  Environment,
  NavigationItem,
  Breadcrumb,
  RouteMetadata,
  ErrorInfo,
  AppError,
  ErrorBoundaryState,
  ErrorFallbackProps,
  LoadingState,
  AsyncState,
  PaginationState,
  SortState,
  FilterState,
  TableState,
  NotificationType,
  Notification,
  ToastOptions,
  ModalState,
  ConfirmDialogOptions,
  ThemeMode,
  Theme,
  FormField,
  FormState,
  SearchState,
  SearchResult,
  FeatureFlag,
  FeatureFlagsState,
  AnalyticsEvent,
  PageViewEvent,
  PerformanceMetric,
  WebVitals,
  A11yState,
  DeviceInfo,
  SessionInfo,
  StorageState,
  WebSocketState,
  RealtimeEvent,
} from './app.types';

// ==========================================
// API TYPES - Core infrastructure
// ==========================================

export type {
  // Core API responses
  ApiResponse,
  ApiError,
  DjangoValidationError,
  PaginatedResponse,
  SimplePaginatedResponse,
  
  // Request configuration
  ApiRequestConfig,
  ApiRequestOptions,
  
  // TanStack Query v5 types
  QueryOptions,
  MutationOptions,
  InfiniteQueryOptions,
  QueryKey,
  BaseQueryKeys,
  
  // HTTP types
  HttpMethod,
  HttpStatusCode,
  
  // Filters & Sorting
  BaseFilters,
  DateRangeFilter,
  BooleanFilters,
  SortDirection,
  SortConfig,
  
  // Advanced API features
  ApiEndpoint,
  ApiEndpoints,
  FileUploadOptions,
  FileUploadResponse,
  WebSocketMessage,
  WebSocketConfig,
  CacheStrategy,
  CacheConfig,
  ApiClientConfig,
  BulkOperation,
  BulkOperationResponse,
  ApiMetrics,
  PerformanceMetrics,
  HealthCheckResponse,
  ApiFeatureFlag,
  FeatureFlagsResponse,
};

// Export constants
export { HTTP_STATUS };

// ==========================================
// APPLICATION TYPES - Core app logic
// ==========================================

export type {
  // Core user & auth (for global usage)
  User,
  AuthTokens,
  AppConfig,
  Environment,
  
  // Navigation & Routing
  NavigationItem,
  Breadcrumb,
  RouteMetadata,
  
  // Error handling React 19
  ErrorInfo,
  AppError,
  ErrorBoundaryState,
  ErrorFallbackProps,
  
  // UI States & Loading
  LoadingState,
  AsyncState,
  PaginationState,
  SortState,
  FilterState,
  TableState,
  
  // Notifications & Toasts
  NotificationType,
  Notification,
  ToastOptions,
  
  // Modals & Dialogs
  ModalState,
  ConfirmDialogOptions,
  
  // Theme & Styling
  ThemeMode,
  Theme,
  
  // Forms & Validation
  FormField,
  FormState,
  
  // Search & Filtering
  SearchState,
  SearchResult,
  
  // Feature flags (app level)
  FeatureFlag,
  FeatureFlagsState,
  
  // Analytics & Tracking
  AnalyticsEvent,
  PageViewEvent,
  
  // Performance Monitoring
  PerformanceMetric,
  WebVitals,
  
  // Accessibility
  A11yState,
  
  // Device & Browser
  DeviceInfo,
  SessionInfo,
  StorageState,
  
  // WebSocket & Real-time
  WebSocketState,
  RealtimeEvent,
};

// ==========================================
// COMMONLY USED TYPE UTILITIES
// ==========================================

// Enhanced conditional types TypeScript 5.8.3
export type NonNullable<T> = T extends null | undefined ? never : T;
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type StrictRequired<T, K extends keyof T> = T & Required<Pick<T, K>>; // Renamed to avoid conflict
export type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

// API response transformation utilities
export type Unwrap<T> = T extends ApiResponse<infer U> ? U : T;
export type PaginatedData<T> = T extends PaginatedResponse<infer U> ? U : never;

// Form utilities
export type FormValues<T> = T extends FormState<infer U> ? U : never;
export type FormErrors<T> = Partial<Record<keyof T, string>>;

// Query key utilities
export type QueryKeyFactory<T extends Record<string, (...args: any[]) => QueryKey>> = {
  readonly [K in keyof T]: T[K];
};

// ==========================================
// BRANDED TYPES for Type Safety
// ==========================================

declare const __brand: unique symbol;
type Brand<T, B> = T & { readonly [__brand]: B };

// Branded IDs for type safety
export type UserId = Brand<number, 'UserId'>;
export type CompanyId = Brand<number, 'CompanyId'>;
export type BrandId = Brand<number, 'BrandId'>;
export type RoleId = Brand<number, 'RoleId'>;
export type PermissionId = Brand<number, 'PermissionId'>;

// Branded strings
export type Email = Brand<string, 'Email'>;
export type Username = Brand<string, 'Username'>;
export type Url = Brand<string, 'Url'>;
export type IsoDate = Brand<string, 'IsoDate'>;
export type JwtToken = Brand<string, 'JwtToken'>;

// ==========================================
// RESULT TYPE for Error Handling
// ==========================================

export type Result<T, E = ApiError> = 
  | { readonly success: true; readonly data: T }
  | { readonly success: false; readonly error: E };

export type AsyncResult<T, E = ApiError> = Promise<Result<T, E>>;

// ==========================================
// COMPONENT PROP UTILITIES
// ==========================================

// React 19 component props extraction
export type ComponentProps<T> = T extends React.ComponentType<infer P> ? P : never;

// Extract ref type from component
export type ComponentRef<T> = T extends React.ForwardRefExoticComponent<
  React.RefAttributes<infer R>
> ? R : never;

// ==========================================
// EVENT HANDLER TYPES
// ==========================================

export type EventHandler<T = Event> = (event: T) => void;
export type AsyncEventHandler<T = Event> = (event: T) => Promise<void>;
export type ClickHandler = EventHandler<React.MouseEvent>;
export type ChangeHandler = EventHandler<React.ChangeEvent<HTMLInputElement>>;
export type SubmitHandler = EventHandler<React.FormEvent>;

// ==========================================
// VALIDATION UTILITIES
// ==========================================

export interface Validator<T> {
  readonly validate: (value: unknown) => Result<T, string>;
  readonly schema?: unknown; // Pour intégration Zod
}

export type ValidationSchema<T> = Record<keyof T, Validator<T[keyof T]>>;

// ==========================================
// STORE/STATE MANAGEMENT TYPES
// ==========================================

export interface StoreSlice<T> {
  readonly state: T;
  readonly actions: Record<string, (...args: any[]) => void>;
  readonly selectors?: Record<string, (state: T) => unknown>;
}

export type StoreState<T extends Record<string, StoreSlice<any>>> = {
  readonly [K in keyof T]: T[K]['state'];
};

// ==========================================
// UTILITY TYPES FOR API INTEGRATION
// ==========================================

// Extract endpoint response type
export type EndpointResponse<T> = T extends (...args: any[]) => Promise<infer R> 
  ? R extends ApiResponse<infer U> 
    ? U 
    : R 
  : never;

// Extract mutation variables type
export type MutationVariables<T> = T extends (variables: infer V) => any ? V : never;

// ==========================================
// THEME SYSTEM TYPES
// ==========================================

export type ThemeToken = `var(--${string})`;
export type TailwindClass = `${string}`;
export type CssValue = string | number | ThemeToken;

// ==========================================
// COMMONLY USED CONSTANTS
// ==========================================

export const LOADING_STATES = {
  IDLE: 'idle',
  PENDING: 'pending', 
  SUCCESS: 'success',
  ERROR: 'error',
} as const;

export const NOTIFICATION_TYPES = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error',
} as const;

export const THEME_MODES = {
  LIGHT: 'light',
  DARK: 'dark',
  SYSTEM: 'system',
} as const;

// ==========================================
// TYPE GUARDS
// ==========================================

export const isApiError = (error: unknown): error is ApiError => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'code' in error
  );
};

export const isAppError = (error: unknown): error is AppError => {
  return error instanceof Error && 'code' in error;
};

export const isPaginatedResponse = <T>(
  response: unknown
): response is PaginatedResponse<T> => {
  return (
    typeof response === 'object' &&
    response !== null &&
    'results' in response &&
    'count' in response
  );
};

export const isUser = (user: unknown): user is User => {
  return (
    typeof user === 'object' &&
    user !== null &&
    'id' in user &&
    'email' in user &&
    'username' in user
  );
};

// ==========================================
// DEFAULT VALUES
// ==========================================

export const DEFAULT_PAGINATION: PaginationState = {
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0,
  hasNext: false,
  hasPrev: false,
};

export const DEFAULT_SORT: SortState = {
  field: 'created_at',
  direction: 'desc',
};

export const DEFAULT_QUERY_OPTIONS: QueryOptions = {
  staleTime: 5 * 60 * 1000, // 5 minutes
  gcTime: 10 * 60 * 1000, // 10 minutes (v5)
  retry: 3,
  refetchOnWindowFocus: false,
  throwOnError: false,
};

// ==========================================
// ENVIRONMENT HELPERS
// ==========================================

export const isDevelopment = (): boolean => 
  import.meta.env.MODE === 'development';

export const isProduction = (): boolean => 
  import.meta.env.MODE === 'production';

export const isTest = (): boolean => 
  import.meta.env.MODE === 'test';