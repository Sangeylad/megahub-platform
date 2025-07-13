// src/components/tools/glossary-search/components/TermCard.tsx
'use client'

import Link from 'next/link'
import { formatters } from '../utils/formatters'
import type { GlossaryTerm } from '../types'

interface TermCardProps {
  term: GlossaryTerm
  searchQuery?: string
  variant?: 'default' | 'compact' | 'detailed'
  className?: string
}

export function TermCard({ 
  term, 
  searchQuery = '', 
  variant = 'default',
  className = ''
}: TermCardProps) {
  
  const title = formatters.getDisplayTitle(term)
  const definition = formatters.getDisplayDefinition(term)
  const examples = formatters.getDisplayExamples(term)
  const termUrl = formatters.getTermUrl(term)
  
  const highlightText = (text: string) => {
    if (!searchQuery) return text
    return formatters.highlightSearchTerm(text, searchQuery)
  }
  
  return (
    <Link href={termUrl} className="block">
      <article className={`
        bg-white border border-neutral-200 rounded-xl p-6 hover:border-brand-300 
        hover:shadow-lg transition-all duration-300 group cursor-pointer
        ${className}
      `}>
        
        {/* Header */}
        <header className="mb-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h3 
                className="text-xl font-bold text-neutral-800 group-hover:text-brand-600 transition-colors"
                dangerouslySetInnerHTML={{ __html: highlightText(title) }}
              />
              
              <div className="flex items-center gap-3 mt-2">
                {/* Catégorie */}
                <span className="px-3 py-1 text-xs font-medium bg-neutral-100 text-neutral-600 rounded-full">
                  📂 {term.category.name}
                </span>
                
                {/* Badge essentiel */}
                {term.is_essential && (
                  <span className="px-3 py-1 text-xs font-medium bg-brand-100 text-brand-700 rounded-full">
                    ⭐ Essentiel
                  </span>
                )}
                
                {/* Difficulté */}
                <span className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                  {formatters.formatDifficulty(term.difficulty_level)}
                </span>
              </div>
            </div>
          </div>
        </header>
        
        {/* Définition */}
        {definition && (
          <div className="mb-4">
            <p 
              className="text-neutral-700 leading-relaxed"
              dangerouslySetInnerHTML={{ 
                __html: highlightText(formatters.truncateText(definition, variant === 'compact' ? 120 : 200))
              }}
            />
          </div>
        )}
        
        {/* Exemples (seulement en mode detailed) */}
        {variant === 'detailed' && examples && (
          <div className="mb-4 p-4 bg-neutral-50 rounded-lg border-l-4 border-brand-400">
            <h4 className="text-sm font-semibold text-neutral-800 mb-2">💡 Exemple concret</h4>
            <p 
              className="text-sm text-neutral-600 italic"
              dangerouslySetInnerHTML={{ 
                __html: highlightText(formatters.truncateText(examples, 150))
              }}
            />
          </div>
        )}
        
        {/* Footer */}
        <footer className="flex items-center justify-between">
          <span className="
            inline-flex items-center gap-2 text-brand-600 group-hover:text-brand-700 
            font-medium transition-colors duration-200
          ">
            Voir la définition complète
            <svg className="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </span>
          
          {/* Termes liés */}
          {term.related_terms && term.related_terms.length > 0 && (
            <div className="text-sm text-neutral-500">
              {term.related_terms.length} terme{term.related_terms.length > 1 ? 's' : ''} lié{term.related_terms.length > 1 ? 's' : ''}
            </div>
          )}
        </footer>
      </article>
    </Link>
  )
}