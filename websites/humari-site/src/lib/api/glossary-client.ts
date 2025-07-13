// src/lib/api/glossary-client.ts
import type {
  SearchParams,
  GlossaryTerm,
  SearchResults,
  GlossaryCategory
} from '@/components/tools/glossary-search/types'

class GlossaryClientApi {
  async searchTerms(params: SearchParams): Promise<SearchResults> {
    const url = new URL('/api/glossaire/search', window.location.origin)
    
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
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.error || `Erreur de recherche: ${response.status}`)
    }
    
    return response.json()
  }
  
  async getCategories(): Promise<{ results: GlossaryCategory[] }> {
    const response = await fetch('/api/glossaire/categories', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    })
    
    if (!response.ok) {
      throw new Error(`Erreur de chargement: ${response.status}`)
    }
    
    return response.json()
  }
  
  async getPopularTerms(limit = 10, lang = 'fr'): Promise<GlossaryTerm[]> {
    const response = await fetch(
      `/api/glossaire/popular?limit=${limit}&lang=${lang}`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      }
    )
    
    if (!response.ok) {
      throw new Error(`Erreur de chargement: ${response.status}`)
    }
    
    return response.json()
  }
  
  async getTermBySlug(slug: string, lang = 'fr'): Promise<GlossaryTerm> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/glossaire/terms/by-slug/${encodeURIComponent(slug)}?lang=${lang}`,
    {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    }
  )
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('Terme non trouvé')
    }
    throw new Error(`Erreur de chargement: ${response.status}`)
  }
  
  return response.json()
}
}

export const glossaryClientApi = new GlossaryClientApi()