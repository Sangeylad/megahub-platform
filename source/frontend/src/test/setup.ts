// frontend/src/test/setup.ts
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeAll, afterAll, vi } from 'vitest';

// ==========================================
// TYPES JEST-DOM GLOBAUX
// ==========================================
declare global {
  namespace Vi {
    interface JestAssertion<T = any> {
      toBeInTheDocument(): void;
      toHaveValue(value: string | number): void;
      toBeChecked(): void;
      toHaveAttribute(attr: string, value?: string): void;
      toHaveClass(className: string): void;
      toBeVisible(): void;
      toBeDisabled(): void;
      toHaveFocus(): void;
    }
  }
}

// ==========================================
// CLEANUP AUTOMATIQUE APRÈS CHAQUE TEST
// ==========================================
afterEach(() => {
  cleanup();
});

// ==========================================
// CONFIGURATION JSDOM COMPLÈTE
// ==========================================
beforeAll(() => {
  // Configuration jsdom avancée
  Object.defineProperty(global, 'document', {
    value: globalThis.document,
    writable: true,
  });

  Object.defineProperty(global, 'window', {
    value: globalThis.window,
    writable: true,
  });

  // Mock IntersectionObserver
  global.IntersectionObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));
  
  // Mock ResizeObserver
  global.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));
  
  // Mock matchMedia (responsive design)
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
  
  // Mock scrollTo et scroll methods
  global.scrollTo = vi.fn();
  Element.prototype.scrollTo = vi.fn();
  Element.prototype.scrollIntoView = vi.fn();
  
  // Mock fetch global pour tests API
  global.fetch = vi.fn();
  
  // Mock localStorage/sessionStorage - Standards MegaHub
  const createStorageMock = () => ({
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    key: vi.fn(),
    length: 0,
  });
  
  Object.defineProperty(window, 'localStorage', {
    value: createStorageMock(),
    writable: true,
  });
  
  Object.defineProperty(window, 'sessionStorage', {
    value: createStorageMock(),
    writable: true,
  });
  
  // Mock crypto.randomUUID
  Object.defineProperty(global, 'crypto', {
    value: {
      randomUUID: vi.fn(() => 'test-uuid-1234'),
      getRandomValues: vi.fn((array) => {
        for (let i = 0; i < array.length; i++) {
          array[i] = Math.floor(Math.random() * 256);
        }
        return array;
      }),
    },
    writable: true,
  });

  // Mock URL constructor - TypeScript strict
  Object.defineProperty(global, 'URL', {
    value: class MockURL {
      href: string;
      origin: string;
      pathname: string;
      
      constructor(url: string, base?: string) {
        this.href = url;
        this.origin = 'http://localhost:3000';
        this.pathname = url.replace(this.origin, '');
      }
    },
    writable: true,
  });

  // Mock HTMLElement methods
  HTMLElement.prototype.scrollIntoView = vi.fn();
  HTMLElement.prototype.hasPointerCapture = vi.fn();
  HTMLElement.prototype.releasePointerCapture = vi.fn();
  HTMLElement.prototype.setPointerCapture = vi.fn();
});

// ==========================================
// SUPPRESSION WARNINGS DÉVELOPPEMENT
// ==========================================
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: ReactDOM.render is no longer supported') ||
       args[0].includes('Warning: React.createElement') ||
       args[0].includes('Warning: useOptimistic') ||
       args[0].includes('Warning: Server Components') ||
       args[0].includes('Warning: Each child in a list should have a unique') ||
       args[0].includes('Warning: Failed prop type'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };

  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('React Router') ||
       args[0].includes('TanStack') ||
       args[0].includes('Zustand'))
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
});

// ==========================================
// VARIABLES ENVIRONNEMENT TESTS
// ==========================================
process.env.NODE_ENV = 'test';
process.env.VITE_API_BASE_URL = 'http://localhost:8000';
process.env.VITE_REACT_VERSION = '19.1.0';
process.env.VITE_TANSTACK_QUERY_VERSION = '5.83.0';
process.env.VITEST = 'true';

// ==========================================
// TIMEOUT CONFIGURATION
// ==========================================
vi.setConfig({
  testTimeout: 10000,
});