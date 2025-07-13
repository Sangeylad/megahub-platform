// src/components/layout/headers/types.ts
export interface MenuItem {
  label: string
  href: string
  children?: MenuItem[]
  // ✅ NOUVEAU : Support blog dynamique
  isDynamicBlog?: boolean
  blogConfig?: {
    slug: string
    name: string
    description: string
  }
}

export interface HeaderConfig {
  variant: 'default' | 'none'
  logo_url?: string
  logo_alt?: string
  navigation?: MenuItem[]
  cta_text?: string
  cta_url?: string
  show_contact_info?: boolean
  contact_phone?: string
  contact_email?: string
  // ✅ NOUVEAU : Support blog global
  blog_enabled?: boolean
  blog_config?: {
    slug: string
    name: string
    description: string
  } | null
}

export interface HeaderComponentProps {
  config: HeaderConfig
}

// src/lib/types/api.ts - AJOUTER CES TYPES À LA FIN

