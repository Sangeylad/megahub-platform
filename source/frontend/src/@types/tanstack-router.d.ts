// frontend/src/@types/tanstack-router.d.ts
declare module '@tanstack/react-router' {
  import type { ReactElement, ComponentType, ReactNode } from 'react';
  
  export interface RouterOptions {
    routeTree: any;
    context?: any;
  }
  
  export interface RouteOptions {
    component?: ComponentType<any>;
    loader?: any;
    beforeLoad?: any;
    errorComponent?: ComponentType<any>;
  }
  
  export function createRouter(options: RouterOptions): any;
  export const RouterProvider: ComponentType<{ router: any }>;
  export function createRootRoute(options?: RouteOptions): any;
  export function createFileRoute(path: string): (options?: RouteOptions) => any;
  export const Outlet: ComponentType<{}>;
  export const Link: ComponentType<any>;
  
  export interface Register {}
}
