// src/lib/api/glossary-server.ts
import type {
  SearchParams,
  GlossaryTerm,
  SearchResults,
  GlossaryCategory
} from '@/components/tools/glossary-search/types'

const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL || 'https://backoffice.humari.fr'

class GlossaryServerApi {
  private baseUrl = `${MEGAHUB_API_URL}/glossaire`
  
  async searchTerms(params: SearchParams): Promise<SearchResults> {
    const url = new URL(`${this.baseUrl}/terms/search/`)
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '' && value !== false) {
        url.searchParams.append(key, String(value))
      }
    })
    
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      cache: 'no-store'
    })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }
    
    return response.json()
  }
  
  async getCategories(): Promise<{ results: GlossaryCategory[] }> {
    const response = await fetch(`${this.baseUrl}/categories/`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      next: { revalidate: 3600 } // Cache 1h
    })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }
    
    return response.json()
  }
  
  async getPopularTerms(limit = 10, lang = 'fr'): Promise<GlossaryTerm[]> {
    const response = await fetch(
      `${this.baseUrl}/terms/popular/?limit=${limit}&lang=${lang}`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        next: { revalidate: 1800 } // Cache 30min
      }
    )
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }
    
    return response.json()
  }
  
  async getTermBySlug(slug: string, lang = 'fr'): Promise<GlossaryTerm> {
    const response = await fetch(
      `${this.baseUrl}/terms/by-slug/${encodeURIComponent(slug)}/?lang=${lang}`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        next: { revalidate: 3600 } // Cache 1h pour les définitions
      }
    )
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }
    
    return response.json()
  }
}

export const glossaryServerApi = new GlossaryServerApi()