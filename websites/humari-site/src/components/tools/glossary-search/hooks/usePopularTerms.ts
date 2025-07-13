// src/components/tools/glossary-search/hooks/usePopularTerms.ts
'use client'

import { useState, useEffect, useCallback } from 'react'
import { glossaryClientApi } from '@/lib/api/glossary-client'
import type { GlossaryTerm } from '../types'

interface UsePopularTermsReturn {
  popularTerms: GlossaryTerm[]
  isLoading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export function usePopularTerms(limit = 10, lang = 'fr'): UsePopularTermsReturn {
  const [popularTerms, setPopularTerms] = useState<GlossaryTerm[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const fetchPopularTerms = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const terms = await glossaryClientApi.getPopularTerms(limit, lang)
      setPopularTerms(terms)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur de chargement des termes populaires'
      setError(errorMessage)
      console.error('Popular terms fetch error:', err)
      
    } finally {
      setIsLoading(false)
    }
  }, [limit, lang])
  
  useEffect(() => {
    fetchPopularTerms()
  }, [fetchPopularTerms])
  
  return {
    popularTerms,
    isLoading,
    error,
    refetch: fetchPopularTerms
  }
}