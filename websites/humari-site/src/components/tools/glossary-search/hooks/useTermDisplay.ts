// src/components/tools/glossary-search/hooks/useTermDisplay.ts
'use client'

import { useState, useEffect, useCallback } from 'react'
import { glossaryClientApi } from '@/lib/api/glossary-client'
import type { GlossaryTerm } from '../types'

interface UseTermDisplayOptions {
  enabled?: boolean
}

interface UseTermDisplayReturn {
  term: GlossaryTerm | null
  relatedTerms: GlossaryTerm[]
  isLoading: boolean
  error: string | null
  refetch: () => Promise<void>
  notFound: boolean
}

export function useTermDisplay(
  slug: string,
  language = 'fr',
  options: UseTermDisplayOptions = {}
): UseTermDisplayReturn {
  
  const { enabled = true } = options
  
  const [term, setTerm] = useState<GlossaryTerm | null>(null)
  const [relatedTerms, setRelatedTerms] = useState<GlossaryTerm[]>([])
  const [isLoading, setIsLoading] = useState(enabled && !!slug)
  const [error, setError] = useState<string | null>(null)
  const [notFound, setNotFound] = useState(false)

  const fetchTerm = useCallback(async () => {
    if (!slug || !enabled) {
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    setError(null)
    setNotFound(false)

    try {
      console.log('🔍 useTermDisplay: Fetching term:', slug)

      const termData = await glossaryClientApi.getTermBySlug(slug, language)
      setTerm(termData)

      if (termData.related_terms && termData.related_terms.length > 0) {
        setRelatedTerms(termData.related_terms)
      } else {
        try {
          const relatedByCategory = await glossaryClientApi.searchTerms({
            category: termData.category.slug,
            page_size: 6,
            lang: language
          })

          const filtered = relatedByCategory.results.filter(t => t.id !== termData.id)
          setRelatedTerms(filtered.slice(0, 5))
        } catch {
          setRelatedTerms([])
        }
      }

    } catch (err) {
      console.error('Term fetch error:', err)

      if (err instanceof Error && err.message.includes('404')) {
        setNotFound(true)
        setError('Terme non trouvé')
      } else {
        setError(err instanceof Error ? err.message : 'Erreur de chargement')
      }

    } finally {
      setIsLoading(false)
    }
  }, [slug, language, enabled])

  useEffect(() => {
    if (enabled) {
      fetchTerm()
    }
  }, [fetchTerm, enabled])

  return {
    term,
    relatedTerms,
    isLoading,
    error,
    refetch: fetchTerm,
    notFound
  }
}