'use client'

import Link from 'next/link'
import { usePopularTerms } from '../hooks/usePopularTerms'
import { formatters } from '../utils/formatters'
import { LoadingSpinner } from './shared/LoadingSpinner'

interface PopularTermsProps {
  limit?: number
  onTermClick?: (term: string) => void
  variant?: 'list' | 'inline' | 'cards'
  showTitle?: boolean
  title?: string
  className?: string
}

export function PopularTerms({ 
  limit = 8,
  onTermClick,
  variant = 'inline',
  showTitle = true,
  title = '🔥 Termes populaires',
  className = ''
}: PopularTermsProps) {
  
  const { popularTerms, isLoading, error } = usePopularTerms(limit)
  
  if (isLoading) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <LoadingSpinner size="medium" />
        <p className="text-neutral-600 mt-2">Chargement des termes populaires...</p>
      </div>
    )
  }
  
  if (error || popularTerms.length === 0) {
    return null
  }
  
  const handleTermClick = (term: string) => {
    if (onTermClick) {
      onTermClick(term)
    }
  }
  
  return (
    <section className={className}>
      {showTitle && (
        <h3 className="text-lg font-semibold text-neutral-800 mb-4">
          {title}
        </h3>
      )}
      
      {variant === 'inline' && (
        <div className="flex flex-wrap gap-2">
          {popularTerms.map((term) => {
            const title = formatters.getDisplayTitle(term)
            return (
              <button
                key={term.id}
                onClick={() => handleTermClick(title)}
                className="
                  inline-flex items-center gap-2 px-4 py-2 bg-neutral-100 hover:bg-brand-100 
                  text-neutral-700 hover:text-brand-700 rounded-full text-sm font-medium
                  transition-all duration-200 hover:shadow-md
                "
              >
                {title}
                {/* ✅ SUPPRESSION DU SCORE ICI AUSSI */}
              </button>
            )
          })}
        </div>
      )}
      
      {variant === 'list' && (
        <div className="space-y-3">
          {popularTerms.map((term) => {
            const title = formatters.getDisplayTitle(term)
            const definition = formatters.getDisplayDefinition(term)
            const termUrl = formatters.getTermUrl(term)
            
            return (
              <div key={term.id} className="border-l-4 border-brand-400 pl-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-neutral-800">
                      <Link href={termUrl} className="hover:text-brand-600 transition-colors">
                        {title}
                      </Link>
                    </h4>
                    {definition && (
                      <p className="text-sm text-neutral-600 mt-1">
                        {formatters.truncateText(definition, 80)}
                      </p>
                    )}
                  </div>
                  {/* ✅ SUPPRESSION DU SCORE ICI AUSSI */}
                </div>
              </div>
            )
          })}
        </div>
      )}
      
      {variant === 'cards' && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {popularTerms.map((term) => {
            const title = formatters.getDisplayTitle(term)
            const definition = formatters.getDisplayDefinition(term)
            const termUrl = formatters.getTermUrl(term)
            
            return (
              <div key={term.id} className="bg-white border border-neutral-200 rounded-lg p-4 hover:border-brand-300 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-neutral-800 flex-1">
                    <Link href={termUrl} className="hover:text-brand-600 transition-colors">
                      {title}
                    </Link>
                  </h4>
                  {/* ✅ SUPPRESSION DU SCORE ICI AUSSI */}
                </div>
                
                <span className="text-xs text-neutral-500 bg-neutral-100 px-2 py-1 rounded-full">
                  {term.category.name}
                </span>
                
                {definition && (
                  <p className="text-sm text-neutral-600 mt-2">
                    {formatters.truncateText(definition, 60)}
                  </p>
                )}
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}