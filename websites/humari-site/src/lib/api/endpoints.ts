// lib/api/endpoints.ts (mise à jour complète)
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const ENDPOINTS = {
  // ========== ENDPOINTS PUBLICS (NO AUTH) ==========
  PUBLIC_PAGE_BY_SLUG: `${API_BASE}/seo/public/pages/by_slug/`,
  PUBLIC_BLOG_PAGES: (websiteId: number) => `${API_BASE}/seo/public/pages/blog/?website=${websiteId}`,
  PUBLIC_NAVIGATION: (websiteId: number) => `${API_BASE}/seo/public/pages/navigation/?website=${websiteId}`,
  PUBLIC_HEALTH: `${API_BASE}/seo/public/health/status/`,
  
  // ========== NOUVEAU: ENDPOINTS RENDER (RECOMMANDÉ) ==========
  // Ces endpoints sont plus performants et supportent les sections
  RENDER_PAGE_BY_SLUG: `${API_BASE}/seo/render/by_slug/`,
  RENDER_SITEMAP_DATA: (websiteId: number) => `${API_BASE}/seo/render/sitemap-data/?website=${websiteId}`,
  RENDER_PAGE_BY_ID: (pageId: number) => `${API_BASE}/seo/render/${pageId}/`,
  
  // ========== ENDPOINTS SECTIONS (BACKOFFICE) ==========
  PAGE_SECTIONS: `${API_BASE}/seo/sections/`,
  PAGE_SECTIONS_BY_PAGE: (pageId: number) => `${API_BASE}/seo/sections/?page=${pageId}`,
  PAGE_SECTIONS_REORDER: `${API_BASE}/seo/sections/reorder/`,
  SECTION_TEMPLATES: `${API_BASE}/seo/section-templates/`,
  SECTION_TEMPLATES_BY_CATEGORY: (category: string) => `${API_BASE}/seo/section-templates/?category=${category}`,
  
  // ========== ENDPOINTS PRIVÉS EXISTANTS (AUTH REQUIRED) ==========
  WEBSITES: `${API_BASE}/seo/websites/`,
  WEBSITE_BY_ID: (id: number) => `${API_BASE}/seo/websites/${id}/`,
  PAGES: `${API_BASE}/seo/pages/`,
  PAGE_BY_ID: (id: number) => `${API_BASE}/seo/pages/${id}/`,
  PAGES_BY_TYPE: (pageType: string) => `${API_BASE}/seo/pages/?page_type=${pageType}`,
  PAGE_CONTENT: (pageId: number) => `${API_BASE}/seo/pages/${pageId}/content/`,
  HEALTH: `${API_BASE}/seo/health/`,
} as const

export const WEBSITE_ID = 34