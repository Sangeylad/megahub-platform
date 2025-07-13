// src/components/tools/glossary-search/hooks/useGlossarySearch.ts
'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { glossaryClientApi } from '@/lib/api/glossary-client'
import type { 
  GlossaryTerm, 
  SearchResults, 
  SearchParams, 
  SearchFilters 
} from '../types'

interface UseGlossarySearchReturn {
  // État
  results: GlossaryTerm[]
  isLoading: boolean
  error: string | null
  hasSearched: boolean
  totalCount: number
  
  // Filtres
  filters: SearchFilters
  setFilters: (filters: Partial<SearchFilters>) => void
  resetFilters: () => void
  applyUrlFilters: (filters: Partial<SearchFilters>) => void // ✅ NOUVEAU
  
  // Actions
  search: (query?: string) => Promise<void>
  clearSearch: () => void
  loadMore: () => Promise<void>
  
  // Pagination
  hasMore: boolean
  currentPage: number
}

const defaultFilters: SearchFilters = {
  query: '',
  category: '',
  language: 'fr',
  essential_only: false,
  difficulty: ''
}

export function useGlossarySearch(
  autoSearch = true,
  resultsPerPage = 10
): UseGlossarySearchReturn {
  
  // État principal
  const [results, setResults] = useState<GlossaryTerm[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)
  const [searchResponse, setSearchResponse] = useState<SearchResults | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  
  // Filtres
  const [filters, setFiltersState] = useState<SearchFilters>(defaultFilters)
  
  // Actions pour gérer les filtres
  const setFilters = useCallback((newFilters: Partial<SearchFilters>) => {
    console.log('🔧 setFilters called with:', newFilters)
    setFiltersState(prev => {
      const updated = { ...prev, ...newFilters }
      console.log('🔧 Updated filters:', updated)
      return updated
    })
    setCurrentPage(1) // Reset pagination
  }, [])
  
  // ✅ NOUVEAU : Fonction pour appliquer filtres depuis URL
  const applyUrlFilters = useCallback((urlFilters: Partial<SearchFilters>) => {
    console.log('🔗 applyUrlFilters called with:', urlFilters)
    setFiltersState(prev => {
      const merged = { ...prev, ...urlFilters }
      console.log('🔗 Merged filters with URL params:', merged)
      return merged
    })
    setCurrentPage(1)
    
    // Trigger search avec les nouveaux filtres après un court délai
    setTimeout(() => {
      search()
    }, 100)
  }, [])
  
  const resetFilters = useCallback(() => {
    setFiltersState(defaultFilters)
    setCurrentPage(1)
    setResults([])
    setHasSearched(false)
    setError(null)
    setSearchResponse(null)
  }, [])
  
  // Fonction de recherche principale
  const search = useCallback(async (customQuery?: string, customPage = 1) => {
    const searchQuery = customQuery !== undefined ? customQuery : filters.query
    
    console.log('🔍 Search called with:', { searchQuery, filters, page: customPage })
    
    // Si aucun critère de recherche, reset proprement
    const hasSearchCriteria = searchQuery.trim() || filters.category || filters.essential_only || filters.difficulty
    
    if (!hasSearchCriteria) {
      console.log('🔍 No search criteria, resetting state')
      setResults([])
      setHasSearched(false)
      setSearchResponse(null)
      setError(null)
      setIsLoading(false)
      return
    }
    
    setIsLoading(true)
    setError(null)
    
    try {
      // Construction des paramètres pour l'API route Next.js
      const searchParams: SearchParams = {
        lang: filters.language,
        page_size: resultsPerPage,
        page: customPage
      }
      
      // Ajouter query seulement si non vide
      if (searchQuery.trim()) {
        searchParams.q = searchQuery.trim()
      }
      
      // Ajouter les autres filtres seulement s'ils sont définis
      if (filters.category) {
        searchParams.category = filters.category
      }
      
      if (filters.essential_only) {
        searchParams.essential = true
      }
      
      if (filters.difficulty) {
        searchParams.difficulty = filters.difficulty
      }
      
      console.log('🔍 Client API params:', searchParams)
      
      const response = await glossaryClientApi.searchTerms(searchParams)
      
      console.log('🔍 Client API response:', response)
      
      if (customPage === 1) {
        setResults(response.results)
      } else {
        // Load more - append results
        setResults(prev => [...prev, ...response.results])
      }
      
      setSearchResponse(response)
      setHasSearched(true)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur de recherche'
      setError(errorMessage)
      console.error('Glossary search error:', err)
      
      // En cas d'erreur avec filtres uniquement, fallback vers recherche générale
      if (!searchQuery.trim() && (filters.category || filters.essential_only || filters.difficulty)) {
        console.log('🔍 Filter-only search failed, falling back to general search')
        setFiltersState(prev => ({ ...prev, category: '', essential_only: false, difficulty: '' }))
        setError(null)
        return
      }
      
      if (customPage === 1) {
        setResults([])
      }
      
    } finally {
      setIsLoading(false)
    }
  }, [filters, resultsPerPage])
  
  // useEffect pour la query (avec debounce)
  useEffect(() => {
    if (!autoSearch) return
    
    if (!filters.query.trim()) {
      search()
      return
    }
    
    const timeoutId = setTimeout(() => {
      console.log('🔍 Debounced search triggered for query')
      search()
    }, 300)
    
    return () => clearTimeout(timeoutId)
  }, [filters.query, autoSearch, search])
  
  // useEffect pour les autres filtres (sans debounce)
  useEffect(() => {
    if (!autoSearch) return
    
    const timeoutId = setTimeout(() => {
      console.log('🔍 Immediate search triggered for filters')
      search()
    }, 50)
    
    return () => clearTimeout(timeoutId)
  }, [filters.category, filters.essential_only, filters.difficulty, filters.language, autoSearch, search])
  
  // Clear search
  const clearSearch = useCallback(() => {
    setFilters({ query: '' })
    setResults([])
    setHasSearched(false)
    setError(null)
    setSearchResponse(null)
    setCurrentPage(1)
  }, [setFilters])
  
  // Load more (pagination)
  const loadMore = useCallback(async () => {
    if (!searchResponse?.next || isLoading) return
    
    const nextPage = currentPage + 1
    setCurrentPage(nextPage)
    search(filters.query, nextPage)
  }, [searchResponse?.next, isLoading, currentPage, search, filters.query])
  
  // Valeurs calculées
  const hasMore = useMemo(() => {
    return Boolean(searchResponse?.next)
  }, [searchResponse?.next])
  
  const totalCount = useMemo(() => {
    return searchResponse?.count || 0
  }, [searchResponse?.count])
  
  return {
    // État
    results,
    isLoading,
    error,
    hasSearched,
    totalCount,
    
    // Filtres
    filters,
    setFilters,
    resetFilters,
    applyUrlFilters, // ✅ NOUVEAU
    
    // Actions
    search,
    clearSearch,
    loadMore,
    
    // Pagination
    hasMore,
    currentPage
  }
}