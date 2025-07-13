// src/components/tools/glossary-search/components/ResultsList.tsx
'use client'

import { TermCard } from './TermCard'
import { LoadingSpinner } from './shared/LoadingSpinner'
import { EmptyState } from './shared/EmptyState'
import type { GlossaryTerm } from '../types'

interface ResultsListProps {
  results: GlossaryTerm[]
  searchQuery: string
  isLoading: boolean
  error: string | null
  hasSearched: boolean
  totalCount: number
  hasMore: boolean
  onLoadMore: () => void
  variant?: 'default' | 'compact' | 'detailed'
  className?: string
}

export function ResultsList({
  results,
  searchQuery,
  isLoading,
  error,
  hasSearched,
  totalCount,
  hasMore,
  onLoadMore,
  variant = 'default',
  className = ''
}: ResultsListProps) {
  
  // État d'erreur
  if (error) {
    return (
      <EmptyState 
        type="error" 
        message={error}
        actionButton={
          <button 
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-brand-500 text-white rounded-lg hover:bg-brand-600 transition-colors"
          >
            Réessayer
          </button>
        }
        className={className}
      />
    )
  }
  
  // Pas encore de recherche
  if (!hasSearched && !isLoading) {
    return (
      <EmptyState 
        type="no-search"
        className={className}
      />
    )
  }
  
  // Recherche en cours (première fois)
  if (isLoading && results.length === 0) {
    return (
      <div className={`flex items-center justify-center py-12 ${className}`}>
        <div className="text-center">
          <LoadingSpinner size="large" className="mb-4" />
          <p className="text-neutral-600">Recherche en cours...</p>
        </div>
      </div>
    )
  }
  
  // Aucun résultat
  if (hasSearched && results.length === 0 && !isLoading) {
    return (
      <EmptyState 
        type="no-results"
        message={`Aucun terme trouvé pour &quot;${searchQuery}&quot;`}
        className={className}
      />
    )
  }
  
  return (
    <div className={className}>
      {/* Header des résultats */}
      {hasSearched && totalCount > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-neutral-800">
            📝 {totalCount} résultat{totalCount > 1 ? 's' : ''} trouvé{totalCount > 1 ? 's' : ''}
            {searchQuery && (
              <span className="font-normal text-neutral-600">
                {' '}pour &quot;{searchQuery}&quot;
              </span>
            )}
          </h3>
        </div>
      )}
      
      {/* Liste des résultats */}
      <div className="space-y-6">
        {results.map((term) => (
          <TermCard
            key={term.id}
            term={term}
            searchQuery={searchQuery}
            variant={variant}
          />
        ))}
      </div>
      
      {/* Bouton Load More */}
      {hasMore && (
        <div className="text-center mt-8">
          <button
            onClick={onLoadMore}
            disabled={isLoading}
            className="
              inline-flex items-center gap-3 px-6 py-3 bg-brand-500 text-white 
              font-medium rounded-xl hover:bg-brand-600 transition-colors duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            {isLoading ? (
              <>
                <LoadingSpinner size="small" />
                Chargement...
              </>
            ) : (
              <>
                Charger plus de résultats
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}