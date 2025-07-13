// src/lib/api/navigation.ts - VERSION CORRIGÉE TYPESCRIPT

import { BaseAPIClient } from './base'
import type { NavigationResponse, NavigationItem } from '@/lib/types/api'
import type { MenuItem } from '@/components/layout/headers/types'

export class NavigationAPIClient extends BaseAPIClient {
  
  constructor() {
    super('')
  }

  async getNavigation(websiteId: number): Promise<NavigationResponse | null> {
    const cacheKey = `navigation_${websiteId}`
    
    console.log('🔍 DEBUG: Starting navigation fetch for website:', websiteId)
    
    // Vérifier le cache
    if (this.isValidCache(cacheKey)) {
      const cached = this.cache.get(cacheKey)
      console.log('🎯 Navigation from cache for website:', websiteId)
      return cached?.data as NavigationResponse
    }

    try {
      // 🎯 CORRECTION: Utiliser les variables d'environnement côté serveur
      const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL
      const apiUrl = `${MEGAHUB_API_URL}/seo/pages/navigation/?website=${websiteId}`
      
      console.log('🔍 DEBUG: Full API URL:', apiUrl)
      console.log('🔍 DEBUG: MEGAHUB_API_URL env var:', MEGAHUB_API_URL)
      
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store',
      })

      console.log('🔍 DEBUG: Response status:', response.status)
      console.log('🔍 DEBUG: Response ok:', response.ok)

      if (!response.ok) {
        console.error('❌ Navigation API Error:', {
          status: response.status,
          statusText: response.statusText,
          websiteId,
          url: apiUrl
        })
        return null
      }

      const data: NavigationResponse = await response.json()
      
      console.log('🔍 DEBUG: Raw response data:', JSON.stringify(data, null, 2))
      console.log('🔍 DEBUG: Navigation items count:', data?.navigation?.length || 0)
      
      // Validation des données
      if (!data.navigation || !Array.isArray(data.navigation)) {
        console.error('❌ Invalid navigation data structure:', data)
        return null
      }

      // Mettre en cache (1h)
      this.setCache(cacheKey, data, 3600000)
      
      console.log(`✅ Navigation loaded: ${data.total_items} top-level items, ${data.total_level_2 || 0} sub-items`)
      
      return data

    } catch (error) {
      // ✅ FIX: Gestion TypeScript stricte des erreurs
      console.error('❌ Navigation fetch error:', error)
      
      if (error instanceof Error) {
        console.error('❌ Error details:', {
          name: error.name,
          message: error.message,
          stack: error.stack
        })
      } else {
        console.error('❌ Unknown error type:', String(error))
      }
      
      return null
    }
  }

  transformToMenuItem(navigationItems: NavigationItem[]): MenuItem[] {
    console.log('🔄 Transforming navigation items:', navigationItems.length)
    
    const result = navigationItems.map(item => {
      console.log('🔄 Processing item:', { id: item.id, title: item.title, childrenCount: item.children.length })
      
      return {
        label: item.title,
        href: item.url_path,
        ...(item.children.length > 0 && {
          children: this.transformToMenuItem(item.children)
        })
      }
    })
    
    console.log('✅ Transformation complete, result:', JSON.stringify(result, null, 2))
    return result
  }

  invalidateNavigationCache(websiteId: number): void {
    const cacheKey = `navigation_${websiteId}`
    this.cache.delete(cacheKey)
    console.log('🗑️ Navigation cache invalidated for website:', websiteId)
  }
}

export const navigationAPI = new NavigationAPIClient()