// src/components/tools/glossary-search/components/RelatedTerms.tsx
'use client'

import Link from 'next/link'
import { formatters } from '../utils/formatters'
import type { GlossaryTerm } from '../types'

interface RelatedTermsProps {
  terms: GlossaryTerm[]
  currentTermId: number
  title?: string
  className?: string
}

export function RelatedTerms({ 
  terms, 
  currentTermId, 
  title = "📚 Termes liés", 
  className = '' 
}: RelatedTermsProps) {
  
  // Filtrer le terme actuel et limiter à 6 termes
  const filteredTerms = terms
    .filter(term => term.id !== currentTermId)
    .slice(0, 6)
  
  if (filteredTerms.length === 0) {
    return null
  }
  
  return (
    <section className={className}>
      <h2 className="text-2xl font-bold text-neutral-800 mb-6">
        {title}
      </h2>
      
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filteredTerms.map((term) => {
          const termTitle = formatters.getDisplayTitle(term)
          const definition = formatters.getDisplayDefinition(term)
          const termUrl = formatters.getTermUrl(term)
          
          return (
            <Link
              key={term.id}
              href={termUrl}
              className="group block p-4 bg-white border border-neutral-200 rounded-xl hover:border-brand-300 hover:shadow-lg transition-all duration-200"
            >
              <article>
                {/* Header avec badge catégorie */}
                <div className="flex items-start justify-between mb-2">
                  <span className="text-xs font-medium text-neutral-500 bg-neutral-100 px-2 py-1 rounded-full">
                    {term.category.name}
                  </span>
                  
                  {term.is_essential && (
                    <span className="text-xs font-medium text-brand-600 bg-brand-100 px-2 py-1 rounded-full">
                      ⭐
                    </span>
                  )}
                </div>
                
                {/* Titre */}
                <h3 className="font-semibold text-neutral-800 group-hover:text-brand-600 transition-colors mb-2">
                  {termTitle}
                </h3>
                
                {/* Définition tronquée */}
                {definition && (
                  <p className="text-sm text-neutral-600 line-clamp-3">
                    {formatters.truncateText(definition, 80)}
                  </p>
                )}
                
                {/* Footer avec difficulté */}
                <div className="flex items-center justify-between mt-3">
                  <span className="text-xs text-neutral-500">
                    {formatters.formatDifficulty(term.difficulty_level)}
                  </span>
                  
                  <svg className="w-4 h-4 text-brand-500 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </article>
            </Link>
          )
        })}
      </div>
    </section>
  )
}