// frontend/src/test/utils.tsx
import React from 'react';
import { render, type RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { userEvent } from '@testing-library/user-event';
import type { ReactElement } from 'react';

// ==========================================
// QUERY CLIENT POUR TESTS - TanStack v5
// ==========================================
export const createQueryClientForTesting = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: Infinity,
        gcTime: Infinity,
      },
      mutations: {
        retry: false,
      },
    },
  });

// ==========================================
// WRAPPER PROVIDERS SIMPLIFIÉ - React 19 + TanStack v5
// ==========================================
interface TestProvidersProps {
  children: React.ReactNode;
  queryClient?: QueryClient;
}

function TestProviders({ 
  children, 
  queryClient = createQueryClientForTesting(),
}: TestProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

// ==========================================
// RENDER CUSTOM AVEC PROVIDERS - React 19
// ==========================================
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
}

export function renderWithProviders(
  ui: ReactElement,
  {
    queryClient = createQueryClientForTesting(),
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <TestProviders queryClient={queryClient}>
      {children}
    </TestProviders>
  );

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    queryClient,
  };
}

// ==========================================
// FACTORIES POUR MOCKS - TypeScript strict
// ==========================================
export const createMockUser = (overrides: Record<string, any> = {}) => ({
  id: 1,
  username: 'test_user',
  email: 'test@megahub.fr',
  first_name: 'Test',
  last_name: 'User',
  user_type: 'brand_admin' as const,
  can_access_analytics: true,
  can_access_reports: false,
  phone: '0123456789',
  position: 'Testeur',
  is_active: true,
  is_staff: false,
  is_superuser: false,
  date_joined: '2024-01-01T00:00:00Z',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

export const createMockBusiness = (overrides: Record<string, any> = {}) => ({
  id: '1',
  name: 'Test Business',
  slug: 'test-business',
  domain: 'https://test-business.com',
  createdAt: '2024-01-01T00:00:00Z',
  ...overrides,
});

export const createMockBrand = (overrides: Record<string, any> = {}) => ({
  id: '1',
  name: 'Test Brand',
  slug: 'test-brand',
  domain: 'https://test.com',
  businessId: '1',
  createdAt: '2024-01-01T00:00:00Z',
  ...overrides,
});

// ==========================================
// HELPERS ASYNC - TanStack v5 Suspense
// ==========================================
export const waitForLoadingToFinish = () =>
  new Promise(resolve => setTimeout(resolve, 0));

export async function waitForQueryToSettle(queryClient: QueryClient) {
  await new Promise(resolve => setTimeout(resolve, 100));
  return queryClient.getQueryCache().clear();
}

export const waitForSuspenseToResolve = () =>
  new Promise(resolve => setTimeout(resolve, 10));

// ==========================================
// MOCK API RESPONSES - React 19 + TanStack v5
// ==========================================
export function mockApiResponse<T>(data: T, delay = 0) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        ok: true,
        json: () => Promise.resolve({ data, status: 'success' }),
      });
    }, delay);
  });
}

export function mockApiError(message = 'API Error', status = 500, delay = 0) {
  return new Promise((_, reject) => {
    setTimeout(() => {
      reject({
        response: {
          status,
          data: { message, status: 'error' },
        },
      });
    }, delay);
  });
}

// ==========================================
// USER EVENT HELPER
// ==========================================
export const createUserEvent = (options: Record<string, any> = {}) => userEvent.setup(options);

// Re-export everything from testing-library
export * from '@testing-library/react';