// lib/api/pages.ts
import { BaseAPIClient } from './base'
import type { Page } from '@/lib/types/api'  // ✅ Import direct au lieu de '@/lib/types'

export class PagesAPIClient extends BaseAPIClient {
  /**
   * Récupère une page par son slug (pour routes dynamiques)
   * POST /public/pages/by_slug/
   */
  async getPageBySlug(slugArray: string[], websiteId: number): Promise<Page | null> {
    const slug = '/' + slugArray.join('/')
    const cacheKey = `public-page-${websiteId}-${slug}`
     
    if (this.isValidCache(cacheKey)) {
      return this.cache.get(cacheKey)?.data as Page
    }

    const response = await this.fetchWithErrorHandling<Page>(
      '/seo/public/pages/by_slug/',
      {
        method: 'POST',
        body: JSON.stringify({ 
          url_path: slug,
          website_id: websiteId 
        })
      }
    )

    if (response) {
      this.setCache(cacheKey, response)
    }
     
    return response
  }

  /**
   * Récupère les articles de blog publiés
   * GET /public/pages/blog/?website=X
   */
  async getBlogPages(websiteId: number): Promise<Page[]> {
    const cacheKey = `public-blog-${websiteId}`
     
    if (this.isValidCache(cacheKey)) {
      return (this.cache.get(cacheKey)?.data as Page[]) || []
    }

    const response = await this.fetchWithErrorHandling<Page[]>(
      `/seo/public/pages/blog/?website=${websiteId}`
    )

    const pages = response || []
    this.setCache(cacheKey, pages)
    return pages
  }

  /**
   * Récupère les pages de navigation principales
   * GET /public/pages/navigation/?website=X
   */
  async getNavigationPages(websiteId: number): Promise<Page[]> {
    const cacheKey = `public-navigation-${websiteId}`
     
    if (this.isValidCache(cacheKey)) {
      return (this.cache.get(cacheKey)?.data as Page[]) || []
    }

    const response = await this.fetchWithErrorHandling<Page[]>(
      `/seo/public/pages/navigation/?website=${websiteId}`
    )

    const pages = response || []
    this.setCache(cacheKey, pages)
    return pages
  }

  /**
   * Pages outils (filtrées depuis la navigation)
   */
  async getToolPages(websiteId: number): Promise<Page[]> {
    const cacheKey = `public-tools-${websiteId}`
     
    if (this.isValidCache(cacheKey)) {
      return (this.cache.get(cacheKey)?.data as Page[]) || []
    }

    // Récupère toutes les pages de navigation et filtre sur /tools
    const allPages = await this.getNavigationPages(websiteId)
    const toolPages = allPages.filter(page => 
      page.url_path.startsWith('/tools') ||
      page.url_path.startsWith('/outils')
    )
     
    this.setCache(cacheKey, toolPages)
    return toolPages
  }
}