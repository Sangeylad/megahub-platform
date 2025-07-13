// src/components/layout/headers/HeaderRenderer.tsx
import { DefaultHeader } from './variants/DefaultHeader'
import { NoHeader } from './variants/NoHeader'
import type { HeaderConfig } from './types'

interface HeaderRendererProps {
  config: HeaderConfig
}

export function HeaderRenderer({ config }: HeaderRendererProps) {
  switch (config.variant) {
    case 'default':
      return <DefaultHeader config={config} />
    case 'none':
      return <NoHeader />
    default:
      console.warn(`Header variant "${config.variant}" not found, falling back to default`)
      return <DefaultHeader config={config} />
  }
}