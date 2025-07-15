/// <reference types="vite/client" />

// frontend/src/vite-env.d.ts

// Types environnement Vite + React 19
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_NODE_ENV: string;
  readonly VITE_ENABLE_REACT_COMPILER: string;
  readonly VITE_ENABLE_LIGHTNING_CSS: string;
  readonly VITE_ENABLE_DEVTOOLS: string;
  readonly VITE_DEBUG: string;
  readonly VITE_ENABLE_MOCK_API: string;
  readonly GENERATE_SOURCEMAP: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Types React 19 augmentations - Server Components ready
declare module 'react' {
  interface CSSProperties {
    [key: `--${string}`]: string | number | undefined;
  }
  
  // React 19 - ref comme prop normale (plus de forwardRef)
  interface ComponentProps<T extends keyof JSX.IntrinsicElements | React.JSXElementConstructor<any>> {
    ref?: React.Ref<T extends keyof JSX.IntrinsicElements ? JSX.IntrinsicElements[T] extends React.DetailedHTMLProps<React.HTMLAttributes<infer U>, any> ? U : any : any>;
  }
}

// Process.env types pour Node.js
declare namespace NodeJS {
  interface ProcessEnv {
    readonly npm_package_version: string;
    readonly GENERATE_SOURCEMAP: string;
  }
}

// Types pour assets
declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.png' {
  const content: string;
  export default content;
}

declare module '*.jpg' {
  const content: string;
  export default content;
}

declare module '*.jpeg' {
  const content: string;
  export default content;
}

declare module '*.gif' {
  const content: string;
  export default content;
}

declare module '*.webp' {
  const content: string;
  export default content;
}

// Types TanStack Router v5
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
