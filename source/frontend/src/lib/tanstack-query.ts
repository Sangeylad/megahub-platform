// frontend/src/lib/tanstack-query.ts
import { QueryClient, DefaultOptions } from '@tanstack/react-query';
import type { ApiError } from '@/types';

const queryConfig: DefaultOptions = {
  queries: {
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: (failureCount: number, error: unknown) => {
      if (isApiError(error) && error.status_code && error.status_code >= 400 && error.status_code < 500) {
        return false;
      }
      return failureCount < 3;
    },
    retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
    refetchOnMount: true,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
    throwOnError: false,
    structuralSharing: true,
    networkMode: 'online',
  },
  mutations: {
    retry: (failureCount: number, error: unknown) => {
      if (isApiError(error) && error.status_code && error.status_code >= 400 && error.status_code < 500) {
        return false;
      }
      return failureCount < 1;
    },
    retryDelay: 1000,
    networkMode: 'online',
  },
};

export const queryClient = new QueryClient({
  defaultOptions: queryConfig,
});

queryClient.getQueryCache().config.onError = (error, query) => {
  console.error('Query Error:', { error, queryKey: query.queryKey });
  
  if (isApiError(error) && error.status_code && error.status_code >= 500) {
    reportQueryError('Query failed with server error', { error, queryKey: query.queryKey });
  }
  
  if (isApiError(error) && error.status_code === 401) {
    window.dispatchEvent(new CustomEvent('auth:unauthorized', { detail: { error } }));
  }
};

queryClient.getMutationCache().config.onError = (error, variables, context, mutation) => {
  console.error('Mutation Error:', { error, variables, mutationKey: mutation.options.mutationKey });
  
  if (isApiError(error)) {
    reportQueryError('Mutation failed', { 
      error, 
      variables, 
      mutationKey: mutation.options.mutationKey 
    });
  }
};

queryClient.getQueryCache().config.onSuccess = (data, query) => {
  if (import.meta.env.MODE === 'development') {
    console.log('Query Success:', { queryKey: query.queryKey, data });
  }
};

queryClient.getMutationCache().config.onSuccess = (data, variables, context, mutation) => {
  if (import.meta.env.MODE === 'development') {
    console.log('Mutation Success:', { 
      mutationKey: mutation.options.mutationKey, 
      data, 
      variables 
    });
  }
};

function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'code' in error
  );
}

function reportQueryError(...args: unknown[]): void {
  if (typeof window !== 'undefined' && 'navigator' in window) {
    try {
      fetch('/api/monitoring/query-error/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href,
          args: args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
          ),
        }),
      }).catch(() => {});
    } catch {}
  }
}

export const invalidateAuthQueries = () => {
  queryClient.invalidateQueries({ queryKey: ['auth'] });
};

export const invalidateUserQueries = () => {
  queryClient.invalidateQueries({ queryKey: ['auth', 'user'] });
};

export const invalidatePagesQueries = () => {
  queryClient.invalidateQueries({ queryKey: ['pages'] });
};

export const invalidateAllQueries = () => {
  queryClient.invalidateQueries();
};

export const prefetchUser = () => {
  return queryClient.prefetchQuery({
    queryKey: ['auth', 'user'],
    queryFn: () => Promise.resolve(null),
    staleTime: 5 * 60 * 1000,
  });
};

export const clearQueryCache = () => {
  queryClient.clear();
};

export const removeAuthQueries = () => {
  queryClient.removeQueries({ queryKey: ['auth'] });
};

export const getQueryData = <T = unknown>(queryKey: unknown[]): T | undefined => {
  return queryClient.getQueryData<T>(queryKey);
};

export const setQueryData = <T = unknown>(queryKey: unknown[], data: T): void => {
  queryClient.setQueryData(queryKey, data);
};

export const useQueryClient = () => queryClient;

export const useMutationWithInvalidation = (
  invalidateKeys: string[][]
) => {
  return {
    onSuccess: () => {
      invalidateKeys.forEach(key => {
        queryClient.invalidateQueries({ queryKey: key });
      });
    },
  };
};

export default queryClient;

export type {
  QueryClient,
  DefaultOptions,
} from '@tanstack/react-query';
