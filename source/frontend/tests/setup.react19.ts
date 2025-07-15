// frontend/tests/setup.react19.ts
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Import setup de base
import './setup';

// Mock React 19 features
vi.mock('react', async () => {
  const actual = await vi.importActual('react');
  return {
    ...actual,
    use: vi.fn(),
    useOptimistic: vi.fn(() => [null, vi.fn()]),
    useTransition: vi.fn(() => [false, vi.fn()]),
  };
});

vi.mock('react-dom', async () => {
  const actual = await vi.importActual('react-dom');
  return {
    ...actual,
    useFormStatus: vi.fn(() => ({ pending: false, data: null, method: null })),
  };
});

// Suppression warnings React 19
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render is no longer supported') ||
       args[0].includes('Warning: React.createElement') ||
       args[0].includes('Warning: useOptimistic') ||
       args[0].includes('Warning: Server Components'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
