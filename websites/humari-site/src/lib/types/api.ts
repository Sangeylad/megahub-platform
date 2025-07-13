// lib/types/api.ts - COMPLET ACTUALISÉ AVEC TOOLS

// Types mappés exactement sur tes models Django
export interface Brand {
  id: number
  name: string
  description?: string
  url?: string
}

export interface Website {
  id: number
  name: string
  url: string
  brand: Brand
  domain_authority?: number
  max_competitor_backlinks?: number
  max_competitor_kd?: number
  created_at: string
  updated_at: string
}

export interface Page {
  id: number
  title: string
  url_path: string
  meta_description?: string
  website: Website
  parent?: Page
  children?: Page[]
  
  // Classification
  search_intent: 'TOFU' | 'MOFU' | 'BOFU' | null
  page_type: 'vitrine' | 'blog' | 'produit' | 'landing' | 'categorie' | 'legal' | 'outils' | 'calculateur' | 'autre'
  
  // 🆕 Métadonnées sitemap
  sitemap_priority: number
  sitemap_changefreq: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never'
  exclude_from_sitemap: boolean
  
  // Relations
  content?: PageContent
  keywords?: Keyword[]
  
  // Timestamps
  created_at: string
  updated_at: string
}

export interface PageContent {
  id: number
  page: number // ID de la page
  
  // Meta SEO
  meta_title: string
  meta_description: string
  
  // Contenu
  content_markdown: string
  
  // État
  source: 'ai_generated' | 'manual' | 'ai_edited'
  status: 'draft' | 'review' | 'approved' | 'published'
  
  // Métriques
  word_count: number
  reading_time_minutes: number
  
  // Timestamps
  generated_at: string
  created_at: string
  updated_at: string
}

export interface Keyword {
  id: number
  keyword: string
  volume: number
  search_intent: 'TOFU' | 'MOFU' | 'BOFU' | null
  kdifficulty?: string
  da_median?: number
  cpc?: string
}

// ========== TYPES POUR LE SYSTÈME DE RENDU ==========

export interface PageSection {
  id: number
  section_type: string
  data: Record<string, unknown>
  order: number
  version: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SectionComponentProps {
  type: string
  data: Record<string, unknown>
  version: string
  section_id: number
  last_updated: string
  // 🆕 Support hiérarchie CSS Grid
  layout_config?: LayoutConfig
  children?: SectionComponentProps[]
}

export interface LayoutConfig {
  columns?: number[]
  gap?: string
  align?: 'start' | 'center' | 'end'
  grid_template_columns?: string
  grid_template_rows?: string
  auto_rows?: string
  responsive?: {
    [breakpoint: string]: Partial<LayoutConfig>
  }
}

// Types pour la réponse de l'API render (exactement comme PageRenderSerializer)
export interface RenderResponse {
  id: number
  title: string
  url_path: string
  page_type: string
  render_data: {
    strategy: 'markdown' | 'sections' | 'hybrid'
    sections?: SectionComponentProps[]
    content?: {
      markdown: string
      meta_title: string
      meta_description: string
    }
    metadata: {
      page_id: number
      title: string
      url_path: string
      page_type: string
      search_intent?: string
      hierarchy_level: number
      parent_title?: string
      breadcrumb: Array<{title: string, url: string}>
      featured_image?: string
      keywords: {
        primary?: {keyword: string, volume: number}
        secondary: Array<{keyword: string, volume: number}>
      }
      last_modified: string
      template: string
    }
  }
  seo_metadata: {
    title: string
    description: string
    canonical: string
    featured_image?: string
    page_type: string
    breadcrumb: Array<{title: string, url: string}>
    keywords: Record<string, unknown>
    last_modified: string
  }
  structured_data: Record<string, unknown>
  
  // 🆕 Support pour les pages d'outils avec données enrichies
  tools_data?: {
    is_tools_page: boolean
    hierarchy_level: number
    tools_categories?: Array<{
      id: number
      title: string
      url_path: string
    }>
    category_tools?: Array<{
      id: number
      title: string
      url_path: string
    }>
  }
}

// ========== 🆕 TYPES SITEMAP MULTI-SEGMENTS ==========

export interface SitemapPage {
  url: string
  lastmod: string
  priority: number
  changefreq: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never'
  page_type?: string
  title?: string
}

// ✅ CORRECTION : Ajouter 'outils' au type union
export type SitemapType = 'index' | 'vitrine' | 'blog' | 'outils' | 'glossaire'

// 🆕 Réponse index sitemap (liste des sitemaps)
export interface SitemapIndexResponse {
  sitemaps: Array<{
    loc: string
    lastmod: string
    type: string
    name: string
    pages_count: number
  }>
  generated_at: string
  total_types: number
}

// 🆕 Réponse sitemap par type
export interface SitemapTypeResponse {
  pages: SitemapPage[]
  total: number
  type: string
  type_name: string
  generated_at: string
}

// 🔧 CORRECTION: Legacy avec contenu spécifique au lieu d'extends vide
export interface SitemapResponse {
  pages: SitemapPage[]
  total: number
  generated_at: string
  // Champs legacy pour compatibilité
  website_id?: number
  last_updated?: string
}

// 🆕 Stats sitemap pour debug
export interface SitemapStatsResponse {
  total_pages: number
  included_in_sitemap: number
  excluded_from_sitemap: number
  by_type: Record<string, number>
  website_id: number
}

// 🆕 Debug sitemap complet
export interface SitemapDebugResponse {
  sitemaps: Record<string, SitemapTypeResponse>
  index: SitemapIndexResponse
  stats: SitemapStatsResponse
}

// ========== 🆕 TYPES NAVIGATION DYNAMIQUE ==========


export interface NavigationItem {
  id: number | string  // ✅ Support ID artificiel pour blog
  title: string
  url_path: string
  children: NavigationItem[]
  // ✅ NOUVEAU : Métadonnées blog
  page_type?: string
  is_dynamic_blog?: boolean
  blog_config?: {
    slug: string
    name: string
    description: string
  }
}

export interface NavigationResponse {
  navigation: NavigationItem[]
  website_id: number
  total_items: number
  total_level_2: number
  has_dynamic_blog: boolean  // ✅ NOUVEAU : Flag blog présent
  generated_at: string
}

import type { HeaderConfig } from '@/components/layout/headers/types'

// Extension du HeaderConfig pour la navigation dynamique
export interface DynamicHeaderConfig extends Omit<HeaderConfig, 'navigation'> {
  navigation: NavigationItem[]
  navigation_loaded: boolean
  navigation_error?: string
  // ✅ NOUVEAU : Métadonnées navigation
  has_dynamic_blog?: boolean
}

// ========== 🆕 TYPES TOOLS API ==========

export interface ToolCategory {
  id: number
  title: string
  url_path: string
  tools_count: number
  description: string
  status: string
  last_updated: string
}

export interface Tool {
  id: number
  title: string
  url_path: string
  description: string
  status?: string
  last_updated?: string
}

export interface ToolsByCategoryResponse {
  category: {
    id: number
    title: string
    url_path: string
    description: string
  }
  tools: Tool[]
  tools_count: number
  generated_at: string
}

export interface CategoriesResponse {
  categories: ToolCategory[]
  total_categories: number
  website_id: number
  generated_at: string
}

export interface AllToolsResponse {
  tools_by_category: Array<{
    category: {
      id: number
      title: string
      url_path: string
      description: string
    }
    tools: Tool[]
    tools_count: number
  }>
  total_tools: number
  total_categories: number
  website_id: number
  generated_at: string
}

export interface MainPageResponse {
  main_page: {
    id: number
    title: string
    url_path: string
    description: string
    status: string
    last_updated: string
  }
  categories_preview: ToolCategory[]
  total_categories: number
  website_id: number
  generated_at: string
}

export interface ToolsSitemapResponse {
  tools_sitemap: Array<{
    url: string
    lastmod: string
    priority: number
    changefreq: string
    page_type: string
    hierarchy_level: number
  }>
  total_pages: number
  website_id: number
  generated_at: string
}

export interface ToolsStatsResponse {
  stats: {
    total_tools: number
    total_categories: number
    tools_by_status: Record<string, number>
    most_active_category: {
      id: number
      title: string
      tools_count: number
    } | null
    last_updated: string
  }
  website_id: number
}

// ========== TYPES GÉNÉRIQUES API ==========

// Types pour les réponses API
export interface APIResponse<T> {
  data: T
  status: 'success' | 'error'
  message?: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Types pour les erreurs
export interface APIError {
  detail: string
  field_errors?: Record<string, string[]>
  status_code: number
}

// 🆕 Types pour health check
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'error'
  services?: {
    nextjs: 'healthy' | 'error'
    megahub: 'healthy' | 'error'
  }
  timestamp: string
}

// ========== TYPES UTILITAIRES ==========

// Type helper pour les API calls avec cache
export interface CachedAPIResponse<T> {
  data: T
  cached: boolean
  cache_key: string
  ttl: number
  timestamp: number
}

// Type pour les métadonnées d'API
export interface APIMetadata {
  endpoint: string
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  cached: boolean
  cache_duration?: number
  last_call?: string
}

// Type pour les paramètres de filtrage communs
export interface FilterParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  website?: number
}

// Type pour les paramètres Tools spécifiques
export interface ToolsFilterParams extends FilterParams {
  category_id?: number
  category_path?: string
  status?: string
  page_type?: string
}