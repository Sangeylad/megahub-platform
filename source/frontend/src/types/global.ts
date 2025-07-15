// frontend/src/types/global.ts
export interface ApiResponse<T = unknown> {
  readonly data: T;
  readonly success?: boolean;
  readonly message?: string;
  readonly timestamp?: string;
  readonly version?: string;
  readonly request_id?: string;
}

export interface ApiError {
  readonly message: string;
  readonly code: string;
  readonly details?: Record<string, string[]>;
  readonly non_field_errors?: string[];
  readonly field_errors?: Record<string, string[]>;
  readonly timestamp: string;
  readonly status_code?: number;
  readonly request_id?: string;
  readonly trace_id?: string;
}

export interface AppError extends ApiError {
  readonly type: 'validation' | 'network' | 'auth' | 'permission' | 'server' | 'client';
  readonly recoverable: boolean;
  readonly retry_after?: number;
  readonly context?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  readonly results: T[];
  readonly count: number;
  readonly next: string | null;
  readonly previous: string | null;
  readonly page_size: number;
  readonly current_page: number;
  readonly total_pages: number;
  readonly has_next: boolean;
  readonly has_previous: boolean;
}

export interface PaginationParams {
  readonly page?: number;
  readonly page_size?: number;
  readonly limit?: number;
  readonly offset?: number;
}

export interface PaginationState {
  readonly page: number;
  readonly pageSize: number;
  readonly total: number;
  readonly totalPages: number;
  readonly hasNext: boolean;
  readonly hasPrev: boolean;
}

export interface QueryParams extends PaginationParams {
  readonly search?: string;
  readonly ordering?: string;
  readonly filters?: Record<string, string | number | boolean | string[]>;
  readonly include?: string[];
  readonly exclude?: string[];
  readonly fields?: string[];
}

export interface QueryOptions {
  readonly enabled?: boolean;
  readonly staleTime?: number;
  readonly gcTime?: number;
  readonly retry?: number | boolean;
  readonly retryDelay?: number;
  readonly refetchOnMount?: boolean;
  readonly refetchOnWindowFocus?: boolean;
  readonly refetchOnReconnect?: boolean;
  readonly refetchInterval?: number;
  readonly suspense?: boolean;
  readonly select?: (data: unknown) => unknown;
  readonly onSuccess?: (data: unknown) => void;
  readonly onError?: (error: unknown) => void;
}

export interface MutationOptions {
  readonly retry?: number | boolean;
  readonly retryDelay?: number;
  readonly onSuccess?: (data: unknown, variables: unknown) => void;
  readonly onError?: (error: unknown, variables: unknown) => void;
  readonly onSettled?: (data: unknown, error: unknown, variables: unknown) => void;
  readonly onMutate?: (variables: unknown) => void;
}

export interface SortOption {
  readonly field: string;
  readonly direction: 'asc' | 'desc';
  readonly label: string;
}

export interface FilterOption {
  readonly key: string;
  readonly value: string | number | boolean;
  readonly label: string;
  readonly type: 'text' | 'number' | 'boolean' | 'date' | 'select' | 'multiselect';
  readonly options?: { label: string; value: string | number }[];
}

export interface SortState {
  readonly field: string;
  readonly direction: 'asc' | 'desc';
}

export interface FilterState {
  readonly [key: string]: string | number | boolean | string[] | number[] | null;
}

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'OPTIONS' | 'HEAD';

export interface ApiRequestConfig {
  readonly method?: HttpMethod;
  readonly headers?: Record<string, string>;
  readonly params?: Record<string, unknown>;
  readonly data?: unknown;
  readonly timeout?: number;
  readonly retry?: number;
  readonly retryDelay?: number;
  readonly signal?: AbortSignal;
}

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T = unknown, E = ApiError> {
  readonly data: T | null;
  readonly error: E | null;
  readonly loading: boolean;
  readonly loaded: boolean;
  readonly lastFetch: number | null;
}

export interface RequestState {
  readonly isPending: boolean;
  readonly isLoading: boolean;
  readonly isFetching: boolean;
  readonly isSuccess: boolean;
  readonly isError: boolean;
  readonly isStale: boolean;
  readonly dataUpdatedAt: number;
  readonly errorUpdatedAt: number;
  readonly fetchStatus: 'fetching' | 'paused' | 'idle';
}

export type ThemeMode = 'light' | 'dark' | 'system';

export type NotificationType = 'success' | 'error' | 'warning' | 'info' | 'loading';

export interface Notification {
  readonly id: string;
  readonly type: NotificationType;
  readonly title: string;
  readonly message?: string;
  readonly duration?: number;
  readonly persistent?: boolean;
  readonly actions?: NotificationAction[];
  readonly metadata?: Record<string, unknown>;
  readonly timestamp: number;
}

export interface NotificationAction {
  readonly label: string;
  readonly action: () => void;
  readonly style?: 'primary' | 'secondary' | 'danger';
}

export interface Theme {
  readonly mode: ThemeMode;
  readonly colors: Record<string, string>;
  readonly fonts: Record<string, string>;
  readonly spacing: Record<string, string>;
  readonly breakpoints: Record<string, string>;
}

export interface UIState {
  readonly theme: ThemeMode;
  readonly sidebar: {
    readonly collapsed: boolean;
    readonly mobile: boolean;
  };
  readonly modal: {
    readonly stack: string[];
    readonly backdrop: boolean;
  };
  readonly loading: {
    readonly global: boolean;
    readonly components: Record<string, boolean>;
  };
}

export interface NavigationItem {
  readonly id: string;
  readonly label: string;
  readonly path: string;
  readonly icon?: string;
  readonly badge?: string | number;
  readonly children?: NavigationItem[];
  readonly permissions?: string[];
  readonly exact?: boolean;
  readonly external?: boolean;
  readonly disabled?: boolean;
}

export interface BreadcrumbItem {
  readonly label: string;
  readonly path?: string;
  readonly active?: boolean;
}

export interface RouteParams {
  readonly [key: string]: string | undefined;
}

export interface SearchParams {
  readonly [key: string]: string | string[] | undefined;
}

export type Environment = 'development' | 'staging' | 'production' | 'test';

export interface AppConfig {
  readonly api: {
    readonly baseUrl: string;
    readonly timeout: number;
    readonly retries: number;
  };
  readonly features: {
    readonly analytics: boolean;
    readonly notifications: boolean;
    readonly realtime: boolean;
    readonly offline: boolean;
  };
  readonly ui: {
    readonly theme: ThemeMode;
    readonly language: string;
    readonly timezone: string;
  };
  readonly security: {
    readonly csrfProtection: boolean;
    readonly rateLimiting: boolean;
    readonly sessionTimeout: number;
  };
}

export interface EnvironmentInfo {
  readonly name: Environment;
  readonly debug: boolean;
  readonly version: string;
  readonly buildDate: string;
  readonly commitHash: string;
}

export interface FileMetadata {
  readonly name: string;
  readonly size: number;
  readonly type: string;
  readonly lastModified: number;
  readonly extension: string;
  readonly checksum?: string;
}

export interface UploadProgress {
  readonly file: FileMetadata;
  readonly progress: number;
  readonly status: 'pending' | 'uploading' | 'success' | 'error' | 'cancelled';
  readonly error?: string;
  readonly url?: string;
  readonly uploadId: string;
}

export interface SearchResult<T = unknown> {
  readonly id: string | number;
  readonly title: string;
  readonly description?: string;
  readonly url?: string;
  readonly type: string;
  readonly score: number;
  readonly highlight?: Record<string, string[]>;
  readonly data: T;
}

export interface SearchResponse<T = unknown> {
  readonly results: SearchResult<T>[];
  readonly total: number;
  readonly query: string;
  readonly filters: Record<string, unknown>;
  readonly facets?: Record<string, Array<{ value: string; count: number }>>;
  readonly suggestions?: string[];
  readonly took: number;
}

export interface FieldError {
  readonly field: string;
  readonly code: string;
  readonly message: string;
  readonly params?: Record<string, unknown>;
}

export interface FormError {
  readonly field?: string;
  readonly code: string;
  readonly message: string;
  readonly type: 'field' | 'non_field' | 'form';
}

export interface ValidationResult {
  readonly valid: boolean;
  readonly errors: FieldError[];
  readonly warnings?: FieldError[];
}

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

export type Maybe<T> = T | null | undefined;
export type Optional<T> = T | undefined;
export type Nullable<T> = T | null;

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

export type KeysOfType<T, U> = {
  [K in keyof T]: T[K] extends U ? K : never;
}[keyof T];

export type Mutable<T> = {
  -readonly [P in keyof T]: T[P];
};

export type Brand<T, B> = T & { readonly __brand: B };

export type PromiseValue<T> = T extends Promise<infer U> ? U : T;

export type AsyncReturnType<T extends (...args: any) => Promise<any>> = 
  T extends (...args: any) => Promise<infer R> ? R : never;

export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
} as const;

export const LOADING_STATES = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
} as const;

export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
  LOADING: 'loading',
} as const;

export const THEME_MODES = {
  LIGHT: 'light',
  DARK: 'dark',
  SYSTEM: 'system',
} as const;

export const DEFAULT_PAGINATION = {
  page: 1,
  page_size: 20,
  limit: 20,
  offset: 0,
} as const;

export const DEFAULT_SORT = {
  field: 'created_at',
  direction: 'desc',
} as const;

export const DEFAULT_QUERY_OPTIONS: QueryOptions = {
  staleTime: 5 * 60 * 1000,
  gcTime: 10 * 60 * 1000,
  retry: 3,
  refetchOnWindowFocus: false,
  refetchOnMount: true,
  refetchOnReconnect: true,
} as const;

export const isApiError = (error: unknown): error is ApiError => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'code' in error
  );
};

export const isAppError = (error: unknown): error is AppError => {
  return (
    isApiError(error) &&
    'type' in error &&
    'recoverable' in error
  );
};

export const isPaginatedResponse = <T>(data: unknown): data is PaginatedResponse<T> => {
  return (
    typeof data === 'object' &&
    data !== null &&
    'results' in data &&
    'count' in data &&
    Array.isArray((data as any).results)
  );
};

export const isDevelopment = (): boolean => {
  return import.meta.env.MODE === 'development';
};

export const isProduction = (): boolean => {
  return import.meta.env.MODE === 'production';
};

export const isTest = (): boolean => {
  return import.meta.env.MODE === 'test';
};

export const getEnvironment = (): Environment => {
  return (import.meta.env.MODE as Environment) || 'development';
};
