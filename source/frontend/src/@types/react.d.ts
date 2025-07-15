// frontend/src/@types/react.d.ts
declare module 'react' {
  export type ReactNode = any;
  export type ReactElement = any;
  export type ComponentType<P = {}> = (props: P) => ReactElement;
  export type FC<P = {}> = ComponentType<P>;
  
  export const StrictMode: ComponentType<{ children?: ReactNode }>;
  export const Suspense: ComponentType<{ children?: ReactNode; fallback?: ReactNode }>;
  export const Fragment: ComponentType<{ children?: ReactNode }>;
  
  export function createElement(type: any, props?: any, ...children: any[]): ReactElement;
  export function createContext<T>(defaultValue: T): any;
  export function useState<T>(initial: T): [T, (value: T) => void];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useMemo<T>(factory: () => T, deps: any[]): T;
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
  
  export default any;
}
