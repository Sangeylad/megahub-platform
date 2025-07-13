// src/components/tools/glossary-search/hooks/useCategories.ts
'use client'

import { useState, useEffect } from 'react'
import { glossaryClientApi } from '@/lib/api/glossary-client'
import type { GlossaryCategory } from '../types'

interface UseCategoriesReturn {
  categories: GlossaryCategory[]
  isLoading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export function useCategories(): UseCategoriesReturn {
  const [categories, setCategories] = useState<GlossaryCategory[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const fetchCategories = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await glossaryClientApi.getCategories()
      setCategories(response.results)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erreur de chargement des catégories'
      setError(errorMessage)
      console.error('Categories fetch error:', err)
      
    } finally {
      setIsLoading(false)
    }
  }
  
  useEffect(() => {
    fetchCategories()
  }, [])
  
  return {
    categories,
    isLoading,
    error,
    refetch: fetchCategories
  }
}