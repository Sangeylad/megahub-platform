// src/components/tools/glossary-search/hooks/useUrlFilters.ts
'use client'

import { useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import type { SearchFilters } from '../types'

interface UseUrlFiltersOptions {
  onFiltersDetected: (filters: Partial<SearchFilters>) => void
  enabled?: boolean
}

export function useUrlFilters({ onFiltersDetected, enabled = true }: UseUrlFiltersOptions) {
  const searchParams = useSearchParams()
  
  useEffect(() => {
    if (!enabled) return
    
    const urlFilters: Partial<SearchFilters> = {}
    
    // Détecter category depuis URL
    const categoryParam = searchParams.get('category')
    if (categoryParam) {
      urlFilters.category = categoryParam
      console.log('🔗 URL category filter detected:', categoryParam)
    }
    
    // Détecter query depuis URL
    const queryParam = searchParams.get('q')
    if (queryParam) {
      urlFilters.query = queryParam
      console.log('🔗 URL query filter detected:', queryParam)
    }
    
    // Détecter difficulty depuis URL
    const difficultyParam = searchParams.get('difficulty')
    if (difficultyParam) {
      urlFilters.difficulty = difficultyParam
      console.log('🔗 URL difficulty filter detected:', difficultyParam)
    }
    
    // Détecter essential depuis URL
    const essentialParam = searchParams.get('essential')
    if (essentialParam === 'true') {
      urlFilters.essential_only = true
      console.log('🔗 URL essential filter detected')
    }
    
    // Appliquer les filtres détectés
    if (Object.keys(urlFilters).length > 0) {
      console.log('🔗 Applying URL filters:', urlFilters)
      onFiltersDetected(urlFilters)
    }
  }, [searchParams, onFiltersDetected, enabled])
}