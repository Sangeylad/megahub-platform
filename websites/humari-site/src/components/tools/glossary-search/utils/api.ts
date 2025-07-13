// src/components/tools/glossary-search/utils/api.ts
import type { 
  GlossaryTerm, 
  GlossaryCategory, 
  SearchResults 
} from '../types'

// ✅ Gestion robuste de l'URL de base
const getApiBaseUrl = (): string => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL
  
  if (!baseUrl) {
    console.error('NEXT_PUBLIC_API_URL environment variable is not defined')
    return 'https://backoffice.humari.fr' // Fallback
  }
  
  // Enlever le slash final s'il existe
  return baseUrl.replace(/\/$/, '')
}

const GLOSSARY_API_BASE = `${getApiBaseUrl()}/glossaire`

export interface ApiSearchParams {
  q?: string
  lang?: string
  category?: string
  essential?: boolean
  difficulty?: string
  page_size?: number
  page?: number
  [key: string]: string | number | boolean | undefined
}

class GlossaryApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message)
    this.name = 'GlossaryApiError'
  }
}

async function apiRequest<T>(endpoint: string, params?: Record<string, unknown>): Promise<T> {
  try {
    const url = new URL(`${GLOSSARY_API_BASE}${endpoint}`)
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        // ✅ NOUVEAU: Filtrage plus strict des paramètres
        if (value !== undefined && value !== null && value !== '' && value !== false) {
          url.searchParams.append(key, String(value))
        }
      })
    }

    console.log('🔍 API Request URL:', url.toString())

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      cache: 'no-store'
    })

    if (!response.ok) {
      // ✅ NOUVEAU: Gestion plus détaillée des erreurs
      let errorMessage = `API Error: ${response.status} ${response.statusText}`
      
      try {
        const errorData = await response.json()
        if (errorData.detail) {
          errorMessage = errorData.detail
        } else if (errorData.message) {
          errorMessage = errorData.message
        }
      } catch {
        // Si on peut pas parser l'erreur JSON, on garde le message par défaut
      }
      
      throw new GlossaryApiError(errorMessage, response.status)
    }

    const data = await response.json()
    return data
    
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('Invalid URL')) {
      console.error('❌ Invalid URL construction:', {
        baseUrl: GLOSSARY_API_BASE,
        endpoint,
        fullUrl: `${GLOSSARY_API_BASE}${endpoint}`
      })
      throw new GlossaryApiError(`Configuration error: Invalid API URL`)
    }
    
    if (error instanceof GlossaryApiError) {
      throw error
    }
    
    throw new GlossaryApiError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`)
  }
}

export const glossaryApi = {
  // Recherche de termes
  searchTerms: async (params: ApiSearchParams): Promise<SearchResults> => {
    return apiRequest('/terms/search/', params as Record<string, unknown>)
  },

  // Récupérer un terme par slug
  getTermBySlug: async (slug: string, lang = 'fr', context = ''): Promise<GlossaryTerm> => {
    const params: Record<string, string> = { lang }
    if (context) params.context = context
    return apiRequest(`/terms/by-slug/${encodeURIComponent(slug)}/`, params)
  },

  // Liste des catégories
  getCategories: async (): Promise<{ results: GlossaryCategory[] }> => {
    return apiRequest('/categories/')
  },

  // Arbre des catégories
  getCategoryTree: async (): Promise<GlossaryCategory[]> => {
    return apiRequest('/categories/tree/')
  },

  // Termes populaires
  getPopularTerms: async (limit = 10, lang = 'fr'): Promise<GlossaryTerm[]> => {
    return apiRequest('/terms/popular/', { limit, lang })
  },

  // Termes essentiels
  getEssentialTerms: async (category = '', lang = 'fr'): Promise<GlossaryTerm[]> => {
    const params: Record<string, string> = { lang }
    if (category) params.category = category
    return apiRequest('/terms/essential/', params)
  },

  

  // Statistiques
  getStats: async (): Promise<{
    total_terms: number
    essential_terms: number
    terms_by_difficulty: Record<string, number>
    terms_by_category: Record<string, number>
  }> => {
    return apiRequest('/terms/stats/')
  }
}

export { GlossaryApiError }