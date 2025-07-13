// lib/api/tools.ts - CORRIGÉ COMPLET avec appel direct Django
import { BaseAPIClient } from './base'
import type {
  CategoriesResponse,
  ToolsByCategoryResponse,
  AllToolsResponse,
  MainPageResponse,
  ToolsSitemapResponse,
  ToolsStatsResponse
} from '@/lib/types/tools'

export class ToolsAPIClient extends BaseAPIClient {
  
  constructor() {
    super('') // URL de base vide - on appelle directement Django
  }

  /**
   * 🚀 APPEL DIRECT DJANGO (comme render.ts)
   */
  private async fetchDirectFromMegahub<T>(endpoint: string): Promise<T | null> {
  // 🚀 UTILISER LA MÊME VARIABLE QUE RENDER.TS
  const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL! // ← Pas NEXT_PUBLIC_API_URL
  
  try {
    const response = await fetch(`${MEGAHUB_API_URL}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store'
    })

      if (!response.ok) {
        console.error(`Tools API Error: ${response.status} ${response.statusText}`)
        return null
      }

      return await response.json()
    } catch (error) {
      console.error('Tools Network error:', error)
      return null
    }
  }

  /**
   * Récupère toutes les catégories d'outils
   * GET /seo/tools/categories/?website=34
   */
  async getCategories(websiteId: number = 34): Promise<CategoriesResponse | null> {
    const cacheKey = `tools-categories-${websiteId}`
    
    if (this.isValidCache(cacheKey)) {
      return this.cache.get(cacheKey)?.data as CategoriesResponse
    }

    const response = await this.fetchDirectFromMegahub<CategoriesResponse>(
      `/seo/tools/categories/?website=${websiteId}`
    )

    if (response) {
      this.setCache(cacheKey, response, 1800000) // 30 min cache
    }

    return response
  }

  /**
   * Récupère les outils d'une catégorie spécifique
   * GET /seo/tools/category_tools/?website=34&category_id=5
   */
  async getCategoryTools(
    categoryId: number, 
    websiteId: number = 34
  ): Promise<ToolsByCategoryResponse | null> {
    const cacheKey = `tools-category-${categoryId}-${websiteId}`
    
    if (this.isValidCache(cacheKey)) {
      return this.cache.get(cacheKey)?.data as ToolsByCategoryResponse
    }

    const response = await this.fetchDirectFromMegahub<ToolsByCategoryResponse>(
      `/seo/tools/category_tools/?website=${websiteId}&category_id=${categoryId}`
    )

    if (response) {
      this.setCache(cacheKey, response, 1800000) // 30 min cache
    }

    return response
  }

  /**
   * Récupère les outils d'une catégorie par URL path
   * GET /seo/tools/category_tools/?website=34&category_path=/outils/seo
   */
  async getCategoryToolsByPath(
    categoryPath: string, 
    websiteId: number = 34
  ): Promise<ToolsByCategoryResponse | null> {
    const cacheKey = `tools-category-path-${categoryPath}-${websiteId}`
    
    if (this.isValidCache(cacheKey)) {
      return this.cache.get(cacheKey)?.data as ToolsByCategoryResponse
    }

    const response = await this.fetchDirectFromMegahub<ToolsByCategoryResponse>(
      `/seo/tools/category_tools/?website=${websiteId}&category_path=${encodeURIComponent(categoryPath)}`
    )

    if (response) {
      this.setCache(cacheKey, response, 1800000) // 30 min cache
    }

    return response
  }

  /**
   * Récupère tous les outils organisés par catégorie
   * GET /seo/tools/all_tools/?website=34
   */
  async getAllTools(websiteId: number = 34): Promise<AllToolsResponse | null> {
    const cacheKey = `tools-all-${websiteId}`
    
    if (this.isValidCache(cacheKey)) {
      return this.cache.get(cacheKey)?.data as AllToolsResponse
    }

    const response = await this.fetchDirectFromMegahub<AllToolsResponse>(
      `/seo/tools/all_tools/?website=${websiteId}`
    )

    if (response) {
      this.setCache(cacheKey, response, 1800000) // 30 min cache
    }

    return response
  }

  /**
   * Récupère la page principale des outils avec aperçu des catégories
   * GET /seo/tools/main_page/?website=34
   */
  async getMainPage(websiteId: number = 34): Promise<MainPageResponse | null> {
    const cacheKey = `tools-main-page-${websiteId}`
    
    if (this.isValidCache(cacheKey)) {
      return this.cache.get(cacheKey)?.data as MainPageResponse
    }

    const response = await this.fetchDirectFromMegahub<MainPageResponse>(
      `/seo/tools/main_page/?website=${websiteId}`
    )

    if (response) {
      this.setCache(cacheKey, response, 1800000) // 30 min cache
    }

    return response
  }

  /**
   * Récupère le sitemap spécifique aux outils
   * GET /seo/tools/sitemap/?website=34
   */
  async getSitemap(websiteId: number = 34): Promise<ToolsSitemapResponse | null> {
    const cacheKey = `tools-sitemap-${websiteId}`
    
    if (this.isValidCache(cacheKey)) {
      return this.cache.get(cacheKey)?.data as ToolsSitemapResponse
    }

    const response = await this.fetchDirectFromMegahub<ToolsSitemapResponse>(
      `/seo/tools/sitemap/?website=${websiteId}`
    )

    if (response) {
      this.setCache(cacheKey, response, 3600000) // 1h cache pour sitemap
    }

    return response
  }

  /**
   * Récupère les statistiques des outils
   * GET /seo/tools/stats/?website=34
   */
  async getStats(websiteId: number = 34): Promise<ToolsStatsResponse | null> {
    const cacheKey = `tools-stats-${websiteId}`
    
    if (this.isValidCache(cacheKey)) {
      return this.cache.get(cacheKey)?.data as ToolsStatsResponse
    }

    const response = await this.fetchDirectFromMegahub<ToolsStatsResponse>(
      `/seo/tools/stats/?website=${websiteId}`
    )

    if (response) {
      this.setCache(cacheKey, response, 900000) // 15 min cache pour stats
    }

    return response
  }

  /**
   * Invalide le cache des outils
   */
  invalidateToolsCache(websiteId: number = 34): void {
    const patterns = [
      `tools-categories-${websiteId}`,
      `tools-all-${websiteId}`,
      `tools-main-page-${websiteId}`,
      `tools-sitemap-${websiteId}`,
      `tools-stats-${websiteId}`
    ]
    
    patterns.forEach(pattern => {
      this.cache.delete(pattern)
    })
    
    // Invalider aussi les caches par catégorie (pattern matching simple)
    for (const key of this.cache.keys()) {
      if (key.startsWith(`tools-category-`) && key.includes(`-${websiteId}`)) {
        this.cache.delete(key)
      }
    }
  }
}

// Instance singleton
export const toolsAPI = new ToolsAPIClient()