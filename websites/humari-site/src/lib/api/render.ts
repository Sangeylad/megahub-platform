// lib/api/render.ts - COMPLET ACTUALISÉ ET CORRIGÉ AVEC GLOSSAIRE
import { BaseAPIClient } from './base'
import type { 
  RenderResponse, 
  SitemapIndexResponse, 
  SitemapTypeResponse,
  SitemapStatsResponse,
  SitemapDebugResponse,
  SitemapType,
  SitemapResponse 
} from '@/lib/types/api'

export class RenderAPIClient extends BaseAPIClient {
  
  constructor() {
    super('') // Pas utilisé car on appelle directement MEGAHUB
  }
  
  // ========== MÉTHODES RENDER EXISTANTES ==========
  
  async getPageForRender(slugArray: string[]): Promise<RenderResponse | null> {
    const url_path = slugArray.length === 0 ? '/' : '/' + slugArray.join('/')
    
    console.log('🔍 SSR Render Debug:', {
      slugArray,
      url_path,
      isHomepage: slugArray.length === 0,
      timestamp: new Date().toISOString()
    })

    try {
      return this.fetchDirectFromMegahub(url_path)
    } catch (error) {
      console.error('❌ Render API error:', error)
      return null
    }
  }

  private async fetchDirectFromMegahub(url_path: string): Promise<RenderResponse | null> {
  const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL!
  const MEGAHUB_WEBSITE_ID = process.env.MEGAHUB_WEBSITE_ID!
  
  // ✅ DEBUG EXPLICITE
  const debugInfo = {
    url_path,
    MEGAHUB_API_URL,
    MEGAHUB_WEBSITE_ID,
    fullUrl: `${MEGAHUB_API_URL}/seo/render/by_slug/`,
    payload: { url_path, website_id: parseInt(MEGAHUB_WEBSITE_ID) }
  }
  
  // Force l'affichage dans les logs
  process.stdout.write(`🔍 NEXT.JS FETCH: ${JSON.stringify(debugInfo, null, 2)}\n`)
  
  try {
    const response = await fetch(`${MEGAHUB_API_URL}/seo/render/by_slug/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url_path,
        website_id: parseInt(MEGAHUB_WEBSITE_ID)
      }),
      cache: 'no-store'
    })

    process.stdout.write(`🔍 RESPONSE STATUS: ${response.status}\n`)

    if (!response.ok) {
      const errorText = await response.text()
      process.stdout.write(`❌ ERROR RESPONSE: ${errorText}\n`)
      return null
    }

    const data = await response.json()

// ✅ DEBUG: Voir le contenu de la réponse
if (url_path.includes('definition-')) {
  process.stdout.write(`🔍 GLOSSAIRE RESPONSE: ${JSON.stringify(data, null, 2)}\n`)
}

process.stdout.write(`✅ SUCCESS for: ${url_path}\n`)
return data

    return data
  } catch (error) {
    process.stdout.write(`❌ FETCH ERROR: ${error}\n`)
    return null
  }
}

  // ========== MÉTHODES SITEMAP ==========

  async getSitemapIndex(): Promise<SitemapIndexResponse> {
    console.log('🗺️ Fetching sitemap index...')
    return this.fetchSitemapData('index') as Promise<SitemapIndexResponse>
  }
  
  // ✅ CORRECTION : Changer le type pour accepter 'glossaire'
  async getSitemapForType(type: 'vitrine' | 'blog' | 'outils' | 'glossaire'): Promise<SitemapTypeResponse> {
    console.log(`🗺️ Fetching sitemap for type: ${type}`)
    return this.fetchSitemapData(type) as Promise<SitemapTypeResponse>
  }

  async getSitemapStats(): Promise<SitemapStatsResponse> {
    const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL!
    const MEGAHUB_WEBSITE_ID = process.env.MEGAHUB_WEBSITE_ID!
    
    try {
      const response = await fetch(
        `${MEGAHUB_API_URL}/seo/pages/sitemap_stats/?website=${MEGAHUB_WEBSITE_ID}`,
        {
          cache: 'no-store',
          headers: { 'Content-Type': 'application/json' }
        }
      )
      
      if (!response.ok) {
        throw new Error(`Sitemap stats API Error: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('❌ Sitemap stats error:', error)
      throw error
    }
  }

  async getSitemapDebug(): Promise<SitemapDebugResponse> {
    const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL!
    const MEGAHUB_WEBSITE_ID = process.env.MEGAHUB_WEBSITE_ID!
    
    try {
      const response = await fetch(
        `${MEGAHUB_API_URL}/seo/render/sitemap-debug/?website=${MEGAHUB_WEBSITE_ID}`,
        {
          cache: 'no-store',
          headers: { 'Content-Type': 'application/json' }
        }
      )
      
      if (!response.ok) {
        throw new Error(`Sitemap debug API Error: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('❌ Sitemap debug error:', error)
      throw error
    }
  }

  private async fetchSitemapData(type: SitemapType): Promise<SitemapIndexResponse | SitemapTypeResponse> {
    const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL!
    const MEGAHUB_WEBSITE_ID = process.env.MEGAHUB_WEBSITE_ID!
    
    try {
      const response = await fetch(
        `${MEGAHUB_API_URL}/seo/render/sitemap-data/?website=${MEGAHUB_WEBSITE_ID}&type=${type}`,
        {
          cache: 'no-store',
          headers: { 'Content-Type': 'application/json' }
        }
      )
      
      if (!response.ok) {
        throw new Error(`Sitemap ${type} API Error: ${response.status}`)
      }
      
      const data = await response.json()
      console.log(`✅ Sitemap ${type} fetched successfully`)
      return data
    } catch (error) {
      console.error(`❌ Sitemap ${type} error:`, error)
      
      if (type === 'index') {
        return {
          sitemaps: [],
          generated_at: new Date().toISOString(),
          total_types: 0
        } as SitemapIndexResponse
      } else {
        return {
          pages: [],
          total: 0,
          type,
          type_name: `Sitemap ${type}`,
          generated_at: new Date().toISOString()
        } as SitemapTypeResponse
      }
    }
  }

  // Legacy support
  async getSitemapData(): Promise<SitemapResponse> {
    console.log('⚠️ Using legacy getSitemapData - redirecting to vitrine sitemap')
    return this.getSitemapForType('vitrine')
  }
}