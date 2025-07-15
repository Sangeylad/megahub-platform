// frontend/src/types/global/api.types.ts - Version Finale TypeScript 5.8.3 Enhanced

// 🎯 Types API globaux - TypeScript 5.8.3 enhanced inference selon architecture Django

// ==========================================
// RESPONSES API STANDARDS - Enhanced TypeScript 5.8.3
// ==========================================

export interface ApiResponse<T = unknown> {
  readonly data: T;
  readonly message?: string;
  readonly success: boolean;
  readonly timestamp: string;
  readonly status_code?: number;
}

export interface ApiError {
  readonly message: string;
  readonly code: string;
  readonly details?: Record<string, string[] | string>; // Django form errors
  readonly non_field_errors?: string[];
  readonly timestamp: string;
  readonly status_code?: number;
  readonly request_id?: string;
}

export interface DjangoValidationError {
  readonly [field: string]: string[] | undefined; // Django field errors (optional)
  readonly non_field_errors?: string[];
}

export interface PaginatedResponse<T = unknown> {
  readonly results: T[]; // Django REST pagination utilise 'results'
  readonly count: number; // Total d'items
  readonly next?: string | null; // URL page suivante
  readonly previous?: string | null; // URL page précédente
  readonly page_size?: number;
  readonly num_pages?: number;
}

// Version simplifiée pour frontend
export interface SimplePaginatedResponse<T = unknown> {
  readonly data: T[];
  readonly pagination: {
    readonly page: number;
    readonly limit: number;
    readonly total: number;
    readonly totalPages: number;
    readonly hasNext: boolean;
    readonly hasPrev: boolean;
  };
}

// ==========================================
// API CLIENT ERROR TYPES - Enhanced TypeScript 5.8.3 Strict
// ==========================================

export interface ApiClientError extends Error {
  readonly isApiError: true;
  readonly status_code?: number;
  readonly response?: {
    readonly data?: unknown;
    readonly status: number;
    readonly headers: Record<string, string>;
  };
  readonly request?: {
    readonly url: string;
    readonly method: string;
    readonly headers: Record<string, string>;
  };
}

export interface NetworkError extends Error {
  readonly isNetworkError: true;
  readonly code: 'NETWORK_ERROR' | 'TIMEOUT_ERROR' | 'ABORT_ERROR';
  readonly originalError?: Error;
}

// ==========================================
// API REQUEST CONFIGURATION
// ==========================================

export interface ApiRequestConfig {
  readonly timeout?: number;
  readonly retries?: number;
  readonly cache?: boolean;
  readonly headers?: Record<string, string>;
  readonly params?: Record<string, string | number | boolean>;
  readonly signal?: AbortSignal; // Pour annulation requêtes
}

export interface ApiRequestOptions extends ApiRequestConfig {
  readonly method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  readonly data?: unknown;
  readonly url: string;
}

// ==========================================
// TANSTACK QUERY V5 TYPES
// ==========================================

export interface QueryOptions {
  readonly staleTime?: number;
  readonly gcTime?: number; // v5: gcTime remplace cacheTime
  readonly retry?: number | boolean | ((failureCount: number, error: Error) => boolean);
  readonly retryDelay?: number | ((retryAttempt: number) => number);
  readonly refetchOnWindowFocus?: boolean;
  readonly refetchOnReconnect?: boolean;
  readonly refetchInterval?: number | false;
  readonly enabled?: boolean;
  readonly suspense?: boolean; // v5: Support natif Suspense
  readonly throwOnError?: boolean; // v5: Enhanced error handling
  readonly select?: <TData>(data: unknown) => TData; // Transform data
}

export interface MutationOptions<TData = unknown, TError = ApiError, TVariables = unknown> {
  readonly retry?: number | boolean;
  readonly retryDelay?: number;
  readonly onSuccess?: (data: TData, variables: TVariables) => void;
  readonly onError?: (error: TError, variables: TVariables) => void;
  readonly onSettled?: (data: TData | undefined, error: TError | null, variables: TVariables) => void;
  readonly onMutate?: (variables: TVariables) => Promise<unknown> | unknown;
  readonly throwOnError?: boolean;
}

export interface InfiniteQueryOptions extends QueryOptions {
  readonly getNextPageParam?: (lastPage: unknown, allPages: unknown[]) => unknown;
  readonly getPreviousPageParam?: (firstPage: unknown, allPages: unknown[]) => unknown;
  readonly maxPages?: number;
}

// ==========================================
// QUERY KEYS FACTORY PATTERN
// ==========================================

export type QueryKey = readonly (string | number | boolean | object)[];

export interface BaseQueryKeys {
  readonly all: QueryKey;
  readonly lists: () => QueryKey;
  readonly list: (filters?: Record<string, unknown>) => QueryKey;
  readonly details: () => QueryKey;
  readonly detail: (id: string | number) => QueryKey;
}

// ==========================================
// REQUEST OPTIONS - Enhanced for TypeScript 5.8.3
// ==========================================

export interface RequestOptions {
  readonly signal?: AbortSignal;
  readonly timeout?: number;
  readonly retries?: number;
  readonly retryDelay?: number;
  readonly skipAuth?: boolean;
  readonly skipCache?: boolean;
  readonly headers?: Record<string, string>;
}

// ==========================================
// PAGINATION TYPES
// ==========================================

export interface PaginationParams {
  readonly page?: number;
  readonly limit?: number;
  readonly offset?: number;
  readonly search?: string;
  readonly sort?: string;
  readonly order?: 'asc' | 'desc';
}

// ==========================================
// FILE UPLOAD TYPES
// ==========================================

export interface FileUploadOptions {
  readonly maxSize?: number; // bytes
  readonly allowedTypes?: string[]; // MIME types
  readonly multiple?: boolean;
  readonly onProgress?: (progress: number) => void;
}

export interface FileUploadResponse {
  readonly id: string;
  readonly filename: string;
  readonly size: number;
  readonly type: string;
  readonly url: string;
  readonly created_at: string;
}

export interface FileUploadProgress {
  readonly loaded: number;
  readonly total: number;
  readonly percentage: number;
}

// ==========================================
// SEARCH & FILTER TYPES
// ==========================================

export interface SearchParams {
  readonly query?: string;
  readonly filters?: Record<string, unknown>;
  readonly facets?: string[];
  readonly highlight?: boolean;
}

export interface SearchResponse<T> extends ApiResponse<T[]> {
  readonly meta: {
    readonly query: string;
    readonly took: number;
    readonly total: number;
    readonly facets?: Record<string, Array<{ value: string; count: number }>>;
  };
}

// ==========================================
// CONSTANTS
// ==========================================

export const HTTP_STATUS = {
  // Success
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,

  // Client errors
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,

  // Server errors
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

export type HttpStatusCode = typeof HTTP_STATUS[keyof typeof HTTP_STATUS];

export const ERROR_CODES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  ABORT_ERROR: 'ABORT_ERROR',
  PARSE_ERROR: 'PARSE_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  NOT_FOUND_ERROR: 'NOT_FOUND_ERROR',
  CONFLICT_ERROR: 'CONFLICT_ERROR',
  RATE_LIMIT_ERROR: 'RATE_LIMIT_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];

// ==========================================
// REQUEST METHODS
// ==========================================

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';

// ==========================================
// COMMON FILTERS & SORTING
// ==========================================

export interface BaseFilters {
  readonly page?: number;
  readonly page_size?: number;
  readonly ordering?: string; // Django ordering format: 'field' ou '-field'
  readonly search?: string;
}

export interface DateRangeFilter {
  readonly created_at__gte?: string; // ISO date
  readonly created_at__lte?: string; // ISO date
  readonly updated_at__gte?: string;
  readonly updated_at__lte?: string;
}

export interface BooleanFilters {
  readonly is_active?: boolean;
  readonly is_deleted?: boolean;
}

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  readonly field: string;
  readonly direction: SortDirection;
}

// ==========================================
// API ENDPOINTS CONFIGURATION
// ==========================================

export interface ApiEndpoint {
  readonly url: string;
  readonly method: HttpMethod;
  readonly description?: string;
  readonly auth_required?: boolean;
  readonly rate_limit?: number;
}

export interface ApiEndpoints {
  readonly [key: string]: ApiEndpoint | ApiEndpoints;
}

// ==========================================
// WEBSOCKET TYPES
// ==========================================

export interface WebSocketMessage<T = unknown> {
  readonly type: string;
  readonly data: T;
  readonly timestamp: string;
  readonly id?: string;
}

export interface WebSocketConfig {
  readonly url: string;
  readonly protocols?: string[];
  readonly retry?: boolean;
  readonly retryInterval?: number;
  readonly maxRetries?: number;
}

// ==========================================
// CACHE STRATEGIES
// ==========================================

export type CacheStrategy =
  | 'cache-first'    // Cache puis réseau si pas en cache
  | 'network-first'  // Réseau puis cache si échec
  | 'cache-only'     // Cache uniquement
  | 'network-only'   // Réseau uniquement
  | 'stale-while-revalidate'; // Cache + revalidation background

export interface CacheConfig {
  readonly strategy: CacheStrategy;
  readonly ttl?: number; // Time to live en ms
  readonly key?: string; // Clé de cache personnalisée
  readonly enabled?: boolean;
  readonly maxSize?: number;
}

export interface CacheEntry<T> {
  readonly data: T;
  readonly timestamp: number;
  readonly ttl: number;
  readonly key: string;
}

// ==========================================
// API CLIENT CONFIGURATION
// ==========================================

export interface ApiClientConfig {
  readonly baseURL: string;
  readonly timeout: number;
  readonly headers: Record<string, string>;
  readonly retries: number;
  readonly retryDelay: number;
  readonly interceptors?: {
    readonly request?: Array<(config: ApiRequestConfig) => ApiRequestConfig>;
    readonly response?: Array<(response: unknown) => unknown>;
    readonly error?: Array<(error: ApiError) => Promise<unknown> | unknown>;
  };
}

// ==========================================
// BULK OPERATIONS
// ==========================================

export interface BulkOperation<T = unknown> {
  readonly action: 'create' | 'update' | 'delete';
  readonly items: T[];
  readonly options?: {
    readonly batch_size?: number;
    readonly continue_on_error?: boolean;
  };
}

export interface BulkOperationResponse<T = unknown> {
  readonly success_count: number;
  readonly error_count: number;
  readonly results: Array<{
    readonly item: T;
    readonly status: 'success' | 'error';
    readonly error?: string;
  }>;
}

// ==========================================
// ANALYTICS & METRICS
// ==========================================

export interface ApiMetrics {
  readonly request_count: number;
  readonly average_response_time: number;
  readonly error_rate: number;
  readonly success_rate: number;
  readonly last_request?: string;
}

export interface PerformanceMetrics {
  readonly start_time: number;
  readonly end_time: number;
  readonly duration: number;
  readonly endpoint: string;
  readonly method: HttpMethod;
  readonly status_code: HttpStatusCode;
  readonly cache_hit?: boolean;
}

// ==========================================
// HEALTH CHECK
// ==========================================

export interface HealthCheckResponse {
  readonly status: 'healthy' | 'degraded' | 'unhealthy';
  readonly timestamp: string;
  readonly version: string;
  readonly uptime: number;
  readonly checks: Record<string, {
    readonly status: boolean;
    readonly response_time: number;
    readonly error?: string;
  }>;
}

// ==========================================
// FEATURE FLAGS
// ==========================================

export interface FeatureFlag {
  readonly name: string;
  readonly enabled: boolean;
  readonly description?: string;
  readonly rollout_percentage?: number;
  readonly conditions?: Record<string, unknown>;
}

export interface FeatureFlagsResponse {
  readonly flags: Record<string, FeatureFlag>;
  readonly user_segment?: string;
  readonly updated_at: string;
}

// ==========================================
// UTILITY TYPES - Enhanced TypeScript 5.8.3
// ==========================================

// Type pour les réponses qui peuvent être data directement ou wrapped
export type ApiResponseOrDirect<T> = T | ApiResponse<T>;

// Type pour extraire le type de data d'une ApiResponse
export type ExtractApiData<T> = T extends ApiResponse<infer U> ? U : T;

// Type pour les endpoints API
export interface ApiEndpointConfig<TRequest = void, TResponse = unknown> {
  readonly method: HttpMethod;
  readonly path: string;
  readonly authenticated?: boolean;
  readonly timeout?: number;
  readonly retries?: number;
}

// ==========================================
// ERROR HANDLING TYPES - Enhanced
// ==========================================

export type ErrorHandler = (error: ApiError | NetworkError) => void;

export interface ErrorHandlerConfig {
  readonly global?: ErrorHandler;
  readonly byStatus?: Record<number, ErrorHandler>;
  readonly byCode?: Record<string, ErrorHandler>;
  readonly fallback?: ErrorHandler;
}

// ==========================================
// TYPE GUARDS - TypeScript 5.8.3 Strict
// ==========================================

export function isApiError(error: unknown): error is ApiError {
  return typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'code' in error &&
    'timestamp' in error;
}

export function isNetworkError(error: unknown): error is NetworkError {
  return typeof error === 'object' &&
    error !== null &&
    'isNetworkError' in error &&
    (error as NetworkError).isNetworkError === true;
}

export function isApiResponse<T>(value: unknown): value is ApiResponse<T> {
  return typeof value === 'object' &&
    value !== null &&
    'data' in value &&
    'success' in value;
}

export function isDjangoValidationError(error: unknown): error is DjangoValidationError {
  return typeof error === 'object' &&
    error !== null &&
    (('non_field_errors' in error) ||
      Object.keys(error).some(key => Array.isArray((error as any)[key])));
}

// ==========================================
// ERROR HANDLING UTILITIES - TypeScript 5.8.3
// ==========================================

/**
 * Type-safe error normalization for unknown catch blocks
 */
export function normalizeError(error: unknown): ApiError {
  // Si c'est déjà une ApiError
  if (isApiError(error)) {
    return error;
  }

  // Si c'est une Error standard
  if (error instanceof Error) {
    return {
      message: error.message,
      code: 'UNKNOWN_ERROR',
      timestamp: new Date().toISOString(),
    };
  }

  // Si c'est un objet avec message
  if (typeof error === 'object' && error !== null && 'message' in error) {
    return {
      message: String(error.message),
      code: 'UNKNOWN_ERROR',
      timestamp: new Date().toISOString(),
    };
  }

  // Fallback pour types primitifs
  return {
    message: String(error || 'Une erreur inconnue est survenue'),
    code: 'UNKNOWN_ERROR',
    timestamp: new Date().toISOString(),
  };
}

/**
 * Type-safe status code checking
 */
export function hasStatusCode(error: unknown): error is { status_code: number } {
  return typeof error === 'object' &&
    error !== null &&
    'status_code' in error &&
    typeof (error as any).status_code === 'number';
}

/**
 * Enhanced retry condition checking
 */
export function shouldRetryRequest(error: unknown, attempt: number, maxRetries: number): boolean {
  if (attempt >= maxRetries) return false;

  // Ne pas retry sur les erreurs client (4xx sauf 401)
  if (hasStatusCode(error)) {
    const statusCode = error.status_code;
    return !(statusCode >= 400 && statusCode < 500 && statusCode !== 401);
  }

  // Retry sur les erreurs réseau
  if (isNetworkError(error)) {
    return true;
  }

  // Retry par défaut sur les erreurs inconnues
  return true;
}