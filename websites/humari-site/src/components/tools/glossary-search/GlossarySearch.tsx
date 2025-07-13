// src/components/tools/glossary-search/GlossarySearch.tsx
'use client'

import { Suspense } from 'react'
import { useGlossarySearch } from './hooks/useGlossarySearch'
import { SearchInput } from './components/SearchInput'
import { CategoryFilter } from './components/CategoryFilter'
import { ResultsList } from './components/ResultsList'
import { PopularTerms } from './components/PopularTerms'
import type { GlossarySearchProps } from './types'

function SearchContent({
  variant = 'full',
  show_categories = true,
  show_popular = true,
  show_filters = true,
  popular_limit = 8,
  results_per_page = 10,
  auto_search = true,
  placeholder = 'Rechercher un terme du glossaire...'
}: Omit<GlossarySearchProps, 'className'>) {
  
  const {
    results,
    isLoading,
    error,
    hasSearched,
    totalCount,
    filters,
    setFilters,
    clearSearch,
    loadMore,
    hasMore
  } = useGlossarySearch(auto_search, results_per_page)
  
  const handleSearchChange = (query: string) => {
    console.log('🔍 Search query changed:', query) // Debug
    setFilters({ query })
  }
  
  const handleCategoryChange = (category: string) => {
    console.log('🏷️ Category filter changed:', category) // Debug
    setFilters({ category })
  }
  
  const handlePopularTermClick = (term: string) => {
    console.log('🔥 Popular term clicked:', term) // Debug
    setFilters({ query: term })
  }
  
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      
      {/* Header avec titre (mode full uniquement) */}
      {variant === 'full' && (
        <header className="text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-neutral-800 mb-4">
            🔍 Recherche dans le Glossaire Business
          </h1>
          <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
            Découvrez plus de <strong>300 définitions</strong> essentielles du marketing digital, 
            SEO, vente et business pour développer vos connaissances.
          </p>
        </header>
      )}
      
      {/* Barre de recherche principale */}
      <div className="space-y-4">
        <SearchInput
          value={filters.query}
          onChange={handleSearchChange}
          onClear={clearSearch}
          placeholder={placeholder}
          isLoading={isLoading}
        />
        
        {/* Filtres */}
        {show_filters && show_categories && (
          <div className="grid gap-4 md:grid-cols-2">
            <CategoryFilter
              selectedCategory={filters.category}
              onCategoryChange={handleCategoryChange}
            />
            
            {/* Autres filtres futurs */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-neutral-700">
                Filtres rapides
              </label>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilters({ essential_only: !filters.essential_only })}
                  className={`
                    px-3 py-2 text-sm rounded-lg border transition-colors
                    ${filters.essential_only 
                      ? 'bg-brand-100 border-brand-300 text-brand-700' 
                      : 'bg-white border-neutral-300 text-neutral-600 hover:border-brand-300'
                    }
                  `}
                >
                  ⭐ Essentiels uniquement
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Termes populaires (si pas de recherche) */}
      {show_popular && !hasSearched && !isLoading && (
        <PopularTerms
          limit={popular_limit}
          onTermClick={handlePopularTermClick}
          variant={variant === 'minimal' ? 'inline' : 'cards'}
          showTitle={variant !== 'minimal'}
        />
      )}
      
      {/* Résultats de recherche */}
      <ResultsList
        results={results}
        searchQuery={filters.query}
        isLoading={isLoading}
        error={error}
        hasSearched={hasSearched}
        totalCount={totalCount}
        hasMore={hasMore}
        onLoadMore={loadMore}
        variant={variant === 'minimal' ? 'compact' : 'default'}
      />
      
      {/* Footer avec stats (mode full uniquement) */}
      {variant === 'full' && !hasSearched && (
        <footer className="text-center bg-gradient-to-r from-neutral-50 to-neutral-100 py-8 rounded-xl border border-neutral-200">
          <p className="font-semibold text-neutral-700 mb-2">
            🔒 <strong>Recherche instantanée et sécurisée</strong> • Aucune donnée collectée
          </p>
          <p className="text-sm text-neutral-500">
            Base de données mise à jour quotidiennement avec les dernières définitions business
          </p>
        </footer>
      )}
    </div>
  )
}

export function GlossarySearch({ className = '', ...props }: GlossarySearchProps) {
  return (
    <div className={className}>
      <Suspense fallback={
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse space-y-8">
            <div className="h-16 bg-neutral-200 rounded-xl"></div>
            <div className="h-64 bg-neutral-200 rounded-xl"></div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="h-32 bg-neutral-200 rounded-xl"></div>
              <div className="h-32 bg-neutral-200 rounded-xl"></div>
            </div>
          </div>
        </div>
      }>
        <SearchContent {...props} />
      </Suspense>
    </div>
  )
}