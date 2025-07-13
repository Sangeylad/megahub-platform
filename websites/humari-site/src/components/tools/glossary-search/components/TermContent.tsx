// src/components/tools/glossary-search/components/TermContent.tsx
'use client'

import { formatters } from '../utils/formatters'
import type { GlossaryTerm } from '../types'

interface TermContentProps {
  term: GlossaryTerm
  className?: string
}

export function TermContent({ term, className = '' }: TermContentProps) {
  
  const definition = formatters.getDisplayDefinition(term)
  const examples = formatters.getDisplayExamples(term)
  const translation = formatters.getPrimaryTranslation(term)
  
  return (
    <article className={`prose prose-lg max-w-none ${className}`}>
      
      {/* Définition principale */}
      {definition && (
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-neutral-800 mb-4">
            📖 Définition
          </h2>
          <div 
            className="text-lg leading-relaxed text-neutral-700"
            dangerouslySetInnerHTML={{ __html: definition }}
          />
        </section>
      )}
      
      {/* Exemples concrets */}
      {examples && (
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-neutral-800 mb-4">
            💡 Exemples concrets
          </h2>
          <div className="p-6 bg-gradient-to-r from-brand-50 to-blue-50 rounded-xl border-l-4 border-brand-400">
            <div 
              className="text-neutral-700 leading-relaxed"
              dangerouslySetInnerHTML={{ __html: examples }}
            />
          </div>
        </section>
      )}
      
      {/* Formule (si applicable) */}
      {translation?.formula && (
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-neutral-800 mb-4">
            🧮 Formule
          </h2>
          <div className="p-6 bg-neutral-900 text-white rounded-xl">
            <code 
              className="text-green-400 text-lg"
              dangerouslySetInnerHTML={{ __html: translation.formula }}
            />
          </div>
        </section>
      )}
      
    </article>
  )
}